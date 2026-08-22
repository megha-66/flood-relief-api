from nicegui import ui, app
import requests
import jwt
import os
from dotenv import load_dotenv

# ============================================================
# Configuration
# ============================================================
load_dotenv()

API_URL = os.getenv("API_URL","http://127.0.0.1:8000")


# ============================================================
# Authentication / Session Helpers
# ============================================================

def get_token():
    return app.storage.user.get("access_token")


def get_current_role():
    return app.storage.user.get("role")


def auth_headers():
    token = get_token()

    if not token:
        return {}

    return {
        "Authorization": f"Bearer {token}"
    }


# ============================================================
# Response Helper
# ============================================================

def show_response(response):
    try:
        data = response.json()
    except Exception:
        data = response.text

    if response.ok:
        if isinstance(data, dict):
            message = data.get("message", "Operation successful")
        else:
            message = str(data)

        ui.notify(message, type="positive")

    else:
        if isinstance(data, dict):
            message = data.get("detail", "Something went wrong")
        else:
            message = str(data)

        ui.notify(
            f"Error {response.status_code}: {message}",
            type="negative"
        )


# ============================================================
# Authentication
# ============================================================

def register_user():
    email = register_email.value.strip()
    password = register_password.value
    role = register_role.value

    if not email or not password or not role:
        ui.notify(
            "Please fill all registration fields.",
            type="warning"
        )
        return

    payload = {
        "email": email,
        "password": password,
        "role": role
    }

    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json=payload,
            timeout=10
        )

        show_response(response)

        if response.status_code == 201:
            register_email.value = ""
            register_password.value = ""

    except requests.exceptions.RequestException as e:
        ui.notify(
            f"Could not connect to API: {e}",
            type="negative"
        )


def login_user():
    email = login_email.value.strip()
    password = login_password.value

    if not email or not password:
        ui.notify(
            "Please enter email and password.",
            type="warning"
        )
        return

    # IMPORTANT:
    # OAuth2PasswordRequestForm expects form data,
    # not JSON.
    form_data = {
        "username": email,
        "password": password
    }

    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            data=form_data,
            timeout=10
        )

        if response.status_code != 200:
            show_response(response)
            return

        data = response.json()

        token = data.get("access_token")

        if not token:
            ui.notify(
                "No access token received.",
                type="negative"
            )
            return

        # Store JWT in browser session
        app.storage.user["access_token"] = token

        # Decode JWT only to determine what UI to show.
        # The backend is still responsible for authorization.
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False}
            )

            role = payload.get("role")

            # Depending on PyJWT/SQLAlchemy enum representation
            role = str(role)

            # Normalize RoleEnum.CAMP_COORDINATOR
            if "CAMP_COORDINATOR" in role:
                role = "CAMP_COORDINATOR"

            elif "DONOR" in role:
                role = "DONOR"

            app.storage.user["role"] = role

        except Exception:
            app.storage.user["role"] = ""

        login_status.refresh()
        coordinator_section.refresh()

        ui.notify(
            "Login successful!",
            type="positive"
        )

    except requests.exceptions.RequestException as e:
        ui.notify(
            f"Could not connect to API: {e}",
            type="negative"
        )


def logout():
    
    # Clear login fields
    login_email.value = ""
    login_password.value = ""

    app.storage.user.clear()

    login_status.refresh()
    coordinator_section.refresh()

    ui.notify(
        "Logged out successfully.",
        type="positive"
    )


# ============================================================
# Camp
# ============================================================

def create_camp():
    if not get_token():
        ui.notify(
            "Please login first.",
            type="warning"
        )
        return

    payload = {
        "name": camp_name.value.strip(),
        "district": camp_district.value.strip(),
        "contact_person": camp_contact.value.strip()
    }

    if not all(payload.values()):
        ui.notify(
            "Please fill all camp fields.",
            type="warning"
        )
        return

    try:
        response = requests.post(
            f"{API_URL}/camps/",
            json=payload,
            headers=auth_headers(),
            timeout=10
        )

        show_response(response)

        if response.status_code == 201:
            camp_name.value = ""
            camp_district.value = ""
            camp_contact.value = ""

    except requests.exceptions.RequestException as e:
        ui.notify(
            f"Could not connect to API: {e}",
            type="negative"
        )


# ============================================================
# Inventory
# ============================================================

