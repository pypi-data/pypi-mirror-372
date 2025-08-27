from odoo.addons.component.core import Component
from datetime import date


class ResPartner(Component):
    _name = "partner.listener"
    _inherit = "base.event.listener"
    _apply_on = ["res.partner"]

    def on_record_write(self, record, fields=None):
        if "member" in fields and record.member is False:
            for sponsee in record.sponsee_ids:

                has_active_contracts = any(
                    not (contract.date_end and contract.date_end < date.today())
                    for contract in sponsee.contract_ids
                )
                if has_active_contracts:
                    template = self.env.ref(
                        "cooperator_somconnexio.sponsor_sell_back_template"
                    )
                    template.send_mail(sponsee.id)
