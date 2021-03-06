from subprocess import CalledProcessError

from esgissue.esgissue import process_command
from esgissue.constants import *
from esgissue.utils import set_credentials, reset_passphrase, encrypt_with_key, reset_credentials, get_datasets, \
                            prepare_retrieval

from b2handle.handleclient import EUDATHandleClient
import uuid
import subprocess as sub
import json
import esgfpid
import requests
from time import sleep


prefix = '21.14100/'
download_dir = 'samples/download/'
download_issue = 'dw_issue.json'
download_dset = 'dw_dset.txt'
username = 'AtefBN'
token = 'xx'
passphrase = 'atef'
new_passphrase = 'atefbennasser'


class Actionwords:
    def __init__(self, test_issue_file, test_dset_file, extra_dsets_file=None, uid=None):
        with open(test_issue_file, 'r') as issue_file:
            self.issue = json.load(issue_file)
        self.issue_path = test_issue_file
        with open(test_dset_file, 'r') as dset_file:
            self.dsets = get_datasets(dset_file)
        self.dsets_path = test_dset_file
        self.extra_dsets = extra_dsets_file
        self.uid = uid

    def create_issue(self):
        set_credentials(username=username, token=token, passphrase=passphrase)
        # Required if the datasets don't have handles before.
        # create_handle_for_dataset(self.dsets)
        process_command(command=CREATE, issue_file=self.issue, dataset_file=self.dsets, passphrase=passphrase,
                        issue_path=self.issue_path, dataset_path=self.dsets_path)
        self.check_issue_files()
        reset_credentials()

    def update_issue(self):
        set_credentials(username=username, token=token, passphrase=passphrase)
        process_command(command=UPDATE, issue_file=self.issue, dataset_file=self.dsets, passphrase=passphrase,
                        issue_path=self.issue_path, dataset_path=self.dsets_path)
        print(len(self.dsets))
        self.check_issue_files()
        reset_credentials()

    def close_issue(self):
        set_credentials(username=username, token=token, passphrase=passphrase)
        process_command(command=CLOSE, issue_file=self.issue, dataset_file=self.dsets, passphrase=passphrase,
                        issue_path=self.issue_path, dataset_path=self.dsets_path)
        self.check_issue_files()
        reset_credentials()

    def retrieve_issue(self):
        process_command(command=RETRIEVE, issue_path=self.issue, dataset_path=self.dsets,
                        list_of_ids=[self.uid])

    def check_issue_pid(self):
        # Checking PID HANDLE
        print('checkin PIDs')
        sleep(5)
        handle_client = EUDATHandleClient.instantiate_for_read_access()
        self.uid = self.issue['uid']
        for line in self.dsets:
            print('CHECKING {} ERRATA IDS'.format(line))
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
                    if 'ERRATA_IDS' in handle_record.keys():
                        for uid in str(handle_record['ERRATA_IDS']).split(';'):
                            if uid == self.uid:
                                exists = True
                                break
            if not exists:
                print('An error occurred updating handle.')
                return exists

    def check_issue_files(self):
        # Comparing local file to server copy.
        self.uid = self.issue['uid']
        dataset_dw = os.path.join(download_dir, download_dset)
        issue_dw = os.path.join(download_dir, download_issue)
        list_of_ids, issues, dsets = prepare_retrieval([self.uid], issue_dw, dataset_dw)
        process_command(command=RETRIEVE, issue_path=issues, dataset_path=dsets, list_of_ids=list_of_ids)
        with open(self.issue_path, 'r') as issue:
            local_data = json.load(issue)
        with open(issue_dw, 'r') as remote_issue:
            downloaded_data = json.load(remote_issue)
        # Server copy and local copy of date updated and closed will never match
        # on second level.
        issue_file_test = self.compare_json(local_data, downloaded_data, [DATE_UPDATED, DATE_CLOSED])
        if not issue_file_test:
            print(local_data)
            print(downloaded_data)
        with open(self.dsets_path, 'r') as dsets:
            datasets = dsets.readlines()
        with open(dataset_dw, 'r') as remote_dsets:
            remote_datasets = remote_dsets.readlines()
        # Test must be manual, retrieved list is not sorted
        dataset_file_test = set(datasets) == set(remote_datasets)
        if not dataset_file_test:
            print(datasets)
            print(remote_datasets)
        if issue_file_test and dataset_file_test:
            return True
        else:
            return False

    def change_severity(self):
        self.change_attribute('severity', 'medium')

    def change_description(self):
        self.change_attribute('description', 'Issue description updated')

    def change_status(self):
        self.change_attribute('status', 'onhold')

    def change_url(self):
        self.change_attribute('url', 'http://www.ipsl.fr/')

    def clear_issue(self):
        data = self.issue
        if 'uid' in data.keys():
            del data['uid']
        if 'dateCreated' in data.keys():
            del data['dateCreated']
        if 'dateUpdated' in data.keys():
            del data['dateUpdated']
        if 'status' in data.keys():
            del data['status']
        if 'dateClosed' in data.keys():
            del data['dataClosed']
        self.issue = data
        with open(self.issue_path, 'w') as issue_file:
            json.dump(data, issue_file)
            print('Issue file cleared.')

    def add_dsets_to_file(self):
        with open(self.extra_dsets, 'r') as extra_file:
            extra_dsets = extra_file.readlines()
        with open(self.dsets_path, 'w+') as dset_file:
            for dset in extra_dsets:
                dset_file.write(dset)

    def remove_dsets_from_file(self):
        with open(self.dsets_path, 'r') as dsets:
            lines = dsets.readlines()
        self.dsets = get_datasets([item for item in lines[:-1]])
        with open(self.dsets_path, 'w') as dsets_file:
            for dset in self.dsets:
                print(dset)
                dsets_file.write(dset + '\n')

    def change_attribute(self, key, new_value):
        data = self.issue
        data[key] = new_value
        with open(self.issue_path, 'w') as issue:
            json.dump(data, issue)

    @staticmethod
    def save_credentials():
        set_credentials(username=username, token=token, passphrase=passphrase)

    @staticmethod
    def reset_passphrase():
        oldpass = passphrase
        newpass = new_passphrase
        reset_passphrase(old_pass=oldpass, new_pass=newpass)

    @staticmethod
    def reset_credentials():
        reset_credentials()

    @staticmethod
    def check_credentials(test):
        if test:
            passphrase_key = passphrase
        else:
            passphrase_key = new_passphrase
        encrypted_username = encrypt_with_key(username, passphrase_key)
        encrypted_token = encrypt_with_key(token, passphrase_key)
        with open('cred.txt', 'rb') as cred_file:
            content = cred_file.readlines()
        file_username = content[0].split('entry:')[1].replace('\n', '')
        file_token = content[1].split('entry:')[1]
        if file_username == encrypted_username and file_token == encrypted_token:
            return True
        else:
            return False

    @staticmethod
    def check_installation():
        try:
            sub.check_output(['esgissue', '-h'])
            return True
        except CalledProcessError:
            return False

    @staticmethod
    def compare_json(d1, d2, ignore_keys):
        d1_filtered = dict((k, v) for k, v in d1.iteritems() if k not in ignore_keys)
        d2_filtered = dict((k, v) for k, v in d2.iteritems() if k not in ignore_keys)
        return d1_filtered == d2_filtered


