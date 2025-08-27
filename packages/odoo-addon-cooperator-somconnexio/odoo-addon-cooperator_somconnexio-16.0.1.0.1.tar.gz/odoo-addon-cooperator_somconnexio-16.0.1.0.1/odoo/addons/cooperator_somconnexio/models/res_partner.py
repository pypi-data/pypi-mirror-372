from odoo import _, models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    coop_agreement_id = fields.Many2one("coop.agreement", string="Coop Agreement")
    coop_agreement = fields.Boolean(
        string="Has cooperator agreement?",
        compute="_compute_coop_agreement",
        store=True,
        readonly=True,
    )
    cooperator_end_date = fields.Date(
        string="Cooperator End Date",
        compute="_compute_cooperator_end_date",
        readonly=True,
    )
    effective_date = fields.Date(related="cooperative_membership_id.effective_date")

    discovery_channel_id = fields.Many2one(
        "discovery.channel",
        "Discovery Channel",
        compute="_compute_discovery_channel",
        store=True,
    )

    @api.depends("sponsor_id", "coop_agreement_id")
    def _compute_coop_agreement(self):
        for partner in self:
            if partner.coop_agreement_id:
                partner.coop_agreement = True
            else:
                partner.coop_agreement = False

    @api.depends("old_member", "member", "coop_candidate")
    def _compute_cooperator_end_date(self):
        for partner in self:
            if not partner.old_member or partner.coop_candidate or partner.member:
                end_date = False
            else:
                subsc_register_end_date = self.env["subscription.register"].search(
                    [
                        ("partner_id", "=", partner.id),
                        ("type", "=", "sell_back"),
                    ],
                    limit=1,
                    order="date DESC",
                )
                end_date = subsc_register_end_date.date or False
            partner.cooperator_end_date = end_date

    @api.depends("subscription_request_ids.state")
    def _compute_discovery_channel(self):
        for partner in self:
            sr = self.env["subscription.request"].search(
                [("partner_id", "=", partner.id), ("state", "in", ("done", "paid"))],
                limit=1,
                order="id DESC",
            )
            if sr:
                partner.discovery_channel_id = sr.discovery_channel_id

    def _domain_sponsor_id(self):
        return [
            "|",
            ("member", "=", True),
            ("coop_candidate", "=", True),
        ]

    def write(self, vals):
        for partner in self:
            if "sponsor_id" in vals and vals["sponsor_id"] != partner["sponsor_id"].id:
                msg = _("sponsor has been changed from {} to {}").format(
                    partner["sponsor_id"].name,
                    self.env["res.partner"].browse(vals["sponsor_id"]).name,
                )
                partner.message_post(msg)

                msg = _("Is Cooperator Sponsee? has been changed from {} to {}").format(
                    partner["coop_sponsee"], bool(vals["sponsor_id"])
                )
                partner.message_post(msg)

            if (
                "coop_agreement_id" in vals
                and vals["coop_agreement_id"] != partner["coop_agreement_id"].id
            ):
                msg = _("coop_agreement has been changed from {} to {}").format(
                    partner["coop_agreement_id"].code,
                    self.env["coop.agreement"].browse(vals["coop_agreement_id"]).code,
                )
                partner.message_post(msg)

                msg = _("has_coop_agreement has been changed from {} to {}").format(
                    partner["coop_agreement"], bool(vals["coop_agreement_id"])
                )
                partner.message_post(msg)

        super().write(vals)
        return True
