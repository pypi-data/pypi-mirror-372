#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import logging

import yaml

from xenoslib.base import SingletonWithArgs


logger = logging.getLogger(__name__)


class ConfigLoader(SingletonWithArgs):
    """Centralized configuration management with optional Vault integration.

    Args:
        config_file_path (str): Path to the YAML configuration file. Defaults to "config.yml".
        vault_secret_id (str, optional): Secret ID for Vault authentication.
            If provided, enables Vault functionality and imports hvac module.

    Attributes:
        cache (dict): Cache storage for frequently accessed configuration values.

    Example:
        # Without Vault (hvac not imported)
        >>> config = ConfigLoader("config.yml")

        # With Vault (hvac imported on demand)
        >>> config = ConfigLoader("config.yml", vault_secret_id="my-secret-id")

        # Write to Vault using attribute style
        >>> config.test_section.test_key = "new_value"

        # Write to Vault using dictionary style
        >>> config["test_section"]["test_key"] = "new_value"
    """

    VAULT_SUFFIX = "@vault"
    KV_MOUNT_POINT = "kv"

    cache = {}
    vault_client = None

    def __init__(self, config_file_path="config.yml", vault_secret_id=None):
        """Initialize the ConfigLoader with a configuration file and optional Vault secret."""
        with open(config_file_path, "r") as f:
            config_data = yaml.safe_load(f)
            self._raw_config = config_data if isinstance(config_data, dict) else {}

        if vault_secret_id is not None:
            self.vault_secret_id = vault_secret_id
            self._check_and_renew_vault_client()

    def _init_vault_client(self):
        """Initialize and authenticate the Vault client (imports hvac on demand)."""
        try:
            import hvac  # Lazy import
        except ImportError as e:
            raise ImportError(
                "hvac package is required for Vault integration. Install with: pip install hvac"
            ) from e

        try:
            vault_config = self._raw_config.get("vault", {})
            vault_url = vault_config.get("url")
            vault_space = vault_config.get("space")
            vault_role_id = vault_config.get("role_id")

            if not all([vault_url, vault_space, vault_role_id]):
                raise KeyError("Missing required Vault configuration in config.yml")

            self.vault_client = hvac.Client(url=vault_url, namespace=vault_space, timeout=45)
            self.vault_client.auth.approle.login(
                role_id=vault_role_id, secret_id=self.vault_secret_id
            )
        except Exception as e:
            self.vault_client = None
            raise Exception(f"Failed to initialize Vault client: {str(e)}") from e

    def _check_and_renew_vault_client(self):
        if not self.vault_client or not self.vault_client.is_authenticated():
            self._init_vault_client()

    def _is_vault_reference(self, section_config, key_name):
        """检查键是否是Vault引用"""
        return f"{key_name}{self.VAULT_SUFFIX}" in section_config

    def get(self, section, key_name, use_cache=True):
        """Retrieve a configuration value."""
        section_config = self._raw_config.get(section)
        if section_config is None:
            raise KeyError(f"Section '{section}' not found")

        if key_name in section_config:
            return section_config[key_name]

        if self._is_vault_reference(section_config, key_name):
            if self.vault_client is None:
                raise Exception(
                    f"Vault access required for {key_name} but Vault is not initialized"
                )

            cache_key = f"{section}:{key_name}"
            if use_cache and cache_key in self.cache:
                return self.cache[cache_key]
            value = self._get_value_from_vault(section, key_name)
            self.cache[cache_key] = value
            return value

        raise KeyError(f"Key '{key_name}' not found in section '{section}'")

    def set(self, section, key_name, value, use_cache=True):
        """Set a configuration value to Vault."""
        section_config = self._raw_config.get(section)
        if section_config is None:
            raise KeyError(f"Section '{section}' not found")

        if not self._is_vault_reference(section_config, key_name):
            raise KeyError(f"Key '{key_name}' is not a Vault reference in section '{section}'")

        if self.vault_client is None:
            raise Exception(f"Vault access required for {key_name} but Vault is not initialized")

        self._set_value_to_vault(section, key_name, value)

        cache_key = f"{section}:{key_name}"
        if use_cache:
            self.cache[cache_key] = value

    def _get_value_from_vault(self, section, key_name):
        """Retrieve a secret value from Vault."""
        try:
            section_config = self._raw_config[section]
            vault_path = section_config.get("vault_path")
            if not vault_path:
                raise KeyError(f"Missing vault_path in section '{section}'")

            vault_key_ref = f"{key_name}{self.VAULT_SUFFIX}"
            vault_key = section_config[vault_key_ref]

            namespace = section_config.get("vault_namespace") or self._raw_config["vault"]["space"]
            self.vault_client.adapter.namespace = namespace

            data = self.vault_client.secrets.kv.read_secret_version(
                path=vault_path, mount_point=self.KV_MOUNT_POINT, raise_on_deleted_version=True
            )
            return data["data"]["data"][vault_key]
        except Exception as e:
            raise Exception(f"Failed to fetch {key_name} from Vault: {str(e)}") from e

    def _set_value_to_vault(self, section, key_name, value):
        """Set a secret value to Vault."""
        try:
            self._check_and_renew_vault_client()

            section_config = self._raw_config[section]
            vault_path = section_config.get("vault_path")
            if not vault_path:
                raise KeyError(f"Missing vault_path in section '{section}'")

            vault_key_ref = f"{key_name}{self.VAULT_SUFFIX}"
            vault_key = section_config[vault_key_ref]

            namespace = section_config.get("vault_namespace") or self._raw_config["vault"]["space"]
            self.vault_client.adapter.namespace = namespace

            try:
                data = self.vault_client.secrets.kv.read_secret_version(
                    path=vault_path, mount_point=self.KV_MOUNT_POINT, raise_on_deleted_version=True
                )
                secret_data = data["data"]["data"]
            except Exception:
                logger.warning(f"Secret not found, creating new secret at {vault_path}")
                secret_data = {}

            secret_data[vault_key] = value

            self.vault_client.secrets.kv.create_or_update_secret(
                path=vault_path, secret=secret_data, mount_point=self.KV_MOUNT_POINT
            )

            logger.info(f"Updated Vault secret: {vault_path}/{vault_key}")
        except Exception as e:
            raise Exception(f"Failed to set {key_name} to Vault: {str(e)}") from e

    def __getitem__(self, section):
        """Dictionary-style access to configuration sections."""
        if section not in self._raw_config:
            raise KeyError(f"Section '{section}' not found")
        return SectionProxy(self, section)

    def __setitem__(self, section, proxy):
        """Prevent direct assignment to sections."""
        raise TypeError("ConfigLoader does not support direct section assignment")

    def __getattr__(self, section):
        """Attribute-style access to configuration sections."""
        try:
            return self[section]
        except KeyError as e:
            raise AttributeError(str(e))


