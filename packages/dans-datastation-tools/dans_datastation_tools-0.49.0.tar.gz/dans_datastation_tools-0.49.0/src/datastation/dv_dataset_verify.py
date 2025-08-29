import argparse

import rich

from datastation.common.config import init
from datastation.common.utils import add_dry_run_arg
from datastation.verifydataset.verify_dataset import VerifyDatasetService


def main():
    config = init()
    verify_dataset_service = VerifyDatasetService(config['verify_dataset'])

    parser = argparse.ArgumentParser(description='Verify metadata of a dataset')
    parser.add_argument('pid', help='The pid of the datasets to verify')
    add_dry_run_arg(parser)

    args = parser.parse_args()
    r = verify_dataset_service.verify_dataset(args.pid, dry_run=args.dry_run)
    rich.print_json(data=r)


if __name__ == '__main__':
    main()
