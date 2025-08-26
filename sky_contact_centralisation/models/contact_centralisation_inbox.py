# -*- coding: utf-8 -*-
import logging
from email.utils import parseaddr

from odoo import api, fields, models, tools

_logger = logging.getLogger(__name__)


class ContactCentralisationInbox(models.Model):
    """
    Minimal model receiving e-mails via a mail alias and syncing contacts.

    Each incoming email triggers ``message_new`` which extracts the sender
    information and delegates contact creation to ``contact.centralisation.mixin``.
    """

    _name = "contact.centralisation.inbox"
    _description = "Inbound mailbox for Contact Centralisation"
    _inherit = ["mail.thread", "mail.alias.mixin"]

    # Store basic information about received messages
    subject = fields.Char()
    email_from = fields.Char()
    description = fields.Text()

    # --- mail.alias.mixin configuration -------------------------------------------------
    def _alias_get_creation_values(self):
        """Default alias configuration when creating from the UI."""
        return {
            "alias_name": "contacts",  # local part of the email alias
            "alias_contact": "everyone",
            "alias_defaults": {},
        }

    def _alias_get_model_id(self):
        """Ensure the alias is linked to this model."""
        return self.env["ir.model"]._get_id(self._name)

    # --- email processing ---------------------------------------------------------------
    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """Process new incoming emails from the alias."""
        name, email = self._extract_sender(msg_dict)
        subject = (msg_dict.get("subject") or "").strip()
        plain_body = tools.html2plaintext(msg_dict.get("body") or "")

        _logger.info(
            "Inbound email for contact centralisation: name=%s email=%s subject=%s",
            name,
            email,
            subject,
        )

        contact_vals = {
            "name": name or (email.split("@")[0] if email else "Unknown"),
            "email": email,
        }

        try:
            self.env["contact.centralisation.mixin"].sudo().create_contact_if_not_exist(
                contact_vals
            )
        except Exception as e:  # pragma: no cover - defensive logging
            _logger.exception("Failed calling contact.centralisation.mixin: %s", e)

        defaults = {
            "subject": subject,
            "email_from": email,
            "description": plain_body,
        }
        defaults.update(custom_values or {})
        return super().message_new(msg_dict, defaults)

    # --- helpers -----------------------------------------------------------------------
    @staticmethod
    def _extract_sender(msg_dict):
        """Extract (name, email) from msg_dict['from'] using RFC822 parsing."""
        raw_from = msg_dict.get("from") or msg_dict.get("email_from") or ""
        name, email = parseaddr(raw_from)
        name = (name or "").strip() or None
        email = (email or "").strip() or None
        return name, email
