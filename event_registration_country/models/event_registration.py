# -*- coding: utf-8 -*-
from odoo import fields, models




class EventRegistration(models.Model):
    _inherit = "event.registration"


    country_text = fields.Char(string="Country")