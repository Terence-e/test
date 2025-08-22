import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class WebsiteContactController(http.Controller):

    @http.route('/contactus', type='http', auth='public', website=True, methods=['GET', 'POST'])
    def website_contact_us(self, **post):
        if request.httprequest.method == 'GET':
            return request.render('website.contactus')

        # Log des données reçues
        _logger.debug("===> Données POST reçues : %s", post)

        # Créer un partenaire automatiquement
        if post.get('name') and post.get('email'):
            partner_vals = {
                'name': post.get('name'),
                'email': post.get('email'),
                'phone': post.get('phone'),
            }
            _logger.info("===> Création/Recherche de contact avec : %s", partner_vals)
            request.env['contact.centralisation.mixin'].create_contact_if_not_exist(partner_vals)

        # Garder l'action d'envoi d'email existante
        template = request.env.ref('website_form.website_contactus_form', raise_if_not_found=False)
        if template:
            _logger.info("===> Envoi de l'email via le template ID %s", template.id)
            request.env['mail.template'].sudo().browse(template.id).send_mail(
                request.website.id, force_send=True
            )
        else:
            _logger.warning("Template website_form.website_contactus_form not found")

        # Redirection vers la page de remerciement
        _logger.info("===> Redirection vers /contactus-thank-you")
        return request.redirect('/contactus-thank-you')
