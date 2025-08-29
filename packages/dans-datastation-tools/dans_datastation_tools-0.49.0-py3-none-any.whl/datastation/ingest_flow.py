import argparse

from datastation.common.config import init
from datastation.ingestflow.ingest_flow import IngestFlow


def main():
    config = init()
    ingest_flow = IngestFlow(config['ingest_flow'])

    parser = argparse.ArgumentParser(description='Commands to control the ingest flow')
    parser.set_defaults(func=lambda _: parser.print_help())
    parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true',
                        help='Only print command to be sent to server, but do not actually send it')

    subparsers = parser.add_subparsers(help='sub-command help', dest='command')

    parser_start_migration = subparsers.add_parser('start-migration', help='Start migration of deposit or batch of '
                                                                           'deposits')
    parser_start_migration.add_argument('deposit_path', metavar='<batch-or-deposit>',
                                        help='Directory containing one deposit or a batch of deposits')
    parser_start_migration.add_argument('-s', '--single', dest="single_deposit", action="store_true",
                                        help="<batch-or-deposit> refers to a single deposit")
    parser_start_migration.add_argument('-c', '--continue', dest='continue_previous', action='store_true',
                                        help="continue previously stopped batch "
                                             "(i.e. allow output directory to be non-empty)")
    parser_start_migration.set_defaults(func=lambda _: ingest_flow.start_ingest(args.deposit_path, args.single_deposit,
                                                                                args.continue_previous,
                                                                                is_migration=True))

    parser_start_import = subparsers.add_parser('start-import', help='Start import of deposit or batch of deposits')
    parser_start_import.add_argument('deposit_path', metavar='<batch-or-deposit>',
                                     help='Directory containing one deposit or a batch of deposits')
    parser_start_import.add_argument('-s', '--single', dest="single_deposit", action="store_true",
                                     help="<batch-or-deposit> refers to a single deposit")
    parser_start_import.add_argument('-c', '--continue', dest='continue_previous', action='store_true',
                                     help="continue previously stopped batch "
                                          "(i.e. allow output directory to be non-empty)")
    parser_start_import.set_defaults(func=lambda _: ingest_flow.start_ingest(args.deposit_path, args.single_deposit,
                                                                             args.continue_previous,
                                                                             is_migration=False))

    parser_block_target = subparsers.add_parser('block-target', help='Block target')
    parser_block_target.add_argument('target', metavar='<target>', help='Target to block')
    parser_block_target.set_defaults(func=lambda _: ingest_flow.block_target(args.target))

    parser_unblock_target = subparsers.add_parser('unblock-target', help='Unblock target')
    parser_unblock_target.add_argument('target', metavar='<target>', help='Target to unblock')
    parser_unblock_target.set_defaults(func=lambda _: ingest_flow.unblock_target(args.target))

    parser_list_events = subparsers.add_parser('list-events', help='List events')
    group = parser_list_events.add_mutually_exclusive_group()
    group.add_argument('-s', '--source', dest='source', help='Source to filter on')
    group.add_argument('-d', '--deposit', dest='deposit', help='UUID of deposit to filter on')
    parser_list_events.set_defaults(func=lambda _: ingest_flow.list_events(args.source, args.deposit))

    parser_progress_report = subparsers.add_parser('progress-report', help='Progress report')
    parser_progress_report.add_argument('batch', metavar='<batch>', help='Batch to report on')
    parser_progress_report.set_defaults(func=lambda _: ingest_flow.progress_report(args.batch))

    parser_copy_batch = subparsers.add_parser('copy-batch', help='Copy batch to ingest area.')
    parser_copy_batch.add_argument('batch', metavar='<batch>', help='Batch to copy')
    parser_copy_batch.add_argument('target', metavar='<target>', help='Target to copy to')
    parser_copy_batch.set_defaults(func=lambda _: ingest_flow.copy_batch_to_ingest_area(args.batch, args.target))

    args = parser.parse_args()
    ingest_flow.set_dry_run(args.dry_run)

    args.func(args)


if __name__ == '__main__':
    main()
