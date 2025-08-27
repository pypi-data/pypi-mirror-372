from odoo import api, models


class Contract(models.Model):
    _inherit = "contract.contract"

    @api.model
    def create(self, values):
        res = super(Contract, self).create(values)
        res.contract_group_id = self._get_contract_group_id(res)
        return res

    def _get_contract_group_id(self, contract):
        """
        Return the first group that match with mandate and email
        If any group match with mandate and email, create a new one.
        """
        if contract.contract_group_id:
            return contract.contract_group_id

        partner = contract.partner_id
        if partner.special_contract_group:
            return self.env.ref(
                "contract_group_somconnexio.to_review_contract_group"
            ).id
        groups = (
            self.env["contract.group"].sudo().search([("partner_id", "=", partner.id)])
        )
        for group in groups:
            if not group.contract_ids:
                continue
            contract_group = group.contract_ids[0]
            if (
                contract_group.mandate_id == contract.mandate_id
                and contract_group.email_ids.mapped("id")
                == contract.email_ids.mapped("id")
            ):
                return group.id
        return (
            self.env["contract.group"]
            .create(
                {
                    "partner_id": partner.id,
                    "code": "",  # TODO: Calculate a code with a sequence?
                }
            )
            .id
        )
