import os
import base64
import sys

import click
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding


def get_instance_password(ec2_client, instance_id: str, key_path: str) -> str:
    """
    Fetches the encrypted Windows Administrator password for an EC2 instance
    and decrypts it using the given PEM key.

    Args:\n
        ec2_client: boto3 EC2 client\n
        instance_id: The EC2 instance ID\n
        key_path: Path to your private-key PEM (expanded/resolved)\n

    Returns:
        The plaintext Administrator password.

    Raises:
        RuntimeError: if no password data is yet available.
    """
    resp = ec2_client.get_password_data(InstanceId=instance_id)
    blob = resp.get("PasswordData", "")
    if not blob:
        raise RuntimeError(
            f"No password data yet for {instance_id}; try again in a minute."
        )

    # now decrypt
    return decrypt_password(blob, key_path)


def decrypt_password(encrypted_blob: str, key_path: str) -> str:
    """
    Decrypt an EC2 Windows password blob with the given private key PEM.
    Args:
        encrypted_blob: The base64-encoded encrypted password blob from EC2.\n
        key_path: Path to the private key PEM file.\n
    Returns:
        The decrypted plaintext password as a UTF-8 string.
    """
    encrypted = base64.b64decode(encrypted_blob)
    with open(key_path, "rb") as f:
        priv = serialization.load_pem_private_key(f.read(), password=None)
    decrypted = priv.decrypt(encrypted, padding=padding.PKCS1v15())
    return decrypted.decode("utf-8")


def _get_base_port(cli_value: int, env_var: str, default: int) -> int:
    """
    Resolve a port‐base value in order:
      1) CLI flag if provided
      2) .env file or environment variable
      3) built‐in default

    Args:\n
        cli_value (int): The value provided via CLI flag, if any.\n
        env_var (str): The environment variable name to check.\n
        default (int): The default value to use if neither CLI nor env var is set.\n

    Returns:
        int: The resolved port base value.
    """
    if cli_value is not None:
        return cli_value
    val = os.getenv(env_var)
    if val:
        try:
            return int(val)
        except ValueError:
            click.echo(f"Invalid {env_var}={val!r}, must be integer", err=True)
            sys.exit(1)
    return default
