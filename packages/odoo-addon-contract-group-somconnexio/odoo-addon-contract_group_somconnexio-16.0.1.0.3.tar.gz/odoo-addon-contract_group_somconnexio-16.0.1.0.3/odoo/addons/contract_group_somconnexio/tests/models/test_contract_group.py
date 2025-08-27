from datetime import datetime

from odoo.addons.somconnexio.tests.sc_test_case import SCComponentTestCase


class TestContractGroup(SCComponentTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.ContractGroup = self.env["contract.group"]
        self.partner = self.browse_ref("somconnexio.res_partner_1_demo")

        partner_bank = self.env["res.partner.bank"].create(
            {
                "acc_number": "ES90 0024 6912 5012 3456 7891",
                "sanitized_acc_number": "ES9000246912501234567891",
                "acc_holder_name": "Felip",
                "partner_id": self.partner.id,
                "bank_id": 1,
            }
        )
        self.new_mandate = self.env["account.banking.mandate"].create(
            {
                "partner_bank_id": partner_bank.id,
                "state": "valid",
                "partner_id": self.partner.id,
                "signature_date": datetime.now(),
            }
        )
        self.contract = self.browse_ref("somconnexio.contract_fibra_600_pack")
        self.contract_group_1 = self.browse_ref(
            "contract_group_somconnexio.contract_group_1"
        )

    def test_first_code_generation(self, *args):
        partner = self.browse_ref("somconnexio.res_partner_2_demo")
        group = self.ContractGroup.create({"partner_id": partner.id})
        self.assertEqual(group.code, "4321_0")

    def test_code_generation(self, *args):
        group = self.ContractGroup.create({"partner_id": self.partner.id})
        self.assertEqual(group.code, "1234_3")

    def test_validate_contract_to_group_ok(self, *args):
        valid, _ = self.contract_group_1.validate_contract_to_group(self.contract)

        self.assertTrue(valid)

    def test_validate_contract_to_group_error(self, *args):
        self.contract.mandate_id = self.new_mandate

        valid, error_msg = self.contract_group_1.validate_contract_to_group(
            self.contract
        )

        self.assertFalse(valid)
        self.assertEqual("The IBAN does not match.", error_msg)

    def test_validate_contract_to_group_new_mandate(self, *args):
        valid, error_msg = self.contract_group_1.validate_contract_to_group(
            self.contract, self.new_mandate
        )

        self.assertFalse(valid)
        self.assertEqual("The IBAN does not match.", error_msg)

    def test_get_contract_group_id(self, *args):
        contract_group = self.ContractGroup.get_contract_group_id(self.contract)

        self.assertEqual(contract_group, self.contract_group_1)

    def test_get_contract_group_id_special_group(self, *args):
        self.contract.partner_id.special_contract_group = True

        expected_group = self.browse_ref(
            "contract_group_somconnexio.to_review_contract_group"
        )

        contract_group = self.ContractGroup.get_contract_group_id(self.contract)

        self.assertEqual(contract_group, expected_group)

    def test_get_contract_group_id_force_create(self, *args):
        contract_group = self.ContractGroup.get_or_create_contract_group_id(
            self.contract, new_group=True
        )

        self.assertEqual(contract_group.code, "1234_3")
