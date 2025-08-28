import asyncio
import sys
from typing import Any, cast

import click

from exponent.commands.common import (
    check_inside_git_repo,
    check_running_from_home_directory,
    check_ssl,
    create_cloud_chat,
    redirect_to_login,
    start_chat_turn,
)
from exponent.commands.settings import use_settings
from exponent.commands.types import exponent_cli_group
from exponent.commands.utils import (
    launch_exponent_browser,
    print_exponent_message,
)
from exponent.core.config import Settings
from exponent.core.graphql.client import GraphQLClient
from exponent.core.graphql.mutations import (
    CREATE_CLOUD_CHAT_FROM_REPOSITORY_MUTATION,
    ENABLE_CLOUD_REPOSITORY_MUTATION,
    INCREMENTAL_BUILD_CLOUD_REPOSITORY_MUTATION,
    REBUILD_CLOUD_REPOSITORY_MUTATION,
    START_CHAT_TURN_MUTATION,
)
from exponent.core.graphql.queries import GITHUB_REPOSITORIES_QUERY
from exponent.utils.version import check_exponent_version_and_upgrade


@exponent_cli_group(hidden=True)
def cloud_cli() -> None:
    pass


async def enable_cloud_repository(
    api_key: str,
    base_api_url: str,
    base_ws_url: str,
    org_name: str,
    repo_name: str,
) -> dict[str, Any]:
    graphql_client = GraphQLClient(
        api_key=api_key, base_api_url=base_api_url, base_ws_url=base_ws_url
    )

    variables = {
        "orgName": org_name,
        "repoName": repo_name,
    }

    result = await graphql_client.execute(
        ENABLE_CLOUD_REPOSITORY_MUTATION,
        variables,
        "EnableCloudRepository",
        timeout=120,
    )

    return cast(dict[str, Any], result["enableCloudRepository"])


async def incremental_build_cloud_repository(
    api_key: str,
    base_api_url: str,
    base_ws_url: str,
    org_name: str,
    repo_name: str,
) -> dict[str, Any]:
    graphql_client = GraphQLClient(
        api_key=api_key, base_api_url=base_api_url, base_ws_url=base_ws_url
    )

    variables = {
        "orgName": org_name,
        "repoName": repo_name,
    }

    result = await graphql_client.execute(
        INCREMENTAL_BUILD_CLOUD_REPOSITORY_MUTATION,
        variables,
        "IncrementalBuildCloudRepository",
        timeout=120,
    )

    return cast(dict[str, Any], result["incrementalBuildCloudRepository"])


async def rebuild_cloud_repository(
    api_key: str,
    base_api_url: str,
    base_ws_url: str,
    org_name: str,
    repo_name: str,
) -> dict[str, Any]:
    graphql_client = GraphQLClient(
        api_key=api_key, base_api_url=base_api_url, base_ws_url=base_ws_url
    )

    variables = {
        "orgName": org_name,
        "repoName": repo_name,
    }

    result = await graphql_client.execute(
        REBUILD_CLOUD_REPOSITORY_MUTATION,
        variables,
        "RebuildCloudRepository",
        timeout=120,
    )

    return cast(dict[str, Any], result["rebuildCloudRepository"])


async def list_github_repositories(
    api_key: str,
    base_api_url: str,
    base_ws_url: str,
) -> dict[str, Any]:
    graphql_client = GraphQLClient(
        api_key=api_key, base_api_url=base_api_url, base_ws_url=base_ws_url
    )

    result = await graphql_client.execute(
        GITHUB_REPOSITORIES_QUERY,
        None,
        "GithubRepositories",
        timeout=120,
    )

    return cast(dict[str, Any], result["githubRepositories"])


async def create_cloud_chat_from_repository(
    api_key: str,
    base_api_url: str,
    base_ws_url: str,
    repository_id: str,
) -> dict[str, Any]:
    graphql_client = GraphQLClient(
        api_key=api_key, base_api_url=base_api_url, base_ws_url=base_ws_url
    )

    variables = {
        "repositoryId": repository_id,
    }

    result = await graphql_client.execute(
        CREATE_CLOUD_CHAT_FROM_REPOSITORY_MUTATION,
        variables,
        "CreateCloudChatFromRepository",
        timeout=120,
    )

    return cast(dict[str, Any], result["createCloudChat"])


