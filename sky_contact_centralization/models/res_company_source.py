# -*- coding: utf-8 -*-
from odoo import models, fields

SOURCE_CHOICES = [
("outlook", "Outlook"),
("carte", "Carte"),
("site_web", "Site Web"),
("liste_de_distribution", "Liste de distribution"),
("evenement", "Événement"),

]


class SourceLine(models.Model):
    _name = "pdg.source"
    _description = "Étiquettes des contacts en fonction du module source"

    source = fields.Selection(
        selection=SOURCE_CHOICES,
        string="Source",
        required=True,
    )
    source_module = fields.Many2one(
        "ir.module.module",
        string="Module",
        domain="[('state','=','installed')]",
        help="Related Odoo module for this source.",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    source_line_ids = fields.One2many(
        "pdg.source",
        "id",   # dummy inverse (since no company_id)
        string="Source ↔ Module",
    )
