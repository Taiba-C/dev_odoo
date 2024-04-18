from odoo import models, fields, api


class ComponentSelectionWizard(models.TransientModel):
    _name = 'component.selection.wizard.option'
    _description = 'Component Selection Wizard'

    product_id = fields.Many2one('product.product', 'Nomenclature', default=lambda self: self._get_default_product(),
                           readonly=True)
    # @api.onchange('bom_product_template_attribute_value_ids')
    # def _get_options_by_ref(self):
    #     boms = self.env.context.get('mrp_bom_line')
    #     lines = []
    #     old_options = self._get_default_option_ids()
    #     if self.bom_product_template_attribute_value_ids:
    #         self.option_ids = lines.append((5, 0, 0))
    #         for bom in boms:
    #             bom_line = self.env['mrp.bom.line'].search([('id', '=', bom)])
    #             bom_line.ensure_one()
    #             for old_option in old_options:
    #                 if bom_line.product_id.id == old_option[2]['product_id']:
    #                     res = set(self.bom_product_template_attribute_value_ids.ids).issubset(set(bom_line.bom_product_template_attribute_value_ids.ids))
    #                     if res:
    #                         lines.append((0, 0, {
    #                             'product_id': bom_line.product_id,
    #                             'quantity': old_option[2]['quantity'],
    #                             'selected_product': old_option[2]['selected_product'] if 'selected_product' in old_option[2].keys()  else False,
    #                         }))
    #         self.option_ids = lines
    #     else:
    #         self.option_ids = lines.append((5, 0,0))
    #         self.option_ids = self._get_default_option_ids()

    # bom_product_template_attribute_value_ids = fields.Many2many(
    #     'product.template.attribute.value',string="",
    #     related='product_id.product_template_variant_value_ids')
    product_image = fields.Binary(string='Product Image', related='product_id.image_1920')

    bom_id = fields.Many2one('mrp.bom', string='bom', compute="_compute_default_bom_id")
    order_line_id = fields.Many2one('sale.order.line', 'Sale Order Line',readonly=True)
    option_line_id = fields.Many2one('sale.order.option', 'Sale Order Line',
                                    default=lambda self: self._get_default_option_line_id(), readonly=True)
    component_ids = fields.Many2many('mrp.bom.line', string='Composants')
    

    option_ids = fields.One2many('stock.quantity.line', 'wizard_id_option', string='Composants du tableau de chiffrage',
                                 default=lambda self: self._get_default_option_ids())

    def action_confirm(self):
        product_boms = []
        
        order_options = self.env['sale.order.option.nesil'].search([('option_line_id', '=', self.option_line_id.id)])
        order_options.unlink()

        total_sale_price = 0
        for line in self.option_ids:
            if line.selected_product:
                total_sale_price += line.product_id.lst_price * line.quantity
                product_boms.append({'id': line.product_id.id, 'quantity': line.quantity})

        option_line = self.option_line_id
        option_line.order_id.generate_bom_order(order_line=None,products=product_boms, option_line=self.option_line_id.id)
        option_line.write({'price_unit':total_sale_price})

        return {'type': 'ir.actions.act_window_close'}

    def _get_default_product(self):
        return self._context.get('product_id')

    def _get_default_option_line_id(self):
        return self._context.get('option_line_id')

    @api.depends('product_id')
    def _compute_default_bom_id(self):
        for record in self:
            if record.product_id:
                bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', record.product_id.product_tmpl_id.id)])

                record.bom_id = bom
            else:
                record.bom_id = False

    def _get_default_option_ids(self):
        print("##############")
        print("##############")
        print("ato ve")
        print("##############")
        print("##############")
        print("##############")
        boms = self.env.context.get('mrp_bom_line')
        option_line = self.env.context.get('option_line_id')

        options = self.env['sale.order.option.nesil'].search([('option_line_id', '=', option_line)])

        lines = []

        options_info = []
        if len(options) > 0:
            for option in options:
                options_info.append({
                    'product_id': option.product_id.id,
                    'quantity': option.quantity,
                })

        for bom in boms:
            bom_lines = self.env['mrp.bom.line'].search([('id', '=', bom)])
            for bom_line in bom_lines:
                if len(options) == 0:
                    lines.append((0, 0, {
                        'product_id': bom_line.product_id.id,
                        'quantity': bom_line.product_qty,
                        # Add other fields as needed
                    }))
                else:
                    product_options_ids = [x['product_id'] for x in options_info]

                    if bom_line.product_id.id in product_options_ids:
                        for line in options_info:
                            if bom_line.product_id.id == line['product_id'] and bom_line.product_qty != line['quantity'] and bom_line.product_id.active == True:
                                lines.append((0, 0, {
                                        'product_id': line['product_id'],
                                        'quantity': line['quantity'],
                                        'updated': True,
                                        'selected_product': True,
                                        # Add other fields as needed
                                    }))
                            elif bom_line.product_id.id == line['product_id'] and bom_line.product_id.active == True:
                                lines.append((0, 0, {
                                    'product_id': line['product_id'],
                                    'quantity': line['quantity'],
                                    'selected_product': True,
                                    'updated': True,
                                    # Add other fields as needed
                                }))
                    elif bom_line.product_id.active == True:
                        lines.append((0, 0, {
                            'product_id': bom_line.product_id.id,
                            'quantity': bom_line.product_qty,
                            # Add other fields as needed
                        }))
        return lines

    # @api.onchange('option_line_id')
    # def _onchange_option_line_id(self):
    #     bom_lines = self.env['sale.order.option.nesil'].search([('option_line_id', '=', self.option_line_id.id)])
    #
    #     option_values = []
    #     for bom_line in bom_lines:
    #         option_values.append((0, 0, {
    #             'product_id': bom_line.product_id.id,
    #             'quantity': bom_line.quantity,
    #         }))
    #
    #     self.option_ids = option_values
