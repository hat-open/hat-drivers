from collections.abc import Collection
import asyncio
import datetime
import math
import pytest

from hat import aio
from hat import util

from hat.drivers import iec61850
from hat.drivers import mms
from hat.drivers import tcp


@pytest.fixture
async def mms_srv_addr():
    return tcp.Address('127.0.0.1', util.get_unused_tcp_port())


def assert_equal(value, expected_value):
    if isinstance(value, float):
        assert math.isclose(value, expected_value, rel_tol=1e-3)
    elif isinstance(value, (tuple, list)):
        for v, exp_v in zip(value, expected_value):
            assert_equal(v, exp_v)
    else:
        assert value == expected_value


async def test_connect(mms_srv_addr):
    mms_conn_queue = aio.Queue()
    mms_srv = await mms.listen(connection_cb=mms_conn_queue.put_nowait,
                               addr=mms_srv_addr)

    conn = await iec61850.connect(addr=mms_srv_addr)
    assert conn.is_open

    mms_conn = await mms_conn_queue.get()

    conn.close()
    assert not conn.is_open
    await conn.wait_closing()
    assert conn.is_closing
    await conn.wait_closed()
    assert conn.is_closed

    await mms_conn.wait_closed()

    await mms_srv.async_close()


async def test_conn_status_loop(mms_srv_addr):
    mms_conn_queue = aio.Queue()
    mms_conn_req_queue = aio.Queue()

    def on_request(conn, request):
        mms_conn_req_queue.put_nowait((conn, request))
        return mms.StatusResponse(logical=1, physical=1)

    mms_srv = await mms.listen(
        connection_cb=mms_conn_queue.put_nowait,
        addr=mms_srv_addr,
        request_cb=on_request)

    conn = await iec61850.connect(addr=mms_srv_addr,
                                  status_delay=0.01,
                                  status_timeout=0.1)

    mms_conn = await mms_conn_queue.get()

    for _ in range(3):
        mms_conn_req, req = await mms_conn_req_queue.get()
        assert mms_conn_req == mms_conn
        assert req == mms.StatusRequest()

    await conn.async_close()
    await mms_srv.async_close()


async def test_conn_status_late_response(mms_srv_addr):
    mms_conn_queue = aio.Queue()
    mms_conn_req_queue = aio.Queue()

    async def on_request(conn, request):
        mms_conn_req_queue.put_nowait((conn, request))
        await asyncio.sleep(0.1)
        return mms.StatusResponse(logical=1, physical=1)

    mms_srv = await mms.listen(
        connection_cb=mms_conn_queue.put_nowait,
        addr=mms_srv_addr,
        request_cb=on_request)

    conn = await iec61850.connect(addr=mms_srv_addr,
                                  status_delay=0.01,
                                  status_timeout=0.05)

    mms_conn = await mms_conn_queue.get()

    await mms_conn_req_queue.get()

    await conn.wait_closed()
    await mms_conn.wait_closed()
    assert mms_conn_req_queue.empty()

    await mms_srv.async_close()


@pytest.mark.timeout(1)
async def test_conn_close_on_mms_closed(mms_srv_addr):

    def on_request(conn, request):
        return mms.StatusResponse(logical=1, physical=1)

    mms_srv = await mms.listen(
        connection_cb=lambda _: None,
        addr=mms_srv_addr,
        request_cb=on_request,
        bind_connections=True)

    conn = await iec61850.connect(addr=mms_srv_addr,
                                  status_delay=0.05,
                                  status_timeout=0.1)

    mms_srv.close()
    await conn.wait_closed()

    await mms_srv.async_close()


@pytest.mark.parametrize("dataset_ref, data_refs, mms_request", [
     (iec61850.NonPersistedDatasetRef("ds_xyz"),
      [iec61850.DataRef(
         logical_device='ld',
         logical_node='ln',
         fc='ST',
         names=('d', 'a1')),
       iec61850.DataRef(
          logical_device='ld',
          logical_node='ln',
          fc='ST',
          names=('d', 'a2'))],
      mms.DefineNamedVariableListRequest(
         name=mms.AaSpecificObjectName(identifier="ds_xyz"),
         specification=[
             mms.NameVariableSpecification(
                mms.DomainSpecificObjectName(
                    domain_id='ld',
                    item_id='ln$ST$d$a1')),
             mms.NameVariableSpecification(
                mms.DomainSpecificObjectName(
                    domain_id='ld',
                    item_id='ln$ST$d$a2'))])),

     (iec61850.PersistedDatasetRef(logical_device='ld',
                                   logical_node='ln',
                                   name='ds_xyz'),
      [iec61850.DataRef(logical_device='ld',
                        logical_node='ln',
                        fc='ST',
                        names=('d', '1')),
       iec61850.DataRef(logical_device='ld',
                        logical_node='ln',
                        fc='FC',
                        names=('d', '2'))],
      mms.DefineNamedVariableListRequest(
         name=mms.DomainSpecificObjectName(
            domain_id="ld",
            item_id="ln$ds_xyz"),
         specification=[
             mms.NameVariableSpecification(
                mms.DomainSpecificObjectName(
                    domain_id="ld",
                    item_id="ln$ST$d$1")),
             mms.NameVariableSpecification(
                mms.DomainSpecificObjectName(
                    domain_id="ld",
                    item_id="ln$FC$d$2"))]))
])
@pytest.mark.parametrize("mms_response, response", [
    (mms.DefineNamedVariableListResponse(), None),

    (mms.AccessError.OBJECT_NON_EXISTENT,
     iec61850.ServiceError.INSTANCE_NOT_AVAILABLE),

    (mms.AccessError.OBJECT_ACCESS_DENIED,
     iec61850.ServiceError.ACCESS_VIOLATION),

    (mms.DefinitionError.OBJECT_EXISTS,
     iec61850.ServiceError.INSTANCE_IN_USE),

    (mms.DefinitionError.OBJECT_UNDEFINED,
     iec61850.ServiceError.PARAMETER_VALUE_INCONSISTENT),

    (mms.ResourceError.CAPABILITY_UNAVAILABLE,
     iec61850.ServiceError.FAILED_DUE_TO_SERVER_CONSTRAINT),

    # any class any, unmapped error codes
    (mms.ApplicationReferenceError.OTHER,
     iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT),

    # TODO: add MMS Reject, when added to mms
])
async def test_create_dataset(mms_srv_addr, dataset_ref, data_refs,
                              mms_request, mms_response, response):
    request_queue = aio.Queue()

    def on_request(conn, req):
        request_queue.put_nowait(req)
        return mms_response

    mms_srv = await mms.listen(
        connection_cb=lambda _: None,
        addr=mms_srv_addr,
        request_cb=on_request)

    conn = await iec61850.connect(addr=mms_srv_addr)

    resp = await conn.create_dataset(ref=dataset_ref, data=data_refs)
    assert resp == response

    req = await request_queue.get()
    assert req == mms_request

    await conn.async_close()
    await mms_srv.async_close()


@pytest.mark.parametrize("dataset_ref, mms_request", [
    (iec61850.PersistedDatasetRef(logical_device='ld',
                                  logical_node='ln',
                                  name='ds_xyz'),
     mms.DeleteNamedVariableListRequest(names=[
        mms.DomainSpecificObjectName(
            domain_id="ld",
            item_id="ln$ds_xyz")])),

    (iec61850.NonPersistedDatasetRef('ds_xyz'),
     mms.DeleteNamedVariableListRequest([mms.AaSpecificObjectName("ds_xyz")])),
    ])
@pytest.mark.parametrize("mms_response, response", [
    (mms.DeleteNamedVariableListResponse(matched=1,
                                         deleted=1),
     None),

    (mms.DeleteNamedVariableListResponse(matched=0,
                                         deleted=0),
     iec61850.ServiceError.INSTANCE_NOT_AVAILABLE),

    (mms.DeleteNamedVariableListResponse(matched=1,
                                         deleted=0),
     iec61850.ServiceError.FAILED_DUE_TO_SERVER_CONSTRAINT),

    (mms.DeleteNamedVariableListResponse(matched=0,
                                         deleted=1),
     iec61850.ServiceError.FAILED_DUE_TO_SERVER_CONSTRAINT),

    (mms.DeleteNamedVariableListResponse(matched=1,
                                         deleted=13),
     iec61850.ServiceError.FAILED_DUE_TO_SERVER_CONSTRAINT),

    (mms.AccessError.OBJECT_NON_EXISTENT,
     iec61850.ServiceError.INSTANCE_NOT_AVAILABLE),

    (mms.AccessError.OBJECT_ACCESS_DENIED,
     iec61850.ServiceError.ACCESS_VIOLATION),

    # any class any, unmapped error codes
    (mms.ServicePreemptError.DEADLOCK,
     iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT),
    ])
async def test_delete_dataset(mms_srv_addr, dataset_ref, mms_request,
                              mms_response, response):
    request_queue = aio.Queue()

    def on_request(conn, req):
        request_queue.put_nowait(req)
        return mms_response

    mms_srv = await mms.listen(
        connection_cb=lambda _: None,
        addr=mms_srv_addr,
        request_cb=on_request)

    conn = await iec61850.connect(addr=mms_srv_addr)

    resp = await conn.delete_dataset(ref=dataset_ref)
    assert resp == response

    req = await request_queue.get()
    assert req == mms_request

    await conn.async_close()
    await mms_srv.async_close()


@pytest.mark.parametrize('logical_device, mms_res, response', [
    ('ld1',
     mms.GetNameListResponse(identifiers=[],
                             more_follows=False),
     []),

    ('ld2',
     mms.GetNameListResponse(identifiers=['ln1$ds1', 'ln2$ds2'],
                             more_follows=False),
     [iec61850.PersistedDatasetRef(logical_device='ld2',
                                   logical_node='ln1',
                                   name='ds1'),
      iec61850.PersistedDatasetRef(logical_device='ld2',
                                   logical_node='ln2',
                                   name='ds2')]),

    ('ld',
     mms.AccessError.OBJECT_NON_EXISTENT,
     iec61850.ServiceError.INSTANCE_NOT_AVAILABLE),

    ('ld',
     mms.AccessError.OBJECT_ACCESS_DENIED,
     iec61850.ServiceError.ACCESS_VIOLATION),

    ('ld',
     mms.ServiceError.OBJECT_CONSTRAINT_CONFLICT,
     iec61850.ServiceError.PARAMETER_VALUE_INCONSISTENT),

    ('ld',
     mms.ConcludeError.FURTHER_COMMUNICATION_REQUIRED,
     iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT)
])
async def test_get_persisted_dataset_refs(mms_srv_addr, logical_device,
                                          mms_res, response):

    def on_request(conn, req):
        assert req == mms.GetNameListRequest(
            object_class=mms.ObjectClass.NAMED_VARIABLE_LIST,
            object_scope=mms.DomainSpecificObjectScope(logical_device),
            continue_after=None)

        return mms_res

    mms_srv = await mms.listen(
        connection_cb=lambda _: None,
        addr=mms_srv_addr,
        request_cb=on_request)

    conn = await iec61850.connect(addr=mms_srv_addr)

    resp = await conn.get_persisted_dataset_refs(logical_device)
    if not isinstance(resp, iec61850.ServiceError):
        resp = list(resp)
    assert resp == response

    await conn.async_close()
    await mms_srv.async_close()


