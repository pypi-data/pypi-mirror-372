import json
import logging
import os
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

import requests
import yaml

from datastation.common.find_bags import find_bags
from datastation.common.result_writer import ResultWriter


class ValidateDansBag:
    def __init__(self, config: dict, accept_type: str = 'application/json'):
        self.server_url = config['service_baseurl']
        self.accept_type = accept_type

    def validate(self, path: str, info_package_type: str, result_writer: ResultWriter, dry_run: bool = False):
        try:
            is_first = True
            for bag in find_bags(path, max_depth=2):
                self.validate_dans_bag(bag, info_package_type, result_writer, is_first, dry_run)
                is_first = False
        finally:
            result_writer.close()

    def validate_dans_bag(self, path: str, info_package_type: str, result_writer: ResultWriter, is_first: bool = True,
                          dry_run: bool = False):
        logging.info("Validating bag: {}".format(path))
        command = {
            'bagLocation': os.path.abspath(path),
            'packageType': info_package_type,
        }

        msg = MIMEMultipart("form-data")
        p = MIMEApplication(json.dumps(command), "json", _encoder=encoders.encode_noop)
        p.add_header("Content-Disposition", "form-data; name=command")
        msg.attach(p)

        body = msg.as_string().split('\n\n', 1)[1]
        headers = dict(msg.items())
        headers.update({'Accept': self.accept_type})

        if dry_run:
            print("Would have sent the following request:")
            print("POST {}/validate".format(self.server_url))
            return
        r = requests.post('{}/validate'.format(self.server_url), data=body,
                          headers=headers)
        if self.accept_type == 'application/json':
            result = json.loads(r.text)
        elif self.accept_type == 'text/plain':
            result = yaml.safe_load(r.text)
        else:
            raise Exception("Unknown accept type: {}".format(self.accept_type))

        result_writer.write(result, is_first)
