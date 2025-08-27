from odoo import fields, models


class PartnerOTRSView(models.Model):
    _name = "partner.otrs.view"
    _auto = False

    customerid = fields.Integer(string="Customer ID", required=True)
    partner_id = fields.Integer(string="Partner ID", required=True)
    first_name = fields.Char(string="First Name", required=True)
    name = fields.Char(string="Name", required=True)
    partner_number = fields.Char(string="Partner Number", required=True)
    date_partner = fields.Date(string="Date Partner", required=True)
    date_partner_end = fields.Date(string="Date Partner End", required=True)
    active = fields.Integer(string="Active", required=True)
    birthday = fields.Date(string="Birthday", required=True)
    party_type = fields.Char(string="Party Type", required=True)
    identifier_type = fields.Char(string="Identifier Type", required=True)
    identifier_code = fields.Char(string="Identifier Code", required=True)
    email = fields.Char(string="Email", required=True)
    language = fields.Char(string="Language", required=True)
    address = fields.Char(string="Address", required=True)
    city = fields.Char(string="City", required=True)
    zip = fields.Char(string="Zip", required=True)
    country_code = fields.Char(string="Country Code", required=True)
    country = fields.Char(string="Country", required=True)
    subdivision_code = fields.Char(string="Subdivision Code", required=True)
    subdivision = fields.Char(string="Subdivision", required=True)
    has_active_contracts = fields.Integer(string="Has Active Contracts", required=True)

    def init(self):
        """The CREATE OR REPLACE VIEW statement is not working like we spect,
        to replace the view remove it before in the DB directly and then update
        the module to recreate it.
        """
        self.env.cr.execute(
            """
                CREATE OR REPLACE VIEW %s AS (%s)
            """
            % (self._table, self._query())
        )

    def _query(self):
        return """
            SELECT %s
            FROM res_partner partner
            LEFT JOIN res_country country ON partner.country_id = country.id
            LEFT JOIN res_country_state state ON partner.state_id = state.id
            LEFT JOIN cooperative_membership membership
                ON partner.id = membership.partner_id
            LEFT JOIN subscription_register sr
                ON partner.id = sr.partner_id AND sr.type = 'sell_back'
            WHERE partner.parent_id IS NULL AND
                partner.ref IS NOT NULL AND partner.customer_rank > 0
            ORDER BY partner.id
        """ % (
            self._sql_select()
        )

    def _sql_select(self):
        return """
        DISTINCT ON (partner.id)
            partner.ref AS customerid,
            partner.ref AS partner_id,
            COALESCE(partner.firstname, '-'::character varying) AS first_name,
            COALESCE(partner.lastname, '-'::character varying) AS name,
            membership.cooperator_register_number::character varying AS partner_number,
            membership.effective_date AS date_partner,
            CASE
                WHEN membership.old_member = true THEN sr.date
                ELSE NULL
            END AS date_partner_end,

            CASE
                WHEN partner.active = true THEN 1
                WHEN partner.active = false THEN 2
                ELSE NULL::integer
            END AS active,
            partner.birthdate_date AS birthday,
            CASE
                WHEN partner.is_company = true THEN 'organization'
                ELSE 'person'
            END AS party_type,
            'eu_vat' AS identifier_type,
            partner.vat AS identifier_code,
            partner.email AS email,
            CASE
                WHEN partner.lang::text = 'ca_ES'::text THEN 'ca'::character varying
                WHEN partner.lang::text = 'es_ES'::text THEN 'es'::character varying
                ELSE NULL::character varying
            END AS language,
            partner.street AS address,
            partner.city AS city,
            partner.zip AS zip,
            upper(country.code) AS country_code,
            country.name AS country,
            upper(country.code) || '-' || upper(state.code) AS subdivision_code,
            state.name AS subdivision,
            CASE
                WHEN partner.has_active_contract = true THEN 1
                WHEN partner.has_active_contract = false THEN 0
                ELSE NULL::integer
            END AS has_active_contracts
        """
