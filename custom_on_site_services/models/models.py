# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class custom_on_site_services(models.Model):
#     _name = 'custom_on_site_services.custom_on_site_services'
#     _description = 'custom_on_site_services.custom_on_site_services'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
