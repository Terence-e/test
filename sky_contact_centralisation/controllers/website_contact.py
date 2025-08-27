# -*- coding: utf-8 -*-
import logging

from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm as WebsiteFormController
from email_validator import EmailNotValidError, validate_email

_logger = logging.getLogger(__name__)


class WebsiteForm(WebsiteFormController):
    """Override the default website form submit to capture Contact Us data."""

    def website_form(self, model_name, **kwargs):
        # Run contact centralisation before delegating to Odoo's controller
        if model_name == 'crm.lead':
            name = (kwargs.get('contact_name') or kwargs.get('name') or '').strip()
            email = (kwargs.get('email_from') or '').strip().lower()
            phone = (kwargs.get('phone') or '').strip()

            try:
                email = validate_email(email).email
                request.env['contact.centralisation.mixin'].sudo().create_contact_if_not_exist({
                    'name': name or email.split('@')[0],
                    'email': email,
                    'phone': phone,
                })
            except EmailNotValidError:
                _logger.warning("Invalid email '%s' in contact form", email)
            except Exception:
                _logger.exception("Failed to centralise contact from website form")

        return super().website_form(model_name, **kwargs)
