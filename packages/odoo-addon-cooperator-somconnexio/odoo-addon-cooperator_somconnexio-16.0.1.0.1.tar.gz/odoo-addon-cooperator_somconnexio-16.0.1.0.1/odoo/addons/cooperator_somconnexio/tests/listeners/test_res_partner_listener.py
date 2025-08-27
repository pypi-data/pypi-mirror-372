from mock import patch
from datetime import date, timedelta

from odoo.addons.somconnexio.tests.sc_test_case import SCComponentTestCase
from odoo.addons.cooperator.tests.cooperator_test_mixin import CooperatorTestMixin


class TestPartnerListener(SCComponentTestCase, CooperatorTestMixin):
    @classmethod
    def setUpClass(cls):
        super(TestPartnerListener, cls).setUpClass()
        cls.set_up_cooperator_test_data()
        # disable tracking test suite wise
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                test_queue_job_no_delay=False,
            )
        )

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.subscription_request_1.iban = 'ES91 2100 0418 4502 0005 1332'
        self.subscription_request_1.vat = 'ES71127582J'
        self.subscription_request_1.country_id = self.ref('base.es')
        self.subscription_request_1.validate_subscription_request()
        self.pay_invoice(self.subscription_request_1.capital_release_request)
        self.member = self.subscription_request_1.partner_id
        self.partner = self.browse_ref("somconnexio.res_partner_2_demo")
        self.vodafone_fiber_contract_service_info = self.env[
            "vodafone.fiber.service.contract.info"
        ].create(
            {
                "phone_number": "999990999",
                "vodafone_id": "123",
                "vodafone_offer_code": "456",
            }
        )
        partner_id = self.partner.id
        self.service_partner = self.env["res.partner"].create(
            {"parent_id": partner_id, "name": "Partner service OK", "type": "service"}
        )
        self.ba_contract = self.env["contract.contract"].create(
            {
                "name": "Test Contract Broadband",
                "partner_id": partner_id,
                "service_partner_id": self.service_partner.id,
                "invoice_partner_id": partner_id,
                "service_technology_id": self.ref(
                    "somconnexio.service_technology_fiber"
                ),
                "service_supplier_id": self.ref(
                    "somconnexio.service_supplier_vodafone"
                ),
                "vodafone_fiber_service_contract_info_id": (
                    self.vodafone_fiber_contract_service_info.id
                ),
            }
        )

    @patch("odoo.addons.mail.models.mail_template.MailTemplate.send_mail")
    def test_sell_back_member_without_sponsees(self, send_mail_mock):
        self.partner.member = False
        send_mail_mock.assert_not_called()

    @patch("odoo.addons.mail.models.mail_template.MailTemplate.send_mail")
    def test_sell_back_member_with_sponsees(self, send_mail_mock):
        sponsee = self.env["res.partner"].create(
            {
                "sponsor_id": self.member.id,
                "name": "test",
                "street": "test",
                "street2": "test",
                "city": "city",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
                "lang": "ca_ES",
            }
        )
        self.ba_contract.write(
            {
                "partner_id": sponsee.id,
                "invoice_partner_id": sponsee.id,
                "service_partner_id": sponsee.id,
            }
        )
        operation_request = self.env["operation.request"].create(
            {
                "operation_type": "sell_back",
                "partner_id": self.member.id,
                "share_product_id": (
                    self.env.ref(
                        'cooperator_somconnexio.cooperator_share_product'
                    ).product_variant_id.id
                ),
                "quantity": 3,
            }
        )
        operation_request.submit_operation()
        operation_request.approve_operation()
        operation_request.execute_operation()
        self.assertFalse(self.member.member)

        send_mail_mock.assert_called()

    @patch("odoo.addons.mail.models.mail_template.MailTemplate.send_mail")
    def test_sell_back_member_with_sponsees_terminated_contract(self, send_mail_mock):
        sponsee = self.env["res.partner"].create(
            {
                "sponsor_id": self.member.id,
                "name": "test",
                "street": "test",
                "street2": "test",
                "city": "city",
                "state_id": self.ref("base.state_es_b"),
                "country_id": self.ref("base.es"),
                "email": "test@example.com",
                "lang": "ca_ES",
            }
        )
        self.ba_contract.write(
            {
                "partner_id": sponsee.id,
                "invoice_partner_id": sponsee.id,
                "service_partner_id": sponsee.id,
                "date_end": date.today() - timedelta(days=1),
            }
        )
        self.member.write({'member': False})
        send_mail_mock.assert_not_called()