def create_handle_for_dataset(dataset_list):

    prefix_handle = '21.14100'
    rabbit_exchange = 'esgffed-exchange'
    rabbit_user_trusted = 'esgf-publisher'
    rabbit_url_trusted = 'handle-esgf-open.dkrz.de'
    rabbit_password_trusted = '975a21fe1e'
    rabbit_urls_open = []
    rabbit_user_open = 'esgf-publisher-open'
    is_test = False
    data_node1 = 'foo'
    thredds_service_path1 = 'bar'

    # Initialize library for that data node:
    data_node1 = 'foo'
    thredds_service_path1 = 'bar'
    trusted_node_1 = {
        'user': rabbit_user_trusted,
        'password': rabbit_password_trusted,
        'url':rabbit_url_trusted,
        'priority':1
    }
    open_node = {
        'user': rabbit_user_open,
        'url': rabbit_urls_open
    }

    list_cred = [trusted_node_1, open_node]
    connector = esgfpid.Connector(messaging_service_credentials=list_cred,
                                  handle_prefix=prefix_handle,
                                  messaging_service_exchange_name=rabbit_exchange,
                                  data_node=data_node1,
                                  thredds_service_path=thredds_service_path1,
                                  test_publication=is_test)
    connector.start_messaging_thread()
    for dset in dataset_list:
        dataset = dset.split('#')
        dataset_id = dataset[0]
        version_number = dataset[1]
        is_replica = False
        number_of_files = 1
        print('Creating handle for dataset {}'.format(dataset_id))
        wizard = connector.create_publication_assistant(
            drs_id=dataset_id,
            version_number=int(version_number),
            is_replica=is_replica
            )
        ds_handle = wizard.get_dataset_handle() # HERE YOU GET THE DATASET PID

    # Adding a number of files
        for i in xrange(number_of_files):
            # Test file info:       ### PLEASE COMPLETE!
            file_num = i+1
            file_handle = 'hdl:'+prefix_handle+'/erratatestfile_'+str(uuid.uuid1())
            file_name = 'testfile_number_'+str(file_num)+'.nc'
            file_size = 1000
            file_checksum = 'foo'
            file_publish_path = 'my/path/'+file_name
            file_checksum_type='SHA256'
            file_version = 'foo'

            # Add this test file info:
            wizard.add_file(
                file_name=file_name,
                file_handle=file_handle,
                file_size=file_size,
                checksum=file_checksum,
                publish_path=file_publish_path,
                checksum_type=file_checksum_type,
                file_version=file_version
            )

        wizard.dataset_publication_finished()
        print('\n\nChecking PID existence')
        handle = ds_handle.replace('hdl:', '')
        resp = requests.get('http://hdl.handle.net/api/handles/'+handle+'?auth=True')
        print('\n\nHandle '+handle)
        print('HTTP code: '+str(resp.status_code))
        print('Content:   '+str(resp.content))
    # Finish messaging thread
    connector.finish_messaging_thread()