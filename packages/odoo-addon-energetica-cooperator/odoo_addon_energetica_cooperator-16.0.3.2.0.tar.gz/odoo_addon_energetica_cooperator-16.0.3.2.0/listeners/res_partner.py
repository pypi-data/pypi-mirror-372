import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class PartnerListener(Component):
    _name = "partner.listener"
    _inherit = "base.event.listener"
    _apply_on = ["res.partner"]

    def on_record_create(self, record, fields=None):
        _logger.debug(f"Creating user from partner...{record.id}")
        record.create_users_from_cooperator_partners()
