# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.osv import expression


class TelegramBackendChat(models.Model):
    _name = "telegram_backend_chat"
    _description = "List of telegram Chat ID"
    _order = "backend_id"

    backend_id = fields.Many2one(
        string="Backend",
        comodel_name="telegram_backend",
        required=True,
        copy=False,
    )
    name = fields.Char(
        string="Chat ID",
        required=True,
    )
    username = fields.Char(
        string="Username",
        required=False,
    )
    description = fields.Text(
        string="Description",
        required=True,
        default="/",
    )

    def name_get(self):
        result = []
        for record in self:
            name = "[%s] %s" % (
                record.description,
                record.name,
            )
            result.append([record.id, name])
        return result

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        if operator in ("ilike", "like", "=", "=like", "=ilike"):
            args = expression.AND(
                [
                    args or [],
                    ["|", ("description", operator, name), ("name", operator, name)],
                ]
            )
            return self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return super(TelegramBackendChat, self)._name_search(
            name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid
        )
