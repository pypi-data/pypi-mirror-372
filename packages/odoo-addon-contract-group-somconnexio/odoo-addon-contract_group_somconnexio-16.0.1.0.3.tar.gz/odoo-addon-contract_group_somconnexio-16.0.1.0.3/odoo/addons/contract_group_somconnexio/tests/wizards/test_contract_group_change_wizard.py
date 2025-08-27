from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class TestContractGroupChange(SCTestCase):
    def setUp(self):
        super().setUp()
        self.partner = self.browse_ref("base.partner_demo")
        self.contract_group = self.env["contract.group"].create({"code": "TEST"})
        partner_id = self.partner.id
        service_partner = self.env["res.partner"].create(
            {"parent_id": partner_id, "name": "Partner service OK", "type": "service"}
        )
        self.vodafone_fiber_contract_service_info = self.env[
            "vodafone.fiber.service.contract.info"
        ].create(
            {
                "phone_number": "654321123",
                "vodafone_id": "123",
                "vodafone_offer_code": "456",
            }
        )
        vals_contract = {
            "name": "Test Contract Broadband",
            "partner_id": partner_id,
            "service_partner_id": service_partner.id,
            "invoice_partner_id": partner_id,
            "service_technology_id": self.ref("somconnexio.service_technology_fiber"),
            "service_supplier_id": self.ref("somconnexio.service_supplier_vodafone"),
            "vodafone_fiber_service_contract_info_id": (
                self.vodafone_fiber_contract_service_info.id
            ),
            "contract_group_id": self.contract_group.id,
        }

        self.company_id = self.env["res.company"].search([], limit=1).id
        self.contract = self.env["contract.contract"].create(vals_contract)
        self.wizard = (
            self.env["contract.group.change.wizard"]
            .with_context(active_id=self.contract.id)
            .create(
                {
                    "contract_group_id": self.contract_group.id,
                }
            )
        )

    def test_default_get(self):
        defaults = self.wizard.default_get(["contract_id", "contract_group_id"])
        self.assertEqual(defaults["contract_id"], self.contract.id)
        self.assertEqual(defaults["contract_group_id"], self.contract_group.id)

    def test_button_change(self):
        contract_group2 = self.env["contract.group"].create({"code": "TEST2"})
        wizard = (
            self.env["contract.group.change.wizard"]
            .with_context(active_id=self.contract.id)
            .create(
                {
                    "contract_group_id": contract_group2.id,
                }
            )
        )
        wizard.button_change()
        self.contract.invalidate_model()
        actual_message = self.contract.message_ids[0].body
        expected_message = "<p>Contract group changed from TEST to TEST2.TEST group was deleted because it was empty.</p>"  # noqa
        self.assertEqual(self.contract.contract_group_id, contract_group2)
        self.assertFalse(self.contract_group.exists())
        self.assertEqual(expected_message.strip(), actual_message.strip())
