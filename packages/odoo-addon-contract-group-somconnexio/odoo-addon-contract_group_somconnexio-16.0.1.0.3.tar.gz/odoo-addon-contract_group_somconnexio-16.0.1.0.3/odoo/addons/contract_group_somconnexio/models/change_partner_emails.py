from odoo import _, models
from odoo.exceptions import ValidationError


class ChangePartnerEmails(models.AbstractModel):
    _inherit = "change.partner.emails"

    def change_contracts_emails(
        self,
        partner,
        contracts,
        emails,
        activity_args,
        contract_group_id=None,
        create_contract_group=False,
    ):
        for contract in contracts:
            # Validation
            if not contract_group_id:
                contract_group_id = self.env[
                    "contract.group"
                ].get_or_create_contract_group_id(
                    contract,
                    email_ids=emails,
                    new_group=create_contract_group,
                )
            (
                validation_result,
                validation_message,
            ) = contract_group_id.validate_contract_to_group(contract, email_ids=emails)
            if not validation_result and not create_contract_group:
                raise ValidationError(validation_message)
            # Post messages
            message_partner = _("Email changed ({} --> {}) in partner's contract '{}'")
            partner.message_post(
                message_partner.format(
                    ", ".join([email.email for email in contract.email_ids]),
                    ", ".join([email.email for email in emails]),
                    contract.name,
                )
            )
            message_contract = _("Contract email changed ({} --> {})")
            contract.message_post(
                message_contract.format(
                    ", ".join([email.email for email in contract.email_ids]),
                    ", ".join([email.email for email in emails]),
                )
            )
            # Update contracts
            contract.write(
                {
                    "email_ids": [(6, 0, [email.id for email in emails])],
                    "contract_group_id": contract_group_id.id,
                }
            )
            # Create activity
            self._create_activity(
                contract.id,
                activity_args,
            )

        return True
