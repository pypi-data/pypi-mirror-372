from __future__ import annotations

import json
import os
import secrets
import sqlite3
import traceback
from pathlib import Path
from typing import TYPE_CHECKING

import requests
import sqlite_vec
from pydantic import BaseModel

if TYPE_CHECKING:
    from toolbox.installed_mcp import InstalledMCP
import time

from toolbox.external_dependencies.external_depenencies import (
    screenpipe_installed,
    syftbox_installed,
    syftbox_running,
)
from toolbox.mcp_installer.python_package_installer import install_python_mcp

HOME = Path.home()

INHERIT_SECRET_FROM_ENV = True

from typing import TYPE_CHECKING  # noqa: E402

if TYPE_CHECKING:
    from toolbox.store.installation_context import InstallationContext


class Callback(BaseModel):
    def on_install_start(self, context: InstallationContext):
        pass

    def on_input(self, context: InstallationContext):
        pass

    def on_external_dependency_check(self, context: InstallationContext):
        return {}

    def on_install_init(self, context: InstallationContext, json_body: dict):
        pass

    def on_run_mcp(self, context: InstallationContext):
        pass

    def on_external_dependency_status_check(self, mcp: "InstalledMCP"):
        pass

    def on_delete(self, mcp: "InstalledMCP"):
        pass

    def on_data_stats(self, mcp: "InstalledMCP"):
        pass


class RequestedSecret(BaseModel):
    result_name: str


class DeleteNotesMCPCallback(Callback):
    def on_delete(self, mcp: "InstalledMCP"):
        db_path = HOME / ".meeting-notes-mcp" / "db.sqlite"
        screenpipe_db_path = HOME / ".screenpipe" / "db.sqlite"
        if db_path.exists():
            print(f"Deleting {db_path}")
            db_path.unlink()
        if screenpipe_db_path.exists():
            conn = sqlite3.connect(screenpipe_db_path)
            cursor = conn.cursor()
            print("Deleting table meeting_meta from screenpipe")
            cursor.execute("DELETE FROM meeting_meta")
            print("Deleting table meeting_audio_chunks from screenpipe")
            cursor.execute("DELETE FROM meeting_audio_chunks")
            print(
                "Deleting audio_transcriptions from screenpipe where transcription_engine='syftbox-whisper-v3-large'"
            )
            cursor.execute(
                "DELETE FROM audio_transcriptions where transcription_engine='syftbox-whisper-v3-large'"
            )
            conn.commit()
            conn.close()


class DeleteSyftboxQueryengineMCPCallback(Callback):
    def on_delete(self, mcp: "InstalledMCP"):
        db_path = HOME / ".query-engine-mcp" / "data.db"
        if db_path.exists():
            print(f"Deleting {db_path}")
            db_path.unlink()


class TextInputEnvRequestedSecretCallback(RequestedSecret, Callback):
    request_text: str
    value: str | None = None

    def on_input(self, context: InstallationContext):
        if INHERIT_SECRET_FROM_ENV and self.result_name in os.environ:
            print(f"inheriting secret {self.result_name} from env")
            self.value = os.environ[self.result_name]
        else:
            res = input(self.request_text + "\n" + "Enter value:")
            self.value = res

    def on_install_init(self, context: InstallationContext, json_body: dict):
        if "env" not in json_body:
            json_body["env"] = {}
        json_body["env"][self.result_name] = self.value


def request_reuse(key: str) -> bool:
    reuse = input(f"Found existing {key}. Reuse? (y/n)")
    if reuse in ["y", "Y"]:
        return True
    elif reuse in ["n", "N"]:
        return False
    else:
        print("Invalid input. Please enter y or n.")
        return request_reuse(key)


class SyftboxExternalDependencyCallback(Callback):
    def on_external_dependency_check(self, context: InstallationContext):
        if not syftbox_installed():
            input(
                """
Syftbox is not installed. Please install it from https://www.syftbox.net/ and run it.
Press Enter to continue."""
            )
        elif not syftbox_running():
            input(
                """
Syftbox is not running. Please install it from https://www.syftbox.net/ and run it.
Press Enter to continue."""
            )

    def on_external_dependency_status_check(self, mcp: "InstalledMCP") -> dict:
        running = syftbox_running()
        installed = syftbox_installed()
        if running:
            return {
                "syftbox": "🟢",
            }
        elif installed:
            return {
                "syftbox": "🟠 (not running)",
            }
        else:
            return {
                "syftbox": "🔴",
            }


