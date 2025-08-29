import argparse

import rich

from datastation.common.config import init
from datastation.common.utils import add_dry_run_arg
from datastation.dataverse.dataverse_client import DataverseClient


def add_lock(args, dataverse_client: DataverseClient):
    r = dataverse_client.dataset(args.pid).add_lock(args.lock_type, dry_run=args.dry_run)
    if r is not None:
        rich.print_json(data=r)


def remove_lock(args, dataverse_client: DataverseClient):
    if args.lock_type == 'all':
        r = dataverse_client.dataset(args.pid).remove_all_locks(dry_run=args.dry_run)
    else:
        r = dataverse_client.dataset(args.pid).remove_lock(args.lock_type, dry_run=args.dry_run)
    if r is not None:
        rich.print_json(data=r)


def list_locks(args, dataverse_client: DataverseClient):
    r = dataverse_client.dataset(args.pid).get_locks()
    if r is not None:
        rich.print_json(data=r)


def main():
    config = init()
    dataverse = DataverseClient(config['dataverse'])
    lock_types = ['Ingest', 'Workflow', 'InReview', 'DcmUpload', 'finalizePublication', 'EditInProgress',
                  'FileValidationFailed']

    parser = argparse.ArgumentParser(description='Manage locks on datasets. Locks can have the following types: '
                                                 ', '.join(lock_types) + '.')

    subparsers = parser.add_subparsers(help='subcommands', dest='subcommand')

    parser_add = subparsers.add_parser('add', help='add a lock to a dataset.')
    parser_add.add_argument('lock_type', help='the type of lock to add.', choices=lock_types)
    parser_add.add_argument('pid', help='the persistent identifier of the dataset.')
    add_dry_run_arg(parser_add)
    parser_add.set_defaults(func=add_lock)

    parser_remove = subparsers.add_parser('remove', help='remove a lock from a dataset.')
    parser_remove.add_argument('lock_type', help='the type of lock to remove or all to remove all locks.',
                               choices=lock_types + ['all'])
    parser_remove.add_argument('pid', help='the persistent identifier of the dataset.')
    add_dry_run_arg(parser_remove)
    parser_remove.set_defaults(func=remove_lock)

    parser_list = subparsers.add_parser('list', help='list locks on a dataset.')
    parser_list.add_argument('pid', help='the persistent identifier of the dataset.')
    add_dry_run_arg(parser_list)
    parser_list.set_defaults(func=list_locks)

    args = parser.parse_args()
    args.func(args, dataverse)


if __name__ == '__main__':
    main()
