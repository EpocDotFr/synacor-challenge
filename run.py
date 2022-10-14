from virtual_machine import VirtualMachine
import argparse


def run():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('file')
    arg_parser.add_argument('--debug', action='store_true')

    args = arg_parser.parse_args()

    vm = VirtualMachine(args.debug)
    vm.load(args.file)
    vm.run()


if __name__ == '__main__':
    run()
