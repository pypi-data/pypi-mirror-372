#!/usr/bin/env python3

"""
Token Manager for Upstox API
Handles smart token caching, validation, and renewal
"""

import os
import json
import stat
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
import upstox_client
from upstox_client.rest import ApiException
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import getpass
import requests

console = Console()

class TokenManager:
    def __init__(self):
        """Initialize the token manager with storage location."""
        self.token_file = Path.home() / ".upstox_token.json"
        self.env_token_key = "UPSTOX_ACCESS_TOKEN"
        self.oauth_config = self._load_oauth_config()
        
    def _get_stored_token_data(self) -> Optional[dict]:
        """Load token data from storage file."""
        if not self.token_file.exists():
            return None
            
        try:
            with open(self.token_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            console.print(f"[yellow]Warning: Could not read token file: {e}[/yellow]")
            return None
    
    def _save_token_data(self, token: str) -> bool:
        """Save token data to storage file with metadata."""
        # Calculate token expiry (3:30 AM IST next day)
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        expiry = tomorrow.replace(hour=3, minute=30, second=0, microsecond=0)
        if now.hour < 3 or (now.hour == 3 and now.minute < 30):
            expiry = now.replace(hour=3, minute=30, second=0, microsecond=0)
        
        token_data = {
            "token": token,
            "created_at": now.isoformat(),
            "expires_at": expiry.isoformat(),
            "is_valid": True,
            "last_validated": now.isoformat(),
            "auth_type": "manual"  # Default to manual for backward compatibility
        }
        
        try:
            # Create file with restricted permissions (user only)
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            # Set file permissions to be readable/writable only by owner
            os.chmod(self.token_file, stat.S_IRUSR | stat.S_IWUSR)
            return True
        except IOError as e:
            console.print(f"[red]Error saving token: {e}[/red]")
            return False
    
    def _validate_token(self, token: str) -> bool:
        """Validate token by making a lightweight API call."""
        if not token:
            return False
            
        try:
            # Use a lightweight API call to test the token
            configuration = upstox_client.Configuration()
            configuration.access_token = token
            api_client = upstox_client.ApiClient(configuration)
            
            # Use UserApi to get profile - a simple call that requires authentication
            user_api = upstox_client.UserApi(api_client)
            response = user_api.get_profile(api_version='2.0')
            
            # If we get here without exception, token is valid
            return True
            
        except ApiException as e:
            # Check if it's an authentication error
            if e.status in [401, 403]:
                return False
            # For other errors, we'll assume token might be valid but API had issues
            console.print(f"[yellow]Warning: Could not fully validate token (API error {e.status})[/yellow]")
            return True  # Give benefit of doubt for non-auth errors
        except Exception as e:
            console.print(f"[yellow]Warning: Token validation failed: {e}[/yellow]")
            return True  # Give benefit of doubt for other errors
    
    def _prompt_for_token(self) -> Optional[str]:
        """Prompt user for a new access token."""
        console.print("\n" + "="*60)
        
        header_text = Text("Upstox Access Token Required", style="bold cyan")
        header_text.append("\nYour current token has expired or is invalid.", style="dim")
        header_text.append("\nPlease provide a new access token from Upstox.", style="dim")
        console.print(Panel(header_text, border_style="cyan"))
        
        console.print("\n[yellow]Steps to get your token:[/yellow]")
        console.print("1. Log in to Upstox Developer Console")
        console.print("2. Go to your app and generate a new access token")
        console.print("3. Copy the token and paste it below")
        console.print("\n[dim]Note: Tokens typically expire daily and need to be refreshed.[/dim]\n")
        
        while True:
            try:
                # Use getpass to hide token input (though it might still show in some terminals)
                token = getpass.getpass("Enter your Upstox access token: ").strip()
                
                if not token:
                    console.print("[red]Token cannot be empty. Please try again.[/red]")
                    continue
                
                # Basic format validation (Upstox tokens are typically JWTs)
                if len(token) < 100:  # JWT tokens are usually much longer
                    console.print("[yellow]Warning: Token seems too short. Are you sure this is correct?[/yellow]")
                    confirm = input("Continue anyway? (y/N): ").strip().lower()
                    if confirm not in ['y', 'yes']:
                        continue
                
                # Validate the token
                console.print("\n[dim]Validating token...[/dim]")
                if self._validate_token(token):
                    console.print("[green]✓ Token is valid![/green]")
                    return token
                else:
                    console.print("[red]✗ Token validation failed. Please check and try again.[/red]\n")
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Token input cancelled by user[/yellow]")
                return None
            except Exception as e:
                console.print(f"[red]Error during token input: {e}[/red]")
                return None
    
    def _get_env_token(self) -> Optional[str]:
        """Get token from environment variable (.env file)."""
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv(self.env_token_key)
    
    def invalidate_current_token(self):
        """Mark the current stored token as invalid."""
        token_data = self._get_stored_token_data()
        if token_data:
            token_data["is_valid"] = False
            token_data["invalidated_at"] = datetime.now().isoformat()
            
            try:
                with open(self.token_file, 'w') as f:
                    json.dump(token_data, f, indent=2)
            except IOError:
                pass  # Ignore errors when invalidating
    
    def get_valid_token(self) -> Optional[str]:
        """Get a valid access token using smart caching and validation."""
        
        # Step 1: Try to get token from stored cache
        stored_data = self._get_stored_token_data()
        if stored_data and stored_data.get("is_valid"):
            token = stored_data.get("token")
            if token:
                # Check if token was validated recently (within last hour)
                last_validated = stored_data.get("last_validated")
                if last_validated:
                    try:
                        validated_time = datetime.fromisoformat(last_validated)
                        if datetime.now() - validated_time < timedelta(hours=1):
                            # Token was validated recently, use it
                            return token
                    except ValueError:
                        pass  # Invalid date format, continue with validation
                
                # Validate token before using
                console.print("[dim]Validating cached token...[/dim]")
                if self._validate_token(token):
                    # Update validation timestamp
                    stored_data["last_validated"] = datetime.now().isoformat()
                    try:
                        with open(self.token_file, 'w') as f:
                            json.dump(stored_data, f, indent=2)
                    except IOError:
                        pass  # Ignore save errors
                    return token
                else:
                    console.print("[yellow]Cached token is no longer valid[/yellow]")
                    self.invalidate_current_token()
        
        # Step 2: Try to get token from environment (.env file) as fallback
        env_token = self._get_env_token()
        if env_token:
            console.print("[dim]Found token in environment, validating...[/dim]")
            if self._validate_token(env_token):
                console.print("[green]Environment token is valid[/green]")
                # Save this token for future use
                self._save_token_data(env_token)
                return env_token
            else:
                console.print("[yellow]Environment token is invalid or expired[/yellow]")
        
        # Step 3: Prompt user for new token
        console.print("[cyan]Need a new access token...[/cyan]")
        new_token = self._prompt_for_token()
        
        if new_token:
            # Save the new token
            if self._save_token_data(new_token):
                console.print("[green]Token saved successfully![/green]")
            return new_token
        
        return None
    
    def handle_api_error(self, api_exception: ApiException) -> bool:
        """Handle API errors and determine if token needs renewal.
        
        Returns:
            bool: True if error was handled and token renewed, False otherwise
        """
        if api_exception.status in [401, 403]:
            console.print(f"[yellow]Authentication error ({api_exception.status}): Token appears to be expired[/yellow]")
            
            # Invalidate current token
            self.invalidate_current_token()
            
            # Try to get a new token
            console.print("\n[cyan]Attempting to get a new token...[/cyan]")
            new_token = self.get_valid_token()
            
            return new_token is not None
        
        return False
    
    def get_token_info(self) -> dict:
        """Get information about the current token for debugging."""
        stored_data = self._get_stored_token_data()
        env_token = self._get_env_token()
        
        info = {
            "has_stored_token": bool(stored_data and stored_data.get("token")),
            "has_env_token": bool(env_token),
            "stored_token_valid": bool(stored_data and stored_data.get("is_valid")),
            "storage_file": str(self.token_file),
            "storage_file_exists": self.token_file.exists(),
            "oauth_configured": bool(self.oauth_config.get("client_id"))
        }
        
        if stored_data:
            info["token_created"] = stored_data.get("created_at")
            info["token_last_validated"] = stored_data.get("last_validated")
            info["auth_type"] = stored_data.get("auth_type", "manual")
            info["expires_at"] = stored_data.get("expires_at")
        
        return info
    
    def _load_oauth_config(self) -> Dict[str, str]:
        """Load OAuth configuration from environment."""
        from dotenv import load_dotenv
        load_dotenv()
        return {
            "client_id": os.getenv("UPSTOX_CLIENT_ID", ""),
            "client_secret": os.getenv("UPSTOX_CLIENT_SECRET", ""),
            "redirect_uri": os.getenv("UPSTOX_REDIRECT_URI", "http://localhost:8000/auth/callback")
        }
    
    def exchange_code_for_token(self, authorization_code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token.
        
        Args:
            authorization_code: The authorization code from OAuth callback
            
        Returns:
            Token response containing access_token and other metadata
        """
        if not self.oauth_config.get("client_id") or not self.oauth_config.get("client_secret"):
            console.print("[red]OAuth not configured. Please set UPSTOX_CLIENT_ID and UPSTOX_CLIENT_SECRET[/red]")
            return None
        
        token_url = "https://api.upstox.com/v2/login/authorization/token"
        
        payload = {
            "code": authorization_code,
            "client_id": self.oauth_config["client_id"],
            "client_secret": self.oauth_config["client_secret"],
            "redirect_uri": self.oauth_config["redirect_uri"],
            "grant_type": "authorization_code"
        }
        
        try:
            response = requests.post(token_url, data=payload)
            response.raise_for_status()
            token_data = response.json()
            
            if "access_token" in token_data:
                # Save the token with OAuth metadata
                self._save_oauth_token(token_data)
                return token_data
            else:
                console.print(f"[red]Token exchange failed: No access_token in response[/red]")
                return None
                
        except requests.RequestException as e:
            console.print(f"[red]Token exchange failed: {e}[/red]")
            return None
    
    def _save_oauth_token(self, token_response: Dict[str, Any]) -> bool:
        """Save OAuth token with metadata."""
        access_token = token_response.get("access_token")
        if not access_token:
            return False
        
        # Calculate token expiry (3:30 AM IST next day)
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        expiry = tomorrow.replace(hour=3, minute=30, second=0, microsecond=0)
        if now.hour < 3 or (now.hour == 3 and now.minute < 30):
            expiry = now.replace(hour=3, minute=30, second=0, microsecond=0)
        
        token_data = {
            "token": access_token,
            "created_at": now.isoformat(),
            "expires_at": expiry.isoformat(),
            "is_valid": True,
            "last_validated": now.isoformat(),
            "auth_type": "oauth",
            "extended_token": token_response.get("extended_token"),
            "user_id": token_response.get("user_id")
        }
        
        try:
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            os.chmod(self.token_file, stat.S_IRUSR | stat.S_IWUSR)
            return True
        except IOError as e:
            console.print(f"[red]Error saving OAuth token: {e}[/red]")
            return False
    
    def is_token_expired(self) -> bool:
        """Check if the current token has expired based on Upstox's 3:30 AM IST expiry."""
        stored_data = self._get_stored_token_data()
        if not stored_data:
            return True
        
        expires_at = stored_data.get("expires_at")
        if not expires_at:
            # Legacy token without expiry, assume it might be expired
            return True
        
        try:
            expiry_time = datetime.fromisoformat(expires_at)
            return datetime.now() >= expiry_time
        except (ValueError, TypeError):
            return True
    
    def get_oauth_url(self) -> Optional[str]:
        """Get the OAuth authorization URL for manual navigation."""
        if not self.oauth_config.get("client_id"):
            return None
        
        from urllib.parse import urlencode
        auth_base = "https://api.upstox.com/v2/login/authorization/dialog"
        params = {
            "response_type": "code",
            "client_id": self.oauth_config["client_id"],
            "redirect_uri": self.oauth_config["redirect_uri"]
        }
        return f"{auth_base}?{urlencode(params)}"