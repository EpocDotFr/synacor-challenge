from virtual_machine import VirtualMachine
import argparse


def run():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('file')
    arg_parser.add_argument('--actions')

    args = arg_parser.parse_args()

    vm = VirtualMachine()
    vm.load(args.file)

    if args.actions:
        vm.load_actions(args.actions)

    vm.run()


if __name__ == '__main__':
    run()
