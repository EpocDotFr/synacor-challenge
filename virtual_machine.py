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


def pack_number(f, number):
    f.write(struct.pack('<H', number))


def unpack_number(f):
    value = f.read(2)

    if not value:
        return False

    return struct.unpack('<H', value)[0]


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


class VirtualMachineDebugger:
    def __init__(self, vm):
        self.vm = vm

        self.register_debug_opcodes()

    def register_debug_opcodes(self):
        self.debug_opcodes = {
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
            20: self.in_,
            21: self.noop,
        }

    def halt(self):
        return 'Stop execution'

    def set(self, a, b):
        pass

    def push(self, a):
        pass

    def pop(self, a):
        pass

    def eq(self, a, b, c):
        pass

    def gt(self, a, b, c):
        pass

    def jmp(self, a):
        return 'Jump to address {}'.format(self.get_reg(a, True))

    def jt(self, a, b):
        pass

    def jf(self, a, b):
        pass

    def add(self, a, b, c):
        pass

    def mult(self, a, b, c):
        pass

    def mod(self, a, b, c):
        pass

    def and_(self, a, b, c):
        pass

    def or_(self, a, b, c):
        pass

    def not_(self, a, b):
        pass

    def rmem(self, a, b):
        return 'Read memory from address {} to {}'.format(self.get_reg(b, True), self.get_reg(a, True))

    def wmem(self, a, b):
        return 'Write memory at address {} from {}'.format(self.get_reg(a, True), self.get_reg(b, True))

    def call(self, a):
        pass

    def ret(self):
        pass

    def out(self, a):
        return 'Prints ASCII char {}'.format(self.get_reg(a, True))

    def in_(self, a):
        return 'Write one char from input to {}'.format(self.get_reg(a))

    def noop(self):
        return 'Do nothing'

    def textual_opcode(self, address):
        opcode = self.vm.memory[address]

        if opcode in self.vm.opcodes and opcode in self.debug_opcodes:
            _, num_args = self.vm.opcodes.get(opcode)
            callback = self.debug_opcodes.get(opcode)
            args = self.vm.memory.getvra(address, num_args) if num_args > 0 else []

            return callback(*args)

        return ''

    def get_reg(self, value, show_value=False):
        if self.vm.registers.isri(value):
            return '<{}>{}'.format(
                self.vm.registers.getri(value),
                ' ({})'.format(self.vm.registers.get(value)) if show_value else ''
            )

        return value

    def debug_cmd(self):
        if not self.vm.input_buffer.startswith('!'):
            return False

        parsed = self.vm.input_buffer[1:-1].split(' ', maxsplit=1)
        cmd = parsed[0]

        if not hasattr(self, cmd):
            self.vm.input_buffer = ''

            return True

        args = parsed[1].split(' ') if len(parsed) > 1 else []

        print('')

        getattr(self, cmd)(*args)

        print('')

        self.vm.input_buffer = ''

        return True

    def dump(self, filename):
        self.vm.dump(filename)

        print(f'Dumped to {filename}')

    def reg(self, i=None, v=None):
        if i and v:
            self.vm.registers[int(i)] = int(v)

            return

        for index, value in enumerate(self.vm.registers):
            print(f'{index} = {value:>5}')

    def sta(self):
        print('Left (top)')

        for index, value in enumerate(list(self.vm.stack)):
            print(f'{index} = {value:>5}')

        print('Right (bottom)')

    def mem(self, a=None):
        target = int(a) if a else self.vm.memory.pointer
        start = target - 10

        if start < 0:
            start = 0

        end = target + 10

        if end > len(self.vm.memory):
            end = len(self.vm.memory)

        for address, value in enumerate(self.vm.memory[start:end], start):
            the_one = '>' if address == target else ''
            operation = self.textual_opcode(address)
            operation = ' : ' + operation if operation else ''

            print(f'{the_one:>1} {address:>5} = {value:>5}{operation}')


class VirtualMachine:
    def __init__(self):
        self.memory = Memory()
        self.registers = Registers()
        self.stack = collections.deque()

        self.register_opcodes()

        self.input_buffer = ''

        self.debugger = VirtualMachineDebugger(self)

    def load(self, filename):
        with open(filename, 'rb') as f:
            if f.read(4) == b'DUMP':
                # Registers
                for i in range(0, len(self.registers)):
                    self.registers[i] = unpack_number(f)

                # Stack length
                stack_length = unpack_number(f)

                # Stack
                for _ in range(0, stack_length):
                    self.stack.appendleft(unpack_number(f))

                # Memory pointer
                self.memory.pointer = unpack_number(f)
            else:
                f.seek(0)

            # Memory
            while True:
                number = unpack_number(f)

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
                pack_number(f, value)

            # Stack length
            pack_number(f, len(self.stack))

            # Stack
            for value in reversed(list(self.stack)):
                pack_number(f, value)

            # Memory pointer
            pack_number(f, self.memory.pointer)

            # Memory
            for number in self.memory:
                pack_number(f, number)

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

        self.registers.set(a, msum(b, c))

        self.memory.incp(4)

    def mult(self, a, b, c):
        b, c = self.registers.get(b), self.registers.get(c)

        self.registers.set(a, mmul(b, c))

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

        self.registers.set(a, bitwise_not(b, 15))

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
            self.input_buffer = input('> ') + '\n'

            if self.debugger.debug_cmd():
                return True

        c = self.input_buffer[0]

        self.input_buffer = self.input_buffer[1:]

        self.registers.set(a, ord(c))

        self.memory.incp(2)

    def noop(self):
        self.memory.incp(1)