@pytest.mark.parametrize("dataset_ref, mms_request", [
    (iec61850.NonPersistedDatasetRef('nonp_ds1'),
     mms.GetNamedVariableListAttributesRequest(
        mms.AaSpecificObjectName(identifier="nonp_ds1"))),

    (iec61850.PersistedDatasetRef(logical_device='ld_xyz',
                                  logical_node='ln1',
                                  name='ds_1'),
     mms.GetNamedVariableListAttributesRequest(
        mms.DomainSpecificObjectName(
            domain_id='ld_xyz',
            item_id="ln1$ds_1"))),
    ])
@pytest.mark.parametrize("mms_response, response", [
    (mms.GetNamedVariableListAttributesResponse(
        mms_deletable=True,
        specification=[
            mms.NameVariableSpecification(
                mms.DomainSpecificObjectName(
                    domain_id="ld_abc",
                    item_id="ln2$ST$d$1")),
            mms.NameVariableSpecification(
                mms.DomainSpecificObjectName(
                    domain_id="ld_def",
                    item_id="ln3$MX$d$2"))]),
     [iec61850.DataRef(logical_device='ld_abc',
                       logical_node='ln2',
                       fc='ST',
                       names=('d', '1')),
      iec61850.DataRef(logical_device='ld_def',
                       logical_node='ln3',
                       fc='MX',
                       names=('d', '2'))]),

    (mms.GetNamedVariableListAttributesResponse(
        mms_deletable=True,
        specification=[
            mms.NameVariableSpecification(
                mms.DomainSpecificObjectName(
                    domain_id="ld1",
                    item_id="ln2$MX$d(2)$1"))]),
     [iec61850.DataRef(logical_device='ld1',
                       logical_node='ln2',
                       fc='MX',
                       names=('d', 2, '1'))]),

    (mms.AccessError.OBJECT_NON_EXISTENT,
     iec61850.ServiceError.INSTANCE_NOT_AVAILABLE),

    (mms.AccessError.OBJECT_ACCESS_DENIED,
     iec61850.ServiceError.ACCESS_VIOLATION),

    (mms.ServiceError.PDU_SIZE,  # pdu-size in version 1, reserved in ver 2
     iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT),

    # any class any, unmapped error codes
    (mms.VmdStateError.VMD_STATE_CONFLICT,
     iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT),
    ])
async def test_get_dataset_data_refs(mms_srv_addr, dataset_ref, mms_request,
                                     mms_response, response):
    request_queue = aio.Queue()

    def on_request(conn, req):
        request_queue.put_nowait(req)
        return mms_response

    mms_srv = await mms.listen(
        connection_cb=lambda _: None,
        addr=mms_srv_addr,
        request_cb=on_request)

    conn = await iec61850.connect(addr=mms_srv_addr)

    resp = await conn.get_dataset_data_refs(dataset_ref)

    if isinstance(resp, Collection):
        for data_ref, exp_data_ref in zip(resp, response):
            assert data_ref.logical_device == exp_data_ref.logical_device
            assert data_ref.logical_node == exp_data_ref.logical_node
            assert data_ref.fc == exp_data_ref.fc
            assert data_ref.names == exp_data_ref.names
    else:
        assert resp == response

    req = await request_queue.get()
    assert req == mms_request

    await conn.async_close()
    await mms_srv.async_close()


@pytest.mark.parametrize('rcb_type', iec61850.RcbType)
@pytest.mark.parametrize('rcb_attr_type, mms_response, rcb_attr_value', [
    (iec61850.RcbAttrType.REPORT_ID,
     mms.ReadResponse([mms.VisibleStringData('rpt_xyz')]),
     'rpt_xyz'),

    (iec61850.RcbAttrType.REPORT_ENABLE,
     mms.ReadResponse([mms.BooleanData(True)]),
     True),

    (iec61850.RcbAttrType.DATASET,
     mms.ReadResponse([mms.VisibleStringData("ld/ln$ds")]),
     iec61850.PersistedDatasetRef(logical_device='ld',
                                  logical_node='ln',
                                  name='ds')),

    (iec61850.RcbAttrType.DATASET,
     mms.ReadResponse([mms.VisibleStringData("@ds")]),
     iec61850.NonPersistedDatasetRef('ds')),

    (iec61850.RcbAttrType.CONF_REVISION,
     mms.ReadResponse([mms.UnsignedData(123)]),
     123),

    (iec61850.RcbAttrType.OPTIONAL_FIELDS,
     mms.ReadResponse([mms.BitStringData([False, *([True] * 8), False])]),
     set(iec61850.OptionalField)),

    (iec61850.RcbAttrType.BUFFER_TIME,
     mms.ReadResponse([mms.UnsignedData(3)]),
     3),

    (iec61850.RcbAttrType.SEQUENCE_NUMBER,
     mms.ReadResponse([mms.UnsignedData(456)]),
     456),

    (iec61850.RcbAttrType.TRIGGER_OPTIONS,
     mms.ReadResponse([mms.BitStringData([False, *([True] * 5)])]),
     set(iec61850.TriggerCondition)),

    (iec61850.RcbAttrType.INTEGRITY_PERIOD,
     mms.ReadResponse([mms.UnsignedData(23)]),
     23),

    (iec61850.RcbAttrType.GI,
     mms.ReadResponse([mms.BooleanData(True)]),
     True),

    (iec61850.RcbAttrType.PURGE_BUFFER,
     mms.ReadResponse([mms.BooleanData(True)]),
     True),

    (iec61850.RcbAttrType.ENTRY_ID,
     mms.ReadResponse([mms.OctetStringData(b'entry_xyz')]),
     b'entry_xyz'),

    (iec61850.RcbAttrType.TIME_OF_ENTRY,
     mms.ReadResponse([
        mms.BinaryTimeData(datetime.datetime(2020, 2, 3, 4, 5,
                                             tzinfo=datetime.timezone.utc))]),
     datetime.datetime(2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc)),

    (iec61850.RcbAttrType.RESERVATION_TIME,
     mms.ReadResponse([mms.IntegerData(5)]),
     5),

    (iec61850.RcbAttrType.RESERVE,
     mms.ReadResponse([mms.BooleanData(True)]),
     True),

    (iec61850.RcbAttrType.REPORT_ID,
     mms.ServiceError.PDU_SIZE,
     iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT),

    (iec61850.RcbAttrType.REPORT_ID,
     mms.ReadResponse([mms.DataAccessError.OBJECT_ACCESS_DENIED]),
     iec61850.ServiceError.ACCESS_VIOLATION),

    (iec61850.RcbAttrType.REPORT_ID,
     mms.ReadResponse([mms.DataAccessError.OBJECT_NON_EXISTENT]),
     iec61850.ServiceError.INSTANCE_NOT_AVAILABLE),

    (iec61850.RcbAttrType.REPORT_ID,
     mms.ReadResponse([mms.DataAccessError.HARDWARE_FAULT]),
     iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT)
])
async def test_get_rcb_attrs(mms_srv_addr, rcb_type, rcb_attr_type,
                             mms_response, rcb_attr_value):
    if rcb_type == iec61850.RcbType.BUFFERED:
        if rcb_attr_type == iec61850.RcbAttrType.RESERVE:
            return

    elif rcb_type == iec61850.RcbType.UNBUFFERED:
        if rcb_attr_type in (iec61850.RcbAttrType.PURGE_BUFFER,
                             iec61850.RcbAttrType.ENTRY_ID,
                             iec61850.RcbAttrType.TIME_OF_ENTRY,
                             iec61850.RcbAttrType.RESERVATION_TIME):
            return

    rcb_ref = iec61850.RcbRef(logical_device='ld',
                              logical_node='ln',
                              type=rcb_type,
                              name='name')

    def on_request(conn, req):
        assert req == mms.ReadRequest([
            mms.NameVariableSpecification(
                mms.DomainSpecificObjectName(
                    domain_id=rcb_ref.logical_device,
                    item_id=(f'{rcb_ref.logical_node}$'
                             f'{rcb_type.value}$'
                             f'{rcb_ref.name}$'
                             f'{rcb_attr_type.value}')))])

        return mms_response

    mms_srv = await mms.listen(
        connection_cb=lambda _: None,
        addr=mms_srv_addr,
        request_cb=on_request)

    conn = await iec61850.connect(addr=mms_srv_addr)

    resp = await conn.get_rcb_attrs(rcb_ref, [rcb_attr_type])
    assert resp == {rcb_attr_type: rcb_attr_value}

    await conn.async_close()
    await mms_srv.async_close()


