from datetime import date
from odoo import api, fields, models


class PartnerEmailChangeWizard(models.TransientModel):
    _inherit = "partner.email.change.wizard"

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

    @api.onchange("email_ids", "contract_ids")
    def _compute_available_contract_group_ids(self):
        if not self.contract_ids or not self.email_ids:
            self.available_contract_group_ids = False
            return

        self.available_contract_group_ids = (
            self.env["contract.group"]
            .search([("partner_id", "=", self.contract_ids[0].partner_id.id)])
            .filtered(
                lambda x: x.validate_contract_to_group(
                    self.contract_ids[0], email_ids=self.email_ids
                )[0]
            )
        )
        self.contract_group_id = (
            self.available_contract_group_ids[0]
            if self.available_contract_group_ids
            else False
        )

    def _change_contract_emails(self, change_partner_emails):
        emails = self.email_ids or self.email_id
        activity_args = {
            "res_model_id": self.env.ref("contract.model_contract_contract").id,
            "user_id": self.env.user.id,
            "activity_type_id": self.env.ref(
                "somconnexio.mail_activity_type_contract_data_change"
            ).id,
            "date_done": date.today(),
            "date_deadline": date.today(),
            "summary": self.summary,
            "done": self.done,
        }
        change_partner_emails.change_contracts_emails(
            self.partner_id,
            self.contract_ids,
            emails,
            activity_args,
            contract_group_id=self.contract_group_id,
            create_contract_group=not bool(self.contract_group_id),
        )
        return True
