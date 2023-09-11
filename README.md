# Odoo Module with External RestAPIs Integration

## Overview
This Python script is an Odoo module that adds additional functionality to the `res.partner` model for managing client information according to LOPD (Ley Orgánica de Protección de Datos) standards. The script uses the Natural Language Toolkit (NLTK) for name processing and makes HTTP requests to external services.

## Dependencies

- Python Standard Libraries: `datetime`, `re`, `os`, `time`
- Third-Party Libraries: `requests`, `nltk`
- Odoo Libraries: `models`, `fields`, `request`

## How to Install Dependencies

For nltk:
```
pip install nltk
```
For requests:
```
pip install requests
```

## Features

- Name and surname classification using both NLTK and custom data.
- Extends Odoo's `res.partner` model.
- HTTP POST and PUT methods to send data to an external API.
- Custom fields for storing status codes and logs.
- Customizable error handling with retry logic.

## Methods & Functions

### load_names_from_file(filepath)

Loads names from a given file path and returns a list of names.

### Class MNMBLOPDPartnerMyBusiness

#### Attributes

- `mnmblodp_status_code_log`: Integer field that stores HTTP status codes.
- `mnmblopdp_text_log`: Text field that stores logs or error messages.

#### Methods

- `split_name(fullname, all_names, all_surnames, own_names=None)`: Splits full name into first name and last name.
- `create_fields()`: Checks if specific fields are present and then calls `_send_data_lodp()` with 'POST'.
- `update_fields()`: Checks if specific fields are present and then calls `_send_data_lodp()` with 'PUT'.
- `_send_data_lodp(method)`: Handles the POST/PUT requests, including data preparation and error handling.

## Configuration

To use this module effectively, you should place two files `ec_nombres.txt` and `ec_apellidos.txt` containing names and surnames respectively in the module's `data` directory. 

## Usage

1. Deploy this module in your Odoo instance.
2. The module will extend the `res.partner` model.
3. Whenever specific fields like `mnlopdp_otp` are updated or created, the data will be sent to the external API configured in `res.config.settings`.

## Error Handling

The `_send_data_lodp()` function includes a retry mechanism that attempts the HTTP request up to 2 times in case of failure, with a 3-second pause between each try.

## Notes

- Always ensure the external API URL is correctly set in `res.config.settings`.
