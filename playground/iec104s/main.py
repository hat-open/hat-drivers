from pathlib import Path
import asyncio
import contextlib
import ssl

import cryptography.hazmat.primitives.hmac
import cryptography.hazmat.primitives.hashes

from hat import aio

from hat.drivers import tcp
from hat.drivers.iec60870 import apci
from hat.drivers.iec60870.msgs import iec104
from hat.drivers.iec60870.msgs import security


class Connection(aio.Resource):

    def __init__(self, conn):
        self._conn = conn
        self._encoder = security.encoder.Encoder(iec104.encoder.Encoder())

    @property
    def async_group(self):
        return self._conn.async_group

    @property
    def encoder(self):
        return self._encoder

    def send(self, asdu):
        for asdu_bytes in self._encoder.encode_asdu(asdu):
            self._conn.send(asdu_bytes)

    async def receive(self):
        asdu = None
        asdu_bytes = None
        while not asdu:
            asdu_bytes = await self._conn.receive()
            asdu, _ = self._encoder.decode_asdu(asdu_bytes)
        return asdu, asdu_bytes


def main():
    aio.init_asyncio()
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main())


async def async_main():
    await run_slave()


async def run_master():
    addr = tcp.Address('', 2404)
    ssl_ctx = None
    apci_conn = await apci.connect(addr)
    conn = Connection(apci_conn, ssl_ctx=ssl_ctx)


async def run_slave():
    # 192.168.28.200
    addr = tcp.Address('0.0.0.0', 19998)
    ssl_ctx = None  # create_ssl_ctx()
    conn_queue = aio.Queue()
    srv = await apci.listen(conn_queue.put_nowait, addr, ssl_ctx=ssl_ctx)
    conn = await conn_queue.get()
    conn = Connection(conn)

    print('>> nova veza')

    session_slave_key = None
    session_master_key = None
    local_sequence = 0
    remote_sequence = 0
    key_status = security.common.KeyStatus.NOT_INIT
    update_key = (Path(__file__).parent / 'certs/update_key').read_bytes()
    last_key_challange_data = b'x' * 20

    while True:
        asdu, asdu_bytes = await conn.receive()
        print('>>', asdu)

        if asdu.type == iec104.common.AsduType.C_IC_NA:
            res = create_c_ic_na(
                iec104.common.CauseType.ACTIVATION_CONFIRMATION, asdu.address,
                asdu.ios[0].address, asdu.ios[0].elements[0].qualifier)
            print('++', res)
            conn.send(res)

            res = create_m_sp_na(iec104.common.CauseType.INTERROGATED_STATION,
                                 asdu.address, 1, iec104.common.SingleValue.ON)
            print('++', res)
            conn.send(res)

            res = create_c_ic_na(
                iec104.common.CauseType.ACTIVATION_TERMINATION, asdu.address,
                asdu.ios[0].address, asdu.ios[0].elements[0].qualifier)
            print('++', res)
            conn.send(res)

        if asdu.type == security.common.AsduType.S_KR_NA:
            local_sequence += 1
            last_key_challange_data = b'x' * 20
            res = create_s_ks_na(1, local_sequence, 1,
                                 security.common.KeyWrapAlgorithm.AES_128,
                                 key_status,
                                 security.common.MacAlgorithm.NO_MAC,
                                 last_key_challange_data, b'')
            print('++', res)
            conn.send(res)

        if asdu.type == security.common.AsduType.S_KC_NA:
            pass

        if asdu.type == security.common.AsduType.C_TS_NA:
            pass

        if asdu.type == security.common.AsduType.S_RP_NA:
            pass


def calculate_mac(data, key):
    h = cryptography.hazmat.primitives.hmac.HMAC(
        key, cryptography.hazmat.primitives.hashes.SHA256())
    h.update(data)
    return h.finalize()


def create_ssl_ctx(path=Path(__file__).parent / 'certs/server_cert.pem'):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.VerifyMode.CERT_NONE
    ctx.load_cert_chain(certfile=str(path))
    return ctx


