from mock import patch, call
from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.addons.cooperator_sponsorship.tests.helper import (
    subscription_request_create_data,
)
from odoo.addons.cooperator.tests.cooperator_test_mixin import CooperatorTestMixin


class TestResPartner(SCTestCase, CooperatorTestMixin):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.subscription_request_1.iban = 'ES91 2100 0418 4502 0005 1332'
        self.subscription_request_1.vat = 'ES71127582J'
        self.subscription_request_1.country_id = self.ref('base.es')
        self.subscription_request_1.validate_subscription_request()
        self.pay_invoice(self.subscription_request_1.capital_release_request)
        self.member = self.subscription_request_1.partner_id
        self.partner = self.env["res.partner"].create({})

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.set_up_cooperator_test_data()

    def test_discovery_channel(
        self,
    ):
        partner = self.env.ref("somconnexio.res_partner_2_demo")

        SubscriptionRequest = self.env["subscription.request"]
        vals_subscription = subscription_request_create_data(self)
        vals_subscription.update({"partner_id": partner.id, "state": "done"})
        subscription = SubscriptionRequest.create(vals_subscription)
        self.assertEqual(
            subscription.partner_id.discovery_channel_id,
            subscription.discovery_channel_id,
        )

        vals_subscription.update(
            {
                "discovery_channel_id": self.browse_ref(
                    "cooperator_somconnexio.fairs_or_presentations"
                ).id,
            }
        )
        fairs_subscription = SubscriptionRequest.create(vals_subscription)

        self.assertEqual(
            fairs_subscription.partner_id.discovery_channel_id,
            fairs_subscription.discovery_channel_id,
        )

        fairs_subscription.write({"state": "cancelled"})
        self.assertEqual(
            subscription.partner_id.discovery_channel_id,
            subscription.discovery_channel_id,
        )

    @patch("odoo.addons.mail.models.mail_thread.MailThread.message_post")
    def test_sponsor_id_change_message_post(self, message_post_mock):
        sponsor = self.env.ref("somconnexio.res_partner_1_demo")

        self.partner.write({"sponsor_id": sponsor.id})

        message_post_mock.assert_has_calls(
            [
                call(
                    body="sponsor has been changed from False to {}".format(
                        sponsor.name
                    )
                ),
                call(body="Is Cooperator Sponsee? has been changed from False to True"),
            ],
            any_order=True,
        )

    @patch("odoo.addons.mail.models.mail_thread.MailThread.message_post")
    def test_coop_aggreement_change_message_post(self, message_post_mock):
        coop_agreement = self.env.ref("cooperator_somconnexio.coop_agreement_sc")

        self.partner.write({"coop_agreement_id": coop_agreement.id})

        message_post_mock.assert_has_calls(
            [
                call(
                    body="coop_agreement has been changed from False to {}".format(
                        coop_agreement.code
                    )
                ),
                call(body="has_coop_agreement has been changed from False to True"),
            ],
            any_order=True,
        )
