# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class TelegramBackend(models.Model):
    _name = "telegram_backend"
    _inherit = ["backend_mixin"]

    _backend_company_field = "telegram_backend_id"

    send_webhook_id = fields.Many2one(
        string="Send Message API",
        comodel_name="webhook_base",
        copy=False,
        required=True,
    )

    bot_token = fields.Char(
        string="Bot Token",
        copy=False,
        required=True,
    )

    chat_ids = fields.One2many(
        string="Chat ID's",
        comodel_name="telegram_backend_chat",
        inverse_name="backend_id",
    )
