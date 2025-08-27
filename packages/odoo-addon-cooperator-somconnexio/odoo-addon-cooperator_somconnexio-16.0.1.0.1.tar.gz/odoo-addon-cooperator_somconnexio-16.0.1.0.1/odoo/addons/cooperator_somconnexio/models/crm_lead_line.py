from odoo import models, fields


class CRMLeadLine(models.Model):
    _inherit = "crm.lead.line"

    subscription_request_id = fields.Many2one(
        "subscription.request", related="lead_id.subscription_request_id"
    )
