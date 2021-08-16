# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo import _
from odoo.exceptions import ValidationError

class SaleOrderInherit(models.Model):
    _inherit = ['sale.order']


    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('to_approve', 'To Approve'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    def _approval_needed(self):
        """Returns whether the order qualifies to be approved by the current user"""
        self.ensure_one()
        if self.company_id.so_double_validation == True:
            return (
                self.user_has_groups('sales_team.group_sale_manager')
                #self.company_id.so_double_validation == True
                or (
                        self.amount_total < self.env.company.currency_id._convert(
                        self.company_id.so_double_validation_amount, self.currency_id, self.company_id,
                        self.date_order or fields.Date.today())))

                #or self.user_has_groups('sales_team.group_sale_manager'))
        else:
            return False
    def button_approve(self, force=False):
        self = self.filtered(lambda order: order._approval_needed())
        self.write({'state': 'sale','date_order': fields.Datetime.now()})
        return {}


    def action_confirm(self):
        #if self.amount_total < self.company_id.so_double_validation_amount:
        if self._approval_needed():
            self.button_approve()
            print("STAYIN IN IF ELSE",self.company_id.so_double_validation_amount,self.amount_total)
        else:
            print("COMING TO ELSE",self.company_id.so_double_validation_amount,self.amount_total)
            self.update({'state': 'to_approve'})
        # return super(SaleOrderInherit,self).action_confirm()

    # def action_confirm(self):
    #     #if self._approval_needed():
    #     if self.amount_total < self.company_id.so_double_validation_amount:
    #         self.button_approve()
    #     else:
    #         self.write({'state': 'to_approve'})
    #     if self._get_forbidden_state_confirm() & set(self.mapped('state')):
    #         raise UserError(_(
    #             'It is not allowed to confirm an order in the following states: %s'
    #         ) % (', '.join(self._get_forbidden_state_confirm())))
    #     for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
    #         order.message_subscribe([order.partner_id.id])
    #     self.write(self._prepare_confirmation_values())
    #
    #     # Context key 'default_name' is sometimes propagated up to here.
    #     # We don't need it and it creates issues in the creation of linked records.
    #     context = self._context.copy()
    #     context.pop('default_name', None)
    #
    #     self.with_context(context)._action_confirm()
    #     if self.env.user.has_group('sale.group_auto_done_setting'):
    #         self.action_done()
    #     return True




class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_order_approval = fields.Boolean("Sale Order Approval",default=lambda self: self.env.company.so_double_validation == True)
    sale_order_min_amount = fields.Monetary(related='company_id.so_double_validation_amount',string="Minimum Amount",)




