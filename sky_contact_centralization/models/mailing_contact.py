from odoo import models, api

class MailingContact(models.Model):
    _inherit = 'mailing.contact'

    @api.model
    def create(self, vals):

        contact_data = {
            'name': vals.get('name'),
            'email': vals.get('email')
        }

        # Appel à la fonction pour créer ou retrouver le contact
        partner = self.env['contact.centralisation.mixin'].create_contact_if_not_exist(contact_data)

        # Injecte le partner_id dans les valeurs
        #vals['partner_id'] = partner

        # Appel au create original avec le partner_id mis à jour
        return super(MailingContact, self).create(vals)