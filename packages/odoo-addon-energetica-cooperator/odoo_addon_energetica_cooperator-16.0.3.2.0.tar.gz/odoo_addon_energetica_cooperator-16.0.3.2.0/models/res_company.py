# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    display_sepa_approval = fields.Boolean(
        help="Choose to display a SEPA mandate checkbox on the cooperator website form."
    )
    sepa_approval_required = fields.Boolean(
        string="Is SEPA approval required?"
    )
    sepa_approval_text = fields.Html(
        translate=True,
        help="Text to display aside the checkbox to approve SEPA mandate."
    )