async def start_chat_turn_with_prompt(
    api_key: str,
    base_api_url: str,
    base_ws_url: str,
    chat_uuid: str,
    prompt: str,
) -> dict[str, Any]:
    graphql_client = GraphQLClient(
        api_key=api_key, base_api_url=base_api_url, base_ws_url=base_ws_url
    )

    variables = {
        "chatInput": {"prompt": {"message": prompt, "attachments": []}},
        "parentUuid": None,
        "chatConfig": {
            "chatUuid": chat_uuid,
            "exponentModel": "PREMIUM",
            "requireConfirmation": False,
            "readOnly": False,
            "depthLimit": 20,
        },
    }

    result = await graphql_client.execute(
        START_CHAT_TURN_MUTATION, variables, "StartChatTurnMutation", timeout=120
    )

    return cast(dict[str, Any], result["startChatReply"])


@cloud_cli.command(hidden=True)
@click.option(
    "--org-name",
    help="GitHub organization name",
    required=True,
)
@click.option(
    "--repo-name",
    help="GitHub repository name",
    required=True,
)
@use_settings
def enable_repo(
    settings: Settings,
    org_name: str,
    repo_name: str,
) -> None:
    """Test utility for enabling cloud repository."""
    check_exponent_version_and_upgrade(settings)

    if not settings.api_key:
        redirect_to_login(settings)
        return

    loop = asyncio.get_event_loop()

    api_key = settings.api_key
    base_api_url = settings.get_base_api_url()
    base_ws_url = settings.get_base_ws_url()

    try:
        result = loop.run_until_complete(
            enable_cloud_repository(
                api_key, base_api_url, base_ws_url, org_name, repo_name
            )
        )

        if result["__typename"] == "ContainerImage":
            click.secho(
                f"✓ Successfully enabled repository {org_name}/{repo_name}", fg="green"
            )
            click.echo(f"  Build ref: {result.get('buildRef', 'N/A')}")
            click.echo(f"  Created at: {result.get('createdAt', 'N/A')}")
            click.echo(f"  Updated at: {result.get('updatedAt', 'N/A')}")
        else:
            click.secho(
                f"✗ Failed to enable repository: {result.get('message', 'Unknown error')}",
                fg="red",
            )
            click.echo(f"  Error type: {result['__typename']}")

    except Exception as e:
        click.secho(f"✗ Error enabling repository: {e!s}", fg="red")
        sys.exit(1)


@cloud_cli.command(hidden=True)
@click.option(
    "--org-name",
    help="GitHub organization name",
    required=True,
)
@click.option(
    "--repo-name",
    help="GitHub repository name",
    required=True,
)
@use_settings
def incremental_build(
    settings: Settings,
    org_name: str,
    repo_name: str,
) -> None:
    """Test utility for incremental build of cloud repository."""
    check_exponent_version_and_upgrade(settings)

    if not settings.api_key:
        redirect_to_login(settings)
        return

    loop = asyncio.get_event_loop()

    api_key = settings.api_key
    base_api_url = settings.get_base_api_url()
    base_ws_url = settings.get_base_ws_url()

    try:
        result = loop.run_until_complete(
            incremental_build_cloud_repository(
                api_key, base_api_url, base_ws_url, org_name, repo_name
            )
        )

        if result["__typename"] == "ContainerImage":
            click.secho(
                f"✓ Successfully triggered incremental build for {org_name}/{repo_name}",
                fg="green",
            )
            click.echo(f"  Build ref: {result.get('buildRef', 'N/A')}")
            click.echo(f"  Created at: {result.get('createdAt', 'N/A')}")
            click.echo(f"  Updated at: {result.get('updatedAt', 'N/A')}")
        else:
            click.secho(
                f"✗ Failed to trigger incremental build: {result.get('message', 'Unknown error')}",
                fg="red",
            )
            click.echo(f"  Error type: {result['__typename']}")

    except Exception as e:
        click.secho(f"✗ Error triggering incremental build: {e!s}", fg="red")
        sys.exit(1)


@cloud_cli.command(hidden=True)
@click.option(
    "--org-name",
    help="GitHub organization name",
    required=True,
)
@click.option(
    "--repo-name",
    help="GitHub repository name",
    required=True,
)
@use_settings
def rebuild(
    settings: Settings,
    org_name: str,
    repo_name: str,
) -> None:
    """Test utility for full rebuild of cloud repository."""
    check_exponent_version_and_upgrade(settings)

    if not settings.api_key:
        redirect_to_login(settings)
        return

    loop = asyncio.get_event_loop()

    api_key = settings.api_key
    base_api_url = settings.get_base_api_url()
    base_ws_url = settings.get_base_ws_url()

    try:
        result = loop.run_until_complete(
            rebuild_cloud_repository(
                api_key, base_api_url, base_ws_url, org_name, repo_name
            )
        )

        if result["__typename"] == "ContainerImage":
            click.secho(
                f"✓ Successfully triggered rebuild for {org_name}/{repo_name}",
                fg="green",
            )
            click.echo(f"  Build ref: {result.get('buildRef', 'N/A')}")
            click.echo(f"  Created at: {result.get('createdAt', 'N/A')}")
            click.echo(f"  Updated at: {result.get('updatedAt', 'N/A')}")
        else:
            click.secho(
                f"✗ Failed to trigger rebuild: {result.get('message', 'Unknown error')}",
                fg="red",
            )
            click.echo(f"  Error type: {result['__typename']}")

    except Exception as e:
        click.secho(f"✗ Error triggering rebuild: {e!s}", fg="red")
        sys.exit(1)


