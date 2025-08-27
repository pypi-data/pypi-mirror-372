from datetime import date, datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import MissingError, ValidationError

from odoo.addons.somconnexio.helpers.date import date_to_str, first_day_next_month
from otrs_somconnexio.otrs_models.ticket_types.change_tariff_ticket import (
    ChangeTariffExceptionalTicket,
    ChangeTariffTicket,
)
from otrs_somconnexio.otrs_models.ticket_types.change_tariff_ticket_shared_bonds import (  # noqa
    ChangeTariffTicketSharedBond,
)
from otrs_somconnexio.otrs_models.ticket_types.change_tariff_ticket_mobile_pack import (
    ChangeTariffTicketMobilePack,
)


class AvailableFibers(models.TransientModel):
    # Why is a TransientModel?
    # Is a hackish solution for a cache problem.
    # We need a cache to store the information received from OTRS to avoid to call OTRS
    # API every time the wizard is loaded.
    # The default Odoo wizard load process execute many times the same methods without a
    # common context between them.
    # Using a TransientModel the vacumm remove automaticaly the old records.
    # osv_memory_count_limit: Force a limit on the maximum number of records kept in the
    # virtual osv_memory tables. The default is False, which means no count-based limit.
    # _transient_max_count = lazy_classproperty(
    #    lambda _: config.get("osv_memory_count_limit")
    # )
    # osv_memory_age_limit: Force a limit on the maximum age of records kept in the
    # virtual osv_memory tables. This is a decimal value expressed in hours,
    # and the default is 1 hour.
    # _transient_max_hours = lazy_classproperty(
    #     lambda _: config.get("osv_memory_age_limit")
    # )
    _name = "contract.mobile.tariff.change.wizard.available.fibers"

    partner_ref = fields.Char()
    fiber_contracts_ids = fields.Char()


