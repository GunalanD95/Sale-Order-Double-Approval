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
        """button to approve the record if it is in approve stage by the manager"""
        self = self.filtered(lambda order: order._approval_needed())
        self.write({'state': 'sale','date_order': fields.Datetime.now()})
        return {}


    def action_confirm(self):
        if self._approval_needed():
            return super(SaleOrderInherit, self).action_confirm()
        else:
            self.update({'state': 'to_approve'})


    def action_refuse(self):
        current = self.invoice_ids.filtered(lambda current: current.state == 'to_approve')
        current.button_cancel()
        return self.write({'state': 'cancel'})

class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_order_approval = fields.Boolean("Sale Order Approval",default=lambda self: self.env.company.so_double_validation == True)
    sale_order_min_amount = fields.Monetary(related='company_id.so_double_validation_amount',string="Minimum Amount",)




