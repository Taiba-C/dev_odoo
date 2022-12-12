# -*- coding: utf-8 -*-
# from odoo import http


# class CustomTimeSheet(http.Controller):
#     @http.route('/custom_time_sheet/custom_time_sheet', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_time_sheet/custom_time_sheet/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_time_sheet.listing', {
#             'root': '/custom_time_sheet/custom_time_sheet',
#             'objects': http.request.env['custom_time_sheet.custom_time_sheet'].search([]),
#         })

#     @http.route('/custom_time_sheet/custom_time_sheet/objects/<model("custom_time_sheet.custom_time_sheet"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_time_sheet.object', {
#             'object': obj
#         })
