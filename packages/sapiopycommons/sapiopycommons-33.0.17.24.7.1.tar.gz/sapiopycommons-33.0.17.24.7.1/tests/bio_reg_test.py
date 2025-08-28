import unittest

from sapiopylib.rest.User import SapioUser

from sapiopycommons.multimodal.multimodal import MultiModalManager
from sapiopycommons.multimodal.multimodal_data import BioFileRegistrationRequest, BioFileType
from data_type_models import DNAPartModel

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")
reg_man = MultiModalManager(user)


class BioRegTest(unittest.TestCase):
    def test_genbank_registration(self):
        with open("test.gb", "r") as file_content:
            request = BioFileRegistrationRequest(DNAPartModel.DATA_TYPE_NAME, BioFileType.GENBANK, file_content.read())
            response = reg_man.register_bio(request)
            self.assertTrue(len(response.newRecordIdList) + len(response.oldRecordIdList) == 1)

    def test_fasta_registration(self):
        with open("kappa.chains.fasta", "r") as file_content:
            request = BioFileRegistrationRequest(DNAPartModel.DATA_TYPE_NAME, BioFileType.FASTA, file_content.read())
            response = reg_man.register_bio(request)
            self.assertTrue(len(response.newRecordIdList) + len(response.oldRecordIdList) == 15)
