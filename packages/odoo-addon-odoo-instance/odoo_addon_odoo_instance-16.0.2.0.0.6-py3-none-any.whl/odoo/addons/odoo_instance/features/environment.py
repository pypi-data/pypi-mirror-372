from configparser import ConfigParser
from selenium import webdriver

def before_all(context):
    config = ConfigParser()
    config.read('behave.ini')
    context.odoo_url = config.get('behave', 'odoo_url')
    context.odoo_username = config.get('behave', 'odoo_username')
    context.odoo_password = config.get('behave', 'odoo_password')
    context.instance_name = config.get('behave', 'instance_name')

def before_scenario(context, scenario):
    context.browser = webdriver.Chrome()

def after_scenario(context, scenario):
    context.browser.quit()
