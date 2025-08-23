import logging
import re

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
            body = (
                post.get('body')
                or post.get('description')
                or post.get('message')
                or ''
            )

            name = (post.get('name') or '').strip()
            if not name:
                match = re.search(r"(?im)^name\s*:\s*(.+)$", body)
                name = match.group(1).strip() if match else ''
                if name:
                    _logger.info("===> Nom extrait depuis le corps de l'email : %s", name)

            email = (post.get('email') or '').strip()
            if not email:
                match = re.search(r"(?im)^email\s*:\s*([^\s]+)", body)
                email = match.group(1).strip() if match else ''
                if email:
                    _logger.info("===> Email extrait depuis le corps de l'email : %s", email)

            phone = (post.get('phone') or '').strip()
            if not phone:
                match = re.search(r"\+?\d[\d\-\.\s]{5,}\d", body)
                phone = match.group(0).strip() if match else ''
                if phone:
                    _logger.info("===> Téléphone extrait depuis le corps de l'email : %s", phone)

            if name and email:
                partner_vals = {
                    'name': name,
                    'email': email,
                    'phone': phone,
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

