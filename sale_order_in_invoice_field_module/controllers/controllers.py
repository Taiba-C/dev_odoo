# -*- coding: utf-8 -*-

from odoo import http


class SaleOrderInInvoiceFieldModule(http.Controller):
    @http.route('/sale_order_in_invoice_field_module/sale_order_in_invoice_field_module', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/sale_order_in_invoice_field_module/sale_order_in_invoice_field_module/objects', auth='public')
    def list(self, **kw):
        return http.request.render('sale_order_in_invoice_field_module.listing', {
            'root': '/sale_order_in_invoice_field_module/sale_order_in_invoice_field_module',
            'objects': http.request.env['sale_order_in_invoice_field_module.sale_order_in_invoice_field_module'].search([]),
            })
    @http.route('/sale_order_in_invoice_field_module/sale_order_in_invoice_field_module/objects/<model("sale_order_in_invoice_field_module.sale_order_in_invoice_field_module"):obj>', auth='public')
    def object(self, obj, **kw):              
        return http.request.render('sale_order_in_invoice_field_module.object', {
            'object': obj
            })
