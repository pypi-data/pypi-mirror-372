from odoo import _, api, models
from odoo.exceptions import ValidationError


class Contract(models.Model):
    _inherit = "contract.contract"

    @api.constrains("partner_id", "contract_line_ids")
    def _check_coop_agreement(self):
        self.ensure_one()
        if self.partner_id.coop_agreement:
            for line in self.contract_line_ids:
                line_prod_tmpl_id = line.product_id.product_tmpl_id
                agreement = self.partner_id.coop_agreement_id
                if line_prod_tmpl_id not in agreement.products:
                    raise ValidationError(
                        _("Product %s is not allowed by agreement %s")
                        % (line.product_id.name, agreement.code)
                    )
