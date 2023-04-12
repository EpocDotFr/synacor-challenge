from virtual_machine import VirtualMachine
import argparse


def run():
    arg_parser = argparse.ArgumentParser(description='The virtual machine entry point')
    arg_parser.add_argument('file', help='Path to the virtual machine file (*.bin or *.dump) to load')
    arg_parser.add_argument('--actions', help='Path to the automatic actions file to perform')

    args = arg_parser.parse_args()

    vm = VirtualMachine()
    vm.load(args.file)

    if args.actions:
        vm.load_actions(args.actions)

    vm.run()


if __name__ == '__main__':
    run()
