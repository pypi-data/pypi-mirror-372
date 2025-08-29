import argparse

import rich

from datastation.common.config import init
from datastation.common.utils import add_dry_run_arg
from datastation.dataverse.dataverse_client import DataverseClient


def add_message(args, dataverse):
    r = dataverse.banner().add(args.message, args.dismissible_by_user, dry_run=args.dry_run)
    if r is not None:
        rich.print_json(data=r.json())


def remove_message(args, dataverse):
    for msg_id in args.ids:
        r = dataverse.banner().remove(msg_id, dry_run=args.dry_run)
        if r is not None:
            rich.print_json(data=r.json())


def list_messages(args, dataverse):
    r = dataverse.banner().list(dry_run=args.dry_run)
    if r is not None:
        rich.print_json(data=r.json())


def main():
    config = init()
    dataverse = DataverseClient(config['dataverse'])

    parser = argparse.ArgumentParser()
    parser.set_defaults(func=lambda _: parser.print_help())

    subparsers = parser.add_subparsers()
    parser_add = subparsers.add_parser('add', help="Add a banner message")
    parser_add.add_argument('message', help="Message to add as banner, note that HTML can be included.")
    parser_add.add_argument('-u', '--dismissible-by-user', dest='dismissible_by_user', action='store_true',
                            help="Whether the user can permanently dismiss the banner")
    add_dry_run_arg(parser_add)
    parser_add.set_defaults(func=lambda _: add_message(_, dataverse))

    parser_remove = subparsers.add_parser('remove', help="Remove banner messages")
    parser_remove.add_argument('ids', help="One or more ids of banner messages", nargs='+')
    add_dry_run_arg(parser_remove)
    parser_remove.set_defaults(func=lambda _: remove_message(_, dataverse))

    parser_list = subparsers.add_parser('list', help="List banner messages")
    add_dry_run_arg(parser_list)
    parser_list.set_defaults(func=lambda _: list_messages(_, dataverse))

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
