from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    special_contract_group = fields.Boolean("Special Contract Group")
