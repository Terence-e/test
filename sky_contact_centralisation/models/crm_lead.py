# -*- coding: utf-8 -*-
from odoo import api, models


class CrmLead(models.Model):
    """Extend crm.lead to synchronise website leads into res.partner."""
    _inherit = "crm.lead"

    @api.model
    def create(self, vals):
        lead = super().create(vals)

        # Try to limit to leads that likely come from the website
        is_websiteish = bool(lead.email_from or lead.contact_name) and bool(lead.description)

        if is_websiteish:
            payload = {
                "name": lead.contact_name or (lead.email_from or "Unknown").split("@")[0],
                "email": lead.email_from,
                "phone": lead.phone,
                "company_name": lead.partner_name,
                "subject": lead.name,
                "message": lead.description,
            }
            self.env["contact.centralisation.mixin"].sudo().create_contact_if_not_exist(payload)

        return lead
