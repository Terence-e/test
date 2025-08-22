from odoo import models, api

class EventRegistration(models.Model):
    _inherit = 'event.registration'

    @api.model
    def create(self, vals):
        # Vérifie si le partner_id est déjà fourni
        if not vals.get('partner_id'):
            contact_data = {
                'name': vals.get('name'),
                'email': vals.get('email'),
                'phone': vals.get('phone'),
            }

            # Appel à la fonction pour créer ou retrouver le contact
            partner = self.env['contact.centralisation.mixin'].create_contact_if_not_exist(contact_data)

            # Injecte le partner_id dans les valeurs
            #vals['partner_id'] = partner

        # Appel au create original avec le partner_id mis à jour
        return super(EventRegistration, self).create(vals)