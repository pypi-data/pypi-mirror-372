#!/usr/bin/env python3
"""
Creds Vault - Secure environment variable synchronization tool.

A command-line utility for securely sharing .env files across development teams
using GitHub Gists with client-side AES-256 encryption.
"""

import os
import sys
import json
import argparse
import base64
import secrets as crypto_secrets
import requests
import getpass
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from typing import Optional, Dict, Any
from pathlib import Path

# globals
__version__ = "1.0.1"
__author__ = "Mudassir Mira"

# Exception handlers
class EncryptionError(Exception):
    """ Encryption/Decryption Error """
    pass

class AuthenticationError(Exception):
    """ Authentication error from request or Github """
    pass

class VaultError(Exception):
    """ Raise when vault request failed """
    pass

# Encryption
class Encryptor:
    """ Handles client-side encryption and decryption of secrets """
    SALT_SIZE = 16
    ITERATIONS = 100000

    def derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm = hashes.SHA256(),
            length = 32,
            salt = salt,
            iterations = self.ITERATIONS
        )

        key = base64.urlsafe_base64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, content: str, password: str) -> str:
        """ Encrypt the content with password derived key """
        try:
            salt = crypto_secrets.token_bytes(self.SALT_SIZE)
            key = self.derive_key(password, salt)
            fernet = Fernet(key)

            encrypted_content = fernet.encrypt(content.encode())
            salted = salt + encrypted_content
            return base64.base64encode(salted).decode()
        except Exception as e:
            raise EncryptionError(f"Encryption Failed: {str(e)}")
        
    def decrypt(self, encrypted_content: str, password: str) -> str:
        """ Decrypt content with password derived key """
        try:
            salted = base64.base64decode(encrypted_content.encode())
            salt = salted[:self.SALT_SIZE]
            encrypted_content = salted[self.SALT_SIZE:]
            key = self.derive_key(password, salt)
            fernet = Fernet(key)

            decrypted_content = fernet.decrypt(encrypted_content)
            return decrypted_content.decode()
        except Exception as e:
            raise EncryptionError(f"Decryption Failed: {str(e)}")

# Secure Github Vault
class GithubVault:
    def __init__(self, token: Optional[str]):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.base_url = os.getenv("GITHUB_BASE_URL") or "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": f"secrets-cli/{__version__}"
        }
        self.encryptor = Encryptor()

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """ Make request to Github """

        if not self.token:
            raise AuthenticationError("GitHub token required. Set GITHUB_TOKEN environment variable or use --token")
        try:
            response = requests.request(method, url, header=self.headers, timeout=30, **kwargs)
        except requests.RequestException as e:
            VaultError(f"Vault request failed: {str(e)}")
        
        if response.status_code == 401:
            raise AuthenticationError("Invalid Github Token!")
        if response.status_code == 403:
            raise AuthenticationError("Insufficient Permissions")
        
        return response
    
    def _create_gist_payload(self, filename: str, encrypted_content: str) -> Dict[str, Any]:
        """ Create formatted gist payload with metadat """

        gist_paylaod = {
            "_encrypted": True,
            "_version": "1.0.0",
            "_cli_version": __version__,
            "_filename": filename,
            "data": encrypted_content
        }

        return {
            "description": f"Encrypted secrets vault - {filename}",
            "public": False,
            "files": {
                "secrets.enc": {
                    "content": json.dumps(gist_paylaod, indent=2)
                }
            }
        }
    
    def create(self, filename: str, content: str, password: str) -> str:
        """ Create new gist """

        encrypted_content = self.encryptor.encrypt(content, password)
        payload = self._create_gist_payload(filename, encrypted_content)

        response = self._make_request("POST", f"{self.base_url}/gists", json=payload)

        if response.status_code != 201:
            raise VaultError(f"Failed to create gist: {response.text}")
        
        return response.json()["id"]
    
    def update(self, gist_id: str, filename: str, content: str, password: str) -> None:
        """ Update and existing gist """

        encrypted_content = self.encryptor.encrypt(content, password)

        payload = {
            "files": {
                "secrets.enc": {
                    "content": json.dumps(self._create_gist_payload(filename, encrypted_content)["files"]["secrets.enc"], indent=2)
                }
            }
        }

        response = requests.request("PATCH", f"{self.base_url}/gists/{gist_id}", json=payload)

        if response.status_code != 200:
            raise ValueError("Failed to update gist: {response.text}")
        
    def retrive(self, gist_id: str, password: str) -> tuple[str, str]:
        """ Retrive and decrypt gist """

        response = self._make_request("GET", f"{self.base_url}/gists/{gist_id}")

        if response.status_code == 400:
            raise ValueError("Gist not found. Make sure Gist ID is correct!")
        
        elif response.status_code != 200:
            raise VaultError(f"Failed to retrieve gist: {response.text}")
        
        gist_data = response.json()
        files = gist_data.get("files", {})

        if "secrets.enc" not in files:
            raise VaultError("Not a valid encrypted secrets gist")
        
        try:
            encrypted_file = json.loads(files["secrets.enc"]["content"])
        except json.JSONDecodeError:
            raise VaultError("Corrupted gist data")
        
        if not encrypted_file.get("_encrypted"):
            raise VaultError("Gist is not encrypted")
        
        encrypted_content = encrypted_file["data"]
        filename = encrypted_file.get("_filename", ".env")
        content = self.encryptor.decrypt(encrypted_content, password)
        
        return filename, content
    
