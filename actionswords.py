from esgissue.esgissue import process_command
from esgissue.constants import *
from b2handle.handleclient import EUDATHandleClient
import uuid
import json

prefix = '21.14100'


class Actionwords:
    def __init__(self, test_issue_file, test_dset_file, extra_dsets_file):
        self.issue = test_issue_file
        self.dsets = test_dset_file
        self.extra_dsets = extra_dsets_file
        self.uid = None

    def create_issue(self):
        process_command(CREATE, self.issue, self.dsets)
        self.check_issue()

    def update_issue(self):
        process_command(UPDATE, self.issue, self.dsets)
        self.check_issue()

    def close_issue(self):
        process_command(CLOSE, self.issue, self.dsets)
        self.check_issue()

    def check_issue(self):

        handle_client = EUDATHandleClient.instantiate_for_read_access()
        with open(self.issue) as data_file:
            data = json.load(data_file)
        self.uid = data['uid']
        with open(self.dsets, 'r') as dset_file:
            lines = dset_file.readlines()
            for line in lines:
                exists = False
                dataset = line.split('#')
                dset_id = dataset[0]
                dset_version = dataset[1]
                hash_basis = dset_id+'.v'+dset_version
                hash_basis_utf8 = hash_basis.encode('utf-8')
                handle_string = uuid.uuid3(uuid.NAMESPACE_URL, hash_basis_utf8)
                encoded_dict = handle_client.retrieve_handle_record(prefix + str(handle_string))
                if encoded_dict is not None:
                        handle_record = {k.decode('utf8'): v.decode('utf8') for k, v in encoded_dict.items()}
                        print handle_record
                        if 'ERRATA_IDS' in handle_record.keys():
                            for uid in str(handle_record['ERRATA_IDS']).split(';'):
                                if uid == self.uid:
                                    exists = True
                                    break
                if not exists:
                    print('An error occurred creating issue.')
                    return
        print('Issue created successfully, uid = {}.'.format(self.uid))
        return

    def change_severity(self):
        self.change_attribute('severity', 'medium')

    def change_description(self):
        self.change_attribute('description', 'Issue description updated')

    def change_status(self):
        self.change_attribute('status', 'onhold')

    def change_url(self):
        self.change_attribute('url', 'http://www.ipsl.fr/')

    def clear_issue(self):
        with open(self.issue, 'r') as issue_file:
            data = json.load(issue_file)
            del data['uid']
            del data['dateCreated']
            del data['dateUpdated']
            del data['status']
            if 'dateClosed' in data.keys():
                del data['dataClosed']
        with open(self.issue, 'w') as issue_file:
            json.dump(data, issue_file)
            print('Issue file cleared.')

    def add_dsets_to_file(self):
        with open(self.extra_dsets, 'r') as extra_file:
            extra_dsets = extra_file.readlines()
        with open(self.dsets, 'w+') as dset_file:
            for dset in extra_dsets:
                dset_file.write(dset)

    def remove_dsets_from_file(self):
        with open(self.dsets, 'w+') as dsets:
            lines = dsets.readlines()
        with open(self.dsets, 'w') as dsets:
            dsets.writelines([item for item in lines[:-1]])

    def change_attribute(self, key, new_value):
        with open(self.issue, 'r') as issue:
            data = json.load(issue)
        data[key] = new_value
        with open(self.issue, 'w') as issue:
            json.dump(data, issue)

