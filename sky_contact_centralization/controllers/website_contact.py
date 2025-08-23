import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

CONTACT_TEMPLATE = 'website_form.website_contactus_form'


class WebsiteContactController(http.Controller):

    @http.route(['/contactus'], type='http', auth="public", website=True, methods=['GET', 'POST'])
    def website_contact_us(self, **post):
        """Handle submissions from the contact us form.

        The controller scans the mail template used for the outgoing message. If
        the template corresponds to the standard *contact us* template, a
        partner is created or updated via the ``contact.centralisation.mixin``
        helper before the e-mail is dispatched.
        """
        if request.httprequest.method == 'GET':
            return request.render('website.contactus', {})

        _logger.info("===> Données POST reçues : %s", post)

        template = None
        if post.get('template_id'):
            template = request.env['mail.template'].sudo().browse(int(post['template_id']))
        elif post.get('template_ref'):
            template = request.env.ref(post['template_ref'], False)
        else:
            template = request.env.ref(CONTACT_TEMPLATE, False)

        contact_template = request.env.ref(CONTACT_TEMPLATE, False)
        if template and contact_template and template.id == contact_template.id:
            if post.get('name') and post.get('email'):
                partner_vals = {
                    'name': post.get('name'),
                    'email': post.get('email'),
                    'phone': post.get('phone'),
                }
                _logger.info("===> Création/Recherche de contact avec : %s", partner_vals)
                request.env['contact.centralisation.mixin'].create_contact_if_not_exist(partner_vals)

        if template:
            _logger.info("===> Envoi de l'email via le template ID %s", template.id)
            request.env['mail.template'].sudo().browse(template.id).send_mail(
                request.website.id, force_send=True
            )

        _logger.info("===> Redirection vers /contactus-thank-you")
        return request.redirect('/contactus-thank-you')