class ConfigManager:
    """ Manage local configuration and project settings """

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / "./secrets-cli"
        self.config_file = self.config_dir / "config.json"
        self._secure_config_dir()
    
    def _secure_config_dir(self) -> None:
        """ Create config directory with secure permissions """

        self.config_dir.mkdir(mode=0o700, exist_ok=True)
        if self.config_file.exists:
            os.chmod(self.config_file, 0o600)
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Failed to load config: {e}")
            return {}
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file with secure permissions."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            os.chmod(self.config_file, 0o600)
        except OSError as e:
            raise VaultError(f"Failed to save config: {e}")
    
    def get_project_config(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Get configuration for current project."""
        config = self.load_config()
        project_key = str(project_path.resolve())
        return config.get("projects", {}).get(project_key)
    
    def set_project_config(self, project_path: Path, gist_id: str, filename: str = ".env") -> None:
        """Set configuration for current project."""
        config = self.load_config()
        
        if "projects" not in config:
            config["projects"] = {}
        
        project_key = str(project_path.resolve())
        config["projects"][project_key] = {
            "gist_id": gist_id,
            "filename": filename,
            "encrypted": True,
            "version": __version__
        }
        
        self.save_config(config)

# Main secrets-cli application
class SecretsCLI:
    """ CLI Application """

    def __init__(self):
        self.config_manager = ConfigManager()
        self.vault = None

    def _get_vault(self, token: Optional[str] = None) ->GithubVault:
        if not self.vault:
            self.vault = GithubVault(token)
        return self.vault
    
    def _get_env_file_path(self, filename: str = ".env") -> Path:
        return Path.cwd() / filename
    
    def _get_password(self, prompt: str = "Enter Vault Password") -> str:
        password = getpass.getpass(prompt)

        if not password:
            raise VaultError("Password cannot be empty.")
        
        return password

    def _validate_password(self, password: str) -> None:
        """ Password should be at least 8 characters """
        if len(password) < 8:
            raise VaultError("Password must be 8 characters long")

    def _secure_file_write(self, filepath: Path, content: str) -> None:
        """ Write file with secure permissions """
        with open(filepath, 'w') as f:
            f.write(content)
        os.chmod(filepath, 0o600)

    def __init__(self, args: argparse.Namespace) -> None:
        """ Initialize secure vault """
        env_file = self._get_env_file_path(args.filename)

        if not env_file.exists():
            print(f"❌ Error: {args.filename} not found.")
            print(f"Create the file first: touch {args.filename}")
            sys.exit(1)
        try:
            # check if project is already initialized
            if self.config_manager.get_project_config(Path.cwd()):
                print(f"❌ Project already initialized.")
                print(f"Use 'secrets push' to update or 'secrets status' to check configuration")
                sys.exit(1)

            # get password for vault
            password = self._get_password("Create Vault Password: ")
            self._validate_password(password)

            confirm_password = self._get_password("Confirm Password: ")
            if password != confirm_password:
                raise VaultError("Password don't match")

            # read and encrypt env file
            with open(env_file, 'r') as f:
                file_content = f.read()

            if not file_content.strip():
                print("⚠️ Warning: File is empty.")
            
            vault = self._get_vault(args.token)
            gist_id = vault.create(args.filename, file_content, password)

            # save the project config locally
            self.config_manager.set_project_config(Path.cwd(), gist_id, args.filename)

            print("✅ Successfully initialized encrypted secrets vault")
            print(f"🔒 Content encrypted with AES-256")
            print(f"📝 Gist ID: {gist_id}")
            print("")
            print("📤 Share this command with your team:")
            print(f"   secrets pull --gist-id {gist_id}")
            print("")
            print("⚠️  Important: Share the vault password securely!")
        
        except (ValueError, AuthenticationError, EncryptionError, VaultError) as e:
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected Error: {e}")
            sys.exit(1)

    # helper methods
    def push (self, args: argparse.Namespace) -> None:
        """ push local .env file to secure vault """
        env_file = self._get_env_file_path(args.filename)

        if not env_file.exists():
            print(f"Error: {args.filename} does not exists")
            sys.exit(1)

        # get project config
        config = self.config_manager.get_project_config(Path.cwd())
        if not config:
            print("❌ Project not initialized")
            print("   Run 'secrets init' first or use 'secrets pull --gist-id <id>' to link existing vault")
            sys.exit(1)
        
        try:
            password = self._get_password()

            with open(env_file, 'r') as f:
                file_content = f.read()

            vault = self._get_vault(args.token)
            vault.update(config["gist_id"], args.filename, file_content, password)

            print(f"✅ Successfully pushed encrypted {args.filename} to vault")
        
        except (EncryptionError, VaultError, AuthenticationError) as e:
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected Error: {e}")
            sys.exit(1)
    
    def pull(self, args: argparse.Namespace) -> None:
        """ pull .env file from vault and decrypt """

        gist_id = args.gist_id
        filename = args.filename

        # if gist_id not provided then lookup local config file
        if not gist_id:
            config = self.config_manager.get_project_config(Path.cwd())
            if not config:
                print(f"No Gist ID provided and project not initialized.")
                print("   Use: secrets pull --gist-id <gist-id>")
                sys.exit(1)
            
            gist_id = config["gist_id"]
            filename = filename or config["filename"]
        
        try:
            password = self._get_password()
            vault = self._get_vault(args.token)

            vault_filename, content = vault.retrive(gist_id, password)
            current_filename = filename or vault_filename
            env_file = self._get_env_file_path(current_filename)

            # check if local .env file already exist
            if env_file.exists() and not args.force:
                response = input(f"⚠️  {current_filename} already exists. Overwrite? (y/N): ")
                if response.lower() != 'y':
                    print(f"Session Terminated.")
                    sys.exit(0)
            
            self._secure_file_write(env_file, content)
            print(f"Successfully pulled and decrypted {current_filename}")

            # only for fist time
            if not self.config_manager.get_project_config(Path.cwd()):
                self.config_manager.set_project_config(Path.cwd(), gist_id, current_filename)
                print("Saved project configuration")
            
        except (EncryptionError, VaultError, AuthenticationError) as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            sys.exit(1)

    def status(self, args: argparse.Namespace) -> None:
        """ Return project status and config """

        config = self.config_manager.get_project_config(Path.cwd())
        print(f"Project: {Path.cwd().name}")

        if not config:
            print("❌ Status: Not initialized")
            print("   Run 'secrets init' to get started")
            return
        
        print("Status: Initialized")
        print(f"Gist ID: {config['gist_id']}")
        print(f"Filename: {config['filename']}")
        print(f"Encryption: Enabled")
        print(f"CLI Version: {config.get('version', 'unknown')}")

        env_file = self._get_env_file_path(config['filename'])
        if env_file.exists():
            print(f"Local file: {config['filename']} (exists)")
        else:
            print(f"Local file: {config['filename']} (missing)")
            print("   Run 'secrets pull' to retrieve from vault")


def create_parser() -> argparse.ArgumentParser:
    """ CMD Argument Parser """

    parser = argparse.ArgumentParser(
    prog="secrets",
    description="Secure env sync tool",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
                Examples:
                secrets init                     Initialize encrypted vault with .env
                secrets push                     Push local changes to vault
                secrets pull                     Pull latest from vault
                secrets pull --gist-id xxxxxx    Pull from specific gist ID
                secrets status                   Show project status

                Security:
                • Client-side AES-256 encryption
                • PBKDF2 key derivation (100,000 iterations)
                • Zero-knowledge architecture
                • Secure file permissions (600)

                Authentication:
                Set GITHUB_TOKEN environment variable or use --token
                Create token: https://github.com/settings/tokens (gist scope required)

                For more information: https://github.com/mirzamudassir/secrets-cli
        """
    )

    parser.add_argument(
            "--version", 
            action="version", 
            version=f"%(prog)s {__version__}"
        )
    parser.add_argument(
            "--token", 
            help="GitHub personal access token"
        )
        
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Init command
    init_parser = subparsers.add_parser(
            "init", 
            help="Initialize encrypted secrets vault"
        )
    init_parser.add_argument(
            "--filename", 
            default=".env", 
            help="Environment file name (default: .env)"
        )
        
        # Push command  
    push_parser = subparsers.add_parser(
            "push", 
            help="Push local env file to vault"
        )
    push_parser.add_argument(
            "--filename", 
            default=".env", 
            help="Environment file name (default: .env)"
        )
        
        # Pull command
    pull_parser = subparsers.add_parser(
            "pull", 
            help="Pull env file from vault"
        )
    pull_parser.add_argument(
            "--gist-id", 
            help="Gist ID to pull from (required for first-time setup)"
        )
    pull_parser.add_argument(
            "--filename", 
            help="Environment file name (default: auto-detect)"
        )
    pull_parser.add_argument(
            "--force", 
            action="store_true", 
            help="Overwrite existing file without confirmation"
        )
        
        # Status command
    status_parser = subparsers.add_parser(
            "status",
            help="Show project status"
        )
        
    return parser

def main() -> None:
    """ main entry point """
    
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = SecretsCLI()
    
    try:
        if args.command == "init":
            cli.init(args)
        elif args.command == "push":
            cli.push(args)
        elif args.command == "pull":
            cli.pull(args)
        elif args.command == "status":
            cli.status(args)
    except KeyboardInterrupt:
        print("\n❌ Session terminated by user")
        sys.exit(1)
        
if __name__ == "__main__":
    main()