def create_c_ic_na(cause_type, asdu_address, io_address, qualifier):
    cause = iec104.common.Cause(type=cause_type,
                                is_negative_confirm=False,
                                is_test=False,
                                originator_address=0)
    element = iec104.common.IoElement_C_IC_NA(qualifier)
    io = iec104.common.IO(address=io_address,
                          elements=[element],
                          time=None)
    return iec104.common.ASDU(type=iec104.common.AsduType.C_IC_NA,
                              cause=cause,
                              address=asdu_address,
                              ios=[io])


def create_m_sp_na(cause_type, asdu_address, io_address, value):
    cause = iec104.common.Cause(type=cause_type,
                                is_negative_confirm=False,
                                is_test=False,
                                originator_address=0)
    quality = iec104.common.IndicationQuality(invalid=False,
                                              not_topical=False,
                                              substituted=False,
                                              blocked=False)
    element = iec104.common.IoElement_M_SP_NA(value=value,
                                              quality=quality)
    io = iec104.common.IO(address=io_address,
                          elements=[element],
                          time=None)
    return iec104.common.ASDU(type=iec104.common.AsduType.M_SP_NA,
                              cause=cause,
                              address=asdu_address,
                              ios=[io])


# session key status request
def create_s_kr_na(asdu_address, user):
    element = security.common.IoElement_S_KR_NA(user=user)
    return create_s_xx_na(security.common.AsduType.S_KR_NA,
                          security.common.CauseType.SESSION_KEY_MAINTENANCE,
                          asdu_address, element)


# session key status
def create_s_ks_na(asdu_address, sequence, user, key_wrap_algorithm,
                   key_status, mac_algorithm, data, mac):
    element = security.common.IoElement_S_KS_NA(
        sequence=sequence,
        user=user,
        key_wrap_algorithm=key_wrap_algorithm,
        key_status=key_status,
        mac_algorithm=mac_algorithm,
        data=data,
        mac=mac)
    return create_s_xx_na(security.common.AsduType.S_KS_NA,
                          security.common.CauseType.SESSION_KEY_MAINTENANCE,
                          asdu_address, element)


# session key change
def create_s_kc_na(asdu_address, sequence, user, wrapped_key):
    element = security.common.IoElement_S_KC_NA(
        sequence=sequence,
        user=user,
        wrapped_key=wrapped_key)
    return create_s_xx_na(security.common.AsduType.S_KC_NA,
                          security.common.CauseType.SESSION_KEY_MAINTENANCE,
                          asdu_address, element)


# authentication challenge
def create_s_ch_na(asdu_address, sequence, user, mac_algorithm, data):
    element = security.common.IoElement_S_CH_NA(
        sequence=sequence,
        user=user,
        mac_algorithm=mac_algorithm,
        reason=1,
        data=data)
    return create_s_xx_na(security.common.AsduType.S_CH_NA,
                          security.common.CauseType.AUTHENTICATION,
                          asdu_address, element)


# authentication reply
def create_s_rp_na(asdu_address, sequence, user, mac):
    element = security.common.IoElement_S_RP_NA(
        sequence=sequence,
        user=user,
        mac=mac)
    return create_s_xx_na(security.common.AsduType.S_RP_NA,
                          security.common.CauseType.AUTHENTICATION,
                          asdu_address, element)


# aggressive mode authentication request
def create_s_ar_na(asdu_address, asdu, sequence, user, mac):
    element = security.common.IoElement_S_AR_NA(
        asdu=asdu,
        sequence=sequence,
        user=user,
        mac=mac)
    return create_s_xx_na(security.common.AsduType.S_AR_NA,
                          security.common.CauseType.AUTHENTICATION,
                          asdu_address, element)


def create_s_xx_na(asdu_type, cause_type, asdu_address, element):
    cause = security.common.Cause(type=cause_type,
                                  is_negative_confirm=False,
                                  is_test=False,
                                  originator_address=0)
    io = security.common.IO(address=None,
                            element=element,
                            time=None)
    return security.common.ASDU(type=asdu_type,
                                cause=cause,
                                address=asdu_address,
                                ios=[io])


if __name__ == '__main__':
    main()
