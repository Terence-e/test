from odoo import models, api

class EventRegistration(models.Model):
    _inherit = 'event.registration'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            email = vals.get('email')
            name = vals.get('name')
            company = vals.get('partner_company_name')
            partner = False
            if email:
                partner = self.env['res.partner'].search([('email', '=', email)], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': name or email or 'Attendee',
                    'email': email,
                    'company_name': company or '',
                })
            vals['partner_id'] = partner.id
        return super().create(vals_list)
