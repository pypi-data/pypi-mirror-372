# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


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
