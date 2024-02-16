
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_subcontractor = fields.Boolean('Est un sous-traitant')
