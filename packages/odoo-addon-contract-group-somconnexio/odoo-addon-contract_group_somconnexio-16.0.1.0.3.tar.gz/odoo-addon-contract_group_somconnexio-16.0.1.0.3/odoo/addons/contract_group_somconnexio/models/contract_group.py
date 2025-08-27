from odoo import api, models, _

from odoo.exceptions import ValidationError


class ContractGroup(models.Model):
    _inherit = "contract.group"

    @api.model
    def create(self, vals):
        if not vals.get("code"):
            vals["code"] = self._get_code(vals["partner_id"])
        return super().create(vals)

    def _get_code(self, partner_id):
        """Search the groups of the partner sort them and get the
        last number and add one"""
        partner = self.env["res.partner"].browse(partner_id)
        groups = (
            self.env["contract.group"].sudo().search([("partner_id", "=", partner.id)])
        )
        if not groups:
            return f"{partner.ref}_0"
        group_numbers = [int(g.code.split("_")[1]) for g in groups]
        group_numbers.sort()
        return f"{partner.ref}_{group_numbers[-1]+1}"

    @api.model
    def get_or_create_contract_group_id(
        self, contract, new_group=False, mandate_id=None, email_ids=None
    ):
        """
        Retrieves or creates a contract group based on the specified
        contract and conditions.

        This method searches for an existing contract group that matches
        the given contract based on the validation method. If no matching
        group is found, it creates a new contract group.

        Parameters:
        contract (Record): A contract record, typically an instance of the
                           'contract.contract' model.
        new_group (bool, optional): If True, forces the creation of a new
                                    contract group. Defaults to False.
        mandate_id (int, optional): An optional mandate ID used for
                                    the validation. Defaults to None.
        email_ids (list, optional): An optional email IDs used for
                                    the validation. Defaults to None.

        Returns:
        Record: A record of the 'contract.group' model, either found or newly created.
        """
        partner = contract.partner_id
        if partner.special_contract_group:
            return self.env.ref("contract_group_somconnexio.to_review_contract_group")
        if new_group:
            return self.env["contract.group"].create(
                {
                    "partner_id": partner.id,
                }
            )
        group = self.get_contract_group_id(contract, mandate_id, email_ids)
        if not group:
            group = self.env["contract.group"].create(
                {
                    "partner_id": partner.id,
                }
            )
        return group

    def get_contract_group_id(self, contract, mandate_id=None, email_ids=None):
        """
        Retrieves a contract group based on the specified
        contract and conditions.

        This method searches for an existing contract group that matches
        the given contract based on the validation method.

        If the contract's partner has a special contract group, this method
        returns the reference to the Special Group (`to_review_contract_group`).
        Otherwise, it searches through the contract groups associated with the partner.
        If a valid group is found (validated through `validate_contract_to_group`
        method), it is returned.

        Parameters:
        contract (Record): A contract record, typically an instance of the
                           'contract.contract' model.
        mandate_id (int, optional): An optional mandate ID used for
                                    the validation. Defaults to None.
        email_ids (list, optional): An optional email IDs used for
                                    the validation. Defaults to None.

        Returns:
        Record: A record of the 'contract.group' model found.
        """
        partner = contract.partner_id
        if partner.special_contract_group:
            return self.env.ref("contract_group_somconnexio.to_review_contract_group")
        groups = (
            self.env["contract.group"].sudo().search([("partner_id", "=", partner.id)])
        )
        for group in groups:
            valid, __ = group.validate_contract_to_group(
                contract, mandate_id, email_ids
            )
            if valid:
                return group

    def validate_contract_to_group(self, contract, mandate_id=None, email_ids=None):
        """
        Validates if a given contract is equivalent to
        the first contract in the contract group.

        This method compares the given contract with the first contract
        in the contract group associated with the current object.
        It checks for equality based on two criteria:
        - The mandate IDs of both contracts must be the same.
        - The list of email IDs associated with both contracts must be identical.

        Parameters:
        contract (Contract): The contract to be validated.
                             This should be an instance of the Contract class.
        mandate_id (BankMandate): The mandate to check in the group.
                             This should be an instance of the BankMandate class.
                             This field is used in change contract mandate process.

        Returns:
        bool: True if the given contract is equivalent to the first contract in the
              group, or if the group does not have any related contracts;
              False otherwise.
        string: A message describing the validation result to show to the users.
        """
        if not self.contract_ids:
            return True, "Validation successful."

        try:
            active_contracts = self._get_active_contracts()
            contract_from_group = (active_contracts - contract)[0]
        except IndexError:
            return False, _(f"The group {self.code} has no active contracts.")

        if not mandate_id:
            mandate_id = contract.mandate_id
        # We use the ids to compare integers instead of records
        # because the contract records has a new id
        if contract_from_group.mandate_id.ids != mandate_id.ids:
            return False, _("The IBAN does not match.")
        if not email_ids:
            email_ids = contract.email_ids
        if contract_from_group.email_ids.ids != email_ids.ids:
            return False, _("The email does not match.")

        return True, "Validation successful."

    def _get_active_contracts(self):
        return self.contract_ids.filtered(lambda c: not c.is_terminated)

    def get_mandate_id(self):
        active_contracts = self._get_active_contracts()
        if not active_contracts:
            raise ValidationError(_(f"The group {self.code} has no active contracts."))
        return (active_contracts[0].mandate_id.id,)
