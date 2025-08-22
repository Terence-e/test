from odoo import models, api
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
import pycountry
class ContactCentralisationMixin(models.AbstractModel):
    _name = 'contact.centralisation.mixin'
    _description = 'Automatically sync records into res.partner'

    def normalize_phone_number(self, phone, default_region='CM'):
        """
        Normalise un numéro de téléphone en format international (E.164).
        Si invalide, retourne uniquement les chiffres du numéro d'origine.

        :param phone: str - Numéro de téléphone à normaliser
        :param default_region: str - Code pays ISO (ex. 'CM' pour Cameroun)
        :return: str - Numéro normalisé ou fallback
        """
        if not phone:
            return ''

        phone = phone.strip()

        try:
            parsed = phonenumbers.parse(phone, default_region)
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except NumberParseException:
            pass

        # fallback: supprimer tout ce qui n'est pas chiffre
        return ''.join(c for c in phone if c.isdigit())

    @staticmethod
    def get_country_code(country_name):
        country = pycountry.countries.get(name=country_name)
        if not country:
            # Essaye aussi une recherche partielle
            matches = [c for c in pycountry.countries if country_name.lower() in c.name.lower()]
            if matches:
                return matches[0].alpha_2
            return None
        return country.alpha_2


    def create_contact_if_not_exist(self, values):
        """
        Crée un contact s'il n'existe pas déjà, basé sur l'email ou le numéro de téléphone (normalisé).
        :param values: dict avec les clés 'email', 'phone', 'name'
        :return: ID du partenaire (int)
        """
        email = values.get('email')
        phone_raw = values.get('phone')
        name = values.get('name')

        phone_normalized = self.normalize_phone_number(phone_raw, 'CM')
        partner_obj = self.env['res.partner'].sudo()

        # 1. Recherche par email
        partner = partner_obj.search([('email', '=', email)], limit=1)
        if partner:
            return partner.id

        # 2. Recherche par téléphone normalisé
        if phone_normalized:
            potential_partners = partner_obj.search([
                ('email', '=', False),
                '|', ('phone', '!=', False), ('mobile', '!=', False)
            ])
            for p in potential_partners:
                if (
                    self.normalize_phone_number(p.phone, 'CM') == phone_normalized
                    or self.normalize_phone_number(p.mobile, 'CM') == phone_normalized
                ):
                    return p.id

        # 3. Recherche par nom uniquement si aucun email ou téléphone n'est renseigné
        partner_by_name = partner_obj.search([
            ('email', '=', False),
            ('phone', '=', False),
            ('mobile', '=', False),
            ('name', '=', name)
        ], limit=1)
        if partner_by_name:
            return partner_by_name.id

        # 4. Création d'un nouveau partenaire
        new_partner = partner_obj.create(values)
        return new_partner.id
