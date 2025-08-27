from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class ContractGroupChange(models.TransientModel):
    _name = "contract.group.change.wizard"
    _description = "Contract Group Change"

    new_group = fields.Boolean(string="Create new group")
    contract_id = fields.Many2one("contract.contract", string="Contract", required=True)
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    contract_group_id = fields.Many2one("contract.group", string="Contract Group")

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        contract = self.env["contract.contract"].browse(self.env.context["active_id"])
        defaults["contract_id"] = contract.id
        defaults["contract_group_id"] = contract.contract_group_id.id
        defaults["partner_id"] = contract.partner_id.id
        return defaults

    def button_change(self):
        original_group = self.contract_id.contract_group_id
        if self.new_group:
            contract_group = self.env["contract.group"].get_or_create_contract_group_id(
                self.contract_id, new_group=True
            )
        else:
            contract_group = self.contract_group_id
            valid, error_message = contract_group.validate_contract_to_group(
                self.contract_id
            )
            if not valid:
                raise ValidationError(error_message)

        self.contract_id.write({"contract_group_id": contract_group.id})

        message = _("Contract group changed from {old} to {new}.").format(
            old=original_group.code, new=contract_group.code
        )

        if original_group and not original_group.contract_ids:
            message += _("{} group was deleted because it was empty.").format(
                original_group.code
            )
            original_group.unlink()

        self.contract_id.message_post(message)
