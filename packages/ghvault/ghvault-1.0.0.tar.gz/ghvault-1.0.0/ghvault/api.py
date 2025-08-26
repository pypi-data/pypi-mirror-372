# ghvault/api.py
import base64
import os
from typing import Any

import httpx
from nacl.public import PublicKey, SealedBox
from tqdm import tqdm

PK_CACHE = {}

# GitHub token - will be set by CLI if not in environment
GH_TOKEN = None


def set_github_token(token: str):
    """Set the GitHub token for API calls."""
    global GH_TOKEN
    GH_TOKEN = token


def get_github_token() -> str:
    """Get the GitHub token, raising error if not available."""
    global GH_TOKEN

    if GH_TOKEN:
        return GH_TOKEN

    # Try to get from environment
    env_token = os.getenv("GH_TOKEN")
    if env_token:
        GH_TOKEN = env_token
        return GH_TOKEN

    raise RuntimeError("❌ GitHub token not available. Please set GH_TOKEN environment variable or provide it via CLI.")


def validate_github_token(token: str) -> bool:
    """
    Validate GitHub token by making a test API call.

    Returns:
        True if token is valid, False otherwise
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        # Test with a simple API call to get user info
        response = httpx.get("https://api.github.com/user", headers=headers, timeout=10.0)
        return response.status_code == 200
    except Exception:
        return False


def get_gh_environment_public_key(repo_owner: str, repo_name: str, environment: str) -> dict:
    """
    Get the GitHub environment public key and key_id.
    """
    # Check the cache
    cache_key = f"pk:{repo_owner}/{repo_name}/{environment}"
    if PK_CACHE.get(cache_key):
        return PK_CACHE[cache_key]
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/environments/{environment}/secrets/public-key"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {get_github_token()}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    response = httpx.get(url, headers=headers, timeout=10.0)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"❌ Failed to fetch public key: {e.response.text}") from e

    # Store in cache
    PK_CACHE[cache_key] = response.json()
    return response.json()  # contains "key" and "key_id"


def libsodium_encrypt(secret_value: str, public_key_b64: str) -> str:
    """
    Encrypt secret_value with GitHub's public key using LibSodium (SealedBox).
    Returns base64-encoded ciphertext.
    """
    public_key = PublicKey(base64.b64decode(public_key_b64))
    sealed_box = SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


def create_or_update_secret(
    repo_owner: str,
    repo_name: str,
    environment: str,
    secret_name: str,
    secret_value: str,
) -> dict:
    """
    Creates or updates a secret in a GitHub environment.
    """
    # Step 1: Fetch public key
    pk_info = get_gh_environment_public_key(repo_owner, repo_name, environment)
    public_key_b64 = pk_info["key"]
    key_id = pk_info["key_id"]

    # Step 2: Encrypt secret
    encrypted_value = libsodium_encrypt(secret_value, public_key_b64)

    # Step 3: PUT request
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/environments/{environment}/secrets/{secret_name}"

    payload = {"encrypted_value": encrypted_value, "key_id": key_id}

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {get_github_token()}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    response = httpx.put(url, headers=headers, json=payload, timeout=10.0)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"❌ Failed to set secret '{secret_name}': {e.response.text}") from e

    return response.json() if response.text else {"status": "success"}


def parse_env_file(file_path: str) -> dict:
    """
    Parse a .env file and return a dictionary of key-value pairs.
    Handles comments, empty lines, and quoted values.
    """
    env_vars = {}

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Find the first = sign
            if "=" not in line:
                print(f"⚠️  Warning: Skipping invalid line {line_num}: {line}")
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            # Skip empty keys
            if not key:
                print(f"⚠️  Warning: Skipping empty key on line {line_num}")
                continue

            env_vars[key] = value

    return env_vars


def write_env_to_github(
    repo_owner: str,
    repo_name: str,
    environment: str,
    file_path: str,
    dry_run: bool = False,
) -> Any:
    """
    Write secrets in bulk to a GitHub environment from a .env file.

    Args:
        repo_owner: GitHub repository owner
        repo_name: GitHub repository name
        environment: Target environment name
        file_path: Path to the .env file
        dry_run: If True, only parse and validate without uploading
    """
    # Step 1: Parse the .env file
    try:
        env_vars = parse_env_file(file_path)
    except FileNotFoundError:
        raise RuntimeError(f"❌ .env file not found: {file_path}")
    except Exception as e:
        raise RuntimeError(f"❌ Failed to parse .env file: {e}")

    if not env_vars:
        raise RuntimeError("❌ No valid environment variables found in .env file")

    print(f"📄 Found {len(env_vars)} environment variables in {file_path}")

    if dry_run:
        print("🔍 Dry run mode - showing variables that would be uploaded:")
        for key in env_vars.keys():
            print(f"  • {key}")
        return {"dry_run": True, "variables": list(env_vars.keys())}

    # Step 2: Fetch public key once for all secrets
    try:
        pk_info = get_gh_environment_public_key(repo_owner, repo_name, environment)
        public_key_b64 = pk_info["key"]
        key_id = pk_info["key_id"]
    except Exception as e:
        raise RuntimeError(f"❌ Failed to get environment public key: {e}")

    # Step 3: Upload secrets in bulk
    results = {"success": [], "failed": [], "total": len(env_vars)}

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {get_github_token()}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    print(f"🚀 Uploading {len(env_vars)} secrets to {environment} environment...")

    # Use tqdm for progress tracking
    with tqdm(total=len(env_vars), desc="Uploading secrets", unit="secret") as pbar:
        for secret_name, secret_value in env_vars.items():
            try:
                # Encrypt the secret value
                encrypted_value = libsodium_encrypt(secret_value, public_key_b64)

                # Prepare the request
                url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/environments/{environment}/secrets/{secret_name}"
                payload = {"encrypted_value": encrypted_value, "key_id": key_id}

                # Make the request
                response = httpx.put(url, headers=headers, json=payload, timeout=10.0)
                response.raise_for_status()

                results["success"].append(secret_name)
                pbar.set_postfix_str(f"✅ {secret_name}")

            except httpx.HTTPStatusError as e:
                error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
                results["failed"].append({"name": secret_name, "error": error_msg})
                pbar.set_postfix_str(f"❌ {secret_name}")

            except Exception as e:
                results["failed"].append({"name": secret_name, "error": str(e)})
                pbar.set_postfix_str(f"❌ {secret_name}")

            pbar.update(1)

    # Step 4: Summary
    success_count = len(results["success"])
    failed_count = len(results["failed"])

    print("📊 Upload Summary:")
    print(f"  ✅ Successful: {success_count}")
    print(f"  ❌ Failed: {failed_count}")
    print(f"  📈 Total: {results['total']}")

    if failed_count > 0:
        print(f"\n⚠️  {failed_count} secrets failed to upload. Check the errors above.")


def list_environment_secrets(repo_owner: str, repo_name: str, environment: str) -> list:
    """
    List all secrets in a GitHub environment.

    Returns:
        List of secret names (values are not retrievable via API)
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/environments/{environment}/secrets"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {get_github_token()}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        response = httpx.get(url, headers=headers, timeout=10.0)
        response.raise_for_status()

        data = response.json()
        secrets = data.get("secrets", [])

        return [secret["name"] for secret in secrets]

    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"{e.response.json().get('message', 'Environment not found!')}") from e


