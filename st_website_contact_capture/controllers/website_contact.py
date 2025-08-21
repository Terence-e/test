# -*- coding: utf-8 -*-
import logging

from email_validator import EmailNotValidError, validate_email
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class WebsiteContactController(http.Controller):

    @http.route(['/contactus/submit'], type='http', auth='public', website=True, methods=['GET', 'POST'])
    def contactus_submit(self, **post):
        """Receive name/email/phone, create or update a res.partner, then redirect."""
        if request.httprequest.method == 'GET':
            return request.redirect('/contactus')

        name = (post.get('name') or '').strip()
        email = (post.get('email') or '').strip().lower()
        phone = (post.get('phone') or '').strip()

        _logger.info("Contact form POST: name=%s, email=%s, phone=%s", name, email, phone)

        # Minimal validation
        try:
            email = validate_email(email).email
        except EmailNotValidError:
            _logger.warning("Invalid payload. name='%s' email='%s'", name, email)
            # You could redirect to an error page or back with a query param
            return request.redirect('/contactus')

        if not name:
            _logger.warning("Missing name")
            return request.redirect('/contactus')

        # Try your mixin first (if installed and provides the method)
        partner = None
        try:
            Mixin = request.env.get('contact.centralisation.mixin')
            if Mixin and hasattr(Mixin, 'create_contact_if_not_exist'):
                partner = Mixin.sudo().create_contact_if_not_exist({
                    'name': name,
                    'email': email,
                    'phone': phone,
                })
        except Exception as e:
            _logger.exception("Mixin contact creation failed: %s", e)

        # Fallback: upsert on res.partner by email or name
        if not partner:
            Partner = request.env['res.partner'].sudo()
            partner = Partner.search([('email', '=', email)], limit=1)
            if partner:
                vals = {}
                if name and partner.name != name:
                    vals['name'] = name
                if phone and partner.phone != phone:
                    vals['phone'] = phone
                if vals:
                    partner.write(vals)
            else:
                partner = Partner.create({
                    'name': name,
                    'email': email,
                    'phone': phone,
                })
        _logger.info("Partner upserted: id=%s", partner.id if partner else None)

        # OPTIONAL: send an email using your own template XML (not included)
        # tpl = request.env.ref('st_website_contact_capture.contact_email_template', raise_if_not_found=False)
        # if tpl:
        #     tpl.sudo().send_mail(partner.id, force_send=True)

        return request.redirect('/contactus-thank-you')
