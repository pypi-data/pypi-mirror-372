import argparse
import json
import os
import sys
from contextlib import redirect_stdout

from bmll import Session


def _cli_login(args):
    """Login and return the headers."""
    session = Session(username=args.username, key_path=args.key_path, passphrase=args.passphrase)
    return json.dumps(session.get_headers())


def _get_parser():
    parser = argparse.ArgumentParser('BMLL Command Line Interface')

    parser.add_argument('-u', '--username', help='api username (email)')
    parser.add_argument('-k', '--key-path', help='api private key path')
    parser.add_argument('-p', '--passphrase', help='the passphrase for the key if exists.')

    parser.add_argument('-v', '--verbose', action='store_true', help='enable logging to stdout')

    subparsers = parser.add_subparsers()

    login_parser = subparsers.add_parser('login', help='Login to the service and return the headers.')

    login_parser.set_defaults(func=_cli_login)

    return parser


def main():
    """BMLL Command Line Interface"""
    parser = _get_parser()

    args = parser.parse_args()

    if not hasattr(args, 'func'):
        # no command provided.
        parser.print_help()
        sys.exit(0)

    if args.verbose:
        result = args.func(args)
    else:
        # suppress all stdout
        with open(os.devnull, 'w') as devnull:
            with redirect_stdout(devnull):
                result = args.func(args)

    # print the result
    print(result)


if __name__ == '__main__':
    main()
