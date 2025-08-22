import logging

from odoo import http
from odoo.http import request


_logger = logging.getLogger(__name__)


class WebsiteContactController(http.Controller):
    """Handle contact us form submissions and centralise contacts.

    This controller collects a visitor's name, phone number and email address
    then forwards the data to ``contact.centralisation.mixin`` which is in
    charge of creating the contact or retrieving an existing one based on the
    provided information.
    """

    @http.route('/contactus', type='http', auth='public', website=True, methods=['GET', 'POST'])
    def website_contact_us(self, **post):
        if request.httprequest.method == 'GET':
            return request.render('website.contactus')

        name = (post.get('name') or '').strip()
        email = (post.get('email') or '').strip()
        phone = (post.get('phone') or '').strip()

        if name or email or phone:
            try:
                vals = {'name': name, 'email': email, 'phone': phone}
                partner_id = request.env['contact.centralisation.mixin'].sudo().create_contact_if_not_exist(vals)
                _logger.info('Contact centralised with partner_id=%s', partner_id)
            except Exception as e:
                _logger.exception('Unable to centralise contact: %s', e)

        template = request.env.ref('website_form.website_contactus_form', raise_if_not_found=False)
        if template:
            request.env['mail.template'].sudo().browse(template.id).send_mail(
                request.website.id,
                force_send=True,
            )

        return request.redirect('/contactus-thank-you')

