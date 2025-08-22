from odoo import http
from odoo.http import request


class WebsiteContactController(http.Controller):

    @http.route('/contactus', type='http', auth='public', website=True, methods=['GET', 'POST'])
    def website_contact_us(self, **post):
        if request.httprequest.method == 'GET':
            return request.render('website.contactus')

        # Créer un partenaire automatiquement
        if post.get('name') and post.get('email'):
            partner_vals = {
                'name': post.get('name'),
                'email': post.get('email'),
                'phone': post.get('phone'),
            }
            request.env['contact.centralisation.mixin'].sudo().create_contact_if_not_exist(partner_vals)

        # Garder l'action d'envoi d'email existante
        template = request.env.ref('website_form.website_contactus_form', raise_if_not_found=False)
        if template:
            request.env['mail.template'].sudo().browse(template.id).send_mail(
                request.website.id, force_send=True
            )

        return request.redirect('/contactus-thank-you')
