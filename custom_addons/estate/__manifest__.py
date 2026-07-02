{
    'name': 'Estate',
    'version': '1.0',
    'category': 'Estate',
    'summary': 'Real Estate Management',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
    ],
    'application': True,
    'installable': True,
}