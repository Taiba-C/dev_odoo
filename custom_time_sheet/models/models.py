# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class custom_time_sheet(models.Model):
#     _name = 'custom_time_sheet.custom_time_sheet'
#     _description = 'custom_time_sheet.custom_time_sheet'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
