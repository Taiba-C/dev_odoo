# -*- coding: utf-8 -*-
# from odoo import http


# class CustomStock(http.Controller):
#     @http.route('/custom_stock/custom_stock', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_stock/custom_stock/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_stock.listing', {
#             'root': '/custom_stock/custom_stock',
#             'objects': http.request.env['custom_stock.custom_stock'].search([]),
#         })

#     @http.route('/custom_stock/custom_stock/objects/<model("custom_stock.custom_stock"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_stock.object', {
#             'object': obj
#         })
