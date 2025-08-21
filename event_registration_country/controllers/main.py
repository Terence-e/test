# -*- coding: utf-8 -*-
from odoo.addons.website_event.controllers.main import WebsiteEventController




class WebsiteEventControllerInherit(WebsiteEventController):
    """Save country only if the event has a question named 'Country' (case/space tolerant).
    The posted field name must be: attendee_<ticket.id>_<index>_country_text
    """


    def _prepare_attendee_values(self, event, post, ticket, index):
        vals = super()._prepare_attendee_values(event, post, ticket, index)


        def _norm(s):
            return (s or "").strip().casefold()


        # Support either 'name' or 'title' on event.question (varies by version/translations)
        has_country_q = event.question_ids.filtered(
            lambda q: _norm(getattr(q, "name", None) or getattr(q, "title", None)) == "country"
        )
        if has_country_q and ticket and (index is not None):
            key = f"attendee_{ticket.id}_{index}_country_text"
            value = post.get(key)
            if value:
                vals["country_text"] = value
        return vals