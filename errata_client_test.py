# encoding: UTF-8
import unittest
from actionswords import Actionwords

test_issue_file = 'esgissue/samples/issue1.json'
test_dset_file = 'esgissue/samples/dsets1.txt'
extra_dset_file = 'esgissue/samples/extra_dsets.txt'


class TestESDocERRATA(unittest.TestCase):
    def setUp(self):
        self.actionwords = Actionwords(self, test_issue_file, test_dset_file, extra_dset_file)

    def creating_an_issue_for_a_number_of_datasets(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()

    def updating_issue_add_some_datasets(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.add_dsets_to_file()
        self.actionwords.update_issue()

    def test_Updating_issue_Removing_some_datasets(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.remove_dsets_from_file()
        self.actionwords.update_issue()

    def test_Updating_issue_Changing_status(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.change_status()
        self.actionwords.update_issue()

    def test_Updating_issue_Changing_severity(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.change_severity()
        self.actionwords.update_issue()

    def test_Updating_issue_Altering_description(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.change_description()
        self.actionwords.update_issue()

    def test_Closing_issue(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.check_issue()

    def test_Saving_credentials(self):
        pass

    def test_Resetting_credentials(self):
        pass

    def test_Changing_passphrase(self):
        pass

    def test_Installing_esgissueclient(self):
        pass

    def test_Retrieving_an_issue_with_a_specific_id(self):
        pass

    def test_Retrieving_multiple_issues(self):
        pass

    def test_Retrieve_all_issues(self):
        pass
