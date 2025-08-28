# miniflow/auth.py (Version simplifiée)
import requests
import time
import webbrowser
import keyring
from rich.console import Console

console = Console()

SUPABASE_URL = "https://ecgcwomzrfldosjzvcxf.supabase.co/functions/v1"
SERVICE_NAME = "miniflow-cli"


def handle_login():
    """Orchestrates the device authorization flow."""
    try:
        resp = requests.post(f"{SUPABASE_URL}/device-auth")
        resp.raise_for_status()
        auth_data = resp.json()

        user_code = auth_data["user_code"]
        verification_uri = auth_data["verification_uri_complete"]
        device_code = auth_data["device_code"]
        interval = auth_data["interval"]
        expires_in = auth_data.get("expires_in", 600)

        console.print("Action required")
        console.print(f"To connect, please use this code : {user_code}")
        console.print(f"Open this link in your browser : {verification_uri}")

        webbrowser.open(verification_uri)

        with console.status("Waiting for authorization in the browser...", spinner="dots"):
            start_time = time.time()
            while time.time() - start_time < expires_in:
                time.sleep(interval)

                token_resp = requests.post(
                    f"{SUPABASE_URL}/device-token", json={"device_code": device_code}
                )

                if token_resp.status_code == 200:
                    token_data = token_resp.json()
                    access_token = token_data["access_token"]

                    keyring.set_password(SERVICE_NAME, "user", access_token)
                    console.print("\nAuthentication successful !")
                    return

                error_data = token_resp.json()
                if error_data.get("error") != "authorization_pending":
                    error_desc = error_data.get("error_description", "Unknown error")
                    raise Exception(f"Authentication error : {error_desc}")

            raise Exception("Timeout : The authorization has expired. Please try again.")

    except requests.RequestException as e:
        console.print(f"Connection error : {e}")
    except Exception as e:
        console.print(f"An error occurred : {e}")


def get_token():
    """Get the token from the keyring."""
    return keyring.get_password(SERVICE_NAME, "user")


def handle_logout():
    """Remove the token from the keyring."""
    try:
        token = get_token()
        if not token:
            console.print("No active session to disconnect.")
            return

        keyring.delete_password(SERVICE_NAME, "user")
        console.print("You have been disconnected.")
    except Exception as e:
        console.print(f"An error occurred : {e}")


def get_user_status():
    """Check the token and display user information."""
    token = get_token()
    if not token:
        console.print("You are not connected. Use 'miniflow login' to connect.")
        return

    with console.status("Checking status..."):
        try:
            headers = {"Authorization": f"Bearer {token}"}
            resp = requests.get(f"{SUPABASE_URL}/cli-validate-token", headers=headers)

            if resp.status_code == 401:
                console.print("Your session has expired. Please reconnect with 'miniflow login'.")
                return

            resp.raise_for_status()
            user_data = resp.json()

            if user_data.get("valid"):
                profile = user_data.get("user_profile")
                display_name = profile.get("display_name", "N/A") if profile else "N/A"
                console.print(f"Connected as : {display_name} (ID: {user_data['user_id']})")
            else:
                console.print("Token invalid.")

        except requests.RequestException as e:
            console.print(f"Connection error : {e}")
