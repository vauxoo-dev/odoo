Minimal set of accounts to start to work in Perú.
=================================================

The usage of this CoA must refer to the official documentation on MEF.

https://www.mef.gob.pe/contenidos/conta_publ/documentac/VERSION_MODIFICADA_PCG_EMPRESARIAL.pdf
https://www.mef.gob.pe/contenidos/conta_publ/documentac/PCGE_2019.pdf

All the legal references can be found here.

http://www.sunat.gob.pe/legislacion/general/index.html

Considerations.
===============

Chart of account:
-----------------

The tree of the CoA is done using account groups, all the accounts with move
are available as groups but only the more common ones are available as actual
accounts, if you want to create a new one use the group of accounts as
reference.

# TODO: Image showing what I am talking about.

Taxes:
------

'IGV': {'name': 'VAT', 'code': 'S'},
'IVAP': {'name': 'VAT', 'code': ''},
'ISC': {'name': 'EXC', 'code': 'S'},
'ICBPER': {'name': 'OTH', 'code': ''},
'EXP': {'name': 'FRE', 'code': 'G'},
'GRA': {'name': 'FRE', 'code': 'Z'},
'EXO': {'name': 'VAT', 'code': 'E'},
'INA': {'name': 'FRE', 'code': 'O'},
'OTROS': {'name': 'OTH', 'code': 'S'},

We added on this module the 3 concepts in taxes (necessary for the EDI
signature)

# TODO: Describe new fields.

Products:
---------

Code for products to be used in the EDI are availables here, in order to decide
which tax use due to which code following this reference and python code:

https://docs.google.com/spreadsheets/d/1f1fxV8uGhA-Qz9-R1L1-dJirZ8xi3Wfg/edit#gid=662652969
