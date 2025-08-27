from odoo.addons.somconnexio.tests.helper_service import contract_fiber_create_data
from odoo.addons.somconnexio.tests.sc_test_case import SCComponentTestCase


class TestContract(SCComponentTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.Contract = self.env["contract.contract"]
        self.partner = self.browse_ref("somconnexio.res_partner_2_demo")

    def test_contract_create_check_group(self, *args):
        # Add email
        first_email = self.env["res.partner"].create(
            {
                "parent_id": self.partner.id,
                "type": "contract-email",
                "email": "new-email@somconnexio.coop",
            }
        )
        data = contract_fiber_create_data(self.env, self.partner)
        groups = self.env["contract.group"].search(
            [("partner_id", "=", self.partner.id)]
        )
        self.assertFalse(groups)

        data["email_ids"] = [(4, first_email.id, 0)]
        contract = self.Contract.create(data)
        groups = self.env["contract.group"].search(
            [("partner_id", "=", self.partner.id)]
        )

        self.assertEqual(len(groups), 1)
        self.assertIn(contract.contract_group_id, groups)

        data = data.copy()
        contract = self.Contract.create(data)
        groups = self.env["contract.group"].search(
            [("partner_id", "=", self.partner.id)]
        )

        self.assertEqual(len(groups), 1)
        self.assertIn(contract.contract_group_id, groups)

        new_email = self.env["res.partner"].create(
            {
                "parent_id": self.partner.id,
                "email": "email_group_2@mail.test",
                "type": "contract-email",
            }
        )
        data = data.copy()
        data["email_ids"] = [(4, new_email.id, 0)]
        contract = self.Contract.create(data)
        groups = self.env["contract.group"].search(
            [("partner_id", "=", self.partner.id)]
        )

        self.assertEqual(len(groups), 2)
        self.assertIn(contract.contract_group_id, groups)

    def test_contract_create_check_group_to_review_contract_group(self, *args):
        vals_contract = contract_fiber_create_data(self.env, self.partner)
        self.partner.special_contract_group = True

        contract = self.Contract.create(vals_contract)

        self.assertEqual(
            contract.contract_group_id,
            self.browse_ref("contract_group_somconnexio.to_review_contract_group"),
        )

    def test_contract_cron_compute_current_tariff_contract_line(self, *args):
        contracts = self.Contract.search([])
        for contract in contracts:
            contract.current_tariff_contract_line = False

        self.Contract.cron_compute_current_tariff_contract_line()
        for contract in contracts:
            self.assertTrue(contract.current_tariff_contract_line.id)

    def test_get_contract_group_id_empty(self, *args):
        """
        Test that a partner has a contract_group with no contracts associated,
        the _get_contract_group_id method from contract does not
        return the empty contract group but a new one.
        """
        partner = self.browse_ref("somconnexio.res_partner_company_demo")
        data = contract_fiber_create_data(self.env, partner)
        contract = self.Contract.create(data)
        groups = self.env["contract.group"].search([("partner_id", "=", partner.id)])
        self.assertEqual(len(groups), 1)
        self.assertEqual(contract.contract_group_id, groups)
        self.assertEqual(groups.contract_ids, contract)

        # Remove contract from contract_group, leave it empty
        contract.contract_group_id = False
        self.assertFalse(groups.contract_ids)

        contract_group_id = self.Contract._get_contract_group_id(contract)

        self.assertNotEqual(contract_group_id, groups.id)
