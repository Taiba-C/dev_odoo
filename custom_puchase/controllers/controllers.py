# -*- coding: utf-8 -*-
# from odoo import http


# class CustomPuchase(http.Controller):
#     @http.route('/custom_puchase/custom_puchase', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_puchase/custom_puchase/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_puchase.listing', {
#             'root': '/custom_puchase/custom_puchase',
#             'objects': http.request.env['custom_puchase.custom_puchase'].search([]),
#         })

#     @http.route('/custom_puchase/custom_puchase/objects/<model("custom_puchase.custom_puchase"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_puchase.object', {
#             'object': obj
#         })
