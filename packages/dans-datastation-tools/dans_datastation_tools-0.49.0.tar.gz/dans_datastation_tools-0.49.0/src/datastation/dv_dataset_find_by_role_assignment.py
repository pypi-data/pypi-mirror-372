import argparse
import logging

from datastation.common.config import init
from datastation.dataverse.dataverse_client import DataverseClient


def find_datasets_by_role_assignment(database, role_assignment):
    [role_assignee, role_alias] = role_assignment.split('=')
    logging.debug(f"role_assignee={role_assignee}, role_alias={role_alias}")
    select_statement = \
        f"select concat(dvo.protocol, ':', dvo.authority, '/', dvo.identifier) " \
        f"from roleassignment ra inner join dataverserole dr on ra.role_id=dr.id " \
        f"inner join dvobject dvo on definitionpoint_id=dvo.id " \
        f"where dtype='Dataset' and assigneeidentifier='{role_assignee}' and alias='{role_alias}'"
    logging.debug(f"select_statement={select_statement}")
    result = database.query(select_statement)
    if len(result) == 0:
        print(f"No datasets for user {role_assignee} with role {role_alias}")
    for r in result:
        print(r[0])


def main():
    config = init()
    dataverse = DataverseClient(config['dataverse'])
    parser = argparse.ArgumentParser(description='Find datasets by role assignment.')
    parser.add_argument('role_assignment', help='The role assignment to find, e.g. "@user1=curator"')
    args = parser.parse_args()

    with dataverse.database() as database:
        find_datasets_by_role_assignment(database, args.role_assignment)


if __name__ == '__main__':
    main()
