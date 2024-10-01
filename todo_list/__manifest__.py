# -*- coding: utf-8 -*-
{
    'name': "ToDo List",
    'summary': """
        Create Todo List Using Activities""",
    'description': """
        Scheduling Activities For each model  and General Activities.
            """,
    'author': 'Abrus Networks',
    'company': 'Abrus Networks',
    'maintainer': 'Abrus Networks',
    'website': "https://www.abrusnetworks.com",
    'category': 'Tools',
    'version': '12.0.1.0.0',
    'depends': ['mail','base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',

    ],
    'license': 'LGPL-3',
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
