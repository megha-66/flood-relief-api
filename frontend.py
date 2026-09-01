from nicegui import ui, app
import requests
import jwt
import os
from dotenv import load_dotenv

# ============================================================
# Configuration
# ============================================================
load_dotenv()

API_URL = "http://127.0.0.1:8000"


# ============================================================
# Authentication / Session Helpers
# ============================================================

def relief_background():
    ui.add_head_html("""
    <style>
        /* =========================================================
           FLOOD RELIEF BACKGROUND
           ========================================================= */

        html,
        body {
            margin: 0;
            min-height: 100%;
            background: #071c2b !important;
        }

        body {
            overflow-x: hidden;
        }

        /* NiceGUI root/content must sit ABOVE the background */
        .nicegui-content {
            position: relative;
            z-index: 1;
            background: transparent !important;
        }

        .q-page {
            background: transparent !important;
        }


        /* =========================================================
           BACKGROUND
           ========================================================= */

        #relief-background {
            position: fixed;
            inset: 0;

            width: 100vw;
            height: 100vh;

            z-index: 0;
            pointer-events: none;
            overflow: hidden;

            background:
                radial-gradient(
                    circle at 15% 10%,
                    rgba(54, 190, 190, 0.22),
                    transparent 30%
                ),
                radial-gradient(
                    circle at 85% 20%,
                    rgba(58, 125, 190, 0.22),
                    transparent 30%
                ),
                radial-gradient(
                    circle at 50% 100%,
                    rgba(255, 190, 110, 0.13),
                    transparent 40%
                ),
                linear-gradient(
                    145deg,
                    #061522 0%,
                    #082b3d 48%,
                    #0b5364 100%
                );
        }


        /* =========================================================
           ATMOSPHERIC GLOW
           ========================================================= */

        .relief-glow {
            position: absolute;

            width: 700px;
            height: 700px;

            border-radius: 50%;

            background:
                radial-gradient(
                    circle,
                    rgba(82, 220, 207, 0.28) 0%,
                    rgba(82, 220, 207, 0.12) 35%,
                    transparent 70%
                );

            filter: blur(35px);

            animation: glowFloat 16s ease-in-out infinite alternate;
        }

        .relief-glow.one {
            top: -250px;
            left: -180px;
        }

        .relief-glow.two {
            top: 80px;
            right: -280px;

            animation-delay: -6s;

            background:
                radial-gradient(
                    circle,
                    rgba(85, 155, 230, 0.25) 0%,
                    rgba(85, 155, 230, 0.10) 40%,
                    transparent 70%
                );
        }

        @keyframes glowFloat {
            0% {
                transform: translate(0, 0) scale(1);
            }

            100% {
                transform: translate(70px, 50px) scale(1.12);
            }
        }


        /* =========================================================
           RAIN
           ========================================================= */

        .rain {
            position: absolute;
            inset: 0;

            z-index: 5;

            overflow: hidden;

            opacity: 1;
        }

        .raindrop {
            position: absolute;

            top: -100px;

            width: 2px;
            height: 65px;

            border-radius: 50%;

            background: linear-gradient(
                to bottom,
                rgba(255,255,255,0),
                rgba(210,245,255,0.9)
            );

            box-shadow:
                0 0 4px rgba(180,230,255,0.35);

            animation-name: rainfall;
            animation-timing-function: linear;
            animation-iteration-count: infinite;
        }

        @keyframes rainfall {
            0% {
                transform: translate3d(0, -100px, 0);
            }

            100% {
                transform: translate3d(-90px, 115vh, 0);
            }
        }


/* =========================================================
   WATER
   ========================================================= */

.water {
    position: absolute;

    left: -10%;
    bottom: 0;

    width: 120%;
    height: 35%;

    z-index: 10;

    overflow: hidden;

    background:
        linear-gradient(
            to top,
            rgba(2, 19, 32, 0.95),
            rgba(5, 48, 67, 0.75),
            rgba(8, 65, 82, 0.20)
        );
}


/* =========================================================
   LARGE VISIBLE WAVES
   ========================================================= */

.wave {
    position: absolute;

    left: -25%;

    width: 150%;
    height: 100px;

    border-radius: 50%;

    /* Much more visible than the previous 0.14 */
    border-top: 4px solid rgba(190, 240, 245, 0.35);

    background:
        rgba(80, 190, 200, 0.06);

    box-shadow:
        0 -8px 25px rgba(90, 210, 220, 0.16),
        inset 0 10px 20px rgba(255, 255, 255, 0.05);

    animation:
        waterWave 6s linear infinite ;
}


/* First wave */
.wave:nth-child(1) {
    bottom: 72%;

    height: 90px;

    opacity: 1;

    animation-duration: 7s;
}


/* Second wave */
.wave:nth-child(2) {
    bottom: 45%;

    height: 110px;

    opacity: 0.8;

    animation-duration: 9s;
    animation-delay: -3s;
}


/* Third wave */
.wave:nth-child(3) {
    bottom: 18%;

    height: 130px;

    opacity: 0.65;

    animation-duration: 11s;
    animation-delay: -6s;
}


/* =========================================================
   WAVE ANIMATION
   ========================================================= */

@keyframes waterWave {

      0% {
        transform:
            translateX(-12%)
            scaleY(1);
    }

    25% {
        transform:
            translateX(-4%)
            scaleY(1.06);
    }

    50% {
        transform:
            translateX(4%)
            scaleY(0.96);
    }

    75% {
        transform:
            translateX(10%)
            scaleY(1.05);
    }

    100% {
        transform:
            translateX(18%)
            scaleY(1);
    }
}

/* =========================================================
   WATER SHIMMER
   ========================================================= */

.water-shine {
    position: absolute;

    height: 2px;

    border-radius: 50%;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(210, 250, 250, 0.55),
            transparent
        );

    filter: blur(0.5px);

    animation:
        shineFlow 5s linear infinite;
}


.shine-1 {
    width: 180px;
    left: 10%;
    bottom: 35%;

    animation-duration: 5s;
}


.shine-2 {
    width: 260px;
    left: 45%;
    bottom: 55%;

    opacity: 0.7;

    animation-duration: 7s;
    animation-delay: -2s;
}


.shine-3 {
    width: 140px;
    left: 75%;
    bottom: 25%;

    opacity: 0.55;

    animation-duration: 6s;
    animation-delay: -4s;
}


@keyframes shineFlow {

    0% {
        transform: translateX(-180px);
        opacity: 0;
    }

    20% {
        opacity: 0.7;
    }

    80% {
        opacity: 0.7;
    }

    100% {
        transform: translateX(500px);
        opacity: 0;
    }
}


        /* =========================================================
           GLASSMORPHISM CARDS
           ========================================================= */

        .relief-card {
            position: relative !important;

            background:
                linear-gradient(
                    135deg,
                    rgba(255,255,255,0.14),
                    rgba(255,255,255,0.055)
                ) !important;

            border:
                1px solid rgba(255,255,255,0.20) !important;

            border-radius: 20px !important;

            box-shadow:
                0 10px 35px rgba(0,0,0,0.25),
                inset 0 1px 0 rgba(255,255,255,0.12) !important;

            backdrop-filter: blur(18px) saturate(130%) !important;
            -webkit-backdrop-filter: blur(18px) saturate(130%) !important;

            overflow: hidden !important;
        }

        /* Glass highlight */
        .relief-card::before {
            content: "";

            position: absolute;
            inset: 0;

            background:
                linear-gradient(
                    135deg,
                    rgba(255,255,255,0.10),
                    transparent 40%
                );

            pointer-events: none;
        }

        /* Make card contents stay above highlight */
        .relief-card > * {
            position: relative;
            z-index: 2;
        }

        /* Nice hover effect */
        .relief-card {
            transition:
                transform 0.25s ease,
                box-shadow 0.25s ease,
                border-color 0.25s ease;
        }

        .relief-card:hover {
            transform: translateY(-3px);

            border-color:
                rgba(255,255,255,0.32) !important;

            box-shadow:
                0 16px 45px rgba(0,0,0,0.30),
                inset 0 1px 0 rgba(255,255,255,0.16) !important;
        }


        /* =========================================================
           REDUCED MOTION
           ========================================================= */

        @media (prefers-reduced-motion: reduce) {
            .relief-glow,
            .raindrop,
            .wave,
            .relief-card {
                animation: none !important;
                transition: none !important;
            }
        }
    </style>

    <div id="relief-background">

        <div class="relief-glow one"></div>
        <div class="relief-glow two"></div>

        <div class="rain" id="relief-rain"></div>

        <div class="water">
            <div class="wave"></div>
            <div class="wave"></div>
            <div class="wave"></div>
            
             <div class="water-shine shine-1"></div>
    <div class="water-shine shine-2"></div>
    <div class="water-shine shine-3"></div>

        </div> </div>

    <script>
        const rain = document.getElementById("relief-rain");

        // More drops = more visible rain
        const dropCount = 90;

        for (let i = 0; i < dropCount; i++) {

            const drop = document.createElement("span");

            drop.className = "raindrop";

            drop.style.left =
                Math.random() * 110 + "%";

            drop.style.height =
                (35 + Math.random() * 50) + "px";

            drop.style.width =
                (1 + Math.random() * 1.5) + "px";

            drop.style.opacity =
                (0.35 + Math.random() * 0.55).toFixed(2);

            drop.style.animationDuration =
                (0.7 + Math.random() * 1.5).toFixed(2) + "s";

            drop.style.animationDelay =
                (-Math.random() * 3).toFixed(2) + "s";

            rain.appendChild(drop);
        }
    </script>
    """)



# =============================================================
# YOUR NICEGUI APP
# =============================================================

relief_background()


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
            ).classes("black-7")

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
    ).classes("text-red-7")

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
    title="Flood Relief Tracker",
    port=int(os.getenv("PORT", 8080)),
    storage_secret=os.getenv(
        "STORAGE_SECRET",
        "development-secret"
    )
)
