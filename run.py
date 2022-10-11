from virtual_machine import VirtualMachine

if __name__ == '__main__':
    vm = VirtualMachine()
    vm.load('materials/challenge.bin')
    vm.run()
