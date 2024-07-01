# -*- coding: utf-8 -*-
# from odoo import http


# class NesilBase(http.Controller):
#     @http.route('/nesil_base/nesil_base', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nesil_base/nesil_base/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('nesil_base.listing', {
#             'root': '/nesil_base/nesil_base',
#             'objects': http.request.env['nesil_base.nesil_base'].search([]),
#         })

#     @http.route('/nesil_base/nesil_base/objects/<model("nesil_base.nesil_base"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nesil_base.object', {
#             'object': obj
#         })
