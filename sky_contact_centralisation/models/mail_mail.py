# -*- coding: utf-8 -*-
import re
from odoo import models, api
from odoo.tools import html2plaintext

FIRST_LINE_MARKER = "This message has been posted on your website!"

# Label → res.partner payload key
LINE_MAP = {
    'name':        'name',
    'phone':       'phone',
    'email':       'email',
    'company':     'company_name',  # your mixin ignores unknown keys; we map to a safe one
    'description': 'description',   # keep if you want to use it later
}

LABEL_RE = re.compile(r'^\s*([a-zA-Z]+)\s*:\s*(.*)$')  # matches "name : value"

class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model_create_multi
    def create(self, vals_list):
        mails = super().create(vals_list)

        for mail in mails:
            text = html2plaintext(mail.body_html or '').strip()
            if not text:
                continue

            # 1) Gate: first line must be the known marker
            lines = [ln.strip() for ln in text.splitlines() if ln.strip() != ""]
            if not lines or not lines[0].startswith(FIRST_LINE_MARKER):
                continue

            # 2) Extract data from their corresponding labeled lines
            #    (works even if "___________" separator or extra lines are present)
            payload = {}
            for ln in lines[1:]:  # skip the marker line
                m = LABEL_RE.match(ln)
                if not m:
                    continue
                label, value = m.group(1).lower(), m.group(2).strip()
                if label in LINE_MAP and value:
                    payload[LINE_MAP[label]] = value

            # 3) Upsert only if we have something meaningful
            if payload.get('name') or payload.get('email') or payload.get('phone'):
                self.env['contact.centralisation.mixin'].sudo().create_contact_if_not_exist(payload)

        return mails