class ContractMobileTariffChangeWizard(models.TransientModel):
    _name = "contract.mobile.tariff.change.wizard"

    contract_id = fields.Many2one("contract.contract")
    partner_id = fields.Many2one("res.partner", related="contract_id.partner_id")
    start_date = fields.Date("Start Date")
    note = fields.Char()
    current_tariff_contract_line = fields.Many2one(
        "contract.line",
        related="contract_id.current_tariff_contract_line",
    )
    current_tariff_product = fields.Many2one(
        "product.product",
        related="current_tariff_contract_line.product_id",
        string="Current Tariff",
    )
    new_tariff_product_id = fields.Many2one(
        "product.product",
        string="New tariff",
    )
    exceptional_change = fields.Boolean(default=False)
    send_notification = fields.Boolean(string="Send notification", default=False)
    otrs_checked = fields.Boolean(
        string="I have checked OTRS and no other tariff change is pending",
        default=False,
    )
    mobile_products = fields.Many2many(
        "product.product",
        compute="_compute_mobile_products",
    )
    available_products = fields.Many2many(
        "product.product",
        compute="_compute_available_products",
    )
    location = fields.Char(related="contract_id.phone_number")
    mobile_contracts_in_pack = fields.Many2many(
        comodel_name="contract.contract",
        inverse_name="id",
        string="Mobile contracts to pack",
    )
    available_fiber_contracts = fields.Many2many(
        comodel_name="contract.contract",
        inverse_name="id",
        relation="available_fiber_contracts_change_mobile_tariff_wizard_table",
    )
    fiber_contract_to_link = fields.Many2one(
        "contract.contract",
        string="To which fiber contract should be linked?",
    )
    mobile_contracts_available_to_pack = fields.Many2many(
        "contract.contract",
        compute="_compute_mobile_contracts_available_to_pack",
        default=False,
    )
    pack_options = fields.Selection(
        selection=lambda self: self._get_pack_options(),
        string="Fiber linked options",
    )
    is_pack_full = fields.Boolean(
        compute="_compute_is_pack_full",
        default=False,
    )
    phone_to_exchange = fields.Many2one(
        "contract.contract", string="Mobile contract to exchange from pack"
    )
    new_tariff_product_id_exchanged_phone = fields.Many2one(
        "product.product",
        string="New tariff for exchanged phone",
    )

    will_force_other_mobiles_to_quit_pack = fields.Boolean(
        compute="_compute_will_force_other_mobiles_to_quit_pack",
        default=False,
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults["contract_id"] = self.env.context["active_id"]
        return defaults

    def _get_pack_options(self):
        """
        Options:
        - pinya_mobile_tariff:
            if fibers without linked mobiles available
        - new_pinya_tariff_pack:
            if fibers with 300Mb without linked mobiles and mobiles unlinked
        - new_shared_bond:
            if mobiles without shared bond and fibers above 300Mb available
        - existing_pinya_pack:
            if fibers with unfilled pinya mobile pack
        - existing_shared_bond_pack:
            if fibers with unfilled sharing data mobile pack
        """

        c_id = self.env.context.get("active_id")
        contract_id = self.env["contract.contract"].browse(c_id)

        pack_options = []

        if not contract_id or contract_id.shared_bond_id or self.pack_options:
            return pack_options

        fiber_contracts_to_pack = self._get_fiber_contracts_to_pack(
            contract_id.partner_id.ref
        )

        if not fiber_contracts_to_pack:
            return pack_options

        fiber_contracts_unlinked = fiber_contracts_to_pack.filtered(
            lambda c: not c.children_pack_contract_ids
        )
        if fiber_contracts_unlinked:
            pack_options.append(
                ("pinya_mobile_tariff", _("Create new pinya")),
            )

        fiber_contracts_available_to_pack = fiber_contracts_to_pack.filtered(
            lambda c: not c.children_pack_contract_ids
            or len(c.children_pack_contract_ids) == 1
        )
        fiber_contracts_300Mb = fiber_contracts_to_pack.filtered(
            lambda c: self.env.ref("somconnexio.300Mb")
            in c.current_tariff_product.product_template_attribute_value_ids.product_attribute_value_id  # noqa
        )
        fiber_contracts_available_above_300Mb = (
            fiber_contracts_available_to_pack - fiber_contracts_300Mb
        )

        mobile_contracts = self.env["contract.contract"].search(
            [
                ("id", "!=", contract_id.id),
                ("partner_id", "=", contract_id.partner_id.id),
                (
                    "service_technology_id",
                    "=",
                    self.env.ref("somconnexio.service_technology_mobile").id,
                ),
                ("is_terminated", "=", False),
            ]
        )
        mobile_contracts_available_to_pack = mobile_contracts.filtered(
            lambda c: c.number_contracts_in_pack <= 2
        )

        if fiber_contracts_available_above_300Mb and mobile_contracts_available_to_pack:
            pack_options.append(
                ("new_shared_bond", _("Create new shared bond")),
            )

        fiber_contracts_300Mb_to_pack = (
            fiber_contracts_available_to_pack & fiber_contracts_300Mb
        )
        if fiber_contracts_300Mb_to_pack and mobile_contracts_available_to_pack:
            pack_options.append(
                ("new_pinya_tariff_pack", _("Create new 300Mb fiber pinya pack")),
            )

        fiber_contracts_already_in_pack = fiber_contracts_to_pack.filtered(
            lambda c: 1 < len(c.children_pack_contract_ids)
        )

        sharing_bond_fiber_contract_packs = fiber_contracts_already_in_pack.filtered(
            lambda c: c.children_pack_contract_ids[
                0
            ].current_tariff_product.has_sharing_data_bond
        )
        if sharing_bond_fiber_contract_packs:
            pack_options.append(
                (
                    "existing_shared_bond_pack",
                    _("Add line to existing sharing bond pack"),
                ),
            )
        if fiber_contracts_already_in_pack - sharing_bond_fiber_contract_packs:
            pack_options.append(
                (
                    "existing_pinya_pack",
                    _("Add line to existing pinya pack"),
                ),
            )
        return pack_options

    @api.depends("pack_options")
    def _compute_mobile_contracts_available_to_pack(self):
        if not self.contract_id:
            return self.env["contract.contract"]
        mobile_contracts_from_partner = self.env["contract.contract"].search(
            [
                ("id", "!=", self.contract_id.id),
                ("partner_id", "=", self.partner_id.id),
                (
                    "service_technology_id",
                    "=",
                    self.env.ref("somconnexio.service_technology_mobile").id,
                ),
                ("is_terminated", "=", False),
            ]
        )
        # Both unpacked and single linked mobiles with fibers can be packed
        self.mobile_contracts_available_to_pack = (
            mobile_contracts_from_partner.filtered(
                lambda c: not c.parent_pack_contract_id
                or len(c.parent_pack_contract_id.children_pack_contract_ids) == 1
            )
        )

    @api.depends("contract_id")
    def _compute_mobile_products(self):
        mbl_product_templates = self.env["product.template"].search(
            [
                ("categ_id", "=", self.env.ref("somconnexio.mobile_service").id),
            ]
        )
        mbl_products = self.env["product.product"].search(
            [
                ("product_tmpl_id", "in", mbl_product_templates.ids),
            ]
        )
        if self.contract_id.partner_id.is_company:
            attr_to_exclude = self.env.ref("somconnexio.ParticularExclusive")
        else:
            attr_to_exclude = self.env.ref("somconnexio.CompanyExclusive")

        self.mobile_products = mbl_products.filtered(
            lambda p: attr_to_exclude
            not in p.product_template_attribute_value_ids.product_attribute_value_id  # noqa
        )

    @api.depends("contract_id")
    def _compute_will_force_other_mobiles_to_quit_pack(self):
        """Determine whether removing this mobile contract from the pack
        will cause the pack to dissolve, forcing the other mobiles in the
        same pack to change their tariff as well"""

        if not self.contract_id.contracts_in_pack:
            self.will_force_other_mobiles_to_quit_pack = False
        mobiles_left_in_old_pack = (
            self.contract_id.contracts_in_pack
            - self.contract_id.parent_pack_contract_id
            - self.contract_id
        )
        if mobiles_left_in_old_pack and len(mobiles_left_in_old_pack) == 1:
            self.will_force_other_mobiles_to_quit_pack = True
        else:
            self.will_force_other_mobiles_to_quit_pack = False

    @api.depends("mobile_contracts_in_pack")
    def _compute_is_pack_full(self):
        if not self.mobile_contracts_in_pack:
            self.is_pack_full = False
        self.is_pack_full = bool(
            len(self.mobile_contracts_in_pack._origin - self.contract_id) == 3
        )

    @api.depends("mobile_contracts_in_pack", "pack_options")
    def _compute_available_products(self):
        """
        Filter available products according to the number of mobile contracts
        in the pack
        """

        pack_attr = self.env.ref("somconnexio.IsInPack")
        pack_2_mbl = self.env.ref("somconnexio.Pack2Mobiles")
        pack_3_mbl = self.env.ref("somconnexio.Pack3Mobiles")

        if not self.pack_options:
            self.available_products = self.mobile_products.filtered(
                lambda p: pack_attr
                not in p.product_template_attribute_value_ids.product_attribute_value_id  # noqa
            )
            return
        else:
            is_sharing_data = self.pack_options == "new_shared_bond"
            self.available_products = self.mobile_products.filtered(
                lambda p: pack_attr
                in p.product_template_attribute_value_ids.product_attribute_value_id  # noqa
                and p.has_sharing_data_bond == is_sharing_data
            )

        if not self.mobile_contracts_in_pack:
            return
        elif len(self.mobile_contracts_in_pack) == 1:
            self.available_products = self.available_products.filtered(
                lambda p: not any(
                    attr
                    in p.product_template_attribute_value_ids.product_attribute_value_id
                    for attr in [pack_2_mbl, pack_3_mbl]
                )
            )
        elif len(self.mobile_contracts_in_pack) == 2:
            self.available_products = self.available_products.filtered(
                lambda p: pack_2_mbl
                in p.product_template_attribute_value_ids.product_attribute_value_id  # noqa
            )
        elif len(self.mobile_contracts_in_pack) == 3:
            self.available_products = self.available_products.filtered(
                lambda p: pack_3_mbl
                in p.product_template_attribute_value_ids.product_attribute_value_id  # noqa
            )
        elif self.pack_options not in [
            "existing_shared_bond_pack",
            "existing_pinya_pack",
        ]:
            # Allow to have more than 3 mobiles when joining
            raise ValidationError(_("Maximum 3 mobile contracts to pack"))

    @api.onchange("fiber_contract_to_link")
    def onchange_fiber_contract_to_link(self):
        if not self.fiber_contract_to_link:
            return

        self.mobile_contracts_in_pack = self.contract_id

        if self.fiber_contract_to_link.children_pack_contract_ids:
            self.mobile_contracts_in_pack |= (
                self.fiber_contract_to_link.children_pack_contract_ids
            )

        if self.pack_options in ["existing_shared_bond_pack", "existing_pinya_pack"]:
            pack_product = self.mobile_contracts_in_pack[
                -1
            ]._origin.current_tariff_product

            if self.is_pack_full:
                self.new_tariff_product_id = pack_product
            else:
                self.new_tariff_product_id = pack_product.get_variant_with_attributes(
                    attr_to_exclude=self.env.ref("somconnexio.Pack2Mobiles"),
                    attr_to_include=self.env.ref("somconnexio.Pack3Mobiles"),
                )

    @api.onchange("pack_options")
    def onchange_pack_options(self):
        """
        Filter fibers available according to the
        selected pack option
        """
        self.fiber_contract_to_link = False
        self.mobile_contracts_in_pack = self.contract_id

        fiber_contracts_to_pack = self._get_fiber_contracts_to_pack(
            self.contract_id.partner_id.ref
        )
        if not fiber_contracts_to_pack:
            return

        fiber_contracts_unlinked = fiber_contracts_to_pack.filtered(
            lambda c: not c.children_pack_contract_ids
        )
        fiber_contracts_available_to_pack = fiber_contracts_to_pack.filtered(
            lambda c: not c.children_pack_contract_ids
            or len(c.children_pack_contract_ids) == 1
        )
        fiber_contracts_300 = fiber_contracts_to_pack.filtered(
            lambda c: self.env.ref("somconnexio.300Mb")
            in c.current_tariff_product.product_template_attribute_value_ids.product_attribute_value_id  # noqa
        )

        if self.pack_options == "pinya_mobile_tariff":
            self.available_fiber_contracts = fiber_contracts_unlinked
        elif self.pack_options == "new_pinya_tariff_pack":
            self.available_fiber_contracts = (
                fiber_contracts_300 & fiber_contracts_available_to_pack
            )
        elif self.pack_options == "new_shared_bond":
            self.available_fiber_contracts = (
                fiber_contracts_available_to_pack - fiber_contracts_300
            )
        elif self.pack_options == "existing_shared_bond_pack":
            self.available_fiber_contracts = fiber_contracts_to_pack.filtered(
                lambda c: 1 < len(c.children_pack_contract_ids)
                and c.children_pack_contract_ids[
                    0
                ].current_tariff_product.has_sharing_data_bond
            )
        elif self.pack_options == "existing_pinya_pack":
            self.available_fiber_contracts = fiber_contracts_to_pack.filtered(
                lambda c: 1 < len(c.children_pack_contract_ids)
                and not c.children_pack_contract_ids[
                    0
                ].current_tariff_product.has_sharing_data_bond
            )

    def _get_fiber_contracts_to_pack(self, partner_ref):
        """
        Check fiber contracts available to link with mobile contracts
        """

        fibers = self.env[
            "contract.mobile.tariff.change.wizard.available.fibers"
        ].search(
            [
                ("partner_ref", "=", partner_ref),
            ]
        )
        old_date = datetime.now() - timedelta(minutes=5)
        old_register = fibers and fibers.write_date <= old_date

        if not fibers or old_register:
            service = self.env["fiber.contract.to.pack.service"]
            try:
                fiber_contracts = service.create(partner_ref=partner_ref, all="true")
                fiber_contracts_ids = fiber_contracts.ids
            except MissingError:
                return
            fiber_contracts_id_list = " ".join([str(id) for id in fiber_contracts_ids])
            if not fibers:
                self.env[
                    "contract.mobile.tariff.change.wizard.available.fibers"
                ].create(
                    [
                        {
                            "partner_ref": partner_ref,
                            "fiber_contracts_ids": fiber_contracts_id_list,
                        }
                    ]
                )
            elif old_register:
                fibers.write(
                    {
                        "fiber_contracts_ids": fiber_contracts_id_list,
                    }
                )
        else:
            fiber_contracts_ids = [
                int(n) for n in fibers.fiber_contracts_ids.split(" ")
            ]

        return self.env["contract.contract"].search([("id", "in", fiber_contracts_ids)])

    def button_change(self):
        self.ensure_one()
        self._validate_otrs_checked()
        self._set_start_date()

        if self.pack_options in ["existing_shared_bond_pack", "existing_pinya_pack"]:
            # readonly attribute in the form view of "mobile_contracts_in_pack"
            # field prevents it from being passed from the front context to the
            # new back context after button_change. In here, we compute it again
            self.onchange_fiber_contract_to_link()

        self._update_mobile_contracts_in_pack()

        Ticket, fields_dict = self._prepare_ticket_data()

        Ticket(self.partner_id.vat, self.partner_id.ref, fields_dict).create()
        self._log_tariff_change()
        self._create_activity()

        if self.phone_to_exchange:
            self._create_exchanged_phone_ticket()

        return True

    def _validate_otrs_checked(self):
        """Check that no previous change tariff tickets are found in OTRS."""
        if not self.otrs_checked:
            raise ValidationError(
                _("You must check if any previous tariff change is found in OTRS")
            )

    def _set_start_date(self):
        """Set tariff change starting date (if not set) depending on:
        - excepcional tariff change: today
        - regular tariff change: first day next month.
        """
        if not self.start_date:
            self.start_date = (
                date.today() if self.exceptional_change else first_day_next_month()
            )

    def _update_mobile_contracts_in_pack(self):
        """Exclude phone to exchange from mobile contracts in pack."""
        if self.phone_to_exchange:
            self.mobile_contracts_in_pack = (
                self.mobile_contracts_in_pack - self.phone_to_exchange
            )

    def _prepare_ticket_data(self):
        """Prepare ticket data for OTRS."""
        fields_dict = {
            "phone_number": self.contract_id.phone_number,
            "new_product_code": self.new_tariff_product_id.default_code,
            "current_product_code": self.current_tariff_product.default_code,
            "subscription_email": self.contract_id.email_ids[0].email,
            "effective_date": date_to_str(self.start_date),
            "language": self.partner_id.lang,
            "fiber_linked": self.fiber_contract_to_link.code
            if self.fiber_contract_to_link
            else False,
            "send_notification": self.send_notification,
        }

        Ticket = (
            ChangeTariffExceptionalTicket
            if self.exceptional_change
            else ChangeTariffTicket
        )

        if self.pack_options == "existing_shared_bond_pack":
            fields_dict["shared_bond_id"] = self.mobile_contracts_in_pack[
                1
            ].shared_bond_id

        elif self.pack_options in ["new_shared_bond", "new_pinya_tariff_pack"]:
            self._validate_new_pack_creation()
            Ticket = self._get_ticket_class_for_new_pack()
            fields_dict["contracts"] = self._get_contracts_data_for_new_pack()

        return Ticket, fields_dict

    def _validate_new_pack_creation(self):
        """
        Check that the number of mobile contracts to be packed is correct and
        that is not an exceptional tariff change
        """
        if self.exceptional_change:
            raise ValidationError(
                _("A new pack creation cannot be an exceptional change")
            )
        elif len(self.mobile_contracts_in_pack) < 2:
            raise ValidationError(_("Another mobile is required to create a pack"))
        elif len(self.mobile_contracts_in_pack) > 3:
            raise ValidationError(_("Maximum 3 mobile contracts to pack"))

    def _get_ticket_class_for_new_pack(self):
        """Chose the OTRS ticket type depending on the pack option."""
        ticket_dct = {
            "new_shared_bond": ChangeTariffTicketSharedBond,
            "new_pinya_tariff_pack": ChangeTariffTicketMobilePack,
        }
        return ticket_dct[self.pack_options]

    def _get_contracts_data_for_new_pack(self):
        """Retorna les dades dels contractes per a un nou pack."""
        return [
            {
                "phone_number": contract.phone_number,
                "current_product_code": contract.current_tariff_product.code,
                "subscription_email": contract.email_ids[0].email,
            }
            for contract in self.mobile_contracts_in_pack
        ]

    def _log_tariff_change(self):
        """Log tariff change."""
        message = _(
            "OTRS change tariff ticket created. Tariff to be changed from '{}' to '{}' with start_date: {}"  # noqa
        )
        self.contract_id.message_post(
            message.format(
                self.current_tariff_product.showed_name,
                self.new_tariff_product_id.showed_name,
                self.start_date,
            )
        )

    def _create_exchanged_phone_ticket(self):
        """Create OTRS ticket to change the tariff of the phone leaving the pack."""
        self.phone_to_exchange._create_change_tariff_ticket(
            self.new_tariff_product_id_exchanged_phone, start_date=self.start_date
        )

    def _create_activity(self):
        self.env["mail.activity"].create(
            {
                "summary": " ".join(
                    [_("Tariff change"), self.new_tariff_product_id.showed_name]
                ),
                "res_id": self.contract_id.id,
                "res_model_id": self.env.ref("contract.model_contract_contract").id,
                "user_id": self.env.user.id,
                "activity_type_id": self.env.ref(
                    "somconnexio.mail_activity_type_tariff_change"
                ).id,  # noqa
                "done": True,
                "date_done": date.today(),
                "date_deadline": date.today(),
                "location": self.contract_id.phone_number,
                "note": self.note,
            }
        )
