# -*- coding: utf-8 -*-
# from odoo import http


# class CustomManufacturing(http.Controller):
#     @http.route('/custom_manufacturing/custom_manufacturing', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_manufacturing/custom_manufacturing/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_manufacturing.listing', {
#             'root': '/custom_manufacturing/custom_manufacturing',
#             'objects': http.request.env['custom_manufacturing.custom_manufacturing'].search([]),
#         })

#     @http.route('/custom_manufacturing/custom_manufacturing/objects/<model("custom_manufacturing.custom_manufacturing"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_manufacturing.object', {
#             'object': obj
#         })
