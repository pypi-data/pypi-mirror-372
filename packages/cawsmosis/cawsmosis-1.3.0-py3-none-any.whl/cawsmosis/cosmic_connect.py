#!/usr/bin/env python3
"""
cosmic_connect: Open SSM tunnels (SSH, RDP, Squid) to AWS instances.
"""

from botocore.exceptions import ClientError

import click
from dotenv import load_dotenv
import boto3
import os
import sys
import subprocess
from collections import defaultdict
import tempfile
from cawsmosis.util import get_instance_password, _get_base_port

# Load .env if present (project dir > cwd > home)
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"), override=False)


@click.group()
@click.option(
    "--profile",
    "-p",
    envvar="AWS_PROFILE",
    help="AWS CLI profile to use (env: AWS_PROFILE)",
)
@click.pass_context
def cli(ctx, profile):
    """
    Top‐level command for the Cosmic Connect toolkit.

    $ cosmic_connect --help
    """
    ctx.ensure_object(dict)
    ctx.obj["profile"] = profile


@cli.command()
@click.argument("instance_pattern", type=str)
@click.option(
    "--protocol",
    type=click.Choice(["ssh", "rdp", "squid", "proxy"], case_sensitive=False),
    default="ssh",
    show_default=True,
    help="Protocol to tunnel (proxy is alias for squid)",
)
@click.option(
    "--port", type=int, help="Local port to use (auto-assigns if not specified)"
)
@click.option("--launch", is_flag=True, help="Launch client after opening tunnel")
@click.option(
    "--rdp-key",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="PEM key for Windows password (RDP with --launch)",
)
@click.option("--detach", is_flag=True, help="Run tunnel in background")
@click.pass_context
def tunnel(ctx, instance_pattern, protocol, port, launch, rdp_key, detach):
    """
    Open a single SSM tunnel to a specific instance.

    INSTANCE_PATTERN can be:
      - Full instance name (e.g., dev.myapp.us-east-1)
      - Instance ID (e.g., i-1234567890abcdef0)
      - Partial name pattern (e.g., dev.myapp)

    Examples:
      cosmic-connect tunnel dev.myapp.us-east-1
      cosmic-connect tunnel dc1.myapp --protocol rdp
      cosmic-connect tunnel i-1234567890abcdef0 --protocol squid
      cosmic-connect tunnel dev.myapp --launch
    """
    profile = ctx.obj.get("profile")
    boto3_args = {"profile_name": profile} if profile else {}

    # Normalize protocol (proxy -> squid)
    if protocol == "proxy":
        protocol = "squid"

    # Discover matching instance
    session = boto3.Session(**boto3_args)
    ec2 = session.client("ec2")

    # Check if it's an instance ID
    if instance_pattern.startswith("i-"):
        filters = [
            {"Name": "instance-state-name", "Values": ["running"]},
            {"Name": "instance-id", "Values": [instance_pattern]},
        ]
    else:
        # It's a name pattern
        filters = [
            {"Name": "instance-state-name", "Values": ["running"]},
            {"Name": "tag:Name", "Values": [f"{instance_pattern}*"]},
        ]

    resp = ec2.describe_instances(Filters=filters)

    instances = []
    for res in resp.get("Reservations", []):
        for inst in res.get("Instances", []):
            name = inst["InstanceId"]  # default to ID
            for tag in inst.get("Tags", []):
                if tag["Key"] == "Name":
                    name = tag["Value"]
                    break
            instances.append((name, inst["InstanceId"]))

    if not instances:
        click.echo(f"No running instance found matching '{instance_pattern}'")
        ctx.exit(1)

    if len(instances) > 1:
        click.echo(f"Multiple instances match '{instance_pattern}':")
        for name, iid in instances:
            click.echo(f"  - {name} ({iid})")
        click.echo("Please be more specific.")
        ctx.exit(1)

    instance_name, instance_id = instances[0]

    # Validate protocol for instance type
    if protocol == "rdp" and not instance_name.startswith("dc1"):
        click.echo(
            f"Warning: RDP typically used for Windows (dc1) instances, but {instance_name} selected",
            err=True,
        )
    elif protocol in ["ssh", "squid"] and instance_name.startswith("dc1"):
        click.echo(
            f"Warning: {protocol.upper()} typically used for Linux instances, but {instance_name} is Windows",
            err=True,
        )

    # Check AWS credentials
    sts = (
        ["aws"]
        + (["--profile", profile] if profile else [])
        + ["sts", "get-caller-identity"]
    )
    try:
        subprocess.run(
            sts, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        click.echo("AWS credentials expired—running SSO login...", err=True)
        login_cmd = (
            ["aws"] + (["--profile", profile] if profile else []) + ["sso", "login"]
        )
        subprocess.run(login_cmd, check=True)

    # Determine ports
    if not port:
        if protocol == "ssh":
            port = _get_base_port(None, "COSMIC_SSH_BASE_PORT", 2222)
        elif protocol == "rdp":
            port = _get_base_port(None, "COSMIC_RDP_BASE_PORT", 2389)
        elif protocol == "squid":
            port = _get_base_port(None, "COSMIC_SQUID_BASE_PORT", 3128)

    # Map protocol to remote port
    remote_ports = {
        "ssh": 22,
        "rdp": 3389,
        "squid": 3128,
    }
    remote_port = remote_ports[protocol]

    # Setup subprocess options
    popen_kwargs = {}
    if detach:
        popen_kwargs.update(
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
        if os.name == "nt":
            popen_kwargs["creationflags"] = subprocess.DETACHED_PROCESS
        else:
            popen_kwargs["start_new_session"] = True

    # Open the tunnel
    cmd = [
        "aws",
        "--profile",
        profile,
        "ssm",
        "start-session",
        "--target",
        instance_id,
        "--document-name",
        "AWS-StartPortForwardingSession",
        "--parameters",
        f"localPortNumber={port},portNumber={remote_port}",
    ]

    click.echo(f"Opening {protocol.upper()} tunnel to {instance_name}...")
    click.echo(f"  localhost:{port} → {instance_name}:{remote_port}")

    subprocess.Popen(cmd, **popen_kwargs)

    # Launch client if requested
    if launch:
        if protocol == "ssh":
            ssh_cmd = [os.getenv("SSH", "ssh"), f"-p{port}", "ec2-user@localhost"]
            subprocess.Popen(ssh_cmd, **popen_kwargs)
            click.echo(f"Launched SSH client on port {port}")
        elif protocol == "rdp":
            if rdp_key:
                try:
                    pwd = get_instance_password(ec2, instance_id, rdp_key)
                    # Store credentials for RDP
                    for host in [f"localhost:{port}", f"127.0.0.1:{port}"]:
                        subprocess.run(
                            [
                                "cmdkey",
                                f"/generic:TERMSRV/{host}",
                                "/user:Administrator",
                                f"/pass:{pwd}",
                            ],
                            check=False,
                            capture_output=True,
                        )
                except Exception as e:
                    click.echo(
                        f"Warning: Could not decrypt RDP password: {e}", err=True
                    )
            else:
                click.echo(
                    "Warning: --rdp-key not provided, cannot auto-fill password",
                    err=True,
                )

            # Create RDP file
            rdp_file = tempfile.NamedTemporaryFile(
                delete=False, suffix=".rdp", mode="w"
            )
            rdp_file.write(f"full address:s:localhost:{port}\n")
            rdp_file.write("username:s:Administrator\n")
            rdp_file.close()
            subprocess.Popen(["mstsc", rdp_file.name], **popen_kwargs)
            click.echo(f"Launched RDP client on port {port}")
        elif protocol == "squid":
            click.echo(f"Squid proxy available at localhost:{port}")
            click.echo("Configure your browser/app to use this as HTTP/HTTPS proxy")


@cli.command()
@click.pass_context
def ls(ctx):
    """
    List all running AWS instances with a 'Cluster' tag, formatted as a table.

    $ cosmic_connect ls --help
    """
    session = boto3.Session(profile_name=ctx.obj.get("profile"))
    ec2 = session.client("ec2")
    paginator = ec2.get_paginator("describe_instances")

    # collect only tagged instances
    instances: list[dict] = []
    for page in paginator.paginate():
        for r in page["Reservations"]:
            for inst in r["Instances"]:
                tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
                if "Cluster" in tags:
                    instances.append(
                        {
                            "Cluster": tags["Cluster"],
                            "Name": tags.get("Name", "N/A"),
                            "InstanceId": inst["InstanceId"],
                        }
                    )

    if not instances:
        click.echo("No instances found with 'Cluster' tag.")
        return

    # group by cluster
    clusters: dict[str, list[dict]] = defaultdict(list)
    for inst in instances:
        clusters[inst["Cluster"]].append(inst)

    # compute column widths
    hdrs = ["Cluster", "Name", "Instance ID"]
    w_cluster = max(len(hdrs[0]), *(len(c) for c in clusters))
    w_name = max(
        len(hdrs[1]), *(len(i["Name"]) for grp in clusters.values() for i in grp)
    )
    w_id = max(
        len(hdrs[2]), *(len(i["InstanceId"]) for grp in clusters.values() for i in grp)
    )

    # header and separator
    header = f"{hdrs[0]:<{w_cluster}} │ {hdrs[1]:<{w_name}} │ {hdrs[2]:<{w_id}}"
    sep_line = "─" * len(header)

    click.echo(header)
    click.echo(sep_line)

    # print each cluster block
    for cluster_name in sorted(clusters):
        for inst in clusters[cluster_name]:
            click.echo(
                f"{cluster_name:<{w_cluster}} │ "
                f"{inst['Name']:<{w_name}} │ "
                f"{inst['InstanceId']:<{w_id}}"
            )
        click.echo(sep_line)


@cli.command()
@click.pass_context
def login(ctx):
    """
    Perform an SSO login so that AWS credentials are cached.

    $ cosmic_connect login --help

    """
    profile = ctx.obj.get("profile")
    cmd = ["aws"] + (["--profile", profile] if profile else []) + ["sso", "login"]
    click.echo("Running: " + " ".join(cmd))
    subprocess.run(cmd, check=True)


@cli.command()
@click.argument("cluster_token", type=str)
@click.option(
    "--rdp-user",
    default="Administrator",
    show_default=True,
    help="Username for RDP session",
)
@click.option("--ssh-base-port", type=int, help="Starting port for SSH tunnels")
@click.option("--rdp-base-port", type=int, help="Starting port for RDP tunnels")
@click.option("--squid-base-port", type=int, help="Starting port for Squid tunnels")
@click.option("--launch-ssh", is_flag=True, help="Immediately open SSH session")
@click.option("--launch-rdp", is_flag=True, help="Immediately open RDP session")
@click.option(
    "--rdp-key",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
    help="Path to your PEM private key for decrypting Windows Administrator password",
)
@click.option("--detach", is_flag=True, help="Fully background all tunnel processes")
@click.option(
    "--close",
    is_flag=True,
    help="Close existing SSM sessions for matching instances and exit",
)
@click.pass_context
def tunnels(
    ctx,
    cluster_token,
    ssh_base_port,
    rdp_base_port,
    squid_base_port,
    launch_ssh,
    launch_rdp,
    rdp_key,
    detach,
    close,
    rdp_user,
):
    """
    Open or close SSM tunnels to matching “dev” (SSH + Squid) and “dc1” (RDP) instances.

    $ cosmic_connect tunnel --help
    """
    profile = ctx.obj.get("profile")
    boto3_args = {"profile_name": profile} if profile else {}

    # discover matching instance IDs
    session = boto3.Session(**boto3_args)
    ec2 = session.client("ec2")
    resp = ec2.describe_instances(
        Filters=[
            {"Name": "instance-state-name", "Values": ["running"]},
            {
                "Name": "tag:Name",
                "Values": [
                    f"dev.{cluster_token}.*",
                    f"proxy.{cluster_token}.*",
                    f"dc1.{cluster_token}.*",
                ],
            },
        ]
    )
    instances = {
        tag["Value"]: inst["InstanceId"]
        for res in resp.get("Reservations", [])
        for inst in res.get("Instances", [])
        for tag in inst.get("Tags", [])
        if tag["Key"] == "Name"
    }

    if not instances:
        click.echo(
            f"No instances matching proxy.{cluster_token}.*, dev.{cluster_token}.* or dc1.{cluster_token}.*"
        )
        return

    # --- CLOSE MODE ----------------------------------------------------------
    if close:
        # Get current user identity to only close their sessions
        sts_client = session.client("sts")
        try:
            caller_identity = sts_client.get_caller_identity()
            current_user_arn = caller_identity["Arn"]
        except ClientError as e:
            click.echo(f"Error getting user identity: {e}", err=True)
            sys.exit(1)

        ssm = session.client("ssm")
        for name, iid in instances.items():
            pages = ssm.get_paginator("describe_sessions").paginate(
                State="Active",
                Filters=[
                    {"key": "Target", "value": iid},
                    {"key": "Owner", "value": current_user_arn},
                ],
            )
            for page in pages:
                for sess in page.get("Sessions", []):
                    sid = sess["SessionId"]
                    try:
                        ssm.terminate_session(SessionId=sid)
                        click.echo(f"Terminated session {sid} ({name}) owned by you")
                    except ClientError as e:
                        click.echo(f"Error terminating {sid}: {e}", err=True)
        return

    # --- OPEN MODE -----------------------------------------------------------
    sts = (
        ["aws"]
        + (["--profile", profile] if profile else [])
        + ["sts", "get-caller-identity"]
    )
    try:
        subprocess.run(
            sts, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        click.echo("AWS creds expired/missing—running SSO login...", err=True)
        login(ctx)

    ssh_base = _get_base_port(ssh_base_port, "COSMIC_SSH_BASE_PORT", 2222)
    rdp_base = _get_base_port(rdp_base_port, "COSMIC_RDP_BASE_PORT", 2389)
    squid_base = _get_base_port(squid_base_port, "COSMIC_SQUID_BASE_PORT", 3128)

    popen_kwargs = {}
    if detach:
        popen_kwargs.update(
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
        if os.name == "nt":
            popen_kwargs["creationflags"] = subprocess.DETACHED_PROCESS
        else:
            popen_kwargs["start_new_session"] = True

    ssh_ctr = ssh_base
    rdp_ctr = rdp_base
    squid_ctr = squid_base
    commands: list[str] = []

    for name, iid in sorted(instances.items()):
        if name.startswith("dev.") or name.startswith("proxy."):
            # SSH tunnel
            cmd_ssh = [
                "aws",
                "--profile",
                profile,
                "ssm",
                "start-session",
                "--target",
                iid,
                "--document-name",
                "AWS-StartPortForwardingSession",
                "--parameters",
                f"localPortNumber={ssh_ctr},portNumber=22",
            ]
            commands.append(" ".join(cmd_ssh))
            subprocess.Popen(cmd_ssh, **popen_kwargs)
            if launch_ssh:
                subprocess.Popen(
                    [os.getenv("SSH", "ssh"), f"-p{ssh_ctr}", "ec2-user@localhost"],
                    **popen_kwargs,
                )
            ssh_ctr += 1

            # Squid tunnel
            cmd_squid = [
                "aws",
                "--profile",
                profile,
                "ssm",
                "start-session",
                "--target",
                iid,
                "--document-name",
                "AWS-StartPortForwardingSession",
                "--parameters",
                f"localPortNumber={squid_ctr},portNumber=3128",
            ]
            commands.append(" ".join(cmd_squid))
            subprocess.Popen(cmd_squid, **popen_kwargs)
            squid_ctr += 1

        elif name.startswith("dc1."):
            cmd_rdp = [
                "aws",
                "--profile",
                profile,
                "ssm",
                "start-session",
                "--target",
                iid,
                "--document-name",
                "AWS-StartPortForwardingSession",
                "--parameters",
                f"localPortNumber={rdp_ctr},portNumber=3389",
            ]
            commands.append(" ".join(cmd_rdp))
            subprocess.Popen(cmd_rdp, **popen_kwargs)

            if launch_rdp:
                # ensure they actually passed --rdp-key
                if not rdp_key:
                    click.echo(
                        "Error: --rdp-key is required when using --launch-rdp", err=True
                    )
                    sys.exit(1)

                # attempt to fetch & decrypt the Windows Administrator password
                try:
                    click.echo(f"[DEBUG] fetching password for {iid}…")
                    pwd = get_instance_password(ec2, iid, rdp_key)
                    click.echo("[DEBUG] successfully decrypted Administrator password")

                    # MSTSC may look up TERMSRV/<host> or TERMSRV/127.0.0.1, with or without port
                    hosts = [
                        f"localhost:{rdp_ctr}",
                        f"127.0.0.1:{rdp_ctr}",
                        "localhost",
                        "127.0.0.1",
                    ]
                    for h in hosts:
                        target = f"TERMSRV/{h}"
                        click.echo(f"[DEBUG] storing credentials for {target}")
                        try:
                            subprocess.run(
                                [
                                    "cmdkey",
                                    "/generic:" + target,
                                    "/user:" + rdp_user,
                                    "/pass:" + pwd,
                                ],
                                check=True,
                                **popen_kwargs,
                            )
                            click.echo(
                                f"[DEBUG] cmdkey stored credentials for {target}"
                            )
                        except subprocess.CalledProcessError as e:
                            click.echo(
                                f"[DEBUG] cmdkey failed for {target}: {e}", err=True
                            )
                except RuntimeError as e:
                    click.echo(f"Warning: {e}", err=True)
                except subprocess.CalledProcessError as e:
                    click.echo(
                        f"Warning: failed to seed creds via cmdkey: {e}", err=True
                    )

                # finally start the RDP client
                # subprocess.Popen(["mstsc", f"/v:localhost:{rdp_ctr}"], **popen_kwargs)
                # generate a temporary .rdp file with embedded username + auto-connect
                rdp_contents = (
                    f"full address:s:localhost:{rdp_ctr}\n"
                    f"username:s:{rdp_user}\n"
                    "domain:s:.\n"
                    "prompt for credentials:i:0\n"
                    "enablecredsspsupport:i:1\n"
                    "administrative session:i:1\n"
                    "authentication level:i:2\n"
                )
                tmp = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".rdp", mode="w", newline="\n"
                )
                tmp.write(rdp_contents)
                tmp.flush()
                tmp_path = tmp.name
                tmp.close()
                click.echo(f"[DEBUG] generated RDP file at {tmp_path}")

                # launch the RDP client against that file
                subprocess.Popen(["mstsc", tmp_path], **popen_kwargs)

            rdp_ctr += 1

    click.echo("\n".join(commands))
    return commands


if __name__ == "__main__":
    cli()
