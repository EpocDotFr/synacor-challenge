from virtual_machine_debugger import VirtualMachineDebugger
import collections
import utils


class Memory(collections.UserList):
    def __init__(self, *args, **kvargs):
        super(Memory, self).__init__(*args, **kvargs)

        self.pointer = 0

    def getpva(self, i):
        """Get pointer value after"""
        return self[self.pointer + i]

    def getpvra(self, i):
        """Get pointer value range after"""
        return self[self.pointer + 1:self.pointer + i + 1]

    def getvra(self, a, i):
        """Get value range after"""
        return self[a + 1:a + i + 1]

    def getpv(self):
        """Get pointer value"""
        return self[self.pointer]

    def setp(self, address):
        """Set pointer"""
        self.pointer = address

    def incp(self, i):
        """Increment pointer"""
        self.pointer += i


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

        self.register_opcodes()

        self.input_buffer = ''

        self.debugger = VirtualMachineDebugger(self)
        self.actions = []

    def load(self, filename):
        with open(filename, 'rb') as f:
            if f.read(4) == b'DUMP':
                # Registers
                for i in range(0, len(self.registers)):
                    self.registers[i] = utils.unpack_number(f)

                # Stack length
                stack_length = utils.unpack_number(f)

                # Stack
                for _ in range(0, stack_length):
                    self.stack.appendleft(utils.unpack_number(f))

                # Memory pointer
                self.memory.pointer = utils.unpack_number(f)
            else:
                f.seek(0)

            # Memory
            while True:
                number = utils.unpack_number(f)

                if number is False:
                    break  # EOF

                if number >= 32776:
                    raise ValueError(f'Out of bounds number {number}')

                self.memory.append(number)

    def dump(self, filename):
        with open(filename, 'wb') as f:
            f.write(b'DUMP')

            # Registers
            for value in self.registers:
                utils.pack_number(f, value)

            # Stack length
            utils.pack_number(f, len(self.stack))

            # Stack
            for value in reversed(list(self.stack)):
                utils.pack_number(f, value)

            # Memory pointer
            utils.pack_number(f, self.memory.pointer)

            # Memory
            for number in self.memory:
                utils.pack_number(f, number)

    def load_actions(self, filename):
        with open(filename, 'r') as f:
            self.actions = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

    def run(self):
        while True:
            try:
                if self.exec() is False:
                    break
            except KeyboardInterrupt:
                break

    def exec(self):
        opcode = self.memory.getpv()

        if opcode in self.opcodes:
            callback, num_args = self.opcodes.get(opcode)
            args = self.memory.getpvra(num_args) if num_args > 0 else []

            return callback(*args)

        print(f'Unhandled opcode {opcode}')

        return False

    def register_opcodes(self):
        self.opcodes = {
            0: (self.halt, 0),
            1: (self.set, 2),
            2: (self.push, 1),
            3: (self.pop, 1),
            4: (self.eq, 3),
            5: (self.gt, 3),
            6: (self.jmp, 1),
            7: (self.jt, 2),
            8: (self.jf, 2),
            9: (self.add, 3),
            10: (self.mult, 3),
            11: (self.mod, 3),
            12: (self.and_, 3),
            13: (self.or_, 3),
            14: (self.not_, 2),
            15: (self.rmem, 2),
            16: (self.wmem, 2),
            17: (self.call, 1),
            18: (self.ret, 0),
            19: (self.out, 1),
            20: (self.in_, 1),
            21: (self.noop, 0),
        }

    def halt(self):
        return False

    def set(self, a, b):
        b = self.registers.get(b)

        self.registers.set(a, b)

        self.memory.incp(3)

    def push(self, a):
        a = self.registers.get(a)

        self.stack.appendleft(a)

        self.memory.incp(2)

    def pop(self, a):
        v = self.stack.popleft()
        v = self.registers.get(v)

        self.registers.set(a, v)

        self.memory.incp(2)

    def eq(self, a, b, c):
        b, c = self.registers.get(b), self.registers.get(c)

        self.registers.set(a, 1 if b == c else 0)

        self.memory.incp(4)

    def gt(self, a, b, c):
        b, c = self.registers.get(b), self.registers.get(c)

        self.registers.set(a, 1 if b > c else 0)

        self.memory.incp(4)

    def jmp(self, a):
        a = self.registers.get(a)

        self.memory.setp(a)

    def jt(self, a, b):
        a, b = self.registers.get(a), self.registers.get(b)

        if a != 0:
            return self.jmp(b)
        else:
            self.memory.incp(3)

    def jf(self, a, b):
        a, b = self.registers.get(a), self.registers.get(b)

        if a == 0:
            return self.jmp(b)
        else:
            self.memory.incp(3)

    def add(self, a, b, c):
        b, c = self.registers.get(b), self.registers.get(c)

        self.registers.set(a, utils.msum(b, c))

        self.memory.incp(4)

    def mult(self, a, b, c):
        b, c = self.registers.get(b), self.registers.get(c)

        self.registers.set(a, utils.mmul(b, c))

        self.memory.incp(4)

    def mod(self, a, b, c):
        b, c = self.registers.get(b), self.registers.get(c)

        self.registers.set(a, b % c)

        self.memory.incp(4)

    def and_(self, a, b, c):
        b, c = self.registers.get(b), self.registers.get(c)

        self.registers.set(a, b & c)

        self.memory.incp(4)

    def or_(self, a, b, c):
        b, c = self.registers.get(b), self.registers.get(c)

        self.registers.set(a, b | c)

        self.memory.incp(4)

    def not_(self, a, b):
        b = self.registers.get(b)

        self.registers.set(a, utils.bitwise_not(b, 15))

        self.memory.incp(3)

    def rmem(self, a, b):
        b = self.registers.get(b)

        self.registers.set(a, self.memory[b])

        self.memory.incp(3)

    def wmem(self, a, b):
        a, b = self.registers.get(a), self.registers.get(b)

        self.memory[a] = b

        self.memory.incp(3)

    def call(self, a):
        a = self.registers.get(a)

        self.stack.appendleft(self.memory.pointer + 2)

        return self.jmp(a)

    def ret(self):
        a = self.stack.popleft()
        a = self.registers.get(a)

        return self.jmp(a)

    def out(self, a):
        a = self.registers.get(a)

        print(chr(a), end='')

        self.memory.incp(2)

    def in_(self, a):
        if not self.input_buffer:
            if self.actions:
                action = self.actions.pop(0)

                print(f'> {action}')

                self.input_buffer = action + '\n'
            else:
                self.input_buffer = input('> ') + '\n'

                if self.debugger.debug_cmd():
                    return True

        c = self.input_buffer[0]

        self.input_buffer = self.input_buffer[1:]

        self.registers.set(a, ord(c))

        self.memory.incp(2)

    def noop(self):
        self.memory.incp(1)
