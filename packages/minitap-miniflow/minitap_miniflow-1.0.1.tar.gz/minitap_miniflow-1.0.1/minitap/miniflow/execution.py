import asyncio
import websockets
import json
import requests
from rich.console import Console

from minitap.miniflow.auth import get_token, handle_login

console = Console()

# FastAPI Backend url
API_BASE_URL = "https://minitap.ai/api/v1"
WS_URL = "wss://api.minitap.ai/api/v1/playground/ws/execute-flow"

# Supabase functions url
SUPABASE_URL = "https://ecgcwomzrfldosjzvcxf.supabase.co/functions/v1"


def get_flow_data(flow_id: str, token: str):
    """Get flow data from Supabase."""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{SUPABASE_URL}/get-flow?flowId={flow_id}", headers=headers)

    if resp.status_code == 401:
        raise Exception("Invalid or expired token. Please reconnect.")
    if resp.status_code == 404:
        raise Exception("Flow not found or access denied.")
    resp.raise_for_status()

    return resp.json()["flow"]


def get_user_id(token: str) -> str:
    """Get user id from Supabase."""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{SUPABASE_URL}/cli-validate-token", headers=headers)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("valid"):
        raise Exception("Invalid token.")
    return data["user_id"]


async def execute_flow_ws(flow_data: dict, user_id: str):
    """Connect to WebSocket and handle execution."""
    uri = WS_URL
    try:
        async with websockets.connect(uri) as websocket:
            # The backend is waiting for a payload with userId
            payload = {**flow_data, "userId": user_id}
            await websocket.send(json.dumps(payload))

            while True:
                try:
                    message_str = await websocket.recv()
                    message = json.loads(message_str)

                    # Colored output with Rich
                    if message["type"] == "log":
                        level = message.get("level", "info")
                        color = (
                            "green"
                            if level == "success"
                            else "red"
                            if level == "error"
                            else "white"
                        )
                        console.print(
                            f"[bold {color}][{message.get('nodeLabel', 'Flow')}]"
                            f"[/bold {color}] {message.get('message')}"
                        )
                    elif message["type"] == "node_start":
                        console.print(f"-> [bold yellow]Executing Node ID:[/] {message['nodeId']}")
                    elif message["type"] == "error":
                        console.print(f"[bold red]Error :[/bold red] {message.get('message')}")
                        break

                except websockets.ConnectionClosed:
                    console.print("\n[bold]Execution completed.[/bold]")
                    break

    except Exception as e:
        console.print(f"[bold red]WebSocket connection error :[/bold red] {e}")


def run_flow_by_id(flow_id: str):
    """Main function to run a flow."""
    token = get_token()
    if not token:
        console.print("You are not logged in. Launching authentication...")
        handle_login()
        token = get_token()
        if not token:
            console.print("[bold red]Authentication failed. Unable to continue.[/bold red]")
            return

    try:
        with console.status("[bold green]Fetching flow and user...[/bold green]"):
            flow_data = get_flow_data(flow_id, token)
            user_id = get_user_id(token)

        asyncio.run(execute_flow_ws(flow_data, user_id))

    except Exception as e:
        console.print(f"[bold red]Flow execution error :[/bold red] {e}")