def add_inventory():
    if not get_token():
        ui.notify(
            "Please login first.",
            type="warning"
        )
        return

    try:
        camp_id = int(inventory_camp_id.value)
        required_quantity = int(inventory_required_quantity.value)

    except (TypeError, ValueError):
        ui.notify(
            "Camp ID and required quantity must be numbers.",
            type="warning"
        )
        return

    item_name = inventory_item_name.value.strip()
    unit = inventory_unit.value.strip()

    if not item_name or not unit:
        ui.notify(
            "Please enter item name and unit.",
            type="warning"
        )
        return

    payload = {
        "camp_id": camp_id,
        "item_name": item_name,
        "unit": unit,
        "required_quantity": required_quantity
    }

    try:
        response = requests.post(
            f"{API_URL}/inventory/",
            json=payload,
            headers=auth_headers(),
            timeout=10
        )

        show_response(response)

        if response.status_code == 201:
            inventory_item_name.value = ""
            inventory_unit.value = ""
            inventory_required_quantity.value = ""

    except requests.exceptions.RequestException as e:
        ui.notify(
            f"Could not connect to API: {e}",
            type="negative"
        )


# ============================================================
# Donation
# ============================================================


def load_inventory():
    global inventory_data
    try:
        response = requests.get(
            f"{API_URL}/inventory/",
            timeout=10
        )

        if not response.ok:
            show_response(response)
            return

        data = response.json()

        # Build dropdown options:
        # {item_id: "Item Name (Unit)"}
        choices = {}

        for item in data:
            item_id = item.get("id")
            item_name = item.get("item_name")
            unit = item.get("unit")

            choices[item_id] = f"{item_name} ({unit})"

        pledge_item_select.options = choices
        pledge_item_select.update()

        # Clear previous selection
        pledge_item_select.value = None
        pledge_unit.value = None
        

        ui.notify(
            f"Loaded {len(data)} inventory items.",
            type="positive"
        )

    except requests.exceptions.RequestException as e:
        ui.notify(
            f"Could not connect to API: {e}",
            type="negative"
        )

def inventory_item_selected(event):

    selected_id = event.value

    if not selected_id:
        pledge_unit.value = None
        return

    try:
        response = requests.get(
            f"{API_URL}/inventory/",
            timeout=10
        )

        if not response.ok:
            show_response(response)
            return

        data = response.json()

        for item in data:

            if str(item.get("id")) == str(selected_id):

                pledge_unit.value = item.get("unit", "")
                return

        pledge_unit.value = None

    except requests.exceptions.RequestException as e:
        ui.notify(
            f"Could not connect to API: {e}",
            type="negative"
        )


def pledge_donation():
    if not get_token():
        ui.notify(
            "Please login first.",
            type="warning"
        )
        return

    # --------------------------------------------------------
    # Check selected item
    # --------------------------------------------------------

    selected_item = pledge_item_select.value

    if selected_item is None or selected_item == "":
        ui.notify(
            "Please select an inventory item.",
            type="warning"
        )
        return

    # --------------------------------------------------------
    # Check quantity
    # --------------------------------------------------------

    quantity_value = pledge_quantity.value

    if quantity_value is None or quantity_value == "":
        ui.notify(
            "Please enter a quantity.",
            type="warning"
        )
        return

    try:
        item_id = int(selected_item)
        quantity = int(quantity_value)

    except (TypeError, ValueError):
        ui.notify(
            "Please select a valid item and enter a valid quantity.",
            type="warning"
        )
        return

    if quantity <= 0:
        ui.notify(
            "Quantity must be greater than zero.",
            type="warning"
        )
        return

    # --------------------------------------------------------
    # Send pledge request
    # --------------------------------------------------------

    try:

        response = requests.patch(
            f"{API_URL}/inventory/{item_id}/pledge",
            params={
                "quantity": quantity
            },
            headers=auth_headers(),
            timeout=10
        )

        if response.status_code == 200:

            # Clear quantity.
            # IMPORTANT: ui.number expects None, not "".
            pledge_quantity.value = None

            ui.notify(
                "Thanks for your donation!",
                type="positive",
                position="top"
            )


        else:
            show_response(response)

    except requests.exceptions.RequestException as e:

        ui.notify(
            f"Could not connect to API: {e}",
            type="negative"
        )

# ============================================================
# Analytics
# ============================================================

def load_analytics():
    try:
        response = requests.get(
            f"{API_URL}/analytics/district-shortages",
            timeout=10
        )

        if not response.ok:
            show_response(response)
            return

        data = response.json()

        rows = []

        for item in data:
            rows.append({
                "district": item.get("district"),
                "item": item.get("item"),
                "unit": item.get("unit"),
                "shortage_quantity": item.get("shortage_quantity")
            })

        analytics_table.rows = rows
        analytics_table.update()

        ui.notify(
            f"Loaded {len(rows)} shortage records.",
            type="positive"
        )

    except requests.exceptions.RequestException as e:
        ui.notify(
            f"Could not connect to API: {e}",
            type="negative"
        )


