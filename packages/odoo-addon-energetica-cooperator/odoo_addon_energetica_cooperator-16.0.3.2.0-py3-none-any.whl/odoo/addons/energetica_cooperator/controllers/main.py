from odoo import http
from odoo.addons.cooperator_website.controllers import main as emyc_wsc
from odoo.http import request
from odoo.tools.translate import _


class WebsiteSubscription(emyc_wsc.WebsiteSubscription):
    def fill_values(self, values, is_company, logged, load_from_user=False):
        values = super().fill_values(values, is_company, logged, load_from_user=False)
        company = request.env["res.company"]._company_default_get()
        values.update(
            {
                "country_id": 68,
                "states": self.get_states(),
                "display_sepa": company.display_sepa_approval,
                "sepa_required": company.sepa_approval_required,
                "sepa_text": company.sepa_approval_text,
            }
        )
        return values

    def validation(self, kwargs, logged, values, post_file):
        sub_req_obj = request.env["subscription.request"]
        required_fields = sub_req_obj.sudo().get_required_field()
        is_company = kwargs.get("is_company") == "on"

        if "vat" in required_fields:
            vat = (kwargs.get("vat") or "").strip()
            if vat and not sub_req_obj.validate_nif(vat):
                values = self.fill_values(values, is_company, logged)
                values.update(kwargs)
                values["error_msg"] = _("Provided NIF is not valid.")

                redirect = "cooperator_website.becomecooperator"
                if is_company:
                    redirect = "cooperator_website.becomecompanycooperator"

                return request.render(redirect, values)

        return super().validation(kwargs, logged, values, post_file)

    def get_states(self):
        # Show only spanish provinces
        states = (
            request.env["res.country.state"].sudo().search([("country_id", "=", 68)])
        )
        return states
