# encoding: UTF-8
import unittest
from actionswords import Actionwords

test_issue_file = 'samples/issue1.json'
test_dset_file = 'samples/dsets1.txt'
extra_dset_file = 'samples/extra_dsets.txt'


class TestESDocERRATA(unittest.TestCase):
    def setUp(self):
        self.actionwords = Actionwords(test_issue_file=test_issue_file, test_dset_file=test_dset_file)

    def test_Saving_credentials(self):
        self.actionwords.save_credentials()
        self.assertTrue(self.actionwords.check_credentials(True))
        self.actionwords.reset_credentials()

    def test_Changing_passphrase(self):

        self.actionwords.save_credentials()
        self.actionwords.reset_passphrase()
        self.assertTrue(self.actionwords.check_credentials(False))
        self.actionwords.reset_credentials()

    def creating_an_issue_for_a_number_of_datasets(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        check_issue_files_and_pid(self)

    def updating_issue_add_some_datasets(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.extra_dsets = extra_dset_file
        self.actionwords.add_dsets_to_file()
        self.actionwords.update_issue()
        check_issue_files_and_pid(self)

    def test_Updating_issue_Removing_some_datasets(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.remove_dsets_from_file()
        print(self.actionwords.issue['uid'])
        self.actionwords.update_issue()
        check_issue_files_and_pid(self)

    def test_Updating_issue_Changing_status(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.change_status()
        self.actionwords.update_issue()
        check_issue_files(self)

    def test_Updating_issue_Changing_severity(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.change_severity()
        self.actionwords.update_issue()
        check_issue_files(self)

    def test_Updating_issue_Altering_description(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.change_description()
        self.actionwords.update_issue()
        check_issue_files(self)

    def test_Closing_issue(self):
        self.actionwords.clear_issue()
        self.actionwords.create_issue()
        self.actionwords.check_issue_files()
        check_issue_files(self)

    def test_Installing_esgissue_client(self):
        self.assertTrue(self.actionwords.check_installation())

    def test_Retrieving_an_issue_with_a_specific_id(self):
        pass

    def test_Retrieving_multiple_issues(self):
        pass

    def test_Retrieve_all_issues(self):
        pass


def check_issue_files_and_pid(test_case):

    test_case.assertTrue(test_case.actionwords.check_issue_files())
    test_case.assertTrue(test_case.actionwords.check_issue_pid())


def check_issue_files(test_case):
    test_case.assertTrue(test_case.actionwords.check_issue_files())

if __name__ == '__main__':
    unittest.main()