# ============================================================
# Refreshable UI Components
# ============================================================

@ui.refreshable
def login_status():
    token = get_token()
    role = get_current_role()

    if token:
        ui.label(
            f"Logged in • {role}"
        ).classes("text-white")

    else:
        ui.label(
            "Not logged in"
        ).classes("text-white")


@ui.refreshable
def coordinator_section():

    role = get_current_role()

    if role != "CAMP_COORDINATOR":

        with ui.card().classes(
            "w-full max-w-5xl mx-auto mt-6"
        ):
            ui.label(
                "Login as CAMP_COORDINATOR to create "
                "relief camps and inventory requirements."
            ).classes("text-grey-7")

        return

    # --------------------------------------------------------
    # Create Relief Camp
    # --------------------------------------------------------

    with ui.card().classes(
        "w-full max-w-5xl mx-auto mt-6"
    ):

        ui.label(
            "Create Relief Camp"
        ).classes("text-h5")

        camp_name = ui.input(
            "Camp Name"
        ).classes("w-full")

        camp_district = ui.input(
            "District"
        ).classes("w-full")

        camp_contact = ui.input(
            "Contact Person"
        ).classes("w-full")

        ui.button(
            "Create Camp",
            on_click=lambda: create_camp_from_values(
                camp_name,
                camp_district,
                camp_contact
            ),
            icon="add_location"
        )

    # --------------------------------------------------------
    # Add Inventory Requirement
    # --------------------------------------------------------

    with ui.card().classes(
        "w-full max-w-5xl mx-auto mt-6"
    ):

        ui.label(
            "Add Resource Requirement"
        ).classes("text-h5")

        inventory_camp_id = ui.number(
            "Camp ID",
            min=1,
            precision=0
        ).classes("w-full")

        inventory_item_name = ui.input(
            "Item Name"
        ).classes("w-full")

        inventory_unit = ui.input(
            "Unit",
            placeholder="e.g. kg, litres, pieces"
        ).classes("w-full")

        inventory_required_quantity = ui.number(
            "Required Quantity",
            min=1,
            precision=0
        ).classes("w-full")

        ui.button(
            "Add Inventory Requirement",
            on_click=lambda: add_inventory_from_values(
                inventory_camp_id,
                inventory_item_name,
                inventory_unit,
                inventory_required_quantity
            ),
            icon="inventory"
        )


# ============================================================
# Versions of functions that receive UI components
# ============================================================

def create_camp_from_values(
    name_field,
    district_field,
    contact_field
):

    if not get_token():
        ui.notify(
            "Please login first.",
            type="warning"
        )
        return

    payload = {
        "name": name_field.value.strip(),
        "district": district_field.value.strip(),
        "contact_person": contact_field.value.strip()
    }

    if not all(payload.values()):
        ui.notify(
            "Please fill all camp fields.",
            type="warning"
        )
        return

    try:

        response = requests.post(
            f"{API_URL}/camps/",
            json=payload,
            headers=auth_headers(),
            timeout=10
        )

        show_response(response)

        if response.status_code == 201:
            name_field.value = ""
            district_field.value = ""
            contact_field.value = ""

    except requests.exceptions.RequestException as e:

        ui.notify(
            f"Could not connect to API: {e}",
            type="negative"
        )


def add_inventory_from_values(
    camp_id_field,
    item_name_field,
    unit_field,
    quantity_field
):

    if not get_token():
        ui.notify(
            "Please login first.",
            type="warning"
        )
        return

    try:
        camp_id = int(camp_id_field.value)
        quantity = int(quantity_field.value)

    except (TypeError, ValueError):

        ui.notify(
            "Camp ID and quantity must be numbers.",
            type="warning"
        )
        return

    item_name = item_name_field.value.strip()
    unit = unit_field.value.strip()

    if not item_name or not unit:

        ui.notify(
            "Please enter item name and unit.",
            type="warning"
        )
        return

    payload = {
        "camp_id": camp_id,
        "item_name": item_name,
        "unit": unit,
        "required_quantity": quantity
    }

    try:

        response = requests.post(
            f"{API_URL}/inventory/",
            json=payload,
            headers=auth_headers(),
            timeout=10
        )

        show_response(response)

        if response.status_code == 201:

            item_name_field.value = ""
            unit_field.value = ""
            quantity_field.value = ""

    except requests.exceptions.RequestException as e:

        ui.notify(
            f"Could not connect to API: {e}",
            type="negative"
        )


# ============================================================
# HEADER
# ============================================================

