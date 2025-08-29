#!/usr/bin/env python3
"""
Clarity CLI - Interactive CLI for test management and execution

This CLI tool provides functionality for:
- Login (generates and stores JWT tokens)
- Executing tests (displays and allows selection from available tests)
"""

import json
import click
from clarity_cli.helpers import ensure_config_dir
from clarity_cli.commands import CliCommands
from clarity_cli.defs import CONFIG_FILE
from clarity_cli.outputs import CliOutput

commands = CliCommands()
out = CliOutput()


def get_profiles():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return [profile for profile in config.keys() if profile != "default"]
    except Exception:
        return []


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Verbose mode')
@click.pass_context
def cli(ctx, verbose=False):
    """Clarity CLI - Interactive test management and execution tool"""
    ctx.ensure_object(dict)
    ctx.obj['VERBOSE'] = verbose
    ensure_config_dir()


@cli.command()
@click.option('--plan-id', help='Specify a plan ID to execute directly')
@click.option('--test-id', '-t', help='Specify a test ID to execute directly')
@click.option('--profile', '-p', type=click.Choice(get_profiles()), help='Specify a name for the new profile')
@click.option('--override-config-path', '-c', help='Path to config.json, default config stored in ~/.config.json')
@click.option('--project', '-proj', help='Specify the default project id for clarity operations')
@click.option('--workspace', '-w', help='Specify the default workspace id for clarity operations')
@click.option('--agent-id', '-a', help='Specify the default agent id for executions')
@click.option('--parameters-file', help="Path to a json file that includes all the flow variables values for execution, if flow var doesn't exist using the default value")
@click.option('-y', is_flag=True, default=False, help='Yes to all')
@click.pass_context
def execute(ctx, plan_id=None, test_id=None, profile=None, override_config_path=None, project=None, workspace=None, agent_id=None, parameters_file=None, y=False):
    try:
        ctx.obj['yes_to_all'] = y
        commands.execute(ctx, plan_id, test_id, profile, override_config_path,
                         project, workspace, agent_id, parameters_file)
    except Exception as e:
        out.vprint(e)
        raise click.Abort()


@cli.command()
@click.option('--profile', '-p', help='Specify a name for the new profile')
@click.option('--client-id', '-id', help='Specify the client ID you got from cyclarity portal')
@click.option('--client-secret', '-cs', help='Specify the client secret you got from cyclarity portal')
@click.option('--token-endpoint', '-e', help='Specify the token endpoint you got from cyclarity portal')
@click.option('--scope', '-s', help='Specify the scope you got from cyclarity portal')
@click.option('--project', '-proj', help='Specify the default project id for clarity operations')
@click.option('--workspace', '-w', help='Specify the default workspace id for clarity operations')
@click.option('--agent_id', '-a', help='Specify the default agent id for executions')
@click.option('--domain', help='Specify the clarity domain')
@click.option('--default', '-d', is_flag=True, help='Use this profile as default profile')
@click.pass_context
def profile_setup(ctx, profile=None, client_id=None, client_secret=None, token_endpoint=None, scope=None, project=None, workspace=None, agent_id=None, default=None, domain=None):
    try:
        commands.write_profile_to_config(ctx, profile, client_id, client_secret,
                                         token_endpoint, scope, project, workspace, agent_id, domain, default)
    except Exception as e:
        out.vprint(e)
        raise click.Abort()


@cli.command()
@click.option('--profile', '-p', type=click.Choice(get_profiles()), help='Profile for login, if not provided use default profile')
@click.option('--override-config-path', '-c', help='Path to config.json, default config stored in ~/.config.json')
@click.pass_context
def login(ctx, profile=None, override_config_path=None):
    try:
        commands.login_using_config_file(ctx, profile, override_config_path)
    except Exception as e:
        out.vprint(e)
        raise click.Abort()


