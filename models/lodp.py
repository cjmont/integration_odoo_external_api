from datetime import date
import re
import os
import nltk
import requests
from nltk.corpus import names
from odoo import models,  fields
import time
from odoo.http import request

def load_names_from_file(filepath):
	with open(filepath, 'r') as file:
		names = file.read().splitlines()
	return names


class MNMBLOPDPartnerMyBusiness(models.Model):
	_inherit = 'res.partner'
	
	# Calculate the absolute path to the data directory
	data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
	
	# Fields
	mnmblodp_status_code_log = fields.Integer(string='Status Code', readonly=True)
	mnmblopdp_text_log = fields.Text(string='Log', readonly=True)
	
	
	# Load names and surnames from XML
	own_names = load_names_from_file(os.path.join(data_dir, 'ec_nombres.txt'))
	own_surnames = load_names_from_file(os.path.join(data_dir, 'ec_apellidos.txt'))
	
	nltk.download('names')
	all_names = set(names.words()).union(own_names)
	all_surnames = own_surnames
	
	# Funcion para separar nombres y apellidos
	def split_name(self, fullname, all_names, all_surnames, own_names=None):
		parts = fullname.split()
		names = []
		surnames = []
		
		for part in parts:
			# Check in your combined set of names to see if a part is a known name
			if part in self.all_names:
				names.append(part)
			elif part in self.all_surnames:  # If it's not a known name, we classify it as surname
				surnames.append(part)
			else:
				if own_names is not None and part in own_names:
					names.append(part)
				else:
					surnames.append(part)
		
		# Unimos los nombres y apellidos en strings separados
		firstname = ' '.join(names)
		lastname = ' '.join(surnames)
		
		return firstname, lastname
	
	def create_fields(self):
		for record in self:
			fields_to_check = ['mnlopdp_otp']
			if any(field in record for field in fields_to_check):
				record._send_data_lodp('POST')
	
	def update_fields(self):
		for record in self:
			fields_to_check = ['mnlopdp_otp']
			if any(field in record for field in fields_to_check):
				record._send_data_lodp('PUT')
			
	
	
	def _send_data_lodp(self, method):
		
		url = request.env['res.config.settings'].sudo().get_values().get('mnmb_mybusiness_url')
		
		# Llamar a la funcion para separar nombres y apellidos
		capitalized_fullname = self.name.title()
		firstname, lastname = self.split_name(capitalized_fullname, self.all_names, self.all_surnames, self.own_names)
		
		# Obtener tipo de documento
		tipe_identi = self.env['l10n_latam.identification.type'].search(
			[('id', '=', self.l10n_latam_identification_type_id.id)])
		type_document = tipe_identi.name if tipe_identi else ''
		
		if type_document == 'RUC':
			type_document = 'R'
		elif type_document == 'Cédula':
			type_document = 'C'
		elif type_document == 'Pasaporte':
			type_document = 'P'
		
		# Obtener marca y modelo del navegador
		pattern = r'\((.*?)\)'
		matches = re.findall(pattern, self.mnlopdp_fingerprint)
		marca_modelo = matches[-1] if matches else ''
		marca, modelo = marca_modelo.split(' ', 1) if marca_modelo else ('', '')
		marca = marca.strip()
		modelo = modelo.strip()
		
		data = {
			"identificacion": str(self.vat),
			"codagencia": 0,
			"numpedido": 0,
			"codcliente": 0,
			"nombrescliente": str(firstname),
			"apellidoscliente": str(lastname),
			"tipoidentificacion": str(type_document),
			"direccioncliente": str(self.street) if str(self.street) else str(""),
			"telefonocliente": str(self.mobile),
			"emailcliente": str(self.email),
			"codempresa": "0",
			"codvendedor": "0",
			"codusuario": "-",
			"fecharegistro": str(date.today()),
			"fechacambioestado": str(date.today()) if method == 'PUT' else None,
			"fechamodificacion": str(date.today()) if method == 'PUT' else None,
			"aplicacionorigen": "lopd-odoo",
			"aplicacionversion": "1.1.1",
			"plataformaorigen": "Odoo",
			"plataformamodifica": "Odoo-Lopd" if method == 'PUT' else '',
			"marcaequipo": str(marca),
			"modeloequipo": str(modelo),
			"codestado": 52,
		}
		headers = {
			'Content-Type': 'application/json',
			'Accept': 'application/json'
		}
		
		retry_count = 0
		max_retries = 2
		timeout = 4
		
		while retry_count < max_retries:
			try:
				if method == 'POST':
					response = requests.post(url, headers=headers, json=data, verify=False, timeout=timeout)
				elif method == 'PUT':
					response = requests.put(url, headers=headers, json=data,  verify=False, timeout=timeout)
				else:
					return
				if response.status_code == 200:
					response_data = response.json()
					self.mnmblodp_status_code_log = response.status_code
					self.mnmblopdp_text_log = str(response_data)
					return
				else:
					error_response = response.text
					self.mnmblodp_status_code_log = response.status_code
					self.mnmblopdp_text_log = str(error_response)
					return
			except requests.exceptions.RequestException as e:
				self.mnmblodp_status_code_log = 0
				self.mnmblopdp_text_log = str(e)
				retry_count += 1
				time.sleep(3)  # wait 3 seconds before retrying
