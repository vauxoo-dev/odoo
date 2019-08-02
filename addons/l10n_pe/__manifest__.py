# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Peru - Accounting',
    "version": "2.0",
    'summary': "PCGE Simplified",
    'category': 'Localization',
    'description': """
Minimal set of accounts to start to work in Perú.
=================================================

The usage of this CoA must refer to the official documentation on MEF.

https://www.mef.gob.pe/contenidos/conta_publ/documentac/VERSION_MODIFICADA_PCG_EMPRESARIAL.pdf
    """,
    'author': 'Vauxoo, Odoo',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'base_vat',
        'base_address_extended',
        'base_address_city',
        'l10n_latam_base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/account_types.xml',
        'data/l10n_pe_chart_data.xml',
        'data/account.group.csv',
        'data/account.account.template.csv',
        'data/l10n_pe_chart_post_data.xml',
        'data/account_tax_data.xml',
        'data/account_chart_template_data.xml',
        'data/res.city.csv',
        'data/l10n_pe.res.city.district.csv',
        'data/res_country_data.xml',
        'data/l10n_latam_identification_type_data.xml',
        'views/res_partner_view.xml',
    ],
}
