#!/usr/bin/env python3

""" """

from argparse import ArgumentParser
from argparse import Namespace as Args
from collections.abc import Sequence
from contextlib import suppress
from nanokontrol_config.nanokontrol_studio import (
    DeviceConnection,
    Configuration,
    to_yaml,
    from_yaml,
)
import mido
from pathlib import Path
import sys
import logging


def fn_info(args):
    for port_name in mido.get_input_names():
        print(port_name)
    print()
    for port_name in mido.get_output_names():
        print(port_name)
    print()
    for port_name in mido.get_ioport_names():
        print(port_name)
    print()


def fn_export_config(args):
    with DeviceConnection(args.port) as connection:
        current_config = Configuration(
            global_config=connection.read_global_config(),
            scene_config=(connection.read_scene_config(i) for i in range(5)),
        )
        # current_config.global_config.dump()
        for i in range(1):
            current_config.scene_config[i].dump()
    if args.output.name == "-":
        sys.stdout.write(to_yaml(current_config))
    else:
        with args.output.open("w") as output_file:
            output_file.write(to_yaml(current_config))


def fn_set_config(args):
    if args.input.name == "-":
        c = from_yaml(sys.stdin)
    else:
        with args.input.open() as input_file:
            c = from_yaml(input_file)
    with DeviceConnection(args.port) as connection:
        # c.global_config.dump()
        connection.write_global_config(c.global_config)
        for i in range(5):
            connection.write_scene_config(i, c.scene_config[i])
        # c.scene_config[0].dump()
        # connection.write_scene_config(0, c.scene_config[0])


def fn_patch_config(args):
    raise NotImplementedError("sorry, not yet")


def parse_args(argv: Sequence[str] | None = None) -> Args:
    parser = ArgumentParser(__doc__)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--port", "-p", type=str, default="nanoKONTROL Studio")

    parser.set_defaults(func=lambda *_: parser.print_usage())
    subparsers = parser.add_subparsers(
        help="available commands", metavar="CMD"
    )

    parser_info = subparsers.add_parser("help")
    parser_info.set_defaults(func=lambda *_: parser.print_help())

    parser_export = subparsers.add_parser("export-config", aliases=["e"])
    parser_export.set_defaults(func=fn_export_config)
    parser_export.add_argument(
        "--output", "-o", type=Path, default="nanoKontrol_Studio-config.yaml"
    )

    parser_set = subparsers.add_parser("set-config", aliases=["s"])
    parser_set.set_defaults(func=fn_set_config)
    parser_set.add_argument(
        "--input", "-i", type=Path, default="nanoKontrol_Studio-config.yaml"
    )

    parser_patch = subparsers.add_parser("patch-config", aliases=["p"])
    parser_patch.set_defaults(func=fn_patch_config)

    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    logging.basicConfig(
        format=f"%(levelname)-7s %(asctime)s.%(msecs)03d %(name)-12s│ %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
    )

    with suppress(KeyboardInterrupt):
        args.func(args)


if __name__ == "__main__":
    main()
