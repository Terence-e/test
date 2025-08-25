import logging
import re

from odoo import models

_logger = logging.getLogger(__name__)

CONTACT_TEMPLATE = 'website_form.website_contactus_form'


class ContactUsTemplate(models.Model):
    """Intercept outbound *contact us* e-mails.

    When a complaint is submitted the corresponding e-mail is generated from
    ``CONTACT_TEMPLATE``.  This override hooks into ``mail.template.send_mail``
    to scan the outgoing body, extract the sender details and create the
    contact through ``contact.centralisation.mixin``.
    """

    _inherit = 'mail.template'

    def send_mail(
        self,
        res_id,
        force_send=False,
        raise_exception=False,
        email_values=None,
        notif_layout=False,
    ):
        mail_id = super().send_mail(
            res_id,
            force_send=force_send,
            raise_exception=raise_exception,
            email_values=email_values,
            notif_layout=notif_layout,
        )

        contact_template = self.env.ref(CONTACT_TEMPLATE, False)
        if contact_template and self.id == contact_template.id:
            mail = self.env['mail.mail'].browse(mail_id)
            body = mail.body_html or ''

            def _extract(pattern):
                match = re.search(pattern, body, re.IGNORECASE | re.MULTILINE)
                return match.group(1).strip() if match else ''

            name = _extract(r"^name\s*:\s*(.+)$")
            email = _extract(r"^email\s*:\s*([^\s<]+)")
            phone = _extract(r"^phone\s*:\s*(.+)$")
            company = _extract(r"^company\s*:\s*(.+)$")

            if name and email:
                partner_vals = {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'company_name': company,
                }
                _logger.info(
                    "===> Création/Recherche de contact avec : %s", partner_vals
                )
                self.env['contact.centralisation.mixin'].create_contact_if_not_exist(
                    partner_vals
                )

        return mail_id