class NotesMCPInstallationSummaryCallback(Callback):
    def on_install_start(self, context: InstallationContext):
        orange = "\033[33m"
        end = "\033[0m"
        end_bold = "\033[21m"
        bold = "\033[1m"
        print(f"""
{orange}{bold}Installation summary:{end_bold}
This app is a background agent running on an Openmined server that transcribes audio recordings
from your laptop. This background agent does not store any recordings or transcriptions.

This app will install the following dependencies:
1. Screenpipe to make audio recordings (stored in ~/.screenpipe/db.sqlite)
2. Syftbox to receive http requests locally without opening your firewall
3. Queryengine to make screenpipe data available to the remote background agent

screenpipe: https://github.com/mediar-ai/screenpipe
syftbox: https://github.com/OpenMined/syftbox
queryengine: https://github.com/OpenMined/toolbox/tree/main/packages/syftbox_queryengine

use `toolbox list`, `toolbox show <app_name>` or `toolbox log <app_name>` to see the status of the installation.
{end}""")


class MeetingNotesMCPDataStatsCallback(Callback):
    def on_data_stats(self, mcp: "InstalledMCP") -> dict:
        try:
            query_engine_port = mcp.settings.get("SYFTBOX_QUERYENGINE_PORT", None)
            if query_engine_port is None:
                query_engine_port = mcp.settings.get("syftbox_queryengine_port", None)
                if query_engine_port is None:
                    raise ValueError("SYFTBOX_QUERYENGINE_PORT not found in settings")
            response = requests.post(
                f"http://localhost:{query_engine_port}/get_meeting_transcriptions"
            )
            response.raise_for_status()
            transcriptions = response.json()

            response = requests.post(
                f"http://localhost:{query_engine_port}/get_transcription_chunks"
            )
            response.raise_for_status()
            transcription_chunks = response.json()

            audio_chunks = requests.post(
                f"http://localhost:{query_engine_port}/get_audio_chunks"
            )
            audio_chunks.raise_for_status()
            audio_chunks = audio_chunks.json()

            return {
                "# meetings": len(transcriptions),
                "# transcribed chunks": len(transcription_chunks),
                "# audio chunks": len(audio_chunks),
            }
        except Exception as e:
            return {"error": str(e)}


def _get_slack_connection():
    slack_mcp_db_path = HOME / ".slack_mcp" / "db.sqlite"
    conn = sqlite3.connect(slack_mcp_db_path)
    conn.row_factory = sqlite3.Row

    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    return conn


def _get_discord_connection():
    discord_mcp_db_path = HOME / ".discord_mcp" / "db.sqlite"
    conn = sqlite3.connect(discord_mcp_db_path)
    conn.row_factory = sqlite3.Row

    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    return conn


