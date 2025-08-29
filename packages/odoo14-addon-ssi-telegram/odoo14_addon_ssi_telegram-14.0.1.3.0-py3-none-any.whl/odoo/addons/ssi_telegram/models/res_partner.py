# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    telegram_username = fields.Char(
        string="Telegram Username",
        help="Enter the Telegram username without '@' symbol. "
        "This will be used to identify the user in Telegram communications. "
        "Example: 'johndoe' instead of '@johndoe'",
    )
