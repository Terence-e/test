# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.tools import html2plaintext

class MailMail(models.Model):
    _inherit = "mail.mail"

    @api.model_create_multi
    def create(self, vals_list):
        mails = super().create(vals_list)
        for m in mails:
            txt = html2plaintext(m.body_html or "")
            name = phone = None
            for line in txt.splitlines():
                L = line.strip()
                l = L.lower()
                if not name and l.startswith("name :"):
                    name = L.split(":", 1)[1].strip()
                elif not phone and l.startswith("phone :"):
                    phone = L.split(":", 1)[1].strip()
                if name and phone:
                    break

            email = m.reply_to
            if name and phone and email:
                contact_data = {
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "category_id": self.env.company.source_line_ids.filtered(lambda s: s.source == "site web").mapped("category_id").ids,
                }
                partner = self.env["contact.centralisation.mixin"].sudo().create_contact_if_not_exist(contact_data)
        return mails
