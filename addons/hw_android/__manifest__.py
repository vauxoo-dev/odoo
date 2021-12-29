{
    'name': 'Hardware Android Driver',
    'category': 'Hidden',
    'sequence': 6,
    'author': 'Vauxoo',
    'summary': 'Add Android devices communication capabilities',
    'website': 'http://www.vauxoo.com',
    'depends': [
        'point_of_sale',
        'pos_iot',
    ],
    'license': 'LGPL-3',
    'auto_install': True,
    'data': [
        'views/pos_config_views.xml',
    ],

    'assets': {
        'point_of_sale.assets': [
            'hw_android/static/src/js/barcode_reader.js',
            'hw_android/static/src/js/models.js',
        ],
    }
}
