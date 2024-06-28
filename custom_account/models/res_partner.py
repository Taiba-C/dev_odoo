from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _signature_malika(self):
        self.ensure_one()
        malika_signature = self.env['res.users'].search([('name', 'ilike', 'malika')])
        return malika_signature