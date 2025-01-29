
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_subcontractors = fields.Boolean('Est un sous-traitant')
    subcontractor_margin = fields.Float('Taux de marge')
    is_coa_installed = fields.Boolean(
        string="COA Installed",
        default=False,
        compute="_compute_is_coa_installed",
    )

    def _compute_is_coa_installed(self):
        for partner in self:
            partner.is_coa_installed = bool(self.env['account.account'].search([], limit=1))