from odoo import models


class CreateLeadFromPartnerWizard(models.TransientModel):
    _inherit = "partner.create.lead.wizard"

    def _get_available_categories(self):
        if self.partner_id.coop_sponsee:
            sc = self.env["coop.agreement"].search([("code", "=", "SC")])
            sc_product_templs = sc.products
            available_categories = [p.categ_id for p in sc_product_templs]
        elif self.partner_id.coop_agreement:
            product_templs = self.partner_id.coop_agreement_id.products
            available_categories = [p.categ_id for p in product_templs]
        else:
            available_categories = super()._get_available_categories()
        return available_categories
