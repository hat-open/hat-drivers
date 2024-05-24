from hat import util


def des_encrypt(des_key: util.Bytes,
                data: util.Bytes,
                iv: util.Bytes
                ) -> util.Bytes:
    if len(des_key) != 8:
        raise Exception('invalid key length')

    if len(iv) != 8:
        raise Exception('invalid iv length')

    raise NotImplementedError()


def des_decrypt(des_key: util.Bytes,
                data: util.Bytes,
                iv: util.Bytes
                ) -> util.Bytes:
    if len(des_key) != 8:
        raise Exception('invalid key length')

    if len(iv) != 8:
        raise Exception('invalid iv length')

    raise NotImplementedError()
