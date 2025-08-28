# -*- coding: utf-8 -*-
from odoo import models, fields, api

SOURCE_CHOICES = [
    ("outlook", "Outlook"),
    ("carte", "Carte"),
    ("site_web", "Site Web"),
    ("liste_de_distribution", "Liste de distribution"),
    ("evenement", "Événement"),
]

class SourceLine(models.Model):
    _name = "pdg.source"
    _description = "ÉTIQUETTES DES CONTACTS EN FONCTION DU MODULE SOURCE"

    company_id = fields.Many2one(
        "res.company",
        string="Société",
        required=True,
        default=lambda self: self.env.company,
        ondelete="cascade",
    )

    source = fields.Selection(
        selection=SOURCE_CHOICES,
        string="Source",
        required=True,
    )

    category_id = fields.Many2one(
        "res.partner.category",
        string="Étiquette",
        required=True,
        ondelete="restrict",
    )

    _sql_constraints = [
        ("uniq_company_source",
         "unique(company_id, source)",
         "Une seule ligne par Source et par Société est autorisée.")
    ]


class ResCompany(models.Model):
    _inherit = "res.company"

    source_line_ids = fields.One2many(
        "pdg.source",
        "company_id",                # <-- inverse CORRECT
        string="Source ↔ Module",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Expose les lignes de la société active dans les Paramètres
    source_line_ids = fields.One2many(
        related="company_id.source_line_ids",
        readonly=False,              # <-- rend le related éditable
        string="Source ↔ Module",
    )
