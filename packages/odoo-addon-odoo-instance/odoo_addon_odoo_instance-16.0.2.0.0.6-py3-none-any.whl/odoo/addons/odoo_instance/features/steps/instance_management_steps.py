from behave import given, when, then
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import behave_odoo as bodoo


@given('the user is on the Odoo Instance form view')
def step_impl(context):
    bodoo.login(context)
    bodoo.switch_module(context, "odoo_instance")
    bodoo.click_button(context, "Create")


@when('the user fills in the form with valid data')
def step_impl(context):
    bodoo.set_text_field(context, "name", context.instance_name)
    bodoo.set_text_field(context, "instance_url", context.odoo_url)
    bodoo.switch_form_tab(context, "Technic")
    bodoo.set_text_field(context, "branch", "14.0")
    bodoo.set_select_field(context, "instance_type", "Test")
    bodoo.set_autocomplete_field(context, "partner_id", "AEAT")
    bodoo.set_autocomplete_field(context, "odoo_version_id", "14")


@when('the user clicks on the "Save" button')
def step_impl(context):
    bodoo.click_button(context, "Save")


@ then('a new instance should be created')
def step_impl(context):
    bodoo.ensure_readonly_mode(context)
    # Verifica que el nombre de la instancia sea el correcto buscando dentro de un div con la clase oe_title un un elemento span
    assert context.browser.find_element(
        By.XPATH, "//div[contains(@class, 'oe_title')]//span[contains(text(), '" + context.instance_name + "')]")


@when('the user clicks on the "Delete" button')
def step_impl(context):

    bodoo.click_button(context, "Action")
    bodoo.select_dropdown_item(context, "Delete")
    bodoo.click_button(context, "Ok")


@then('the instance should be deleted')
def step_impl(context):
    # navega a la lista de instancias
    bodoo.navigate_menu(context, "Instances", "Odoo 14.0 Instances")
    assert bodoo.is_tree_view_by_column_name(
        context, "Instance Name"), "Not in instances tree view"
    instances_names = bodoo.get_first_fields_from_tree_view(context)
    assert instances_names, "No instances found"
    assert context.instance_name not in instances_names, f"Instance '{context.instance_name}' still appears in instances table"
