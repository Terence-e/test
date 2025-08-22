# __manifest__.py

{
    'name': 'Contact Centralisation Mixin',
    'version': '1.0',
    'summary': 'Automatically syncs any record to res.partner (Contact) using dynamic field matching.',
    'description': """
        This module provides a reusable mixin class to sync any Odoo model's fields to the Contacts (res.partner) model
        using automatic detection and dynamic field name matching.
    """,
    'author': 'Your Name',
    'category': 'Tools',
    'depends': ['base', 'contacts', 'event', 'mass_mailing', 'website'],  # 'contacts' ensures res.partner is present
    'data': [],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'application': False,
}