class SectionProxy:
    """Proxy class for configuration section access."""

    def __init__(self, config_loader, section):
        self._loader = config_loader
        self._section = section

    def __getitem__(self, key):
        """Dictionary-style access to configuration values."""
        return self._loader.get(self._section, key)

    def __setitem__(self, key, value):
        """Dictionary-style setting of configuration values to Vault."""
        self.set(key, value)

    def get(self, key, default=None):
        """Dictionary-style access to configuration values."""
        try:
            return self._loader.get(self._section, key)
        except KeyError:
            return default

    def set(self, key, value):
        """Set a configuration value to Vault."""
        self._loader.set(self._section, key, value)

    def __getattr__(self, key):
        """Attribute-style access to configuration values."""
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(str(e))

    def __setattr__(self, name, value):
        """Attribute-style setting of configuration values to Vault."""
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self.set(name, value)

    def __repr__(self):
        """String representation of the section's configuration."""
        return yaml.dump(self.to_dict())

    def __contains__(self, key):
        return key in self.self.to_dict()

    def to_dict(self):
        return self._loader._raw_config[self._section]


if __name__ == "__main__":
    config_without_vault = ConfigLoader("config.yml")
    print("Without Vault:", config_without_vault.get("jira", "url"))

    config_with_vault = ConfigLoader("config.yml", vault_secret_id=os.getenv("VAULT_SECRET_ID"))

    # 属性方式读取
    print("With Vault (attr):", config_with_vault.test.test)

    # 字典方式读取
    print("With Vault (dict):", config_with_vault["cis"]["cis_client_id"])

    # 测试不存在的值
    print("Try val not exists: ", config_with_vault.test.get("not_exists"))

    # 写入示例 - 属性方式
    try:
        print("Current test value (attr read):", config_with_vault.test.test)
        config_with_vault.test.test = "new_value_123"
        print("After write (attr read):", config_with_vault.test.test)
    except Exception as e:
        print("Attribute write failed:", str(e))

    # 写入示例 - 字典方式
    try:
        print("Current test value (dict read):", config_with_vault["test"]["test"])
        config_with_vault["test"]["test"] = "new_value_456"
        print("After write (dict read):", config_with_vault["test"]["test"])

        # 混合方式验证
        print("After write (attr read):", config_with_vault.test.test)
    except Exception as e:
        print("Dictionary write failed:", str(e))

    # 写入新键示例
    try:
        print("Setting new key...")
        config_with_vault["database"]["new_password"] = "secure123!"
        print("New password:", config_with_vault.database.new_password)
    except Exception as e:
        print("New key write failed:", str(e))
