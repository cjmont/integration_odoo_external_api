from odoo import models, fields, api


class MNMBResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'
	
	mnmb_mybusiness_url = fields.Char(string='My Business URL', config_parameter='mybusiness.mnmb_mybusiness_url')
	
	# set values in database
	def set_values(self):
		res = super(MNMBResConfigSettings, self).set_values()
		self.env['ir.config_parameter'].sudo().set_param('mybusiness.mnmb_mybusiness_url', self.mnmb_mybusiness_url)
		
		return res
	
	# load values from database
	@api.model
	def get_values(self):
		res = super(MNMBResConfigSettings, self).get_values()
		res.update(
			mnmb_mybusiness_url=self.env['ir.config_parameter'].sudo().get_param('mybusiness.mnmb_mybusiness_url'),
		)
		return res
		