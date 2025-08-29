import requests

from datastation.common.utils import print_dry_run_message


class VerifyDatasetService:

    def __init__(self, config):
        self.base_url = config['url']

    def verify_dataset(self, pid, dry_run=False):
        url = f'{self.base_url}/verify'
        json = {'datasetPid': pid}
        headers = {'Content-Type': 'application/json'}
        if dry_run:
            print_dry_run_message(method='POST', url=url, headers=headers, json=json)
            return None
        else:
            r = requests.post(url, headers=headers, json=json)

        return r.json()
