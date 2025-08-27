import re

from odoo import fields, models


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    creation_date = fields.Datetime()
    modification_date = fields.Datetime()
    representative_vat = fields.Char()
    notes = fields.Text()
    state_id = fields.Many2one("res.country.state", string="Province")
    vat = fields.Char()
    import_state = fields.Char()

    def get_partner_vals(self):
        vals = super().get_partner_vals()
        vals["vat"] = self.vat
        return vals

    def get_partner_company_vals(self):
        vals = super().get_partner_company_vals()
        vals["vat"] = self.vat
        vals["company_register_number"] = self.company_register_number
        vals["representative_vat"] = self.representative_vat
        return vals

    def get_required_field(self):
        req_fields = super().get_required_field()[:]
        req_fields.append("vat")

        return req_fields

    def _get_partner_domain(self):
        if self.vat:
            return [("vat", "=", self.vat)]
        else:
            return None

    def validate_nif(self, nif):
        nif_regex = re.compile(r'^[XYZ]?\d{5,8}[A-Z]$')
        nif = nif.upper()

        if not nif_regex.match(nif):
            return False

        number = nif[:-1].replace('X', '0').replace('Y', '1').replace('Z', '2')
        expected_letter = "TRWAGMYFPDXBNJZSQVHLCKET"[int(number) % 23]
        actual_letter = nif[-1]

        return expected_letter == actual_letter

    def _find_or_create_representative(self):
        pass