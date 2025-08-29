"""Configuration management service."""

import yaml
from typing import Dict, Any, Optional
from pathlib import Path

from ..constants import CONFIG_PATH, MESSAGES
from ..models import JiraCredentials
from ..exceptions import ConfigurationError


class ConfigService:
    """Service for managing application configuration."""
    
    def __init__(self, config_path: Path = CONFIG_PATH):
        """Initialize the configuration service."""
        self.config_path = config_path
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_path.exists():
            return {}
        
        try:
            return yaml.safe_load(self.config_path.read_text()) or {}
        except yaml.constructor.ConstructorError as e:
            if "python/tuple" in str(e):
                return self._handle_legacy_config()
            raise ConfigurationError(f"Invalid configuration format: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def get_jira_credentials(self) -> Optional[JiraCredentials]:
        """Get Jira credentials from configuration."""
        config = self.load_config()
        
        base_url = config.get("base_url")
        email = config.get("email")
        token = config.get("token")
        
        if all([base_url, email, token]):
            return JiraCredentials(
                base_url=base_url,
                email=email,
                token=token
            )
        return None
    
    def save_jira_credentials(self, credentials: JiraCredentials) -> None:
        """Save Jira credentials to configuration."""
        config = self.load_config()
        config.update({
            "base_url": credentials.base_url,
            "email": credentials.email,
            "token": credentials.token
        })
        self.save_config(config)
    
    def get_preference(self, key: str) -> Any:
        """Get user preference from configuration."""
        config = self.load_config()
        return config.get(key)
    
    def set_preference(self, key: str, value: Any) -> None:
        """Set user preference in configuration."""
        config = self.load_config()
        config[key] = value
        self.save_config(config)
    
    def _handle_legacy_config(self) -> Dict[str, Any]:
        """Handle legacy configuration format with tuple caching."""
        import typer
        
        typer.echo("⚠️  Detected old cache format, clearing cache...", err=True)
        
        # Try to preserve essential config by reading line by line
        essential_config = {}
        try:
            with open(self.config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('base_url:'):
                        essential_config['base_url'] = line.split(':', 1)[1].strip().strip('"\'')
                    elif line.startswith('email:'):
                        essential_config['email'] = line.split(':', 1)[1].strip().strip('"\'')
                    elif line.startswith('token:'):
                        essential_config['token'] = line.split(':', 1)[1].strip().strip('"\'')
                    elif line.startswith('latest_project:'):
                        essential_config['latest_project'] = line.split(':', 1)[1].strip().strip('"\'')
        except Exception:
            pass  # If we can't parse, just continue with empty config
        
        # Backup the current config
        backup_path = self.config_path.with_suffix('.yaml.backup')
        self.config_path.rename(backup_path)
        typer.echo(f"📁 Config backed up to {backup_path}", err=True)
        
        # Save the essential config immediately
        if essential_config:
            self.save_config(essential_config)
            typer.echo("✅ Essential configuration preserved", err=True)
        
        return essential_config