def delete_environment_secret(repo_owner: str, repo_name: str, environment: str, secret_name: str) -> bool:
    """
    Delete a secret from a GitHub environment.

    Returns:
        True if successful, raises exception on failure
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/environments/{environment}/secrets/{secret_name}"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {get_github_token()}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        response = httpx.delete(url, headers=headers, timeout=10.0)
        response.raise_for_status()
        return True

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise RuntimeError(f"❌ Secret '{secret_name}' not found in environment '{environment}'")
        raise RuntimeError(f"❌ Failed to delete secret '{secret_name}': {e.response.text}") from e


def delete_multiple_secrets(
    repo_owner: str,
    repo_name: str,
    environment: str,
    secret_names: list,
    confirm: bool = False,
) -> dict:
    """
    Delete multiple secrets from a GitHub environment.

    Args:
        repo_owner: GitHub repository owner
        repo_name: GitHub repository name
        environment: Target environment name
        secret_names: List of secret names to delete
        confirm: If True, skip confirmation prompt

    Returns:
        Dictionary with deletion results
    """
    results = {"success": [], "failed": [], "total": len(secret_names)}

    if not secret_names:
        print("❌ No secret names provided")
        return results

    print(f"🗑️  Deleting {len(secret_names)} secrets from {environment} environment...")

    # Use tqdm for progress tracking
    with tqdm(total=len(secret_names), desc="Deleting secrets", unit="secret") as pbar:
        for secret_name in secret_names:
            try:
                delete_environment_secret(repo_owner, repo_name, environment, secret_name)
                results["success"].append(secret_name)
                pbar.set_postfix_str(f"✅ {secret_name}")

            except Exception as e:
                results["failed"].append({"name": secret_name, "error": str(e)})
                pbar.set_postfix_str(f"❌ {secret_name}")

            pbar.update(1)

    # Summary
    success_count = len(results["success"])
    failed_count = len(results["failed"])

    print("\n📊 Deletion Summary:")
    print(f"  ✅ Successful: {success_count}")
    print(f"  ❌ Failed: {failed_count}")
    print(f"  📈 Total: {results['total']}")

    if failed_count > 0:
        print(f"\n⚠️  {failed_count} secrets failed to delete. Check the errors above.")

    return results
