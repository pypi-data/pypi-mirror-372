import argparse

from datastation.common.config import init
from datastation.common.utils import add_dry_run_arg
from datastation.dataverse.dataverse_client import DataverseClient
from datastation.dataverse.user_import import UserImport


def main():
    config = init()

    parser = argparse.ArgumentParser(description='Import users from a CSV file')
    parser.add_argument('--easy', dest='is_easy_format',
                        help="The csv file is exported from EASY and has the following columns: UID, INITIALS, SURNAME,"
                             "PREFIX, EMAIL, ORGANISATION, FUNCTION, PASSWORD-HASH. "
                             "If not set, the following columns are expected: Username, GivenName, FamilyName, Email, "
                             "Affiliation, Position, encryptedpassword",
                        action='store_true')
    parser.add_argument('-k', '--builtin-users-key', help="BuiltinUsers.KEY set in Dataverse")
    parser.add_argument('-i', '--input-csv', help="the csv file containing the users and hashed passwords")
    add_dry_run_arg(parser)

    args = parser.parse_args()
    dataverse_client = DataverseClient(config['dataverse'])
    user_import = UserImport(dataverse_client, builtin_users_key=args.builtin_users_key,
                             is_easy_format=args.is_easy_format, dry_run=args.dry_run)
    user_import.import_users(args.input_csv)


if __name__ == '__main__':
    main()
