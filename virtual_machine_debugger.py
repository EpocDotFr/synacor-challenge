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
        return 'halt'

    def set(self, a, b):
        return 'set {} {}'.format(
            self.arg_value(a, True),
            self.arg_value(b, True)
        )

    def push(self, a):
        return 'push {}'.format(
            self.arg_value(a, True)
        )

    def pop(self, a):
        return 'pop {}'.format(
            self.arg_value(a, True)
        )

    def eq(self, a, b, c):
        return 'eq {} {} {}'.format(
            self.arg_value(a, True),
            self.arg_value(b, True),
            self.arg_value(c, True)
        )

    def gt(self, a, b, c):
        return 'gt {} {} {}'.format(
            self.arg_value(a, True),
            self.arg_value(b, True),
            self.arg_value(c, True)
        )

    def jmp(self, a):
        return 'jmp {}'.format(
            self.arg_value(a, True)
        )

    def jt(self, a, b):
        return 'jt {} {}'.format(
            self.arg_value(a, True),
            self.arg_value(b, True)
        )

    def jf(self, a, b):
        return 'jf {} {}'.format(
            self.arg_value(a, True),
            self.arg_value(b, True)
        )

    def add(self, a, b, c):
        return 'add {} {} {}'.format(
            self.arg_value(a, True),
            self.arg_value(b, True),
            self.arg_value(c, True)
        )

    def mult(self, a, b, c):
        return 'mult {} {} {}'.format(
            self.arg_value(a, True),
            self.arg_value(b, True),
            self.arg_value(c, True)
        )

    def mod(self, a, b, c):
        return 'mod {} {} {}'.format(
            self.arg_value(a, True),
            self.arg_value(b, True),
            self.arg_value(c, True)
        )

    def and_(self, a, b, c):
        return 'and {} {} {}'.format(
            self.arg_value(a, True),
            self.arg_value(b, True),
            self.arg_value(c, True)
        )

    def or_(self, a, b, c):
        return 'or {} {} {}'.format(
            self.arg_value(a, True),
            self.arg_value(b, True),
            self.arg_value(c, True)
        )

    def not_(self, a, b):
        return 'not {} {}'.format(
            self.arg_value(a, True),
            self.arg_value(b, True)
        )

    def rmem(self, a, b):
        return 'rmem {} {}'.format(
            self.arg_value(a, True),
            self.arg_value(b, True)
        )

    def wmem(self, a, b):
        return 'wmem {} {}'.format(
            self.arg_value(a, True),
            self.arg_value(b, True)
        )

    def call(self, a):
        return 'call {}'.format(
            self.arg_value(a, True)
        )

    def ret(self):
        return 'ret'

    def out(self, a):
        return 'out {}'.format(
            self.arg_value(a, True)
        )

    def in_(self, a):
        return 'in {}'.format(
            self.arg_value(a)
        )

    def noop(self):
        return 'noop'

    def textual_opcode(self, address):
        opcode = self.vm.memory[address]

        if opcode in self.vm.opcodes and opcode in self.debug_opcodes:
            _, num_args = self.vm.opcodes.get(opcode)
            callback = self.debug_opcodes.get(opcode)
            args = self.vm.memory.getvra(address, num_args) if num_args > 0 else []

            return callback(*args)

        return ''

    def arg_value(self, value, show_value=False):
        if self.vm.registers.isri(value):
            return '<{}{}>'.format(
                self.vm.registers.getri(value),
                ':{}'.format(self.vm.registers.get(value)) if show_value else ''
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
            print(f'<{index}> = {value:>5}')

    def sta(self):
        print('Left (top)')

        for index, value in enumerate(list(self.vm.stack)):
            print(f'{index} = {value:>5}')

        print('Right (bottom)')

    def mem(self, a=None):
        target = int(a) if a else self.vm.memory.pointer
        span = 20
        start = target - span

        if start < 0:
            start = 0

        end = target + span

        if end > len(self.vm.memory):
            end = len(self.vm.memory)

        for address, value in enumerate(self.vm.memory[start:end], start):
            the_one = '>' if address == target else ''
            operation = self.textual_opcode(address)
            operation = ' : ' + operation if operation else ''

            print(f'{the_one:>1} {address:>5} = {value:>5}{operation}')
