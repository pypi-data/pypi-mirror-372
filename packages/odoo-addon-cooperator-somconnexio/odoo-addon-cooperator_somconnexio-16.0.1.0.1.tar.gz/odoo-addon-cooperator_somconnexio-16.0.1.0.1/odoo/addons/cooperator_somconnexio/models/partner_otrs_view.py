from odoo import models


class PartnerOTRSView(models.Model):
    _inherit = "partner.otrs.view"

    def _sql_select(self):
        select = super(PartnerOTRSView, self)._sql_select()
        select += """
            partner.cooperator_register_number::character varying AS partner_number,
            partner.effective_date AS date_partner,
            CASE
                WHEN partner.old_member = true THEN sr.date
                ELSE NULL
            END AS date_partner_end,
            partner.birthdate_date AS birthday,
            LEFT JOIN subscription_register sr
            ON partner.id = sr.partner_id AND sr.type = 'sell_back'
        """
        return select
