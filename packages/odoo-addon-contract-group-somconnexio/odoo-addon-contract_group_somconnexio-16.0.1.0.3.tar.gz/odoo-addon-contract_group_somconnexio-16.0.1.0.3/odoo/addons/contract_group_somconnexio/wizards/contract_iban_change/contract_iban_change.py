from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ContractIbanChangeWizard(models.TransientModel):
    _inherit = "contract.iban.change.wizard"
    available_contract_group_ids = fields.One2many(
        "contract.group",
        string="Available Contract Groups",
        compute="_compute_available_contract_group_ids",
    )
    contract_group_id = fields.Many2one(
        "contract.group",
        string="Contract Group",
        help="The contract groups that are available for the selected contracts. "
        "Keep empty to create a new contract group.",
    )

    @api.onchange("account_banking_mandate_id", "contract_ids")
    def _compute_available_contract_group_ids(self):
        if not self.contract_ids or not self.account_banking_mandate_id:
            self.available_contract_group_ids = []
            return

        self.available_contract_group_ids = (
            self.env["contract.group"]
            .search([("partner_id", "=", self.contract_ids[0].partner_id.id)])
            .filtered(
                lambda x: x.validate_contract_to_group(
                    self.contract_ids[0], mandate_id=self.account_banking_mandate_id
                )[0]
            )
        )
        self.contract_group_id = (
            self.available_contract_group_ids[0]
            if self.available_contract_group_ids
            else False
        )

    def _data_to_update_contracts(self):
        data = super()._data_to_update_contracts()
        if not self.contract_group_id:
            self.contract_group_id = self.env[
                "contract.group"
            ].get_or_create_contract_group_id(
                self.contract_ids[0],
                new_group=True,
            )

        for contract in self.contract_ids:
            valid, error_message = self.contract_group_id.validate_contract_to_group(
                contract,
                self.account_banking_mandate_id,
            )
            if not valid:
                raise ValidationError(error_message)
        data.update({"contract_group_id": self.contract_group_id.id})
        return data
