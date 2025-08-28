"""SSH-related utilities for engine and studio commands."""

import os
import shutil
import subprocess
from pathlib import Path

from .constants import SSH_MANAGED_COMMENT


def get_ssh_public_key() -> str:
    """Get the user's SSH public key.

    Discovery order (container-friendly):
    1) DHT_SSH_PUBLIC_KEY env var (direct key content)
    2) DHT_SSH_PUBLIC_KEY_PATH env var (path to a .pub file)
    3) ssh-agent via `ssh-add -L` (requires SSH_AUTH_SOCK)
    4) Conventional files: ~/.ssh/id_ed25519.pub, ~/.ssh/id_rsa.pub

    Raises:
        FileNotFoundError: If no public key can be discovered.
    """
    # 1) Direct env var content
    env_key = os.environ.get("DHT_SSH_PUBLIC_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    # 2) Env var path
    env_path = os.environ.get("DHT_SSH_PUBLIC_KEY_PATH")
    if env_path:
        p = Path(env_path).expanduser()
        if p.is_file():
            try:
                return p.read_text().strip()
            except Exception:
                pass

    # 3) Agent lookup (ssh-add -L)
    try:
        if shutil.which("ssh-add") is not None:
            proc = subprocess.run(["ssh-add", "-L"], capture_output=True, text=True)
            if proc.returncode == 0 and proc.stdout:
                keys = [
                    line.strip() for line in proc.stdout.splitlines() if line.strip()
                ]
                # Prefer ed25519, then rsa
                for pref in ("ssh-ed25519", "ssh-rsa", "ecdsa-sha2-nistp256"):
                    for k in keys:
                        if k.startswith(pref + " "):
                            return k
                # Fallback to first key if types not matched
                if keys:
                    return keys[0]
    except Exception:
        pass

    # 4) Conventional files
    home = Path.home()
    key_paths = [home / ".ssh" / "id_ed25519.pub", home / ".ssh" / "id_rsa.pub"]
    for key_path in key_paths:
        if key_path.is_file():
            try:
                return key_path.read_text().strip()
            except Exception:
                continue

    raise FileNotFoundError(
        "No SSH public key found. Please create one with 'ssh-keygen' first."
    )


def check_session_manager_plugin():
    """Check if AWS Session Manager Plugin is available and warn if not."""
    from .constants import console

    if shutil.which("session-manager-plugin") is None:
        console.print(
            "[bold red]⚠️  AWS Session Manager Plugin not found![/bold red]\n"
            "SSH connections to engines require the Session Manager Plugin.\n"
            "Please install it following the setup guide:\n"
            "[link]https://github.com/dayhofflabs/nutshell/blob/main/REFERENCE/setup_guides/new-laptop.md[/link]"
        )
        return False
    return True


def update_ssh_config_entry(
    engine_name: str, instance_id: str, ssh_user: str, idle_timeout: int = 600
):
    """Add or update a single SSH config entry for the given SSH user.

    Args:
        engine_name:  Host alias to write into ~/.ssh/config
        instance_id:  EC2 instance-id (used by the proxy command)
        ssh_user:     Username to place into the SSH stanza
        idle_timeout: Idle timeout **in seconds** to pass to the SSM port-forward. 600 = 10 min.
    """
    config_path = Path.home() / ".ssh" / "config"
    config_path.parent.mkdir(mode=0o700, exist_ok=True)

    # Touch the file if it doesn't exist
    if not config_path.exists():
        config_path.touch(mode=0o600)

    # Read existing config
    content = config_path.read_text()
    lines = content.splitlines() if content else []

    # Remove any existing entry for this engine
    new_lines = []
    skip_until_next_host = False
    for line in lines:
        # Check if this is our managed host
        if (
            line.strip().startswith(f"Host {engine_name}")
            and SSH_MANAGED_COMMENT in line
        ):
            skip_until_next_host = True
        elif line.strip().startswith("Host ") and skip_until_next_host:
            skip_until_next_host = False
            # This is a different host entry, keep it
            new_lines.append(line)
        elif not skip_until_next_host:
            new_lines.append(line)

    # Add the new entry
    if new_lines and new_lines[-1].strip():  # Add blank line if needed
        new_lines.append("")

    new_lines.extend(
        [
            f"Host {engine_name} {SSH_MANAGED_COMMENT}",
            f"    HostName {instance_id}",
            f"    User {ssh_user}",
            f"    ProxyCommand sh -c \"AWS_SSM_IDLE_TIMEOUT={idle_timeout} aws ssm start-session --target %h --document-name AWS-StartSSHSession --parameters 'portNumber=%p'\"",
        ]
    )

    # Write back
    config_path.write_text("\n".join(new_lines))
    config_path.chmod(0o600)
