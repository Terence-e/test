# -*- coding: utf-8 -*-
"""Controller helpers for capturing attendee country text."""

import re

from odoo.addons.website_event.controllers.main import WebsiteEventController


class WebsiteEventControllerInherit(WebsiteEventController):
    """Save country only if the event has a question named 'Country' (case/space tolerant).
    The posted field name must be: attendee_<ticket.id>_<index>_country_text
    """

    def _process_attendees_form(self, event, form_details):
        registrations = super()._process_attendees_form(event, form_details)

        def _norm(string):
            return (string or "").strip().casefold()

        # Ensure the event asks for a Country question before processing custom values
        has_country_q = event.question_ids.filtered(
            lambda q: _norm(getattr(q, "name", None) or getattr(q, "title", None)) == "country"
        )
        if not has_country_q:
            return registrations

        pattern = re.compile(r"attendee_(\d+)_(\d+)_country_text")
        for key, value in form_details.items():
            if not value:
                continue
            match = pattern.match(key)
            if not match:
                continue
            index = int(match.group(2))  # 1-based index
            if 0 < index <= len(registrations):
                registrations[index - 1]["country_text"] = value
        return registrations


