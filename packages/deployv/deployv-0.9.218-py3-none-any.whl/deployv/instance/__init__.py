from collections import defaultdict

ODOO_BINARY = defaultdict(lambda: 'odoo-bin',
                          {
                              '7.0': 'openerp-server',
                              '8.0': 'odoo.py',
                              '9.0': 'odoo.py',
                              '10.0': 'odoo-bin',
                              'saas-14': 'odoo-bin',
                              'saas-15': 'odoo-bin',
                          })

SAAS_VERSIONS = {
    'saas-14': 'saas-14',
    'saas-15': 'saas-15',
    'saas-17': 'saas-17',
}

PSQL_VERSIONS = {
  '13.0': '11',
  '12.0': '11',
  '11.0': '9.6',
  '10.0': '9.6',
  '9.0': '9.6',
  '8.0': '9.5'
}

TRAVIS_VERSIONS = {
  '13.0': '3.6',
  '12.0': '3.6',
  '11.0': '3.5',
  '10.0': '2.7',
  '9.0': '2.7',
  '8.0': '2.7'
}