@cloud_cli.command(hidden=True)
@use_settings
def list_repos(
    settings: Settings,
) -> None:
    """Test utility for listing GitHub repositories."""
    check_exponent_version_and_upgrade(settings)

    if not settings.api_key:
        redirect_to_login(settings)
        return

    loop = asyncio.get_event_loop()

    api_key = settings.api_key
    base_api_url = settings.get_base_api_url()
    base_ws_url = settings.get_base_ws_url()

    try:
        result = loop.run_until_complete(
            list_github_repositories(api_key, base_api_url, base_ws_url)
        )

        if result["__typename"] == "GithubRepositories":
            repositories = result.get("repositories", [])
            if repositories:
                click.secho(f"✓ Found {len(repositories)} repositories:", fg="green")
                for repo in repositories:
                    click.echo(
                        f"\n  Repository: {repo['githubOrgName']}/{repo['githubRepoName']}"
                    )
                    click.echo(f"    ID: {repo['id']}")
                    if repo.get("baseHost"):
                        click.echo(f"    Base Host: {repo['baseHost']}")
                    if repo.get("containerImageId"):
                        click.echo(
                            f"    Container Image ID: {repo['containerImageId']}"
                        )
                    click.echo(f"    Created: {repo['createdAt']}")
                    click.echo(f"    Updated: {repo['updatedAt']}")
            else:
                click.secho("No repositories found", fg="yellow")
        else:
            click.secho(
                f"✗ Failed to list repositories: {result.get('message', 'Unknown error')}",
                fg="red",
            )
            click.echo(f"  Error type: {result['__typename']}")

    except Exception as e:
        click.secho(f"✗ Error listing repositories: {e!s}", fg="red")
        sys.exit(1)


def filter_repositories(
    repositories: list[dict[str, Any]], org_name: str | None, repo_name: str | None
) -> list[dict[str, Any]]:
    """Filter repositories by organization and/or repository name."""
    if not (org_name or repo_name):
        return repositories

    filtered = []
    for repo in repositories:
        if org_name and repo["githubOrgName"] != org_name:
            continue
        if repo_name and repo["githubRepoName"] != repo_name:
            continue
        filtered.append(repo)

    return filtered


def select_repository_interactive(repositories: list[dict[str, Any]]) -> dict[str, Any]:
    """Interactively select a repository from a list."""
    if len(repositories) == 1:
        selected = repositories[0]
        click.secho(
            f"Using repository: {selected['githubOrgName']}/{selected['githubRepoName']}",
            fg="cyan",
        )
        return selected

    # Show numbered list for selection
    click.secho("Available repositories:", fg="cyan")
    for i, repo in enumerate(repositories, 1):
        click.echo(f"  {i}. {repo['githubOrgName']}/{repo['githubRepoName']}")

    # Get user selection
    while True:
        try:
            choice = click.prompt("Select a repository (number)", type=int)
            if 1 <= choice <= len(repositories):
                return cast(dict[str, Any], repositories[choice - 1])
            else:
                click.secho(
                    f"Please enter a number between 1 and {len(repositories)}",
                    fg="red",
                )
        except (ValueError, KeyboardInterrupt):
            click.secho("\nCancelled", fg="yellow")
            sys.exit(0)


def send_initial_prompt(
    loop: asyncio.AbstractEventLoop,
    api_key: str,
    base_api_url: str,
    base_ws_url: str,
    chat_uuid: str,
    prompt: str,
) -> None:
    """Send an initial prompt to the chat if provided."""
    click.secho(
        f"\nSending initial prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}",
        fg="cyan",
    )

    prompt_result = loop.run_until_complete(
        start_chat_turn_with_prompt(
            api_key, base_api_url, base_ws_url, chat_uuid, prompt
        )
    )

    if prompt_result["__typename"] == "Chat":
        click.secho("✓ Prompt sent successfully", fg="green")
    else:
        click.secho(
            f"⚠ Failed to send prompt: {prompt_result.get('message', 'Unknown error')}",
            fg="yellow",
        )
        click.echo(f"  Error type: {prompt_result['__typename']}")


