import argparse
import json
import sys

import rich

from datastation.common.config import init
from datastation.common.utils import add_dry_run_arg
from datastation.dataverse.dataverse_client import DataverseClient


def main():
    config = init()
    parser = argparse.ArgumentParser(description='Retrieves the native format for a dataset version')
    parser.add_argument('pid', help='the pid of the dataset')
    parser.add_argument('-v', '---version', dest="version", default=':latest', help='the version of the dataset')
    parser.add_argument('-o', '--output-file', dest='output_file', default='-',
                        help='the file to write the output to or - for stdout')
    add_dry_run_arg(parser)

    args = parser.parse_args()
    dataverse = DataverseClient(config['dataverse'])
    try:
        metadata = dataverse.dataset(args.pid).get_metadata(args.version, dry_run=args.dry_run)
        if args.output_file == '-':
            rich.print_json(data=metadata)
        else:
            with open(args.output_file, 'w') as f:
                json.dump(metadata, f)
        print(f"Retrieved metadata for dataset {args.pid} version {args.version}", file=sys.stderr)
    except Exception as e:
        print(f"Error retrieving metadata: {e}")


if __name__ == '__main__':
    main()