@pytest.mark.parametrize('rcb_type', iec61850.RcbType)
@pytest.mark.parametrize('rcb_attr_type, rcb_attr_value, mms_data', [
    (iec61850.RcbAttrType.REPORT_ID,
     'rpt_xyz',
     mms.VisibleStringData('rpt_xyz')),

    (iec61850.RcbAttrType.REPORT_ENABLE,
     True,
     mms.BooleanData(True)),

    (iec61850.RcbAttrType.DATASET,
     iec61850.PersistedDatasetRef(logical_device='ld',
                                  logical_node='ln',
                                  name='ds'),
     mms.VisibleStringData("ld/ln$ds")),

    (iec61850.RcbAttrType.DATASET,
     iec61850.NonPersistedDatasetRef('ds'),
     mms.VisibleStringData("@ds")),

    (iec61850.RcbAttrType.CONF_REVISION,
     123,
     mms.UnsignedData(123)),

    (iec61850.RcbAttrType.OPTIONAL_FIELDS,
     set(iec61850.OptionalField),
     mms.BitStringData([False, *([True] * 8), False])),

    (iec61850.RcbAttrType.BUFFER_TIME,
     3,
     mms.UnsignedData(3)),

    (iec61850.RcbAttrType.SEQUENCE_NUMBER,
     456,
     mms.UnsignedData(456)),

    (iec61850.RcbAttrType.TRIGGER_OPTIONS,
     set(iec61850.TriggerCondition),
     mms.BitStringData([False, *([True] * 5)])),

    (iec61850.RcbAttrType.INTEGRITY_PERIOD,
     23,
     mms.UnsignedData(23)),

    (iec61850.RcbAttrType.GI,
     True,
     mms.BooleanData(True)),

    (iec61850.RcbAttrType.PURGE_BUFFER,
     True,
     mms.BooleanData(True)),

    (iec61850.RcbAttrType.ENTRY_ID,
     b'entry_xyz',
     mms.OctetStringData(b'entry_xyz')),

    (iec61850.RcbAttrType.TIME_OF_ENTRY,
     datetime.datetime(2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
     mms.BinaryTimeData(datetime.datetime(2020, 2, 3, 4, 5,
                                          tzinfo=datetime.timezone.utc))),

    (iec61850.RcbAttrType.RESERVATION_TIME,
     5,
     mms.IntegerData(5)),

    (iec61850.RcbAttrType.RESERVE,
     True,
     mms.BooleanData(True))
])
@pytest.mark.parametrize('mms_response, response', [
    (mms.WriteResponse([None]),
     None),

    # any class any, unmapped error codes
    (mms.AccessError.OBJECT_NON_EXISTENT,
     iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT),

    (mms.WriteResponse([mms.DataAccessError.OBJECT_ACCESS_DENIED]),
     iec61850.ServiceError.ACCESS_VIOLATION),

    (mms.WriteResponse([mms.DataAccessError.OBJECT_NON_EXISTENT]),
     iec61850.ServiceError.INSTANCE_NOT_AVAILABLE),

    (mms.WriteResponse([mms.DataAccessError.TEMPORARILY_UNAVAILABLE]),
     iec61850.ServiceError.INSTANCE_LOCKED_BY_OTHER_CLIENT),

    (mms.WriteResponse([mms.DataAccessError.TYPE_INCONSISTENT]),
     iec61850.ServiceError.TYPE_CONFLICT),

    (mms.WriteResponse([mms.DataAccessError.OBJECT_VALUE_INVALID]),
     iec61850.ServiceError.PARAMETER_VALUE_INCONSISTENT),

    # Any other DataAccessErrors
    (mms.WriteResponse([mms.DataAccessError.OBJECT_INVALIDATED]),
     iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT),

    # TODO: add MMS Reject, when added to mms
])
async def test_set_rcb_attrs(mms_srv_addr, rcb_type, rcb_attr_type, mms_data,
                             rcb_attr_value, mms_response, response):
    if rcb_type == iec61850.RcbType.BUFFERED:
        if rcb_attr_type == iec61850.RcbAttrType.RESERVE:
            return

    elif rcb_type == iec61850.RcbType.UNBUFFERED:
        if rcb_attr_type in (iec61850.RcbAttrType.PURGE_BUFFER,
                             iec61850.RcbAttrType.ENTRY_ID,
                             iec61850.RcbAttrType.TIME_OF_ENTRY,
                             iec61850.RcbAttrType.RESERVATION_TIME):
            return

    rcb_ref = iec61850.RcbRef(logical_device='ld',
                              logical_node='ln',
                              type=rcb_type,
                              name='name')

    def on_request(conn, req):
        assert req == mms.WriteRequest(
            specification=[
                mms.NameVariableSpecification(
                    mms.DomainSpecificObjectName(
                        domain_id=rcb_ref.logical_device,
                        item_id=(f'{rcb_ref.logical_node}$'
                                 f'{rcb_type.value}$'
                                 f'{rcb_ref.name}$'
                                 f'{rcb_attr_type.value}')))],
            data=[mms_data])

        return mms_response

    mms_srv = await mms.listen(
        connection_cb=lambda _: None,
        addr=mms_srv_addr,
        request_cb=on_request)

    conn = await iec61850.connect(addr=mms_srv_addr)

    resp = await conn.set_rcb_attrs(rcb_ref, [(rcb_attr_type, rcb_attr_value)])
    assert resp == {rcb_attr_type: response}

    await conn.async_close()
    await mms_srv.async_close()


@pytest.mark.parametrize('ref, mms_ref', [
    (iec61850.DataRef(logical_device='ld1',
                      logical_node='ln2',
                      fc='ST',
                      names=('da1', 'da2')),
     mms.NameVariableSpecification(
        mms.DomainSpecificObjectName(
            domain_id='ld1',
            item_id='ln2$ST$da1$da2'))),
    (iec61850.DataRef(logical_device='ld1',
                      logical_node='ln2',
                      fc='ST',
                      names=(2, 'd1')),
     mms.NameVariableSpecification(
        mms.DomainSpecificObjectName(
            domain_id='ld1',
            item_id='ln2$ST(2)$d1'))),
    ])
@pytest.mark.parametrize('value_type, value, mms_value', [
    (iec61850.BasicValueType.BOOLEAN, True,
     mms.BooleanData(True)),

    (iec61850.BasicValueType.INTEGER, -123,
     mms.IntegerData(-123)),

    (iec61850.BasicValueType.UNSIGNED, 123,
     mms.UnsignedData(123)),

    (iec61850.BasicValueType.FLOAT, 123.456,
     mms.FloatingPointData(123.456)),

    (iec61850.BasicValueType.BIT_STRING, [True, False, True],
     mms.BitStringData([True, False, True])),

    (iec61850.BasicValueType.OCTET_STRING, b'xyz',
     mms.OctetStringData(b'xyz')),

    (iec61850.BasicValueType.VISIBLE_STRING, 'bla_abc_123',
     mms.VisibleStringData('bla_abc_123')),

    (iec61850.BasicValueType.MMS_STRING, 'bla_abc_123',
     mms.MmsStringData('bla_abc_123')),

    (iec61850.AcsiValueType.QUALITY,
     iec61850.Quality(
        iec61850.QualityValidity.QUESTIONABLE,
        set([iec61850.QualityDetail.OVERFLOW,
             iec61850.QualityDetail.OUT_OF_RANGE,
             iec61850.QualityDetail.BAD_REFERENCE,
             iec61850.QualityDetail.OSCILLATORY,
             iec61850.QualityDetail.FAILURE,
             iec61850.QualityDetail.OLD_DATA,
             iec61850.QualityDetail.INCONSISTENT,
             iec61850.QualityDetail.INACCURATE]),
        iec61850.QualitySource.SUBSTITUTED,
        True,
        True),
     mms.BitStringData([True] * 13)),

    (iec61850.AcsiValueType.TIMESTAMP,
     iec61850.Timestamp(datetime.datetime(
        2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
        False, True, False, 2),
     mms.UtcTimeData(
        datetime.datetime(2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
        False, True, False, 2)),

    (iec61850.AcsiValueType.DOUBLE_POINT,
     iec61850.DoublePoint.OFF,
     mms.BitStringData([False, True])),

    (iec61850.AcsiValueType.DIRECTION,
     iec61850.Direction.FORWARD,
     mms.IntegerData(1)),

    (iec61850.AcsiValueType.SEVERITY,
     iec61850.Severity.WARNING,
     mms.IntegerData(4)),

    (iec61850.AcsiValueType.ANALOGUE,
     iec61850.Analogue(i=43, f=3.21),
     mms.StructureData([mms.IntegerData(43), mms.FloatingPointData(3.21)])),

    (iec61850.AcsiValueType.VECTOR,
     iec61850.Vector(magnitude=iec61850.Analogue(i=432, f=3.21),
                     angle=iec61850.Analogue(i=-123, f=-13.456)),
     mms.StructureData([
        mms.StructureData([mms.IntegerData(432),
                           mms.FloatingPointData(3.21)]),
        mms.StructureData([mms.IntegerData(-123),
                           mms.FloatingPointData(-13.456)])
     ])),

    (iec61850.AcsiValueType.STEP_POSITION,
     iec61850.StepPosition(value=63, transient=True),
     mms.StructureData([mms.IntegerData(63),
                        mms.BooleanData(True)])),

    (iec61850.AcsiValueType.BINARY_CONTROL,
     iec61850.BinaryControl.RESERVED,
     mms.BitStringData([True, True])),

    (iec61850.ArrayValueType(type=iec61850.BasicValueType.VISIBLE_STRING,
                             length=10),
     [f'abc{i}' for i in range(10)],
     mms.ArrayData([mms.VisibleStringData(f'abc{i}') for i in range(10)])),

    (iec61850.StructValueType([('v', iec61850.AcsiValueType.DOUBLE_POINT),
                               ('q', iec61850.AcsiValueType.QUALITY),
                               ('t', iec61850.AcsiValueType.TIMESTAMP)]),
     {'v': iec61850.DoublePoint.OFF,
      'q': iec61850.Quality(iec61850.QualityValidity.GOOD,
                            set([]),
                            iec61850.QualitySource.PROCESS,
                            False,
                            False),
      't': iec61850.Timestamp(
        datetime.datetime(2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
        True, True, True, 3)},
     mms.StructureData([  # values
        mms.BitStringData([False, True]),
        mms.BitStringData(value=[False] * 13),
        mms.UtcTimeData(datetime.datetime(
                   2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
                 True, True, True, 3)])),

    ])
@pytest.mark.parametrize('mms_response, response', [
    (mms.WriteResponse([None]), None),

    # any class any, unmapped error codes
    (mms.InitiateError.MAX_SERVICES_OUTSTANDING_CALLING_INSUFFICIENT,
     iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT),

    (mms.WriteResponse([mms.DataAccessError.OBJECT_ACCESS_DENIED]),
     iec61850.ServiceError.ACCESS_VIOLATION),

    (mms.WriteResponse([mms.DataAccessError.OBJECT_NON_EXISTENT]),
     iec61850.ServiceError.INSTANCE_NOT_AVAILABLE),

    (mms.WriteResponse([mms.DataAccessError.TEMPORARILY_UNAVAILABLE]),
     iec61850.ServiceError.INSTANCE_LOCKED_BY_OTHER_CLIENT),

    (mms.WriteResponse([mms.DataAccessError.TYPE_INCONSISTENT]),
     iec61850.ServiceError.TYPE_CONFLICT),

    (mms.WriteResponse([mms.DataAccessError.OBJECT_VALUE_INVALID]),
     iec61850.ServiceError.PARAMETER_VALUE_INCONSISTENT),

    # Any other DataAccessErrors
    (mms.WriteResponse([mms.DataAccessError.OBJECT_ACCESS_UNSUPPORTED]),
     iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT),

    # TODO: add MMS Reject, when added to mms
    ])
async def test_write_data(mms_srv_addr, ref, value_type, value,
                          mms_ref, mms_value, mms_response, response):
    request_queue = aio.Queue()

    def on_request(conn, req):
        request_queue.put_nowait(req)
        return mms_response

    mms_srv = await mms.listen(
        connection_cb=lambda _: None,
        addr=mms_srv_addr,
        request_cb=on_request)

    conn = await iec61850.connect(
        addr=mms_srv_addr,
        data_value_types={ref: value_type})

    resp = await conn.write_data(ref, value)
    assert resp == response

    req = await request_queue.get()
    assert isinstance(req, mms.WriteRequest)
    assert len(req.specification) == 1
    assert req.specification[0] == mms_ref
    assert len(req.data) == 1
    assert type(req.data[0]) is type(mms_value)
    assert_equal(req.data[0], mms_value)

    await conn.async_close()
    await mms_srv.async_close()


@pytest.mark.parametrize('ref, mms_request', [
    (iec61850.CommandRef(
        logical_device='ld1',
        logical_node='ln2',
        name='cmd1'),
     mms.ReadRequest([
        mms.NameVariableSpecification(
            mms.DomainSpecificObjectName(
                domain_id='ld1',
                item_id='ln2$CO$cmd1$SBO'))]))
])
@pytest.mark.parametrize('mms_response, response', [
    (mms.ReadResponse([mms.VisibleStringData('ln1/ln2$CO$cmd1$SBO')]),
        None),

    (mms.ReadResponse([mms.VisibleStringData('')]),
     iec61850.CommandError(
        iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT,
        additional_cause=None,
        test_error=None)),

    # according to mms Read mapping 8.1.3.4.4.1
    (mms.ServiceError.PDU_SIZE,
     iec61850.CommandError(
        iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT,
        additional_cause=None,
        test_error=None)),

    # any class, any unmapped error codes
    (mms.ResourceError.MEMORY_UNAVAILABLE,
     iec61850.CommandError(
        iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT,
        additional_cause=None,
        test_error=None)),

    (mms.ReadResponse([mms.DataAccessError.OBJECT_ACCESS_DENIED]),
     iec61850.CommandError(
        service_error=iec61850.ServiceError.ACCESS_VIOLATION,
        additional_cause=None,
        test_error=None)),

    (mms.ReadResponse([mms.DataAccessError.OBJECT_NON_EXISTENT]),
     iec61850.CommandError(
        service_error=iec61850.ServiceError.INSTANCE_NOT_AVAILABLE,
        additional_cause=None,
        test_error=None)),

    # any other DataAccessError
    (mms.ReadResponse([mms.DataAccessError.OBJECT_ACCESS_UNSUPPORTED]),
     iec61850.CommandError(
        iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT,
        additional_cause=None,
        test_error=None)),
])
async def test_select_normal(mms_srv_addr, ref, mms_request,
                             mms_response, response):
    request_queue = aio.Queue()

    def on_request(conn, req):
        request_queue.put_nowait(req)
        return mms_response

    mms_srv = await mms.listen(
        connection_cb=lambda _: None,
        addr=mms_srv_addr,
        request_cb=on_request)

    conn = await iec61850.connect(addr=mms_srv_addr)

    resp = await conn.select(ref, None)
    assert resp == response

    req = await request_queue.get()
    assert req == mms_request

    await conn.async_close()
    await mms_srv.async_close()


@pytest.mark.parametrize('cmd_ref, mms_cmd_ref, value_type, cmd, mms_req', [
    (iec61850.CommandRef('ld1', 'ln2', 'cmd3'),
     mms.VisibleStringData('ld1/ln2$CO$cmd3$SBOw'),
     iec61850.BasicValueType.BOOLEAN,
     iec61850.Command(
        value=True,
        operate_time=None,
        origin=iec61850.Origin(
            iec61850.OriginCategory.STATION_CONTROL,
            b'orig_xyz'),
        control_number=123,
        t=iec61850.Timestamp(
            value=datetime.datetime(
                2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
            leap_second=False,
            clock_failure=False,
            not_synchronized=False,
            accuracy=None),
        test=False,
        checks=set([iec61850.Check.SYNCHRO, iec61850.Check.INTERLOCK])),
     mms.WriteRequest(
        specification=[
            mms.NameVariableSpecification(
                mms.DomainSpecificObjectName(domain_id='ld1',
                                             item_id='ln2$CO$cmd3$SBOw'))],
        data=[mms.StructureData([
              mms.BooleanData(True),  # ctlVal
              mms.StructureData([
                  mms.IntegerData(2),
                  mms.OctetStringData(b'orig_xyz')]),  # origin
              mms.UnsignedData(123),  # ctlNum
              mms.UtcTimeData(
                  datetime.datetime(
                    2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
                  False,
                  False,
                  False,
                  None),  # T
              mms.BooleanData(False),  # Test
              mms.BitStringData([True, True])])])),  # Check

    (iec61850.CommandRef('ld2', 'ln3', 'cmd4'),
     mms.VisibleStringData('ld2/ln3$CO$cmd4$SBOw'),
     iec61850.AcsiValueType.DOUBLE_POINT,
     iec61850.Command(
        value=iec61850.DoublePoint.OFF,
        operate_time=iec61850.Timestamp(
            value=datetime.datetime(
                2025, 3, 25, 10, 27, 30, 41219, datetime.timezone.utc),
            leap_second=False,
            clock_failure=False,
            not_synchronized=False,
            accuracy=1),
        origin=iec61850.Origin(
            iec61850.OriginCategory.STATION_CONTROL,
            b'orig_xyz'),
        control_number=321,
        t=iec61850.Timestamp(
            value=datetime.datetime(
                2025, 3, 25, 10, 10, 19, 79806, datetime.timezone.utc),
            leap_second=True,
            clock_failure=True,
            not_synchronized=True,
            accuracy=3),
        test=True,
        checks=set([])),
     mms.WriteRequest(
        specification=[
            mms.NameVariableSpecification(
                mms.DomainSpecificObjectName(domain_id='ld2',
                                             item_id='ln3$CO$cmd4$SBOw'))],
        data=[mms.StructureData([
              mms.BitStringData([False, True]),  # ctlVal
              mms.UtcTimeData(
                  datetime.datetime(
                    2025, 3, 25, 10, 27, 30, 41219, datetime.timezone.utc),
                  False,
                  False,
                  False,
                  1),  # OperTm
              mms.StructureData([
                  mms.IntegerData(2),
                  mms.OctetStringData(b'orig_xyz')]),  # origin
              mms.UnsignedData(321),  # ctlNum
              mms.UtcTimeData(
                  datetime.datetime(
                    2025, 3, 25, 10, 10, 19, 79806, datetime.timezone.utc),
                  True,
                  True,
                  True,
                  3),  # T
              mms.BooleanData(True),  # Test
              mms.BitStringData([False, False])])])),  # Check

    ])
@pytest.mark.parametrize('mms_response, add_cause, response', [
    (mms.WriteResponse([None]),
        None,
        None),

    (mms.WriteResponse([None]),
        iec61850.AdditionalCause.NOT_SUPPORTED,
        None),

    (mms.WriteResponse([mms.DataAccessError.TEMPORARILY_UNAVAILABLE]),
        None,
        iec61850.CommandError(
            service_error=None,
            additional_cause=None,
            test_error=None)),

    (mms.WriteResponse([mms.DataAccessError.OBJECT_ACCESS_DENIED]),
        iec61850.AdditionalCause.NOT_SUPPORTED,
        iec61850.CommandError(
            service_error=None,
            additional_cause=iec61850.AdditionalCause.NOT_SUPPORTED,
            test_error=iec61850.TestError.UNKNOWN)),

    (mms.VmdStateError.OTHER,
        None,
        iec61850.CommandError(
            iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT,
            additional_cause=None,
            test_error=None)),

    (mms.VmdStateError.OTHER,
        iec61850.AdditionalCause.STEP_LIMIT,
        iec61850.CommandError(
            iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT,
            additional_cause=iec61850.AdditionalCause.STEP_LIMIT,
            test_error=iec61850.TestError.UNKNOWN)),
])
async def test_select_enhanced(mms_srv_addr, cmd_ref, mms_cmd_ref, cmd,
                               value_type, mms_req, mms_response, add_cause,
                               response):
    mms_conn_queue = aio.Queue()
    request_queue = aio.Queue()

    async def on_request(conn, req):
        request_queue.put_nowait(req)

        if add_cause:
            mms_conn_srv = await mms_conn_queue.get()
            inf_rpt = mms.InformationReportUnconfirmed(
                specification=[mms.NameVariableSpecification(
                    mms.VmdSpecificObjectName(identifier='LastApplError'))],
                data=[mms.StructureData(
                    elements=[
                        mms_cmd_ref,
                        mms.IntegerData(value=1),  # Error = Unknown
                        mms.StructureData([  # origin
                            mms.IntegerData(2),
                            mms.OctetStringData(b'orig_abc')]),
                        mms.UnsignedData(cmd.control_number),  # ctlNum
                        mms.IntegerData(value=add_cause.value)])])
            await mms_conn_srv.send_unconfirmed(inf_rpt)

        return mms_response

    mms_srv = await mms.listen(
        connection_cb=mms_conn_queue.put_nowait,
        addr=mms_srv_addr,
        request_cb=on_request)

    conn = await iec61850.connect(
        addr=mms_srv_addr,
        cmd_value_types={cmd_ref: value_type})

    resp = await conn.select(cmd_ref, cmd)
    assert resp == response

    req = await request_queue.get()
    assert req == mms_req

    await conn.async_close()
    await mms_srv.async_close()


@pytest.mark.parametrize('cmd_ref, mms_cmd_ref, cmd, value_type, mms_req', [
    (iec61850.CommandRef('ld1', 'ln2', 'cmd1'),
     mms.VisibleStringData('ld1/ln2$CO$cmd1$Cancel'),
     iec61850.Command(
        value=5,
        operate_time=None,
        origin=iec61850.Origin(
            iec61850.OriginCategory.STATION_CONTROL,
            b'orig_xyz'),
        control_number=123,
        t=iec61850.Timestamp(
            value=datetime.datetime(
                2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
            leap_second=False,
            clock_failure=False,
            not_synchronized=False,
            accuracy=None),
        test=False,
        checks=set([iec61850.Check.INTERLOCK])),
     iec61850.BasicValueType.INTEGER,
     mms.WriteRequest(
        specification=[
            mms.NameVariableSpecification(
                mms.DomainSpecificObjectName(
                    domain_id='ld1',
                    item_id='ln2$CO$cmd1$Cancel'))],
        data=[mms.StructureData([
              mms.IntegerData(5),  # ctlVal
              mms.StructureData([
                  mms.IntegerData(2),
                  mms.OctetStringData(b'orig_xyz')]),  # origin
              mms.UnsignedData(123),  # ctlNum
              mms.UtcTimeData(
                  datetime.datetime(
                    2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
                  False,
                  False,
                  False,
                  None),  # T
              mms.BooleanData(False)])])),  # Test

    (iec61850.CommandRef('ld4', 'ln5', 'cmd6'),
     mms.VisibleStringData('ld4/ln5$CO$cmd6$Cancel'),
     iec61850.Command(
        value=5.43,
        operate_time=None,
        origin=iec61850.Origin(
            iec61850.OriginCategory.STATION_CONTROL,
            b'orig_xyz'),
        control_number=456,
        t=iec61850.Timestamp(
            value=datetime.datetime(
                2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
            leap_second=False,
            clock_failure=False,
            not_synchronized=False,
            accuracy=None),
        test=False,
        checks=set([iec61850.Check.INTERLOCK])),
     iec61850.BasicValueType.FLOAT,
     mms.WriteRequest(
        specification=[
            mms.NameVariableSpecification(
                mms.DomainSpecificObjectName(
                    domain_id='ld4',
                    item_id='ln5$CO$cmd6$Cancel'))],
        data=[mms.StructureData([
              mms.FloatingPointData(5.43),  # ctlVal
              mms.StructureData([
                  mms.IntegerData(2),
                  mms.OctetStringData(b'orig_xyz')]),  # origin
              mms.UnsignedData(456),  # ctlNum
              mms.UtcTimeData(
                  datetime.datetime(
                    2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
                  False,
                  False,
                  False,
                  None),  # T
              mms.BooleanData(False)])])),  # Test
    ])
@pytest.mark.parametrize('mms_response, add_cause, response', [
    (mms.WriteResponse([None]),
        None,
        None),

    (mms.WriteResponse([None]),
        iec61850.AdditionalCause.NOT_SUPPORTED,
        None),

    (mms.WriteResponse([mms.DataAccessError.TEMPORARILY_UNAVAILABLE]),
        None,
        iec61850.CommandError(
            service_error=None,
            additional_cause=None,
            test_error=None)),

    (mms.WriteResponse([mms.DataAccessError.TEMPORARILY_UNAVAILABLE]),
        iec61850.AdditionalCause.NOT_SUPPORTED,
        iec61850.CommandError(
            service_error=None,
            additional_cause=iec61850.AdditionalCause.NOT_SUPPORTED,
            test_error=iec61850.TestError.TIMEOUT_TEST_NOT_OK)),

    (mms.WriteResponse([mms.DataAccessError.TYPE_INCONSISTENT]),
        iec61850.AdditionalCause.PARAMETER_CHANGE_IN_EXECUTION,
        iec61850.CommandError(
            service_error=None,
            additional_cause=iec61850.AdditionalCause.PARAMETER_CHANGE_IN_EXECUTION,  # NOQA
            test_error=iec61850.TestError.TIMEOUT_TEST_NOT_OK)),

    (mms.VmdStateError.OTHER,
        None,
        iec61850.CommandError(
            iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT,
            additional_cause=None,
            test_error=None)),

    (mms.VmdStateError.OTHER,
        iec61850.AdditionalCause.STEP_LIMIT,
        iec61850.CommandError(
            iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT,
            additional_cause=iec61850.AdditionalCause.STEP_LIMIT,
            test_error=iec61850.TestError.TIMEOUT_TEST_NOT_OK)),
])
async def test_cancel(mms_srv_addr, cmd_ref, mms_cmd_ref, cmd, value_type,
                      mms_req, mms_response, add_cause, response):
    mms_conn_queue = aio.Queue()
    request_queue = aio.Queue()

    async def on_request(conn, req):
        request_queue.put_nowait(req)

        if add_cause:
            mms_conn_srv = await mms_conn_queue.get()
            inf_rpt = mms.InformationReportUnconfirmed(
                specification=[mms.NameVariableSpecification(
                    mms.VmdSpecificObjectName(identifier='LastApplError'))],
                data=[mms.StructureData(
                    elements=[
                        mms_cmd_ref,
                        mms.IntegerData(value=2),  # Error, Timeout Test Not OK
                        mms.StructureData([  # origin
                            mms.IntegerData(2),
                            mms.OctetStringData(b'orig_abc')]),
                        mms.UnsignedData(cmd.control_number),  # ctlNum
                        mms.IntegerData(value=add_cause.value)])])
            await mms_conn_srv.send_unconfirmed(inf_rpt)

        return mms_response

    mms_srv = await mms.listen(
        connection_cb=mms_conn_queue.put_nowait,
        addr=mms_srv_addr,
        request_cb=on_request)

    conn = await iec61850.connect(
        addr=mms_srv_addr,
        cmd_value_types={cmd_ref: value_type})

    resp = await conn.cancel(cmd_ref, cmd)
    assert resp == response

    req = await request_queue.get()
    assert_equal(req, mms_req)

    await conn.async_close()
    await mms_srv.async_close()


@pytest.mark.parametrize('cmd_ref, mms_ref, cmd, value_type, mms_req', [
    (iec61850.CommandRef(
         logical_device='ld1',
         logical_node='ln2',
         name='cmd1'),
     mms.VisibleStringData('ld1/ln2$CO$cmd1$Oper'),
     iec61850.Command(
             value=3,
             operate_time=None,
             origin=iec61850.Origin(
                 iec61850.OriginCategory.STATION_CONTROL,
                 b'orig_xyz'),
             control_number=123,
             t=iec61850.Timestamp(
                 value=datetime.datetime(
                     2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
                 leap_second=False,
                 clock_failure=False,
                 not_synchronized=False,
                 accuracy=None),
             test=False,
             checks=set([iec61850.Check.SYNCHRO])),
     iec61850.BasicValueType.UNSIGNED,
     mms.WriteRequest(
        specification=[
            mms.NameVariableSpecification(
                mms.DomainSpecificObjectName(
                    domain_id='ld1',
                    item_id='ln2$CO$cmd1$Oper'))],
        data=[mms.StructureData([
              mms.UnsignedData(3),  # ctlVal
              mms.StructureData([
                  mms.IntegerData(2),
                  mms.OctetStringData(b'orig_xyz')]),  # origin
              mms.UnsignedData(123),  # ctlNum
              mms.UtcTimeData(
                  datetime.datetime(
                    2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
                  False,
                  False,
                  False,
                  None),  # T
              mms.BooleanData(False),  # Test
              mms.BitStringData([True, False])])])),  # Check

    (iec61850.CommandRef(
         logical_device='a',
         logical_node='b',
         name='c'),
     mms.VisibleStringData('a/b$CO$c$Oper'),
     iec61850.Command(
             value=[True, False],
             operate_time=iec61850.Timestamp(
                 value=datetime.datetime(
                    2025, 3, 25, 12, 10, 55, 139367, datetime.timezone.utc),
                 leap_second=True,
                 clock_failure=False,
                 not_synchronized=True,
                 accuracy=None),
             origin=iec61850.Origin(
                 iec61850.OriginCategory.STATION_CONTROL,
                 b'orig_xyz'),
             control_number=11,
             t=iec61850.Timestamp(
                 value=datetime.datetime(
                     2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
                 leap_second=False,
                 clock_failure=False,
                 not_synchronized=False,
                 accuracy=None),
             test=False,
             checks=set([])),
     iec61850.BasicValueType.BIT_STRING,
     mms.WriteRequest(
        specification=[
            mms.NameVariableSpecification(
                mms.DomainSpecificObjectName(
                    domain_id='a',
                    item_id='b$CO$c$Oper'))],
        data=[mms.StructureData([
              mms.BitStringData([True, False]),  # ctlVal
              mms.UtcTimeData(
                  datetime.datetime(
                    2025, 3, 25, 12, 10, 55, 139367, datetime.timezone.utc),
                  True,
                  False,
                  True,
                  None),  # OperTm
              mms.StructureData([
                  mms.IntegerData(2),
                  mms.OctetStringData(b'orig_xyz')]),  # origin
              mms.UnsignedData(11),  # ctlNum
              mms.UtcTimeData(
                  datetime.datetime(
                    2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
                  False,
                  False,
                  False,
                  None),  # T
              mms.BooleanData(False),  # Test
              mms.BitStringData([False, False])])])),  # Check
    ])
@pytest.mark.parametrize('mms_response, add_cause, response', [
    (mms.WriteResponse([None]),
        None,
        None),

    (mms.WriteResponse([None]),
        iec61850.AdditionalCause.NOT_SUPPORTED,
        None),

    (mms.WriteResponse([mms.DataAccessError.OBJECT_ACCESS_DENIED]),
        None,
        iec61850.CommandError(
            service_error=None,
            additional_cause=None,
            test_error=None)),

    (mms.WriteResponse([mms.DataAccessError.TEMPORARILY_UNAVAILABLE]),
        iec61850.AdditionalCause.NOT_SUPPORTED,
        iec61850.CommandError(
            service_error=None,
            additional_cause=iec61850.AdditionalCause.NOT_SUPPORTED,
            test_error=iec61850.TestError.NO_ERROR)),

    (mms.WriteResponse([mms.DataAccessError.OBJECT_NON_EXISTENT]),
        iec61850.AdditionalCause.PARAMETER_CHANGE_IN_EXECUTION,
        iec61850.CommandError(
            service_error=None,
            additional_cause=iec61850.AdditionalCause.PARAMETER_CHANGE_IN_EXECUTION,  # NOQA
            test_error=iec61850.TestError.NO_ERROR)),

    (mms.VmdStateError.OTHER,
        None,
        iec61850.CommandError(
            iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT,
            additional_cause=None,
            test_error=None)),

    (mms.DefinitionError.OBJECT_UNDEFINED,
        iec61850.AdditionalCause.PARAMETER_CHANGE_IN_EXECUTION,
        iec61850.CommandError(
            iec61850.ServiceError.FAILED_DUE_TO_COMMUNICATIONS_CONSTRAINT,
            iec61850.AdditionalCause.PARAMETER_CHANGE_IN_EXECUTION,
            test_error=iec61850.TestError.NO_ERROR)),
])
async def test_operate(mms_srv_addr, cmd_ref, mms_ref, cmd, value_type,
                       mms_req, mms_response, add_cause, response):
    mms_conn_queue = aio.Queue()
    request_queue = aio.Queue()

    async def on_request(conn, req):
        request_queue.put_nowait(req)

        if add_cause:
            mms_conn_srv = await mms_conn_queue.get()
            inf_rpt = mms.InformationReportUnconfirmed(
                specification=[mms.NameVariableSpecification(
                    mms.VmdSpecificObjectName(identifier='LastApplError'))],
                data=[mms.StructureData(
                    elements=[
                        mms_ref,
                        mms.IntegerData(value=0),  # Error = No Error
                        mms.StructureData([  # origin
                            mms.IntegerData(2),
                            mms.OctetStringData(b'orig_abc')]),
                        mms.UnsignedData(cmd.control_number),  # ctlNum
                        mms.IntegerData(value=add_cause.value)])])
            await mms_conn_srv.send_unconfirmed(inf_rpt)

        return mms_response

    mms_srv = await mms.listen(
        connection_cb=mms_conn_queue.put_nowait,
        addr=mms_srv_addr,
        request_cb=on_request)

    conn = await iec61850.connect(
        addr=mms_srv_addr,
        cmd_value_types={cmd_ref: value_type})

    resp = await conn.operate(cmd_ref, cmd)
    assert resp == response

    req = await request_queue.get()
    assert req == mms_req

    await conn.async_close()
    await mms_srv.async_close()


@pytest.mark.parametrize('mms_add_cause, response', [
    # paired correctly with request's name and control numberr
    (mms.InformationReportUnconfirmed(
        specification=[mms.NameVariableSpecification(
            mms.VmdSpecificObjectName(identifier='LastApplError'))],
        data=[mms.StructureData(
            elements=[
                mms.VisibleStringData('ld1/ln2$CO$cmd1$Oper'),
                mms.IntegerData(value=0),  # Error = No Error
                mms.StructureData([  # origin
                    mms.IntegerData(2),
                    mms.OctetStringData(b'orig_abc')]),
                mms.UnsignedData(123),  # ctlNum
                mms.IntegerData(
                    iec61850.AdditionalCause.NOT_SUPPORTED.value)])]),
     iec61850.CommandError(
        service_error=None,
        test_error=iec61850.TestError.NO_ERROR,
        additional_cause=iec61850.AdditionalCause.NOT_SUPPORTED)),

    # not paired - wrong control number
    (mms.InformationReportUnconfirmed(
        specification=[mms.NameVariableSpecification(
            mms.VmdSpecificObjectName(identifier='LastApplError'))],
        data=[mms.StructureData(
            elements=[
                mms.VisibleStringData('ld1/ln2$CO$cmd1$Oper'),
                mms.IntegerData(value=0),  # Error = No Error
                mms.StructureData([  # origin
                    mms.IntegerData(2),
                    mms.OctetStringData(b'orig_abc')]),
                mms.UnsignedData(456),  # ctlNum
                mms.IntegerData(
                    iec61850.AdditionalCause.NOT_SUPPORTED.value)])]),
     iec61850.CommandError(None, None, None)),

    # not paired - wrong reference
    (mms.InformationReportUnconfirmed(
        specification=[mms.NameVariableSpecification(
            mms.VmdSpecificObjectName(identifier='LastApplError'))],
        data=[mms.StructureData(
            elements=[
                mms.VisibleStringData('ld2/ln2$CO$cmd1$Oper'),
                mms.IntegerData(value=0),  # Error = No Error
                mms.StructureData([  # origin
                    mms.IntegerData(2),
                    mms.OctetStringData(b'orig_abc')]),
                mms.UnsignedData(123),  # ctlNum
                mms.IntegerData(
                    iec61850.AdditionalCause.NOT_SUPPORTED.value)])]),
     iec61850.CommandError(None, None, None)),
])
async def test_add_cause_pairing(mms_srv_addr, mms_add_cause, response):
    cmd_ref = iec61850.CommandRef('ld1', 'ln2', 'cmd1')
    cmd = iec61850.Command(
             value=3,
             operate_time=None,
             origin=iec61850.Origin(
                 iec61850.OriginCategory.STATION_CONTROL,
                 b'orig_xyz'),
             control_number=123,
             t=iec61850.Timestamp(
                 value=datetime.datetime(
                     2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
                 leap_second=False,
                 clock_failure=False,
                 not_synchronized=False,
                 accuracy=None),
             test=False,
             checks=set([iec61850.Check.SYNCHRO]))

    mms_conn_queue = aio.Queue()

    async def on_request(conn, req):
        mms_conn_srv = await mms_conn_queue.get()
        await mms_conn_srv.send_unconfirmed(mms_add_cause)

        return mms.WriteResponse([mms.DataAccessError.OBJECT_ACCESS_DENIED])

    mms_srv = await mms.listen(
        connection_cb=mms_conn_queue.put_nowait,
        addr=mms_srv_addr,
        request_cb=on_request)

    conn = await iec61850.connect(
        addr=mms_srv_addr,
        cmd_value_types={cmd_ref: iec61850.BasicValueType.UNSIGNED})

    resp = await conn.operate(cmd_ref, cmd)
    assert resp == response

    await conn.async_close()
    await mms_srv.async_close()


async def test_command_active_control_num(mms_srv_addr):
    cmd_ref = iec61850.CommandRef('ld1', 'ln2', 'cmd1')
    cmd = iec61850.Command(
             value=3,
             operate_time=None,
             origin=iec61850.Origin(
                 iec61850.OriginCategory.STATION_CONTROL,
                 b'orig_xyz'),
             control_number=123,
             t=iec61850.Timestamp(
                 value=datetime.datetime(
                     2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
                 leap_second=False,
                 clock_failure=False,
                 not_synchronized=False,
                 accuracy=None),
             test=False,
             checks=set([iec61850.Check.SYNCHRO]))

    async def on_request(conn, req):
        await asyncio.Future()

    mms_srv = await mms.listen(
        connection_cb=lambda _: None,
        addr=mms_srv_addr,
        request_cb=on_request)

    conn = await iec61850.connect(
        addr=mms_srv_addr,
        cmd_value_types={cmd_ref: iec61850.BasicValueType.UNSIGNED})

    async with aio.Group() as group:
        group.spawn(conn.operate, cmd_ref, cmd)
        await asyncio.sleep(0.001)
        with pytest.raises(Exception):
            await conn.operate(cmd_ref, cmd)

    await conn.async_close()
    await mms_srv.async_close()


@pytest.mark.parametrize('mms_response', [
    None,  # no response, timeout
    mms.WriteResponse([None, None]),  # response length > 1
    # response length > 1
    mms.WriteResponse([mms.DataAccessError.TEMPORARILY_UNAVAILABLE,
                       mms.DataAccessError.OBJECT_NON_EXISTENT]),
    # wrong response type
    mms.ReadResponse([mms.VisibleStringData('ln1/ln2$CO$cmd1$Oper')]),
    ])
async def test_command_response_invalid(mms_srv_addr, mms_response):
    cmd_ref = iec61850.CommandRef('ld1', 'ln2', 'cmd1')
    cmd = iec61850.Command(
             value=3,
             operate_time=None,
             origin=iec61850.Origin(
                 iec61850.OriginCategory.STATION_CONTROL,
                 b'orig_xyz'),
             control_number=123,
             t=iec61850.Timestamp(
                 value=datetime.datetime(
                     2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
                 leap_second=False,
                 clock_failure=False,
                 not_synchronized=False,
                 accuracy=None),
             test=False,
             checks=set([iec61850.Check.SYNCHRO]))

    async def on_request(conn, req):
        if mms_response:
            return mms_response

        await asyncio.Future()

    mms_srv = await mms.listen(
        connection_cb=lambda _: None,
        addr=mms_srv_addr,
        request_cb=on_request)

    conn = await iec61850.connect(
        addr=mms_srv_addr,
        cmd_value_types={cmd_ref: iec61850.BasicValueType.UNSIGNED})

    if mms_response:
        with pytest.raises(Exception):
            await conn.operate(cmd_ref, cmd)
    else:
        with pytest.raises(asyncio.TimeoutError):
            await aio.wait_for(conn.operate(cmd_ref, cmd), 0.01)

    await conn.async_close()
    await mms_srv.async_close()


@pytest.mark.parametrize('mms_inf_report, termination', [
    # response+, without operTm
    (mms.InformationReportUnconfirmed(
        specification=[mms.NameVariableSpecification(
            mms.DomainSpecificObjectName(
                domain_id='ld1',
                item_id='ln2$CO$cmd1$Oper'))],
        data=[mms.StructureData(
            elements=[
                mms.IntegerData(value=1),
                # OperTm
                mms.StructureData([  # origin
                    mms.IntegerData(3),
                    mms.OctetStringData(b'orig_abc')]),
                mms.UnsignedData(123),  # ctlNum
                mms.UtcTimeData(
                  datetime.datetime(
                    2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
                  False,
                  False,
                  False,
                  None),  # T
                mms.BooleanData(False),  # Test
                mms.BitStringData([False, True])])]),  # check
     iec61850.Termination(
        ref=iec61850.CommandRef(
            logical_device='ld1',
            logical_node='ln2',
            name='cmd1'),
        cmd=iec61850.Command(
            value=1,
            operate_time=None,
            origin=iec61850.Origin(
                category=iec61850.OriginCategory.REMOTE_CONTROL,
                identification=b'orig_abc'),
            control_number=123,
            t=iec61850.Timestamp(
                value=datetime.datetime(
                    2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
                leap_second=False,
                clock_failure=False,
                not_synchronized=False,
                accuracy=None),
            test=False,
            checks=set([iec61850.Check.INTERLOCK])),
        error=None)),

    # response-, with operTm
    (mms.InformationReportUnconfirmed(
        specification=[
            mms.NameVariableSpecification(
                mms.VmdSpecificObjectName(identifier='LastApplError')),
            mms.NameVariableSpecification(
                mms.DomainSpecificObjectName(domain_id='ld1',
                                             item_id='ln2$CO$cmd1$Oper'))],
        data=[
            mms.StructureData(
                    elements=[
                        mms.VisibleStringData('ld1/ln2$$cmd1$Oper'),
                        mms.IntegerData(value=1),  # Error = Unknown
                        mms.StructureData([  # origin
                            mms.IntegerData(2),
                            mms.OctetStringData(b'orig_abc')]),
                        mms.UnsignedData(123),  # ctlNum
                        mms.IntegerData(value=7)]),  # AdditionalCause
            mms.StructureData(
                elements=[
                    mms.IntegerData(value=1),
                    mms.UtcTimeData(  # OperTm
                        value=datetime.datetime(
                            1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
                        leap_second=False,
                        clock_failure=False,
                        not_synchronized=False,
                        accuracy=0),
                    mms.StructureData([  # origin
                        mms.IntegerData(3),
                        mms.OctetStringData(b'orig_abc')]),
                    mms.UnsignedData(123),  # ctlNum
                    mms.UtcTimeData(
                      datetime.datetime(
                        2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
                      True,
                      True,
                      True,
                      3),  # T
                    mms.BooleanData(False),  # Test
                    mms.BitStringData([False, False])])]),
     iec61850.Termination(
        ref=iec61850.CommandRef(
            logical_device='ld1',
            logical_node='ln2',
            name='cmd1'),
        cmd=iec61850.Command(
            value=1,
            operate_time=iec61850.Timestamp(
                value=datetime.datetime(
                    1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
                leap_second=False,
                clock_failure=False,
                not_synchronized=False,
                accuracy=0),
            origin=iec61850.Origin(
                category=iec61850.OriginCategory.REMOTE_CONTROL,
                identification=b'orig_abc'),
            control_number=123,
            t=iec61850.Timestamp(
                value=datetime.datetime(
                    2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
                leap_second=True,
                clock_failure=True,
                not_synchronized=True,
                accuracy=3),
            test=False,
            checks=set()),
        error=iec61850.CommandError(
            service_error=None,
            additional_cause=iec61850.AdditionalCause.STEP_LIMIT,
            test_error=iec61850.TestError.UNKNOWN)))
    ])
async def test_termination(mms_srv_addr, mms_inf_report, termination):
    mms_conn_queue = aio.Queue()
    termination_queue = aio.Queue()

    mms_srv = await mms.listen(
        connection_cb=mms_conn_queue.put_nowait,
        addr=mms_srv_addr)

    conn = await iec61850.connect(
        addr=mms_srv_addr,
        cmd_value_types={termination.ref: iec61850.BasicValueType.INTEGER},
        termination_cb=termination_queue.put_nowait)

    mms_conn_srv = await mms_conn_queue.get()

    await mms_conn_srv.send_unconfirmed(mms_inf_report)

    cmd_term = await termination_queue.get()
    assert cmd_term == termination

    await conn.async_close()
    await mms_srv.async_close()


@pytest.mark.parametrize('mms_data_value, data_type, data_value', [
    (mms.BooleanData(False),
        iec61850.BasicValueType.BOOLEAN,
        False),

    (mms.IntegerData(1234),
        iec61850.BasicValueType.INTEGER,
        1234),

    (mms.UnsignedData(4321),
        iec61850.BasicValueType.UNSIGNED,
        4321),

    (mms.FloatingPointData(12.345),
        iec61850.BasicValueType.FLOAT,
        12.345),

    (mms.BitStringData([True, False, True]),
     iec61850.BasicValueType.BIT_STRING,
     [True, False, True]),

    (mms.OctetStringData(b'abc123'),
     iec61850.BasicValueType.OCTET_STRING,
     b'abc123'),

    (mms.VisibleStringData('abc123'),
     iec61850.BasicValueType.VISIBLE_STRING,
     'abc123'),

    (mms.MmsStringData('xyz123'),
     iec61850.BasicValueType.MMS_STRING,
     'xyz123'),

    (mms.BitStringData(value=[True] * 13),
     iec61850.AcsiValueType.QUALITY,
     iec61850.Quality(
        iec61850.QualityValidity.QUESTIONABLE,
        set([iec61850.QualityDetail.OVERFLOW,
             iec61850.QualityDetail.OUT_OF_RANGE,
             iec61850.QualityDetail.BAD_REFERENCE,
             iec61850.QualityDetail.OSCILLATORY,
             iec61850.QualityDetail.FAILURE,
             iec61850.QualityDetail.OLD_DATA,
             iec61850.QualityDetail.INCONSISTENT,
             iec61850.QualityDetail.INACCURATE]),
        iec61850.QualitySource.SUBSTITUTED,
        True,
        True)),

    (mms.BitStringData(value=[False] * 13),
     iec61850.AcsiValueType.QUALITY,
     iec61850.Quality(
        iec61850.QualityValidity.GOOD,
        set([]),
        iec61850.QualitySource.PROCESS,
        False,
        False)),

    (mms.UtcTimeData(
        datetime.datetime(2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
        True, True, True, 3),
     iec61850.AcsiValueType.TIMESTAMP,
     iec61850.Timestamp(datetime.datetime(
        2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
        True, True, True, 3)),

    (mms.BitStringData([True, False]),
     iec61850.AcsiValueType.DOUBLE_POINT,
     iec61850.DoublePoint.ON),

    (mms.IntegerData(1),
     iec61850.AcsiValueType.DIRECTION,
     iec61850.Direction.FORWARD),

    (mms.IntegerData(4),
     iec61850.AcsiValueType.SEVERITY,
     iec61850.Severity.WARNING),

    (mms.StructureData([mms.IntegerData(12), mms.FloatingPointData(1.23)]),
     iec61850.AcsiValueType.ANALOGUE,
     iec61850.Analogue(i=12, f=1.23)),

    (mms.StructureData([
        mms.StructureData([mms.IntegerData(5), mms.FloatingPointData(1.23)]),
        mms.StructureData([mms.IntegerData(0), mms.FloatingPointData(0.456)])
        ]),
     iec61850.AcsiValueType.VECTOR,
     iec61850.Vector(magnitude=iec61850.Analogue(i=5, f=1.23),
                     angle=iec61850.Analogue(i=0, f=0.456))),

    (mms.StructureData([mms.IntegerData(63),
                        mms.BooleanData(True)]),
     iec61850.AcsiValueType.STEP_POSITION,
     iec61850.StepPosition(value=63, transient=True)),

    (mms.BitStringData([True, True]),
     iec61850.AcsiValueType.BINARY_CONTROL,
     iec61850.BinaryControl.RESERVED),

    (mms.ArrayData([mms.IntegerData(i) for i in range(10)]),
     iec61850.ArrayValueType(type=iec61850.BasicValueType.INTEGER,
                             length=10),
     [i for i in range(10)]),

    # DoublePoint, Quality, Timestamp
    (mms.StructureData([  # values
        mms.BitStringData([False, True]),
        mms.BitStringData(value=[False] * 13),
        mms.UtcTimeData(datetime.datetime(
                2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
              True, True, True, 3)]),
     iec61850.StructValueType([('v', iec61850.AcsiValueType.DOUBLE_POINT),
                               ('q', iec61850.AcsiValueType.QUALITY),
                               ('t', iec61850.AcsiValueType.TIMESTAMP)]),
     {'v': iec61850.DoublePoint.OFF,
      'q': iec61850.Quality(
        iec61850.QualityValidity.GOOD,
        set([]),
        iec61850.QualitySource.PROCESS,
        False,
        False),
      't': iec61850.Timestamp(datetime.datetime(
        2020, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
        True, True, True, 3)}),
])
@pytest.mark.parametrize('mms_reasons, reasons', [
    (mms.BitStringData([False, True, False, False, False, True, False]),
     set([iec61850.Reason.DATA_CHANGE,
          iec61850.Reason.GENERAL_INTERROGATION])),

    (mms.BitStringData([False, True, True, True, True, True, True]),
     set([iec61850.Reason.DATA_CHANGE,
          iec61850.Reason.QUALITY_CHANGE,
          iec61850.Reason.DATA_UPDATE,
          iec61850.Reason.INTEGRITY,
          iec61850.Reason.GENERAL_INTERROGATION,
          iec61850.Reason.APPLICATION_TRIGGER])),

    (mms.BitStringData([False, False, False, False, False, False, False]),
     set())
])
async def test_report_value_reason(mms_srv_addr, mms_data_value, data_type,
                                   data_value, mms_reasons, reasons):
    rpt_id = 'rpt_xyz'
    data_ref = iec61850.DataRef(logical_device='ld1',
                                logical_node='ln2',
                                fc='ST',
                                names=('Pos', 'stVal'))

    mms_conn_queue = aio.Queue()
    report_queue = aio.Queue()

    mms_srv = await mms.listen(
        connection_cb=mms_conn_queue.put_nowait,
        addr=mms_srv_addr)

    conn = await iec61850.connect(
        addr=mms_srv_addr,
        data_value_types={data_ref: data_type},
        report_data_refs={rpt_id: [data_ref]},
        report_cb=report_queue.put_nowait)

    mms_conn_srv = await mms_conn_queue.get()

    mms_inf_report = mms.InformationReportUnconfirmed(
        specification=mms.VmdSpecificObjectName(identifier='RPT'),
        data=[
            mms.VisibleStringData(rpt_id),  # RptID
            mms.BitStringData([   # OptFlds
                False,  # reserved
                True, True, True, True, True, True, True, True,
                False,  # segmentation
                ]),
            mms.UnsignedData(123),  # SqNum
            mms.BinaryTimeData(  # TimeOfEntry
                datetime.datetime(2020, 1, 1, 1, 1,
                                  tzinfo=datetime.timezone.utc)),
            mms.VisibleStringData("ld1/ln2$ds1"),  # DataSetReference
            mms.BooleanData(False),  # BufOvfl
            mms.OctetStringData(b'entry_xyz'),  # EntryID
            mms.UnsignedData(12),  # ConfRev
            # mms.UnsignedData(11),  # SubSeqNum
            # mms.BooleanData(False),  # MoreSegmentsFollow
            mms.BitStringData([True]),  # inclusion-bitstring
            mms.VisibleStringData('ld1/ln2$ST$Pos$stVal'),  # data-references
            mms_data_value,
            mms_reasons  # Reason
            ])
    await mms_conn_srv.send_unconfirmed(mms_inf_report)

    report = await report_queue.get()

    assert report.report_id == rpt_id
    assert report.sequence_number == 123
    assert report.subsequence_number is None
    assert report.more_segments_follow is None
    assert report.dataset == iec61850.PersistedDatasetRef(
            logical_device='ld1',
            logical_node='ln2',
            name='ds1')
    assert report.buffer_overflow is False
    assert report.conf_revision == 12
    assert report.entry_time == datetime.datetime(
        2020, 1, 1, 1, 1, tzinfo=datetime.timezone.utc)
    assert report.entry_id == b'entry_xyz'
    assert len(report.data) == 1
    report_data = report.data[0]
    assert report_data.ref == data_ref

    assert report_data.reasons == reasons
    assert_equal(report_data.value, data_value)

    await conn.async_close()
    await mms_srv.async_close()


@pytest.mark.parametrize('mms_report, report', [
    (mms.InformationReportUnconfirmed(
        specification=mms.VmdSpecificObjectName(identifier='RPT'),
        data=[
            mms.VisibleStringData('rpt_xyz'),  # RptID
            mms.BitStringData([   # OptFlds
                False,  # reserved
                True, True, True, True, True, True, True, True,
                False]),  # segmentation
            mms.UnsignedData(123),  # SqNum
            mms.BinaryTimeData(  # TimeOfEntry
                datetime.datetime(2020, 1, 1, 1, 1,
                                  tzinfo=datetime.timezone.utc)),
            mms.VisibleStringData("ld1/ln2$ds1"),  # DataSetReference
            mms.BooleanData(False),  # BufOvfl
            mms.OctetStringData(b'entry_xyz'),  # EntryID
            mms.UnsignedData(12),  # ConfRev
            mms.BitStringData([True]),  # inclusion-bitstring
            mms.VisibleStringData('ld1/ln2$ST$Pos$stVal'),  # data-references
            mms.BooleanData(True),  # value
            mms.BitStringData([
                False, True, False, False, False, True, False])  # Reason
            ]),
     iec61850.Report(
         report_id='rpt_xyz',
         sequence_number=123,
         subsequence_number=None,
         more_segments_follow=None,
         dataset=iec61850.PersistedDatasetRef('ld1', 'ln2', 'ds1'),
         buffer_overflow=False,
         conf_revision=12,
         entry_time=datetime.datetime(
            2020, 1, 1, 1, 1, tzinfo=datetime.timezone.utc),
         entry_id=b'entry_xyz',
         data=[iec61850.ReportData(
            iec61850.DataRef('ld1', 'ln2', 'ST', ('Pos', 'stVal')),
            True,
            reasons=set([iec61850.Reason.DATA_CHANGE,
                         iec61850.Reason.GENERAL_INTERROGATION]))])),

    (mms.InformationReportUnconfirmed(
        specification=mms.VmdSpecificObjectName(identifier='RPT'),
        data=[
            mms.VisibleStringData('rpt_xyz'),  # RptID
            mms.BitStringData([   # OptFlds
                False,  # reserved
                False, False, False, False, False, False, False, False,
                False]),  # segmentation
            mms.BitStringData([True]),  # inclusion-bitstring
            mms.BooleanData(True),  # value
            ]),
     iec61850.Report(
         report_id='rpt_xyz',
         sequence_number=None,
         subsequence_number=None,
         more_segments_follow=None,
         dataset=None,
         buffer_overflow=None,
         conf_revision=None,
         entry_time=None,
         entry_id=None,
         data=[iec61850.ReportData(
            iec61850.DataRef('ld1', 'ln2', 'ST', ('Pos', 'stVal')),
            True,
            reasons=None)])),

    # segmentation
    (mms.InformationReportUnconfirmed(
        specification=mms.VmdSpecificObjectName(identifier='RPT'),
        data=[
            mms.VisibleStringData('rpt_xyz'),  # RptID
            mms.BitStringData([   # OptFlds
                False,  # reserved
                True, True, True, True, True, True, True, True,
                True]),  # segmentation
            mms.UnsignedData(123),  # SqNum
            mms.BinaryTimeData(  # TimeOfEntry
                datetime.datetime(2020, 1, 1, 1, 1,
                                  tzinfo=datetime.timezone.utc)),
            mms.VisibleStringData("ld1/ln2$ds1"),  # DataSetReference
            mms.BooleanData(False),  # BufOvfl
            mms.OctetStringData(b'entry_xyz'),  # EntryID
            mms.UnsignedData(12),  # ConfRev
            mms.UnsignedData(0),  # SubSeqNum
            mms.BooleanData(True),  # MoreSegmentsFollow
            mms.BitStringData([True]),  # inclusion-bitstring
            mms.VisibleStringData('ld1/ln2$ST$Pos$stVal'),  # data-references
            mms.BooleanData(True),  # value
            mms.BitStringData([
                False, True, False, False, False, True, False])  # Reason
            ]),
     iec61850.Report(
         report_id='rpt_xyz',
         sequence_number=123,
         subsequence_number=0,
         more_segments_follow=True,
         dataset=iec61850.PersistedDatasetRef('ld1', 'ln2', 'ds1'),
         buffer_overflow=False,
         conf_revision=12,
         entry_time=datetime.datetime(
            2020, 1, 1, 1, 1, tzinfo=datetime.timezone.utc),
         entry_id=b'entry_xyz',
         data=[iec61850.ReportData(
            iec61850.DataRef('ld1', 'ln2', 'ST', ('Pos', 'stVal')),
            True,
            reasons=set([iec61850.Reason.DATA_CHANGE,
                         iec61850.Reason.GENERAL_INTERROGATION]))])),

    (mms.InformationReportUnconfirmed(
        specification=mms.VmdSpecificObjectName(identifier='RPT'),
        data=[
            mms.VisibleStringData('rpt_xyz'),  # RptID
            mms.BitStringData([   # OptFlds
                False,  # reserved
                False, False, False, False, False, False, False, False,
                True]),  # segmentation
            mms.UnsignedData(11),  # SubSeqNum
            mms.BooleanData(False),  # MoreSegmentsFollow
            mms.BitStringData([True]),  # inclusion-bitstring
            mms.BooleanData(True),  # value
            ]),
     iec61850.Report(
         report_id='rpt_xyz',
         sequence_number=None,
         subsequence_number=11,
         more_segments_follow=False,
         dataset=None,
         buffer_overflow=None,
         conf_revision=None,
         entry_time=None,
         entry_id=None,
         data=[iec61850.ReportData(
            iec61850.DataRef('ld1', 'ln2', 'ST', ('Pos', 'stVal')),
            True,
            reasons=None)])),
])
async def test_report_optional_fields(mms_srv_addr, mms_report, report):
    mms_conn_queue = aio.Queue()
    report_queue = aio.Queue()

    mms_srv = await mms.listen(
        connection_cb=mms_conn_queue.put_nowait,
        addr=mms_srv_addr)

    data_ref = report.data[0].ref
    conn = await iec61850.connect(
        addr=mms_srv_addr,
        data_value_types={data_ref: iec61850.BasicValueType.BOOLEAN},
        report_data_refs={report.report_id: [data_ref]},
        report_cb=report_queue.put_nowait)

    mms_conn_srv = await mms_conn_queue.get()

    await mms_conn_srv.send_unconfirmed(mms_report)

    rcv_report = await report_queue.get()
    rcv_report = rcv_report._replace(data=list(rcv_report.data))
    assert rcv_report == report

    await conn.async_close()
    await mms_srv.async_close()


@pytest.mark.parametrize('data_defs', [
    [{'value': mms.BooleanData(True),
      'type': iec61850.BasicValueType.BOOLEAN,
      'ref': iec61850.DataRef('ld1', 'ln1', 'ST', ('d1', 'Pos')),
      'mms_ref': mms.VisibleStringData('ld1/ln1$ST$d1$Pos'),
      'mms_reason': mms.BitStringData([
            False, True, False, False, False, True, False])},
     {'value': mms.BooleanData(False),
      'type': iec61850.BasicValueType.BOOLEAN,
      'ref': iec61850.DataRef('ld1', 'ln1', 'ST', ('d2', 'Pos')),
      'mms_ref': mms.VisibleStringData('ld1/ln1$ST$d2$Pos'),
      'mms_reason': mms.BitStringData([
            False, True, False, False, False, False, False])},
     {'value': mms.IntegerData(123),
      'type': iec61850.BasicValueType.INTEGER,
      'ref': iec61850.DataRef('ld1', 'ln1', 'ST', ('d3', 'Pos')),
      'mms_ref': mms.VisibleStringData('ld1/ln1$ST$d3$Pos'),
      'mms_reason': mms.BitStringData([
            False, False, False, False, False, False, False])}]
])
@pytest.mark.parametrize('inclusion, report_data', [
    ([True, True, True],
     [iec61850.ReportData(
         ref=iec61850.DataRef('ld1', 'ln1', 'ST', ('d1', 'Pos')),
         value=True,
         reasons=set([iec61850.Reason.DATA_CHANGE,
                      iec61850.Reason.GENERAL_INTERROGATION])),
      iec61850.ReportData(
         ref=iec61850.DataRef('ld1', 'ln1', 'ST', ('d2', 'Pos')),
         value=False,
         reasons=set([iec61850.Reason.DATA_CHANGE])),
      iec61850.ReportData(
         ref=iec61850.DataRef('ld1', 'ln1', 'ST', ('d3', 'Pos')),
         value=123,
         reasons=set([]))]),

    ([False, False, False],
     []),

    ([False, False, True],
     [iec61850.ReportData(
         ref=iec61850.DataRef('ld1', 'ln1', 'ST', ('d3', 'Pos')),
         value=123,
         reasons=set([]))]),

    ([True, False, True],
     [iec61850.ReportData(
         ref=iec61850.DataRef('ld1', 'ln1', 'ST', ('d1', 'Pos')),
         value=True,
         reasons=set([iec61850.Reason.DATA_CHANGE,
                      iec61850.Reason.GENERAL_INTERROGATION])),
      iec61850.ReportData(
         ref=iec61850.DataRef('ld1', 'ln1', 'ST', ('d3', 'Pos')),
         value=123,
         reasons=set([]))]),

])
async def test_report_inclusion(mms_srv_addr, data_defs,
                                inclusion, report_data):
    report_id = 'rpt_xyz'
    mms_conn_queue = aio.Queue()
    report_queue = aio.Queue()

    mms_srv = await mms.listen(
        connection_cb=mms_conn_queue.put_nowait,
        addr=mms_srv_addr)

    conn = await iec61850.connect(
        addr=mms_srv_addr,
        data_value_types={
            data_def['ref']: data_def['type']
            for data_def in data_defs},
        report_data_refs={
            report_id: [data_def['ref']
                        for data_def in data_defs]},
        report_cb=report_queue.put_nowait)

    mms_conn_srv = await mms_conn_queue.get()
    data_references = []
    data_values = []
    data_reasons = []
    for data_def, included in zip(data_defs, inclusion):
        if not included:
            continue
        data_references.append(data_def['mms_ref'])
        data_values.append(data_def['value'])
        data_reasons.append(data_def['mms_reason'])
    mms_report = mms.InformationReportUnconfirmed(
        specification=mms.VmdSpecificObjectName(identifier='RPT'),
        data=[
            mms.VisibleStringData('rpt_xyz'),  # RptID
            mms.BitStringData([   # OptFlds
                False,  # reserved
                False, False, True, False, True, False, False, False,
                False]),  # segmentation
            mms.BitStringData(inclusion),  # inclusion-bitstring
            *data_references,  # data-references
            *data_values,
            *data_reasons  # Reason
        ])  # value

    await mms_conn_srv.send_unconfirmed(mms_report)

    rcv_report = await report_queue.get()
    assert list(rcv_report.data) == report_data

    await conn.async_close()
    await mms_srv.async_close()