def fetch_repositories(
    loop: asyncio.AbstractEventLoop,
    api_key: str,
    base_api_url: str,
    base_ws_url: str,
) -> list[dict[str, Any]]:
    """Fetch the list of GitHub repositories."""
    result = loop.run_until_complete(
        list_github_repositories(api_key, base_api_url, base_ws_url)
    )

    if result["__typename"] != "GithubRepositories":
        click.secho(
            f"✗ Failed to list repositories: {result.get('message', 'Unknown error')}",
            fg="red",
        )
        sys.exit(1)

    repositories = result.get("repositories", [])
    if not repositories:
        click.secho("No repositories found", fg="yellow")
        sys.exit(1)

    return cast(list[dict[str, Any]], repositories)


@cloud_cli.command(hidden=True)
@click.option(
    "--org-name",
    help="GitHub organization name (optional, for filtering)",
    required=False,
)
@click.option(
    "--repo-name",
    help="GitHub repository name (optional, for direct selection)",
    required=False,
)
@click.option(
    "--prompt",
    help="Initial prompt to send to the chat after creation",
    required=False,
)
@use_settings
def create_chat(
    settings: Settings,
    org_name: str | None,
    repo_name: str | None,
    prompt: str | None,
) -> None:
    """Create a cloud chat for a GitHub repository with optional initial prompt."""
    check_exponent_version_and_upgrade(settings)

    if not settings.api_key:
        redirect_to_login(settings)
        return

    loop = asyncio.get_event_loop()
    api_key = settings.api_key
    base_url = settings.base_url
    base_api_url = settings.get_base_api_url()
    base_ws_url = settings.get_base_ws_url()

    try:
        # Fetch repositories
        repositories = fetch_repositories(loop, api_key, base_api_url, base_ws_url)

        # Filter if criteria provided
        filtered_repos = filter_repositories(repositories, org_name, repo_name)

        if not filtered_repos:
            click.secho(
                f"No repositories found matching {org_name}/{repo_name or '*'}",
                fg="yellow",
            )
            sys.exit(1)

        # Select repository
        selected_repo = select_repository_interactive(filtered_repos)

        # Create cloud chat
        click.secho(
            f"\nCreating cloud chat for {selected_repo['githubOrgName']}/{selected_repo['githubRepoName']}...",
            fg="cyan",
        )

        chat_result = loop.run_until_complete(
            create_cloud_chat_from_repository(
                api_key, base_api_url, base_ws_url, selected_repo["id"]
            )
        )

        if chat_result["__typename"] != "Chat":
            click.secho(
                f"✗ Failed to create cloud chat: {chat_result.get('message', 'Unknown error')}",
                fg="red",
            )
            click.echo(f"  Error type: {chat_result['__typename']}")
            sys.exit(1)

        # Success - handle chat creation
        chat_uuid = chat_result["chatUuid"]
        click.secho(f"✓ Successfully created cloud chat: {chat_uuid}", fg="green")
        click.echo(f"\nChat URL: {base_url}/chats/{chat_uuid}")

        # Send initial prompt if provided
        if prompt:
            send_initial_prompt(
                loop, api_key, base_api_url, base_ws_url, chat_uuid, prompt
            )

        # Open browser
        launch_exponent_browser(settings.environment, base_url, chat_uuid)

    except Exception as e:
        click.secho(f"✗ Error creating cloud chat: {e!s}", fg="red")
        sys.exit(1)


@cloud_cli.command(hidden=True)
@click.option(
    "--cloud-config-id",
    help="ID of an existing cloud config to reconnect",
    required=True,
)
@click.option(
    "--prompt",
    help="Prompt to kick off the cloud session.",
    required=True,
)
@click.option(
    "--background",
    "-b",
    help="Start the cloud session without launching the Exponent UI",
    is_flag=True,
    default=False,
)
@use_settings
def cloud(
    settings: Settings,
    cloud_config_id: str,
    prompt: str,
    background: bool,
) -> None:
    check_exponent_version_and_upgrade(settings)

    if not settings.api_key:
        redirect_to_login(settings)
        return

    loop = asyncio.get_event_loop()

    check_running_from_home_directory()
    loop.run_until_complete(check_inside_git_repo(settings))
    check_ssl()

    api_key = settings.api_key
    base_url = settings.base_url
    base_api_url = settings.get_base_api_url()
    base_ws_url = settings.get_base_ws_url()

    chat_uuid = loop.run_until_complete(
        create_cloud_chat(api_key, base_api_url, base_ws_url, cloud_config_id)
    )

    if chat_uuid is None:
        sys.exit(1)

    loop.run_until_complete(
        start_chat_turn(api_key, base_api_url, base_ws_url, chat_uuid, prompt)
    )

    print_exponent_message(base_url, chat_uuid)

    if not background:
        launch_exponent_browser(settings.environment, base_url, chat_uuid)
