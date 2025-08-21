# -*- coding: utf-8 -*-
{
    "name": "Project Data Gold - Settings",
    "summary": "Adds Source & Source Module settings (incl. mapping table) under Purchase settings.",
    "version": "17.0.1.0.0",
    "category": "Settings",
    "author": "You",
    "license": "LGPL-3",
    "depends": ["base", "contacts"],  # contacts needed for res.partner
    "data": [
        "security/ir.model.access.csv",   # ACL for res.config.settings.look
        "views/res_config_view.xml",      # your settings block
    ],
    "installable": True,
    "application": False,
}
