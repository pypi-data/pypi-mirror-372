from odoo import models, fields


class DiscoveryChannel(models.Model):
    _name = "discovery.channel"
    name = fields.Char("Name", translate=True)
    sequence = fields.Integer("Sequence", default=99)
    active = fields.Boolean("Active", default=True)
