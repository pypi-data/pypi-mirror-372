from mock import patch

from odoo.exceptions import MissingError
from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase


@patch(
    "odoo.addons.somconnexio.services.fiber_contract_to_pack.FiberContractToPackService.create"  # noqa
)
class TestCreateLeadfromPartnerWizard(SCTestCase):
    def setUp(self):
        super().setUp()
        self.wizard_params = {
            "opportunity": "test",
            "phone_contact": "888888888",
            "product_id": self.ref("somconnexio.ADSL20MB1000MinFix"),
            "product_categ_id": self.ref("somconnexio.mobile_service"),
            "type": "new",
            "service_street": "Principal A",
            "service_zip_code": "00123",
            "service_city": "Barcelona",
            "service_state_id": self.ref("base.state_es_b"),
            "delivery_street": "Principal B",
            "delivery_zip_code": "08027",
            "delivery_city": "Barcelona",
            "delivery_state_id": self.ref("base.state_es_b"),
        }

    def test_products_filtered_when_partner_has_coop_agreement(
        self, mock_get_fiber_contracts
    ):
        mock_get_fiber_contracts.side_effect = MissingError("")

        partner = self.browse_ref(
            "cooperator_somconnexio.res_coop_agreement_partner_demo"
        )
        email = self.env["res.partner"].create(
            {
                "parent_id": partner.id,
                "email": "new_email@test.com",
                "type": "contract-email",
            }
        )

        wizard = (
            self.env["partner.create.lead.wizard"]
            .with_context(active_id=partner.id)
            .create(
                {
                    "bank_id": partner.bank_ids.id,
                    "email_id": email.id,
                    **self.wizard_params,
                }
            )
        )

        self.assertEqual(
            wizard.available_product_categories,
            partner.coop_agreement_id.products.mapped("categ_id"),
        )

    def test_products_filtered_when_partner_sponsed(self, mock_get_fiber_contracts):
        mock_get_fiber_contracts.side_effect = MissingError("")

        sc_coop_agreement = self.env.ref("cooperator_somconnexio.coop_agreement_sc")
        partner = self.browse_ref("cooperator_somconnexio.res_sponsored_partner_1_demo")
        email = self.env["res.partner"].create(
            {
                "parent_id": partner.id,
                "email": "new_email@test.com",
                "type": "contract-email",
            }
        )
        wizard = (
            self.env["partner.create.lead.wizard"]
            .with_context(active_id=partner.id)
            .create(
                {
                    "bank_id": partner.bank_ids.id,
                    "email_id": email.id,
                    **self.wizard_params,
                }
            )
        )

        self.assertEqual(
            wizard.available_product_categories,
            sc_coop_agreement.products.mapped("categ_id"),
        )