def get_n_embeddings_slack(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM message_embeddings_vec")
    return cursor.fetchone()[0]


def get_n_messages_slack(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messages")
    return cursor.fetchone()[0]


def get_n_embeddings_discord(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM message_embeddings_vec")
    return cursor.fetchone()[0]


def get_n_messages_discord(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messages")
    return cursor.fetchone()[0]


class SlackMCPDataStatsCallback(Callback):
    def on_data_stats(self, mcp: "InstalledMCP") -> dict:
        try:
            conn = _get_slack_connection()
            return {
                "# embeddings": get_n_embeddings_slack(conn),
                "# messages": get_n_messages_slack(conn),
            }
        except Exception as e:
            return {"error": str(e)}


class DiscordMCPDataStatsCallback(Callback):
    def on_data_stats(self, mcp: "InstalledMCP") -> dict:
        res = {}
        try:
            conn = _get_discord_connection()
            res["# embeddings"] = get_n_embeddings_discord(conn)
        except Exception as e:
            res["error"] = str(e)

        try:
            conn = _get_discord_connection()
            res["# messages"] = get_n_messages_discord(conn)
        except Exception as e:
            res["error"] = str(e)

        return res


class ScreenpipeExternalDependencyCallback(Callback):
    def on_external_dependency_check(self, context: InstallationContext):
        if not screenpipe_installed():
            input(
                """
Screenpipe is not installed. You can install it in 2 ways:
1. By installing the screenpipe desktop app from https://web.crabnebula.cloud/mediar/screenpipe/releases
2. Run it using `curl -fsSL get.screenpi.pe/cli | sh`. or by using `screenpipe` if already installed
Press Enter to continue."""
            )

    def on_external_dependency_status_check(self, mcp: "InstalledMCP") -> dict:
        installed = screenpipe_installed()
        installed_icon = "🟢" if installed else "🔴"
        return {
            "screenpipe": installed_icon,
        }


class SyftboxAuthCallback(Callback):
    keys: list[str] = ["syftbox_email", "syftbox_access_token"]

    def on_input(self, context: InstallationContext):
        if "syftbox_email" not in context.context_dict:
            email = input("""\nFill in your syftbox email, if you already have one, enter it, if not you can regsiter by
going to http://172.172.234.167:7000/syftbox/login and get your access token (store it).
syftbox email: """)
            # TODO: maybe only have one
            context.context_dict["syftbox_email"] = email
            context.context_settings["SYFTBOX_EMAIL"] = email
        else:
            print("Found existing syftbox email and access token")

        if "syftbox_access_token" not in context.context_dict:
            access_token = secrets.token_hex(8)
            context.context_dict["syftbox_access_token"] = access_token
            context.context_settings["SYFTBOX_ACCESS_TOKEN"] = access_token

    def on_install_init(self, context: InstallationContext, json_body: dict):
        if "env" not in json_body:
            json_body["env"] = {}
        for key in self.keys:
            json_body["env"][key] = context.context_dict[key]


class RegisterNotesMCPCallback(Callback):
    def on_install_init(self, context: InstallationContext, json_body: dict):
        access_token = context.context_dict["syftbox_access_token"]
        email = context.context_dict["syftbox_email"]
        payload = {
            "email": email,
            "access_token": access_token,
        }
        try:
            url = context.context_settings["notes_webserver_url"]
            print(
                f"Registering user for NotesMCP {url} with access token {access_token[:5]}..."
            )
            response = requests.post(f"{url}/register_user", json=payload)
            response.raise_for_status()
            print(
                f"Succesfully registered account for meeting notes MCP {context.context_dict['syftbox_access_token']}"
            )

        except Exception as e:
            # print(e)
            raise Exception(
                f"Error registering user for NotesMCP, could not connect to {url}"
            ) from e


class RegisterSlackMCPCallback(Callback):
    def on_install_init(self, context: InstallationContext, json_body: dict):
        access_token = context.context_dict["syftbox_access_token"]
        email = context.context_dict["syftbox_email"]
        payload = {
            "email": email,
            "access_token": access_token,
        }
        try:
            url = context.context_settings["slack_webserver_url"]
            print(
                f"Registering user for SlackMCP {url} with access token {access_token[:5]}..."
            )
            response = requests.post(f"{url}/register_user", json=payload)
            response.raise_for_status()
            print(
                f"Succesfully registered account for meeting notes MCP {context.context_dict['syftbox_access_token']}"
            )

        except Exception as e:
            # print(e)
            raise Exception(
                f"Error registering user for SlackMCP, could not connect to {url}"
            ) from e


class RegisterNotesMCPAppHeartbeatMCPCallback(Callback):
    def on_install_init(self, context: InstallationContext, json_body: dict):
        # Check if the uvicorn server is already running
        max_retries = 10
        retry_delay = 2  # seconds
        if "SYFTBOX_QUERYENGINE_PORT" not in context.context_settings:
            raise Exception(
                "SYFTBOX_QUERYENGINE_PORT not found in context.context_settings"
            )

        port = context.context_settings["SYFTBOX_QUERYENGINE_PORT"]
        queryengine_url = f"http://localhost:{port}"
        notes_mcp_url = context.context_settings["notes_webserver_url"]
        # first wait until ready
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{queryengine_url}/healthcheck", timeout=5)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise Exception(
                        f"Server not available after {max_retries} attempts"
                    )

        try:
            response = requests.post(
                f"{queryengine_url}/register_app_healthcheck",
                json={
                    "app_name": "notes_mcp",
                    "email": context.context_dict["syftbox_email"],
                    "url": notes_mcp_url,
                },
            )
            response.raise_for_status()
        except Exception as e:
            raise Exception(
                f"Error registering user for NotesMCP, could not connect to {queryengine_url}/register_app_healthcheck {e} {traceback.format_exc()}"
            ) from e


class InstallSyftboxQueryengineMCPCallback(Callback):
    def on_run_mcp(self, context: InstallationContext):
        mcp = context.mcp
        mcp.settings["syftbox_queryengine_port"] = "8002"
        context.context_settings["SYFTBOX_QUERYENGINE_PORT"] = "8002"

        print("Install syftbox-queryengine-mcp")
        from toolbox.store.store_code import STORE_ELEMENTS

        store_element = STORE_ELEMENTS["syftbox-queryengine-mcp"]
        install_python_mcp(store_element, context)


class ObsidianFindVaultCallback(Callback):
    vault_path: Path | None = None

    def _is_valid_obsidian_vault(self, path: str) -> bool:
        """Check if path exists and has .obsidian subfolder"""
        vault_path = Path(path)
        return (
            vault_path.exists()
            and vault_path.is_dir()
            and (vault_path / ".obsidian").exists()
        )

    def _get_obsidian_vaults_from_config(self) -> dict:
        """Get vaults from obsidian.json config file"""
        obsidian_path = Path.home() / "Library/Application Support/obsidian"
        obsidian_json = obsidian_path / "obsidian.json"

        if not obsidian_json.exists():
            return {}

        try:
            config = json.loads(obsidian_json.read_text())
            return config.get("vaults", {})
        except (json.JSONDecodeError, KeyError):
            return {}

    def _select_vault_from_config(self, vaults: dict) -> str:
        """Let user select from available vaults in config"""
        vault_list = list(vaults.values())

        if len(vault_list) == 1:
            return vault_list[0]["path"]

        print("Found multiple Obsidian vaults:")
        for i, vault in enumerate(vault_list, 1):
            print(f"{i}. {vault['path']}")

        while True:
            try:
                choice = input(f"Choose a vault (1-{len(vault_list)}): ")
                idx = int(choice) - 1
                if 0 <= idx < len(vault_list):
                    return vault_list[idx]["path"]
                print(f"Please enter a number between 1 and {len(vault_list)}")
            except ValueError:
                print("Please enter a valid number")

    def _ask_user_for_vault_path(self) -> str:
        """Ask user to manually enter vault path"""
        while True:
            path = input("Enter the path to your Obsidian vault: ").strip()
            if self._is_valid_obsidian_vault(path):
                return path
            print(
                "Invalid vault path. Please ensure the path exists and contains a .obsidian folder."
            )

    def on_input(self, context: InstallationContext):
        # 1. Check for existing env var
        if "OBSIDIAN_VAULT_PATH" in os.environ:
            vault_path = os.environ["OBSIDIAN_VAULT_PATH"]
            if self._is_valid_obsidian_vault(vault_path):
                self.vault_path = Path(vault_path).resolve()
                print(f"Using Obsidian vault from environment: {self.vault_path}")
                return
            else:
                print(
                    f"Environment variable OBSIDIAN_VAULT_PATH points to invalid vault: {vault_path}"
                )

        # 2. Check obsidian.json config
        vaults = self._get_obsidian_vaults_from_config()
        if vaults:
            vault_path = self._select_vault_from_config(vaults)
            if self._is_valid_obsidian_vault(vault_path):
                self.vault_path = Path(vault_path).resolve()
                return
            else:
                print(f"Selected vault path is invalid: {vault_path}")

        # 3. Ask user for manual input
        vault_path = self._ask_user_for_vault_path()
        self.vault_path = Path(vault_path).resolve()

    def on_install_init(self, context: InstallationContext, json_body: dict):
        if "env" not in json_body:
            json_body["env"] = {}
        if self.vault_path is None:
            raise ValueError("Vault path was not set during input phase")
        json_body["env"]["OBSIDIAN_VAULT_PATH"] = str(self.vault_path)
        context.context_settings["OBSIDIAN_VAULT_PATH"] = str(self.vault_path)

    def on_run_mcp(self, context: "InstallationContext"):
        from toolbox.store.store_code import STORE_ELEMENTS

        store_element = STORE_ELEMENTS["obsidian-mcp"]
        install_python_mcp(store_element, context)
