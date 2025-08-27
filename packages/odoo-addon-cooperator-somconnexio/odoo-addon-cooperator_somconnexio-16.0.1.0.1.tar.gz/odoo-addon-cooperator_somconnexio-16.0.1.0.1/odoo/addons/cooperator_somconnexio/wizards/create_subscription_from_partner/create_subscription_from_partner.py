from odoo import models, fields


class PartnerCreateSubscription(models.TransientModel):
    _inherit = "partner.create.subscription"
    bank_id = fields.Many2one("res.partner.bank", "Bank Account", required=True)
    payment_type = fields.Selection(
        [("single", "One single payment"), ("split", "Ten payments")], required=True
    )

    def create_subscription(self):
        sub_req = self.env["subscription.request"]

        cooperator = self.cooperator
        vals = {
            "partner_id": cooperator.id,
            "vat": cooperator.vat,
            "share_product_id": self.share_product.id,
            "ordered_parts": self.share_qty,
            "user_id": self.env.uid,
            "email": self.email,
            "source": "crm",
            "firstname": cooperator.firstname,
            "lastname": cooperator.lastname,
            "address": cooperator.street,
            "zip_code": cooperator.zip,
            "city": cooperator.city,
            "country_id": cooperator.country_id.id,
            "lang": cooperator.lang,
            "is_company": self.is_company,
        }
        if self.is_company:
            vals.update(
                {
                    "company_name": cooperator.name,
                    "company_email": cooperator.email,
                    "firstname": self.representative_firstname,
                    "lastname": self.representative_lastname,
                }
            )

        coop_vals = {}
        if not self._get_email():
            coop_vals["email"] = self.email

        vals["iban"] = self.bank_id.acc_number
        vals["payment_type"] = self.payment_type

        if coop_vals:
            cooperator.write(coop_vals)

        new_sub_req = sub_req.create(vals)
        context = {
            "__last_update": {},
            "active_model": "subscription.request",
            "active_id": new_sub_req.id,
            "active_ids": [new_sub_req.id],
        }
        return {
            "type": "ir.actions.act_window",
            "view_type": "form, tree",
            "view_mode": "form",
            "res_model": "subscription.request",
            "res_id": new_sub_req.id,
            "target": "current",
            "context": context,
        }