@cli.command()
@click.option('--profile', '-p', type=click.Choice(get_profiles()), help='Profile for login, if not provided use default profile')
@click.option('--override-config-path', '-c', help='Path to config.json, default config stored in ~/.config.json')
@click.option('--component-path', help='A path to poetry project that include the component source code')
@click.option('--entrypoint', '-e', help='The default entrypoint function name for the component (e.g. my_package.module:function)')
@click.option('--running-env', '-r', type=click.Choice(['IOT', 'CLOUD']), help='The default running environment for the component (IOT or CLOUD)')
@click.option('--pyc', is_flag=True, default=False, help='Compile the component and upload it as .pyc files')
@click.option('-y', is_flag=True, default=False, help='Yes to all')
@click.pass_context
def upload(ctx, profile=None, override_config_path=None, component_path=None, entrypoint=None, running_env=None, pyc=False, y=False):
    try:
        ctx.obj['yes_to_all'] = y
        commands.upload_component_from_package(
            ctx, profile, override_config_path, component_path, entrypoint, running_env, pyc)
    except Exception as e:
        out.vprint(e)
        raise click.Abort()


@cli.command('view-executions')
@click.option('--project-id', '-proj', help='Specify the project ID to view executions for')
@click.option('--output-type', '-o', type=click.Choice(['table', 'json']), default='table', help='Output format: table or json (default: table)')
@click.option('--file-path', '-f', help='Optional file path to save the executions data as JSON')
@click.option('--profile', '-p', type=click.Choice(get_profiles()), help='Profile to use, if not provided use default profile')
@click.option('--override-config-path', '-c', help='Path to config.json, default config stored in ~/.config.json')
@click.pass_context
def view_executions(ctx, project_id=None, output_type='table', file_path=None, profile=None, override_config_path=None):
    """View all executions for a project"""
    try:
        commands.view_all_executions(
            ctx, project_id, output_type, file_path, profile, override_config_path)
    except Exception as e:
        out.vprint(e)
        raise click.Abort()


@cli.command('get-findings')
@click.option('--execution-id', '-e', help='Specify the execution ID to get findings for')
@click.option('--output-type', '-o', type=click.Choice(['table', 'json']), default='table', help='Output format: table or json (default: table)')
@click.option('--file-path', '-f', help='Optional file path to save the findings data as JSON')
@click.option('--page-size', '-s', type=int, default=20, help='Number of findings per page (default: 20, use 0 for no pagination)')
@click.option('--profile', '-p', type=click.Choice(get_profiles()), help='Profile to use, if not provided use default profile')
@click.option('--override-config-path', '-c', help='Path to config.json, default config stored in ~/.config.json')
@click.pass_context
def get_findings(ctx, execution_id=None, output_type='table', file_path=None, page_size=20, profile=None, override_config_path=None):
    """Get findings for a specific execution"""
    try:
        commands.get_findings(ctx, execution_id, output_type,
                              file_path, page_size, profile, override_config_path)
    except Exception as e:
        out.vprint(e)
        raise click.Abort()


@cli.command('generate-report')
@click.option('--execution-id', '-e', help='Specify the execution ID to generate report for')
@click.option('--project-id', '-proj', help='Specify the project ID')
@click.option('--report-type', '-r', type=click.Choice(['PDF', 'CSV']), default='PDF', help='Report format: PDF or CSV (default: PDF)')
@click.option('--profile', '-p', type=click.Choice(get_profiles()), help='Profile to use, if not provided use default profile')
@click.option('--override-config-path', '-cfg', help='Path to config.json, default config stored in ~/.config.json')
@click.pass_context
def generate_report(ctx, execution_id=None, project_id=None, report_type=None, profile=None, override_config_path=None):
    """Generate a PDF report for a specific execution"""
    try:
        commands.generate_report(
            ctx, report_type, execution_id, project_id, profile, override_config_path)
    except Exception as e:
        out.vprint(e)
        raise click.Abort()


if __name__ == '__main__':
    cli()
