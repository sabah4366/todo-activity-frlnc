# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class ActivityModel(models.Model):
    _name = 'activity.details'
    _inherit = ['mail.activity', 'mail.thread']
    _rec_name = 'summary'

    name = fields.Char("Name")
    pending_reason = fields.Text(string="Pending Reason")
    date_deadline = fields.Date('Due Date', index=True, required=True,
                                default=fields.Date.today(), store=True)
    user_id = fields.Many2one('res.users', string='user', index=True,
                              tracking=True, default=lambda self: self.env.user)
    # note = fields.Html('Note')
    # activity_type_id = fields.Many2one('mail.activity.type')
    res_id = fields.Integer('Related Document ID', index=True, required=True,default=lambda self: self.id)


    res_model_id = fields.Many2one(
        'ir.model', 'Document Model',
        index=True, ondelete='cascade', required=True,
        default = lambda self: self._get_default_model_id()
        )

    res_model = fields.Char(
        'Related Document Model',
        index=True, related='res_model_id.model', store=True, readonly=True)


    res_name = fields.Char(
        'Document Name',store=True,
        help="Display name of the related document.", readonly=True)


    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
        ('2', 'Very Important'),
        ('3', 'Urgent'),
    ], default='0', index=True, store=True)
    # message_follower_ids = fields.One2many('mail.followers','res_id')
    # message_ids = fields.One2many('mail.message','res_id')
    recurring = fields.Boolean(string="Recurring", store=True)
    state = fields.Selection([
        ('today', 'Today'),
        ('planned', 'Planned'),
        ('requested', 'Requested'),
        ('done', 'Done'),
        ('overdue', 'Pending'),
        ('cancel', 'Cancelled'), ], 'State',
        compute='_compute_state', store=True)
    interval = fields.Selection(
        [('Daily', 'Daily'),
         ('Weekly', 'Weekly'),
         ('Monthly', 'Monthly'),
         ('Quarterly', 'Quarterly'),
         ('Yearly', 'Yearly')],
        string='Recurring Interval', )
    new_date = fields.Date(string="Next Due Date", store=True)
    assigned_ids = fields.Many2many('res.users')
    is_logged_user_assigned = fields.Boolean(compute='_compute_is_logged_user_assigned', store=False)


    # def _get_expired_boolean(self):
    #     for rec in self:
    #         if rec.state == 'overdue':
    #             rec.expired_boolean = True
    #         else:
    #             rec.expired_boolean = False

    @api.depends('assigned_ids')
    def _compute_is_logged_user_assigned(self):
        for record in self:
            record.is_logged_user_assigned = self.env.user in record.assigned_ids

    @api.model
    def _get_default_model_id(self):
        # Search for the ID of the 'activity.detail' model in ir.model
        activity_detail_model = self.env['ir.model'].search([('model', '=', 'activity.details')], limit=1)
        return activity_detail_model.id if activity_detail_model else False

    @api.depends('res_model', 'res_id')
    def _compute_res_name(self):
        for activity in self:
            activity.res_name = activity.res_model and \
                                self.env[activity.res_model].browse(activity.res_id).display_name
    def action_requested(self):
        self.write({'state': 'requested'})

    def action_done(self):
        """Function done button"""
        self.write({'state': 'done'})

    def get_date(self):
        """ function for get new due date on new record"""
        date_deadline = self.new_date if self.new_date else self.date_deadline
        new_date = False
        if self.interval == 'Daily':
            new_date = (
                    date_deadline + timedelta(days=1)).strftime(
                DEFAULT_SERVER_DATE_FORMAT)
        elif self.interval == 'Weekly':
            new_date = (
                    date_deadline + timedelta(days=7)).strftime(
                DEFAULT_SERVER_DATE_FORMAT)
        elif self.interval == 'Monthly':
            new_date = (
                    date_deadline + timedelta(days=30)).strftime(
                DEFAULT_SERVER_DATE_FORMAT)
        elif self.interval == 'Quarterly':
            new_date = (
                    date_deadline + timedelta(days=90)).strftime(
                DEFAULT_SERVER_DATE_FORMAT)
        elif self.interval == 'Yearly':
            new_date = (
                    date_deadline + timedelta(days=365)).strftime(
                DEFAULT_SERVER_DATE_FORMAT)
        return new_date

    @api.onchange('interval', 'date_deadline')
    def onchange_recurring(self):
        """ function for show new due date"""
        self.new_date = False
        if self.recurring:
            self.new_date = self.get_date()

    def action_date(self):
        """ Function for automated actions for deadline"""
        today = fields.date.today()
        dates = self.env['mail.activity'].search(
            [('state', 'in', ['today', 'planned']),
             ('date_deadline', '=', today),
             ('recurring', '=', True)])
        for rec in dates:
            self.env['mail.activity'].create(
                {'res_id': rec.res_id,
                 'res_model_id': rec.res_model_id.id,
                 'summary': rec.summary,
                 'priority': rec.priority,
                 'interval': rec.interval,
                 'recurring': rec.recurring,
                 'date_deadline': rec.new_date,
                 'new_date': rec.get_date(),
                 'activity_type_id': rec.activity_type_id.id,
                 'user_id': rec.user_id.id
                 })
            rec.state = 'done'

    def action_cancel(self):
        """ function for cancel button"""
        return self.write({'state': 'cancel'})

#
# class ActivityGeneral(models.Model):
#     _name = 'activity.general'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#
#     name = fields.Char('Name')
