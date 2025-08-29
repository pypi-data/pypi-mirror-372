# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    telegram_backend_id = fields.Many2one(
        string="Active Telegram Backend",
        comodel_name="telegram_backend",
        domain="[('state', '=', 'running')]",
    )
