from odoo import models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def set_cooperator_effective(self, effective_date):
        if self.partner_id.share_ids.filtered(lambda rec: rec.share_number > 0):
            return True
        super(AccountInvoice, self).set_cooperator_effective(effective_date)
