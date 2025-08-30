import argparse

from motoko.scripts import create_studies, info, kill, launcher, orchestrator

commands = [create_studies, info, kill, launcher, orchestrator]


def main() -> None:
    """Entry point for the command line interface."""
    args = parse_args()

    for command in commands:
        if args.command == command.command:
            command.main(args)
            break


def parse_args():
    parser = argparse.ArgumentParser()
    parser.prog = "motoko"

    # Create subparsers for each command
    command_parsers = parser.add_subparsers(dest="command", help="command to run")
    command_parsers.required = True

    for command in commands:
        command_parser = command_parsers.add_parser(
            command.command, help=command.command_help
        )
        command.populate_arg_parser(command_parser)

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
