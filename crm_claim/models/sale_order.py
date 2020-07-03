# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
_logger = logging.getLogger(__name__)

from odoo import api, models, fields
from odoo.exceptions import Warning

class SaleOrder(models.Model):
    _inherit = 'sale.order'
                        
    claim = fields.Boolean( 
        string='Es una reposicion'
    )
    claim_id = fields.Many2one(
        comodel_name='crm.claim', 
        string='Reclamacion'
    )    
    
    @api.onchange('claim_id')
    def change_claim_id(self):
        if self.claim_id.id>0 and self.partner_id.id==0:
            self.partner_id = self.claim_id.partner_id
            
    @api.model
    def create(self, values): 
        allow_create = True
        #operations
        if 'claim' in values:
            if 'claim_id' in values:
                if values['claim']==True:
                    if values['claim_id']==False:
                        allow_create = False
                        raise Warning("Es necesario definir una reclamacion")
                    else:
                        values['name'] = self.env['ir.sequence'].next_by_code('sale.order.claim') or 'New Claim'                    
        #allow_create
        if allow_create==True:
            return super(SaleOrder, self).create(values)                        