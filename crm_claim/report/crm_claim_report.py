# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools


class CrmClaimReport(models.AbstractModel):
    _name = 'report.crm_claim.pdf'
    _description = 'Crm Claim Report'

    code = fields.Char(
        string='Name',
        readonly=True
    )
    description = fields.Text(
        readonly=True
    )
    resolution = fields.Text(
        readonly=True
    )
    date_closed = fields.Datetime(
        string='Date closed',
        readonly=True
    )
    date = fields.Datetime(
        string='Date',
        readonly=True
    )
    categ_id = fields.Many2one(
        comodel_name='crm.claim.category',
        string='Categ',
        readonly=True
    )
    org_id = fields.Many2one(
        comodel_name='crm.claim.origin',
        string='Org id',
        readonly=True
    )
    corrective_action = fields.Boolean(
        string="Corrective action is need?",
        readonly=True
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User',
        readonly=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        readonly=True
    )
    stage_id = fields.Many2one(
        comodel_name='crm.claim.stage',
        string='Stage',
        readonly=True
    )
    attachment_ids = fields.One2many(
        comodel_name="ir.attachment",
        inverse_name="res_id",
        compute="_compute_attachment_ids",
        readonly=True
    )

    def init(self):
        tools.drop_view_if_exists(self._cr, 'crm_claim_report')
        self._cr.execute("""
            CREATE VIEW crm_claim_report AS (
                SELECT
                min(c.id) AS id,
                c.code,
                c.description,
                c.resolution,
                c.date AS date,
                c.date_closed,
                c.corrective_action,
                c.user_id,
                c.stage_id,
                c.partner_id,
                c.org_id,
                c.categ_id,
                avg(extract('epoch' FROM (c.date_closed-c.create_date)))/(3600*24)
                AS delay_close,
                (
                    SELECT count(id)
                    FROM mail_message
                    WHERE model='crm.claim'
                    AND res_id=c.id
                ) AS email
                FROM crm_claim AS c
                GROUP BY c.id, c.code, c.date, c.date_closed, c.corrective_action,
                c.user_id, c.stage_id, c.partner_id, c.org_id, c.categ_id
            )""")

    @api.multi
    def _compute_attachment_ids(self):
        self.ensure_one()
        self.attachment_ids = self.env['ir.attachment'].search(
            [
                ('res_model', '=', 'crm.claim'),
                ('res_id', '=', self.id)
            ]
        )
        if self.attachment_ids:
            for attachment_id in self.attachment_ids:
                attachment_id.url = '/web/image/%s' % attachment_id.id
