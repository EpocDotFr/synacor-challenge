from collections import UserList
import struct


class Memory(UserList):
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


class VirtualMachine:
    def __init__(self):
        self.memory = Memory()
        self.registers = []
        self.stack = []

        self.opcodes = {
            0: self.halt,
            6: self.jmp,
            7: self.jt,
            8: self.jf,
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

        print(f'Memory: {len(self.memory)} addresses')

    def run(self):
        while True:
            if not self.exec():
                break

    def exec(self):
        number = self.memory.getpv()

        if number in self.opcodes:
            return self.opcodes.get(number)()

        print(number)

        return False

    def halt(self):
        return False

    def jmp(self):
        a = self.memory.getpva(1)

        self.memory.setp(a)

        return True

    def jt(self):
        a, b = self.memory.getpvra(2)

        if a != 0:
            self.memory.setp(b)
        else:
            self.memory.incp(3)

        return True

    def jf(self):
        a, b = self.memory.getpvra(2)

        if a == 0:
            self.memory.setp(b)
        else:
            self.memory.incp(3)

        return True

    def out(self):
        a = self.memory.getpva(1)

        print(chr(a), end='')

        self.memory.incp(2)

        return True

    def noop(self):
        self.memory.incp(1)

        return True
