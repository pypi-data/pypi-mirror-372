from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


class TestCreateSubscriptionFromPartnerWizard(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.payment_type = "single"
        self.share_product = self.browse_ref(
            "cooperator_somconnexio.cooperator_share_product"
        ).product_variant_id

    def test_create_subscription_from_person_partner_wizard(self):
        partner = self.browse_ref("somconnexio.res_partner_2_demo")

        wizard = (
            self.env["partner.create.subscription"]
            .with_context(
                {
                    "active_id": partner.id,
                }
            )
            .create(
                {
                    "share_product": self.share_product.id,
                    "share_qty": 1,
                    "bank_id": partner.bank_ids.id,
                    "bank_account": partner.bank_ids.acc_number,
                    "payment_type": self.payment_type,
                    "is_company": False,
                    "email": "test@example.org"
                }
            )
        )

        sub_req = self.env["subscription.request"].browse(
            wizard.create_subscription()["res_id"]
        )
        self.assertEqual(sub_req.partner_id, partner)
        self.assertEqual(sub_req.share_product_id, self.share_product)
        self.assertEqual(sub_req.ordered_parts, 1)
        self.assertEqual(sub_req.user_id.id, self.env.uid)
        self.assertEqual(sub_req.email, "test@example.org")
        self.assertEqual(sub_req.source, "crm")
        self.assertEqual(sub_req.address, partner.street)
        self.assertEqual(sub_req.zip_code, partner.zip)
        self.assertEqual(sub_req.city, partner.city)
        self.assertEqual(sub_req.country_id, partner.country_id)
        self.assertEqual(sub_req.lang, partner.lang)
        self.assertEqual(sub_req.firstname, partner.firstname)
        self.assertEqual(sub_req.lastname, partner.lastname)
        self.assertEqual(sub_req.name, partner.name)
        self.assertFalse(sub_req.is_company)
        self.assertEqual(sub_req.iban, partner.bank_ids.acc_number)
        self.assertEqual(sub_req.payment_type, self.payment_type)

    def test_create_subscription_from_company_partner_wizard(self):
        partner = self.env["res.partner"].create(
            {
                "street": "Street",
                "zip": "1234",
                "city": "City",
                "country_id": self.ref("base.es"),
                "lang": self.browse_ref("base.lang_es").code,
                "company_name": "Test partner company",
                "email": "testcompany@example.com",
                "firstname": "company firstname",
                "lastname": "company lastname",
                "vat": "ES45475957N",
                "is_company": True,
            }
        )
        # Partner representative
        representative = self.env["res.partner"].create(
            {
                "street": "Street 2",
                "zip": "1234",
                "city": "City",
                "country_id": self.ref("base.es"),
                "lang": self.browse_ref("base.lang_es").code,
                "firstname": "Test firstname",
                "lastname": "Test lastname",
                "email": "test@example.com",
                "name": "Test partner company",
                "vat": "ESA46191557",
                "representative": True,
                "parent_id": partner.id,
            }
        )
        bank = self.env["res.partner.bank"].create(
            {"acc_number": "ES1720852066623456789011", "partner_id": partner.id}
        )

        wizard = (
            self.env["partner.create.subscription"]
            .with_context(
                {
                    "active_id": partner.id,
                }
            )
            .create(
                {
                    "share_product": self.share_product.id,
                    "share_qty": 1,
                    "bank_id": bank.id,
                    "bank_account": partner.bank_ids.acc_number,
                    "payment_type": self.payment_type,
                    "is_company": True,
                    "email": "test@example.com"
                }
            )
        )

        sub_req = self.env["subscription.request"].browse(
            wizard.create_subscription()["res_id"]
        )
        self.assertEqual(sub_req.partner_id, partner)
        self.assertEqual(sub_req.share_product_id, self.share_product)
        self.assertEqual(sub_req.ordered_parts, 1)
        self.assertEqual(sub_req.user_id.id, self.env.uid)
        self.assertEqual(sub_req.email, representative.email)
        self.assertEqual(sub_req.vat, partner.vat)
        self.assertEqual(sub_req.source, "crm")
        self.assertEqual(sub_req.address, partner.street)
        self.assertEqual(sub_req.zip_code, partner.zip)
        self.assertEqual(sub_req.city, partner.city)
        self.assertEqual(sub_req.country_id, partner.country_id)
        self.assertEqual(sub_req.lang, partner.lang)
        self.assertEqual(sub_req.company_name, partner.name)
        self.assertEqual(sub_req.company_email, partner.email)
        self.assertEqual(sub_req.name, partner.name)
        self.assertTrue(sub_req.is_company)
        self.assertEqual(sub_req.iban, bank.acc_number)
        self.assertEqual(sub_req.payment_type, self.payment_type)
