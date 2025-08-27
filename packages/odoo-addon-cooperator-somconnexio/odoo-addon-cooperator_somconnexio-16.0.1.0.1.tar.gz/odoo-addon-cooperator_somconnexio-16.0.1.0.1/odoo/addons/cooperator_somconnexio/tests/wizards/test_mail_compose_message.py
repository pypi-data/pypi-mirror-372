from odoo.tests import patch
from odoo.addons.somconnexio.tests.wizards.test_mail_compose_message_wizard import (
    TestMailComposerWizard as SCTestMailComposerWizard,
)


class TestMailComposerWizard(SCTestMailComposerWizard):
    def test_mail_compose_template_spanish(self):
        sr_id = self.browse_ref("cooperator_somconnexio.sc_subscription_request_2_demo")
        spanish_crm_lead = self.env["crm.lead"].create(
            [
                {
                    "name": "Test spanish partner Lead",
                    "subscription_request_id": sr_id.id,
                    "lead_line_ids": [(6, 0, [self.crm_lead_line.id])],
                }
            ]
        )
        wizard = self.env["mail.compose.message"].create(
            {
                "model": "crm.lead",
                "res_id": spanish_crm_lead.id,
                "template_id": self.browse_ref(
                    "somconnexio.crm_lead_creation_email_template"
                ).id,
            }
        )
        with patch(
                "odoo.models.BaseModel.with_context", autospec=True
        ) as mock_with_context:

            wizard._onchange_template_id_wrapper()

            mock_with_context.assert_called_once_with(
                wizard,
                {
                    "lang": "es_ES",
                    "tracking_disable": True,
                    "test_queue_job_no_delay": True,
                }
            )
