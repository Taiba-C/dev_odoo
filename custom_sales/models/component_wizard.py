from odoo import models, fields, api


class ComponentSelectionWizard(models.TransientModel):
    _name = 'component.selection.wizard'
    _description = 'Component Selection Wizard'

    product_id = fields.Many2one('product.product', 'Nomenclature', default=lambda self: self._get_default_product(),
                           readonly=True)
    @api.onchange('bom_product_template_attribute_value_ids')
    def _get_options_by_ref(self):
        boms = self.env.context.get('mrp_bom_line')
        lines = []
        old_options = self._get_default_option_ids()
        if self.bom_product_template_attribute_value_ids:
            self.option_ids = lines.append((5, 0, 0))
            for bom in boms:
                bom_line = self.env['mrp.bom.line'].search([('id', '=', bom)])
                bom_line.ensure_one()
                for old_option in old_options:
                    if bom_line.product_id.id == old_option[2]['product_id']:
                        res = set(self.bom_product_template_attribute_value_ids.ids).issubset(set(bom_line.bom_product_template_attribute_value_ids.ids))
                        if res:
                            lines.append((0, 0, {
                                'product_id': bom_line.product_id,
                                'quantity': old_option[2]['quantity'],
                                'selected_product': old_option[2]['selected_product'] if 'selected_product' in old_option[2].keys()  else False,
                            }))
            self.option_ids = lines
        else:
            self.option_ids = lines.append((5, 0,0))
            self.option_ids = self._get_default_option_ids()

    bom_product_template_attribute_value_ids = fields.Many2many(
        'product.template.attribute.value',string="",
        related='product_id.product_template_variant_value_ids')
    product_image = fields.Binary(string='Product Image', related='product_id.image_1920')

    bom_id = fields.Many2one('mrp.bom', string='bom', compute="_compute_default_bom_id")
    order_line_id = fields.Many2one('sale.order.line', 'Sale Order Line',
                                    default=lambda self: self._get_default_order_line_id(), readonly=True)
    component_ids = fields.Many2many('mrp.bom.line', string='Composants')
    

    option_ids = fields.One2many('stock.quantity.line', 'wizard_id', string='Composants du tableau de chiffrage',
                                 default=lambda self: self._get_default_option_ids())

    def action_confirm(self):
        product_boms = []

        order_options = self.env['sale.order.option.nesil'].search([('order_line_id', '=', self.order_line_id.id)])
        order_options.unlink()

        for line in self.option_ids:
            if line.selected_product:
                product_boms.append({'id': line.product_id.id, 'quantity': line.quantity})

        order_line = self.order_line_id
        order_line.order_id.generate_bom_order(products=product_boms, order_line=self.order_line_id.id)

        return {'type': 'ir.actions.act_window_close'}

    def _get_default_product(self):
        return self._context.get('product_id')

    def _get_default_order_line_id(self):
        return self._context.get('order_line_id')

    @api.depends('product_id')
    def _compute_default_bom_id(self):
        for record in self:
            if record.product_id:
                bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', record.product_id.product_tmpl_id.id)])

                record.bom_id = bom
            else:
                record.bom_id = False

    def _get_default_option_ids(self):
        boms = self.env.context.get('mrp_bom_line')
        order_line = self.env.context.get('order_line_id')

        options = self.env['sale.order.option.nesil'].search([('order_line_id', '=', order_line)])

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

    # @api.onchange('order_line_id')
    # def _onchange_order_line_id(self):
    #     bom_lines = self.env['sale.order.option.nesil'].search([('order_line_id', '=', self.order_line_id.id)])
    #
    #     option_values = []
    #     for bom_line in bom_lines:
    #         option_values.append((0, 0, {
    #             'product_id': bom_line.product_id.id,
    #             'quantity': bom_line.quantity,
    #         }))
    #
    #     self.option_ids = option_values


class StockQuantityLine(models.TransientModel):
    _name = 'stock.quantity.line'
    _description = 'Stock Quantity Line'

    wizard_id = fields.Many2one(
        comodel_name='component.selection.wizard',
        string='Wizard',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Article',
    )
    product_id_visible = fields.Many2one(
        comodel_name='product.product',
        string='Article',
        compute="_compute_product_id_visible",
        readonly=True,
        store=True
    )
    quantity = fields.Float(string='Quantité')

    updated = fields.Boolean("Modifié")

    selected_product = fields.Boolean('Selection')

    @api.depends('product_id')
    def _compute_product_id_visible(self):
        for record in self:
            record.product_id_visible = record.product_id

    @api.onchange('quantity')
    def _onchange_quantity(self):
        if not self.selected_product:
            self.selected_product = True
