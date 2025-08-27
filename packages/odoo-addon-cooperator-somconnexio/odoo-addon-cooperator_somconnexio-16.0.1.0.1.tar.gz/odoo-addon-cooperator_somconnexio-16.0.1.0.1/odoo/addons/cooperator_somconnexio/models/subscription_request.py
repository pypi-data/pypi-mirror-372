from odoo import _, models, fields, api
from odoo.exceptions import ValidationError, UserError

from odoo.addons.somconnexio.helpers.bank_utils import BankUtils
from odoo.addons.somconnexio.helpers.vat_normalizer import VATNormalizer

import logging

_logger = logging.getLogger(__name__)
try:
    from stdnum.es.nie import is_valid as valid_nie
except (ImportError, IOError) as err:
    _logger.debug(err)


class SubscriptionRequest(models.Model):
    _inherit = ["subscription.request", "mail.thread"]
    _name = "subscription.request"

    iban = fields.Char(required=True)

    type = fields.Selection(
        selection_add=[
            ("sponsorship_coop_agreement", "Sponsorship Coop Agreement"),
        ],
    )

    coop_agreement_id = fields.Many2one("coop.agreement", string="Coop Agreement")
    nationality = fields.Many2one("res.country", "Nationality")

    payment_type = fields.Selection(
        [("single", "One single payment"), ("split", "Ten payments")]
    )

    state_id = fields.Many2one("res.country.state", "Province")
    discovery_channel_id = fields.Many2one("discovery.channel", "Discovery Channel")

    source = fields.Selection(
        selection_add=[("website_change_owner", "Website Change Owner")]
    )

    verbose_name = fields.Char(compute="_compute_verbose_name", store=True)
    _rec_name = "verbose_name"

    firstname = fields.Char(
        string="First name",
        readonly=True,
        required=False,
        states={"draft": [("readonly", False)]},
    )
    lastname = fields.Char(
        string="Last name",
        readonly=True,
        required=False,
        states={"draft": [("readonly", False)]},
    )
    name = fields.Char(
        compute="_compute_name",
        store=True,
    )

    def reopen_subscription_request(self):
        self.ensure_one()
        self.write({"state": "draft"})

    def _domain_sponsor_id(self):
        return [
            "|",
            ("member", "=", True),
            ("coop_candidate", "=", True),
        ]

    @api.depends("firstname", "lastname", "type", "company_name")
    def _compute_verbose_name(self):
        for sr in self:
            if sr.is_company:
                sr.verbose_name = f"{sr.company_name} - {sr.type}"
            else:
                sr.verbose_name = "{} {} - {}".format(
                    sr.firstname, sr.lastname, sr.type
                )

    def get_partner_company_vals(self):
        values = super().get_partner_company_vals()
        values["coop_agreement_id"] = (
            self.coop_agreement_id and self.coop_agreement_id.id
        )
        values["vat"] = VATNormalizer(self.vat).convert_spanish_vat()
        values["state_id"] = self.state_id.id
        values["phone"] = self.phone
        values["is_customer"] = True
        return values

    def get_partner_vals(self):
        values = super().get_partner_vals()
        values["coop_agreement_id"] = (
            self.coop_agreement_id and self.coop_agreement_id.id
        )
        values["vat"] = VATNormalizer(self.vat).convert_spanish_vat()
        values["nationality"] = self.nationality.id
        values["state_id"] = self.state_id.id
        values["is_customer"] = True
        return values

    def vinculate_partner_in_lead(self):
        leads = self.env["crm.lead"].search([("subscription_request_id", "=", self.id)])
        for lead in leads:
            lead.partner_id = self.partner_id

    @api.constrains("coop_agreement_id", "type")
    def _check_coop_agreement_id(self):
        if self.type == "sponsorship_coop_agreement" and not self.coop_agreement_id:
            raise ValidationError(
                _(
                    "If it's a Coop Agreement sponsorship the "
                    + "Coop Agreement must be set."
                )
            )

    @api.constrains("vat", "nationality")
    def _check_nie_nationality(self):
        if valid_nie(self.vat) and not self.nationality:
            raise ValidationError(_("If a NIE is provided, nationality is mandatory."))

    def get_invoice_vals(self, partner):
        invoice_vals = super().get_invoice_vals(partner)
        if self.payment_type == "split":
            invoice_vals["invoice_payment_term_id"] = self.env.ref(
                "cooperator_somconnexio.account_payment_term_10months"
            ).id
        invoice_vals["payment_mode_id"] = self.env.ref(
            "somconnexio.payment_mode_inbound_sepa"
        ).id
        return invoice_vals

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if name:
            records = self.env["subscription.request"].search(
                [
                    "|",
                    "|",
                    "|",
                    "|",
                    ("vat", operator, name),
                    ("email", operator, name),
                    ("firstname", operator, name),
                    ("lastname", operator, name),
                    ("name", operator, name),
                ],
                limit=limit,
            )
            return models.lazy_name_get(records)
        return []

    @api.model
    def create(self, vals):
        if vals.get("is_company") and not vals.get("company_email"):
            vals["company_email"] = ""

        if not vals.get("iban"):
            vals["iban"] = ""

        subscr_request = super(models.Model, self).create(vals)

        # Cooperator's `create` function wrongly changes the ordered parts value to one
        # in sponsored subscription requests and deletes the default share_product_id
        # for new members
        if subscr_request.type in ["sponsorship", "sponsorship_coop_agreement"]:
            subscr_request.ordered_parts = 0
            subscr_request.share_product_id = False
        else:
            subscr_request.share_product_id = self.env.ref(
                "cooperator_somconnexio.cooperator_share_product"
            ).product_variant_id

        return subscr_request

    def validate_subscription_request(self):
        self.ensure_one()

        if self._has_partner_active_shares():
            raise ValidationError(_("The partner has already active shares."))

        if self.ordered_parts == 0 and self.type in self.sponsorship_types():
            return self._validate_sponsorship_subscription_request()
        elif self.ordered_parts > 0:
            return self._validate_member_subscription_request()
        elif self.ordered_parts <= 0:
            raise UserError(_("Number of share must be greater than 0."))

    def _validate_member_subscription_request(self):
        self.ensure_one()
        # todo rename to validate (careful with iwp dependencies)
        BankUtils.validate_iban(self.iban, self.env)

        partner = self.get_create_partner()
        self.write({"state": "done"})
        self.vinculate_partner_in_lead()

        # Create invoice for shares
        invoice = self.create_invoice(partner)
        self.set_membership()

        return invoice

    def _validate_sponsorship_subscription_request(self):
        self.ensure_one()
        # todo rename to validate (careful with iwp dependencies)
        if not self.partner_id:
            partner = self.create_coop_partner()
            self.partner_id = partner
        else:
            self.partner_id = self.partner_id[0]

        self.partner_id.cooperator = True

        self._create_company_contact()

        self.write({"state": "done"})
        self.vinculate_partner_in_lead()

    def get_create_partner(self):
        if self.partner_id:
            partner = self.partner_id
            self.update_partner_info()
        else:
            partner = None
            if self.already_cooperator:
                raise UserError(
                    _(
                        "The checkbox already cooperator is"
                        " checked please select a cooperator."
                    )
                )
            elif self.vat:
                domain = [("vat", "ilike", self.vat)]
                partner = self.env["res.partner"].search(domain)

            if not partner:
                partner = self.create_coop_partner()
                self.partner_id = partner
            else:
                raise UserError(
                    _("A partner with VAT %s already exists in our system") % self.vat
                )

        partner.write({"cooperator": True})
        return partner

    def sponsorship_types(self):
        return ["sponsorship_coop_agreement", "sponsorship"]

    def set_membership(self):
        # Remove the sponsor_id relation
        self._remove_sponsor_relation()
        self._remove_coop_agreement_relation()

    def _remove_sponsor_relation(self):
        if self.partner_id.sponsor_id:
            sponsor = self.sponsor_id
            self.partner_id.write({"sponsor_id": False})
            self.partner_id.message_post(
                _(
                    "Partner sponsored by {name} with VAT {vat} converted to cooperator."  # noqa
                ).format(
                    name=sponsor.name,
                    vat=sponsor.vat,
                )
            )

    def _remove_coop_agreement_relation(self):
        if self.partner_id.coop_agreement_id:
            agreement_code = self.partner_id.coop_agreement_id.code
            self.partner_id.write({"coop_agreement_id": False})
            self.partner_id.message_post(
                _(
                    "Partner with coop agreement {code} converted to cooperator."
                ).format(  # noqa
                    code=agreement_code
                )
            )

    def get_person_info(self, partner):
        super().get_person_info(partner)
        self.state_id = partner.state_id.id

    def _has_partner_active_shares(self):
        if not self.partner_id:
            return False

        shares = self.partner_id.share_ids.filtered(lambda s: s.share_number > 0)
        if shares:
            return True

    @api.onchange("type")
    def onchange_type(self):
        if self.type == "new":
            self.ordered_parts = 1
            self.share_product_id = self.env.ref(
                "cooperator_somconnexio.cooperator_share_product"
            ).product_variant_id
            self.subscription_amount = 100
        if self.type in ["sponsorship", "sponsorship_coop_agreement"]:
            self.ordered_parts = 0
            self.share_product_id = False
            self.subscription_amount = 0

    @api.constrains("sponsor_id")
    def _validate_sponsee_number(self):
        for sr in self:
            if sr.sponsor_id:
                sponsor = sr.sponsor_id
                if (
                    sponsor.active_sponsees_number
                    > sponsor.company_id.max_sponsees_number
                ):  # noqa
                    raise ValidationError(_("Maximum number of sponsees exceeded"))

    def update_partner_info(self):
        self.ensure_one()
        if self.type == "sponsorship_coop_agreement":
            self.partner_id.coop_agreement_id = (
                self.coop_agreement_id and self.coop_agreement_id.id
            )

    def cancel_subscription_request(self):
        self.ensure_one()
        if self.capital_release_request.filtered(lambda r: r.state != "cancel"):
            raise ValidationError(_("Not all invoices are cancelled"))
        # super().cancel_subscription_request()
        # Bug on super method https://github.com/OCA/cooperative/issues/150
        # restore super call and delete the line below when bug is fixed
        if self.state not in ("draft", "waiting", "done", "blocked"):
            raise ValidationError(_("You cannot cancel a request in this " "state."))
        self.write({"state": "cancelled"})

    # Bug on super method https://github.com/OCA/cooperative/issues/150
    # delete this method when bug is fixed
    def block_subscription_request(self):
        self.ensure_one()
        if self.state != "draft":
            raise ValidationError(_("Only draft requests can be blocked."))
        self.write({"state": "blocked"})

    # Bug on super method https://github.com/OCA/cooperative/issues/150
    # delete this method when bug is fixed
    def unblock_subscription_request(self):
        self.ensure_one()
        if self.state != "blocked":
            raise ValidationError(_("Only blocked requests can be unblocked."))
        self.write({"state": "draft"})

    @api.constrains("is_company", "firstname")
    def _check_firstname_required(self):
        for rec in self:
            if not rec.is_company and not rec.firstname:
                raise ValidationError(_("First name is required when not is company."))

    @api.constrains("is_company", "lastname")
    def _check_lastname_required(self):
        for rec in self:
            if not rec.is_company and not rec.lastname:
                raise ValidationError(_("Last name is required when not is company."))

    @api.depends("firstname", "lastname", "company_name")
    def _compute_name(self):
        for sub_request in self:
            if sub_request.is_company:
                sub_request.name = sub_request.company_name
            else:
                sub_request.name = " ".join(
                    [
                        sub_request.firstname,
                        sub_request.lastname,
                    ]
                ).strip()