with ui.header().classes(
    "items-center justify-between"
):

    ui.label(
        "Flood Relief Resource & Donation Tracker"
    ).classes("text-h5")

    with ui.row().classes("items-center"):

        login_status()

        ui.button(
            "Logout",
            on_click=logout,
            icon="logout"
        ).props("flat color=white")


# ============================================================
# AUTHENTICATION UI
# ============================================================

with ui.card().classes(
    "w-full max-w-3xl mx-auto mt-6"
):

    ui.label(
        "Authentication"
    ).classes("text-h5")

    with ui.tabs().classes("w-full") as auth_tabs:

        login_tab = ui.tab("Login")
        register_tab = ui.tab("Register")

    with ui.tab_panels(
        auth_tabs,
        value=login_tab
    ).classes("w-full"):

        # ----------------------------------------------------
        # LOGIN
        # ----------------------------------------------------

        with ui.tab_panel(login_tab):

            ui.label(
                "Login"
            ).classes("text-h6")

            login_email = ui.input(
                "Email"
            ).classes("w-full")

            login_password = ui.input(
                "Password",
                password=True,
                password_toggle_button=True
            ).classes("w-full")

            ui.button(
                "Login",
                on_click=login_user,
                icon="login"
            )

        # ----------------------------------------------------
        # REGISTER
        # ----------------------------------------------------

        with ui.tab_panel(register_tab):

            ui.label(
                "Create Account"
            ).classes("text-h6")

            register_email = ui.input(
                "Email"
            ).classes("w-full")

            register_password = ui.input(
                "Password (8-72 characters)",
                password=True,
                password_toggle_button=True
            ).classes("w-full")

            register_role = ui.select(
                {
                    "DONOR": "Donor",
                    "CAMP_COORDINATOR": "Camp Coordinator"
                },
                label="Role"
            ).classes("w-full")

            register_role.value = "DONOR"

            ui.button(
                "Register",
                on_click=register_user,
                icon="person_add"
            )


# ============================================================
# COORDINATOR UI
# ============================================================

coordinator_section()

# ============================================================
# DONATION UI
# ============================================================

with ui.card().classes(
    "w-full max-w-5xl mx-auto mt-6"
):

    ui.label(
        "Pledge Donation"
    ).classes("text-h5")

    ui.label(
        "Select a resource from the current inventory requirements."
    ).classes("text-grey-7")

    # --------------------------------------------------------
    # Get Inventory
    # --------------------------------------------------------

    ui.button(
        "Get Inventory",
        on_click=load_inventory,
        icon="inventory_2"
    ).props("outline")

    # --------------------------------------------------------
    # Item Selection
    # --------------------------------------------------------

    pledge_item_select = ui.select(
        options={},
        label="Select Item"
    ).classes("w-full")

    pledge_item_select.on_value_change(
        inventory_item_selected
    )

    # --------------------------------------------------------
    # Unit
    # --------------------------------------------------------

    pledge_unit = ui.input(
        "Unit"
    ).props("readonly").classes("w-full")

    # --------------------------------------------------------
    # Quantity
    # --------------------------------------------------------

    pledge_quantity = ui.number(
        "Quantity to Pledge",
        min=1,
        precision=0
    ).classes("w-full")

    # --------------------------------------------------------
    # Pledge
    # --------------------------------------------------------

    ui.button(
        "Pledge Donation",
        on_click=pledge_donation,
        icon="volunteer_activism"
    )

# ============================================================
# ANALYTICS UI
# ============================================================

with ui.card().classes(
    "w-full max-w-5xl mx-auto mt-6 mb-10"
):

    with ui.row().classes(
        "items-center justify-between w-full"
    ):

        ui.label(
            "District Shortages"
        ).classes("text-h5")

        ui.button(
            "Refresh Analytics",
            on_click=load_analytics,
            icon="refresh"
        )

    columns = [
        {
            "name": "district",
            "label": "District",
            "field": "district",
            "align": "left"
        },
        {
            "name": "item",
            "label": "Item",
            "field": "item",
            "align": "left"
        },
        {
            "name": "unit",
            "label": "Unit",
            "field": "unit",
            "align": "left"
        },
        {
            "name": "shortage_quantity",
            "label": "Shortage",
            "field": "shortage_quantity",
            "align": "right"
        }
    ]

    analytics_table = ui.table(
        columns=columns,
        rows=[],
        row_key="district"
    ).classes("w-full")


# ============================================================
# START NICEGUI
# ============================================================

ui.run(
    title="Flood Relief Resource Tracker",
    port=int(os.getenv("PORT", 8080)),
    storage_secret=os.getenv(
        "STORAGE_SECRET",
        "development-secret"
    )
)
