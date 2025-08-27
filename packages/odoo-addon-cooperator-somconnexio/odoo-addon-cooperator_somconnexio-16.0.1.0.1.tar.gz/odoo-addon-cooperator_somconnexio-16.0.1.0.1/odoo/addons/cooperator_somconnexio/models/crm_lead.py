from odoo import _, models, fields
from odoo.exceptions import ValidationError


class CRMLead(models.Model):
    _inherit = "crm.lead"

    subscription_request_id = fields.Many2one(
        "subscription.request", "Subscription Request"
    )

    def _get_email(self, vals):
        if vals.get("subscription_request_id"):
            return (
                self.env["subscription.request"]
                .browse(vals.get("subscription_request_id"))
                .email
            )
        return super()._get_email(vals)

    def validate_remesa(self):
        self.ensure_one()

        # Check if related SR is validated
        if not self.partner_id:
            raise ValidationError(
                _(
                    "Error in {}: The subscription request related must be validated."
                ).format(self.id)
            )
        super().validate_remesa()

    def _get_crm_lead_creation_email_template(self):
        return self.env.ref(
            "cooperator_somconnexio.crm_lead_creation_manual_email_template"
        )
