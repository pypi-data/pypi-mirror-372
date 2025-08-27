# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class BackendMixin(models.AbstractModel):
    _name = "backend_mixin"
    _inherit = ["mixin.master_data"]
    _description = "Mixin for Backend"

    _backend_company_field = ""
    _automatically_insert_print_button = False

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self._default_company_id(),
        copy=True,
    )

    code = fields.Char(
        default="/",
    )

    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("running", "Running"),
        ],
        copy=False,
        default="draft",
        required=True,
        readonly=True,
    )

    def _check_company_backend_field(self):
        self.ensure_one()
        result = False
        company_fields = self.env.user.company_id._fields
        backend_field = self._backend_company_field

        if backend_field in company_fields:
            result = True
        return result

    def action_running(self):
        for record in self:
            if record._check_company_backend_field():
                check_running_backend_ids = self.search(
                    [
                        ("state", "=", "running"),
                        ("company_id", "=", self.env.user.company_id.id),
                        ("id", "!=", record.id),
                    ]
                )
                if check_running_backend_ids:
                    check_running_backend_ids.write({"state": "draft"})
                setattr(
                    self.env.user.company_id,
                    self._backend_company_field,
                    record.id,
                )
                record.write({"state": "running"})

    def action_restart(self):
        for record in self:
            if record._check_company_backend_field():
                setattr(
                    self.env.user.company_id,
                    self._backend_company_field,
                    False,
                )
                record.write({"state": "draft"})
