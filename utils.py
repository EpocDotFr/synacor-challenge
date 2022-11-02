import struct


MODULO = 32768


def msum(a, b):
    """Modulo sum"""
    return (a + b) % MODULO


def mmul(a, b):
    """Modulo multiply"""
    return (a * b) % MODULO


def bitwise_not(number, num_bits):
    return (1 << num_bits) - 1 - number


def pack_number(f, number):
    f.write(struct.pack('<H', number))


def unpack_number(f):
    value = f.read(2)

    if not value:
        return False

    return struct.unpack('<H', value)[0]
