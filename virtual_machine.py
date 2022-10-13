import collections
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


class Memory(collections.UserList):
    def __init__(self, *args, **kvargs):
        super(Memory, self).__init__(*args, **kvargs)

        self.pointer = 0

    def getpvb(self, i):
        """Get pointer value before"""
        return self[self.pointer - i]

    def getpva(self, i):
        """Get pointer value after"""
        return self[self.pointer + i]

    def getpvrb(self, i):
        """Get pointer value range before"""
        return self[self.pointer - i - 1:self.pointer - 1]

    def getpvra(self, i):
        """Get pointer value range after"""
        return self[self.pointer + 1:self.pointer + i + 1]

    def getpv(self):
        """Get pointer value"""
        return self[self.pointer]

    def setp(self, address):
        """Set pointer"""
        self.pointer = address

    def incp(self, i):
        """Increment pointer"""
        self.pointer += i

    def decp(self, i):
        """Decrement pointer"""
        self.pointer -= i


class Registers(collections.UserList):
    START = 32768
    END = 32775

    def __init__(self):
        self.indexes = list(range(self.START, self.END + 1))

        super(Registers, self).__init__(
            [0 for _ in range(0, len(self.indexes))]
        )

    def get(self, iv):
        if not self.isri(iv):
            return iv

        i = self.getri(iv)

        return self[i]

    def set(self, iv, v):
        if not self.isri(iv):
            raise ValueError('Not a register index')

        i = self.getri(iv)

        self[i] = v

    def isri(self, iv):
        """Is register index"""
        return self.START <= iv <= self.END

    def getri(self, iv):
        """Get register index"""
        return self.indexes.index(iv)


class VirtualMachine:
    def __init__(self):
        self.memory = Memory()
        self.registers = Registers()
        self.stack = collections.deque()

        self.opcodes = {
            0: self.halt,
            1: self.set,
            2: self.push,
            3: self.pop,
            4: self.eq,
            5: self.gt,
            6: self.jmp,
            7: self.jt,
            8: self.jf,
            9: self.add,
            10: self.mult,
            11: self.mod,
            12: self.and_,
            13: self.or_,
            14: self.not_,
            15: self.rmem,
            16: self.wmem,
            17: self.call,
            18: self.ret,
            19: self.out,
            21: self.noop,
        }

    def load(self, binary_file):
        with open(binary_file, 'rb') as f:
            while True:
                value = f.read(2)

                if not value:  # EOF
                    break

                number, = struct.unpack('<H', value)

                if number >= 32776:
                    raise ValueError(f'Out of bounds number {number}')

                self.memory.append(number)

        print(f'Memory: loaded {len(self.memory)} addresses')

    def run(self):
        while True:
            if self.exec() is False:
                break

    def exec(self):
        opcode = self.memory.getpv()

        if opcode in self.opcodes:
            return self.opcodes.get(opcode)()

        print(f'Unhandled opcode {opcode}')

        return False

    def halt(self):
        return False

    def set(self):
        a, b = self.memory.getpvra(2)
        b = self.registers.get(b)

        self.registers.set(a, b)

        self.memory.incp(3)

    def push(self):
        a = self.memory.getpva(1)
        a = self.registers.get(a)

        self.stack.appendleft(a)

        self.memory.incp(2)

    def pop(self):
        a = self.memory.getpva(1)

        v = self.stack.popleft()
        v = self.registers.get(v)

        self.registers.set(a, v)

        self.memory.incp(2)

    def eq(self):
        a, b, c = self.memory.getpvra(3)
        b, c = self.registers.get(b), self.registers.get(c)

        self.registers.set(a, 1 if b == c else 0)

        self.memory.incp(4)

    def gt(self):
        a, b, c = self.memory.getpvra(3)
        b, c = self.registers.get(b), self.registers.get(c)

        self.registers.set(a, 1 if b > c else 0)

        self.memory.incp(4)

    def jmp(self, a=None):
        a = a or self.registers.get(self.memory.getpva(1))

        self.memory.setp(a)

    def jt(self):
        a, b = self.memory.getpvra(2)
        a, b = self.registers.get(a), self.registers.get(b)

        if a != 0:
            return self.jmp(b)
        else:
            self.memory.incp(3)

    def jf(self):
        a, b = self.memory.getpvra(2)
        a, b = self.registers.get(a), self.registers.get(b)

        if a == 0:
            return self.jmp(b)
        else:
            self.memory.incp(3)

    def add(self):
        a, b, c = self.memory.getpvra(3)
        b, c = self.registers.get(b), self.registers.get(c)

        self.registers.set(a, msum(b, c))

        self.memory.incp(4)

    def mult(self):
        a, b, c = self.memory.getpvra(3)
        b, c = self.registers.get(b), self.registers.get(c)

        self.registers.set(a, mmul(b, c))

        self.memory.incp(4)

    def mod(self):
        a, b, c = self.memory.getpvra(3)
        b, c = self.registers.get(b), self.registers.get(c)

        self.registers.set(a, b % c)

        self.memory.incp(4)

    def and_(self):
        a, b, c = self.memory.getpvra(3)
        b, c = self.registers.get(b), self.registers.get(c)

        self.registers.set(a, b & c)

        self.memory.incp(4)

    def or_(self):
        a, b, c = self.memory.getpvra(3)
        b, c = self.registers.get(b), self.registers.get(c)

        self.registers.set(a, b | c)

        self.memory.incp(4)

    def not_(self):
        a, b = self.memory.getpvra(2)
        b = self.registers.get(b)

        self.registers.set(a, bitwise_not(b, 15))

        self.memory.incp(3)

    def rmem(self):
        a, b = self.memory.getpvra(2)
        b = self.registers.get(b)

        self.registers.set(a, self.memory[b])

        self.memory.incp(3)

    def wmem(self):
        a, b = self.memory.getpvra(2)
        a, b = self.registers.get(a), self.registers.get(b)

        self.memory[a] = b

        self.memory.incp(3)

    def call(self):
        a = self.memory.getpva(1)
        a = self.registers.get(a)

        self.stack.appendleft(self.memory.pointer + 2)

        return self.jmp(a)

    def ret(self):
        a = self.stack.popleft()
        a = self.registers.get(a)

        return self.jmp(a)

    def out(self):
        a = self.memory.getpva(1)
        a = self.registers.get(a)

        print(chr(a), end='')

        self.memory.incp(2)

    def noop(self):
        self.memory.incp(1)
