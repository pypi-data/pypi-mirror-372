from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo import fields


class AccountInvoice(SCTestCase):
    def test_set_cooperator_effective_in_partner_with_share_lines_not_have_effects(
        self,
    ):
        share_product = self.browse_ref(
            "cooperator_somconnexio.cooperator_share_product"
        ).product_variant_id
        partner = self.browse_ref("somconnexio.res_partner_1_demo")
        self.env["share.line"].create(
            {
                "share_number": 1,
                "share_product_id": share_product.id,
                "partner_id": partner.id,
                "share_unit_price": share_product.lst_price,
                "effective_date": fields.Date.today(),
            }
        )
        invoice = self.env["account.move"].create(
            {
                "partner_id": partner.id,
            }
        )

        invoice.set_cooperator_effective(None)

        self.assertEqual(len(partner.share_ids), 1)
