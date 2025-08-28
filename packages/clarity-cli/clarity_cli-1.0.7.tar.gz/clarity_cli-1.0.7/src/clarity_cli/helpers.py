import json
import jwt
import datetime
import base64
import requests
import py_compile
from clarity_cli.outputs import CliOutput, CliTable
from clarity_cli.input import CliInputs
from clarity_cli.defs import (
    CONFIG_DIR,
    TOKEN_FILE,
    CONFIG_FILE,
    ProfileConfig,
    EXECUTION_VIEW_PATH,
    ALL_EXECUTIONS_VIEW_PATH,
    ALL_PROJECTS_VIEW_PATH,
    GET_EXECUTION_FINDINGS,
    REPORT_TRIGGER_PATH,
    REPORT_STATUS_PATH,
    TEST_LIST,
    DEVICES_LIST,
    SUPPORTED_PYTHON_VERSION,
    STEP_UPLOAD,
    STEP_CREATE,
    SPECIFIC_STEP,
    SPECIFIC_EXECUTION_VIEW_PATH,
    RunningEnv,
    TableColumn,
    ThemeColors,
)
from clarity_cli.exceptions import StopCommand, UnAuthenticated
import os
import zipfile
import tempfile

# import shutil
import tomli
import tomli_w
from pathlib import Path
from packaging.specifiers import SpecifierSet
from packaging.version import Version
import time

input = CliInputs()
out = CliOutput()


def show_test_list(available_tests):
    test_execution_columns = [
        TableColumn("ID", ThemeColors.CYAN),
        TableColumn("Name", ThemeColors.GREEN),
        TableColumn("Version", ThemeColors.RED),
        TableColumn("Description", ThemeColors.YELLOW),
    ]
    tests_table = CliTable("Available Tests", test_execution_columns)
    tests_table.add_data(
        available_tests,
        headers_mapping={
            "ID": "test_id",
            "Name": "test_name",
            "Version": "test_version",
            "Description": "description",
        },
    )
    tests_table.print_table()


def show_plan_list(available_tests):
    test_execution_columns = [
        TableColumn("ID", ThemeColors.CYAN),
        TableColumn("Name", ThemeColors.GREEN),
        TableColumn("Description", ThemeColors.YELLOW),
    ]
    plans_table = CliTable("Available Plans", test_execution_columns)
    plans_table.add_data(
        available_tests,
        headers_mapping={
            "ID": "plan_id",
            "Name": "plan_name",
            "Description": "description",
        },
    )
    plans_table.print_table()


def ensure_config_dir():
    """Ensure the config directory exists"""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True)
        out.ok("Created configuration directory at ~/.clarity")


def is_logged_in(profile):
    """Check if the user is logged in by verifying the token"""
    if not TOKEN_FILE.exists():
        raise UnAuthenticated()
    out.vprint("Token file found")
    try:
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)

        # Verify token hasn't expired
        token = token_data.get(profile)
        if not token:
            raise UnAuthenticated()
        out.vprint("Token was loaded successfully")
        # Decode the token without verification to check expiration
        decoded = jwt.decode(token, options={"verify_signature": False})
        out.vprint("Token was parsed successfully")
        exp_timestamp = decoded.get(
            "exp", datetime.datetime.now(datetime.timezone.utc))

        # Check if token has expired
        if datetime.datetime.fromtimestamp(
            exp_timestamp, tz=datetime.timezone.utc
        ) < datetime.datetime.now(datetime.timezone.utc):
            out.warning("Your session has expired. Please login again.")
            raise UnAuthenticated()

        return token

    except Exception as e:
        out.error(f"Error checking login status: {str(e)}")
        raise UnAuthenticated()


def format_device_state(device):
    if device["state"] == "connected":
        device["state"] = f"[green]{device['state']}[/green]"
    if device["state"] == "disconnected":
        device["state"] = f"[red]{device['state']}[/red]"
    else:
        device["state"] = f"[yellow]{device['state']}[/yellow]"


def format_finding_type(finding_type):
    if finding_type in ["FINDING", "FAILED"]:
        finding_type = f"[red]{finding_type}[/red]"
    else:
        finding_type = f"[green]{finding_type}[/green]"
    return finding_type


def get_devices(token, workspace_id, domain):
    headers = {"Authorization": f"Bearer {token}", "workspace": workspace_id}
    url = f"{domain}/{DEVICES_LIST}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        res = response.json()
        devices = res["device_list"]
        return devices
    else:
        out.vprint("Error getting devices list")
        out.vprint(response.text)
        raise StopCommand("Couldn't get devices list")


def get_all_executions(token, workspace_id, domain, project_id):
    headers = {"Authorization": f"Bearer {token}", "workspace": workspace_id}
    url = f"{domain}/{ALL_EXECUTIONS_VIEW_PATH.format(project_id=project_id)}"
    response = requests.get(url, headers=headers)
    # Check if the request was successful
    if response.status_code == 202:
        res = response.json()
        for execution in res:
            execution["execution_counter"] = f'{int(execution["execution_counter"])}'
        return res
    else:
        out.vprint("Error getting executions list")
        out.vprint(response.text)
        raise StopCommand("Couldn't get executions list")


def get_specific_execution(token, workspace_id, domain, execution_id, project_id):
    headers = {"Authorization": f"Bearer {token}", "workspace": workspace_id}
    url = f"{domain}/{SPECIFIC_EXECUTION_VIEW_PATH.format(execution_id=execution_id, project_id=project_id)}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200 or response.status_code == 202:
        res = response.json()
        return res
    else:
        out.vprint("Error getting execution")
        out.vprint(response.text)
        raise StopCommand("Couldn't get execution")


def get_all_projects(token, workspace_id, domain):
    headers = {"Authorization": f"Bearer {token}", "workspace": workspace_id}
    url = f"{domain}/{ALL_PROJECTS_VIEW_PATH}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        res = response.json()
        # Extract the projects array from the response
        return res.get('projects', [])
    else:
        out.vprint("Error getting projects list")
        out.vprint(response.text)
        raise StopCommand("Couldn't get projects list")


def get_execution_findings(token, workspace_id, domain, execution_id):
    headers = {"Authorization": f"Bearer {token}", "workspace": workspace_id}
    url = f"{domain}/{GET_EXECUTION_FINDINGS.format(execution_id=execution_id)}"
    response = requests.get(url, headers=headers)
    # Check if the request was successful
    if response.status_code == 200:
        res = response.json()
        return res
    else:
        out.vprint("Error getting execution findings")
        out.vprint(response.text)
        raise StopCommand("Couldn't get execution findings")


def get_tests(token, workspace_id, domain):
    headers = {"Authorization": f"Bearer {token}", "workspace": workspace_id}
    url = f"{domain}/{TEST_LIST}"
    response = requests.get(url, headers=headers)
    # Check if the request was successful
    param_res = {}
    if response.status_code == 200:
        res = response.json()
        for test in res["tests"]:
            param_res[test["test_id"]] = test["params_schema"]
        return res, param_res
    else:
        out.vprint("Error getting tests list")
        out.vprint(response.text)
        raise StopCommand("Couldn't get Test list")


def trigger_test_execution(
    domain, token, workspace, project_id, agent_id, test_plan_config
):
    headers = {"Authorization": f"Bearer {token}", "workspace": workspace}
    url = f"{domain}/inv-api/testing/executions/handler"
    data = {
        "project_id": project_id,
        "agent_id": agent_id,
        "test_plan_config": test_plan_config,
    }
    response = requests.post(url, headers=headers, json=data)
    # Check if the request was successful
    if response.status_code == 202:
        res = response.json()
        out.ok("Execution started")
        out.vprint(
            f"execution id: {res['execution_id']}, project id: {res['project_id']}"
        )
        # return URL to track the execution
        return f"{domain}/{EXECUTION_VIEW_PATH.format(execution_id=res['execution_id'], project_id=res['project_id'])}"
    else:
        out.vprint(f"Status code: {response.status_code}")
        raise StopCommand(f"Failed to start execution, {response.text}")


def get_clarity_access_token(profile, client_id, client_secret, token_endpoint, scope):
    # The client credentials grant requires HTTP Basic Authentication,
    # where the username is the client ID and the password is the client secret
    try:
        client_auth = base64.b64encode(
            f"{client_id}:{client_secret}".encode("utf-8")
        ).decode("utf-8")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {client_auth}",
        }

        # The grant_type must be client_credentials
        data = {
            "grant_type": "client_credentials",
            "scope": scope,
        }
        response = requests.post(token_endpoint, headers=headers, data=data)

        if response.status_code != 200:
            out.verbose(response.text)
            raise StopCommand("Failed to get access token")

        response_data = response.json()
        out.vprint(f"Got token: {response_data['access_token']}")
        write_token(response_data["access_token"], profile)
    except Exception as e:
        out.vprint(f"Login error - {e}")
        raise StopCommand("Unable to login")


def read_config(config_override=None):
    config_to_use = config_override or CONFIG_FILE
    try:
        out.vprint(f"Reading config file: {config_to_use}")
        with open(config_to_use, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def read_token():
    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def get_params(params_file):
    try:
        with open(params_file, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def write_new_profile_to_config(
    profile_name: str, default: bool, config: ProfileConfig
):
    try:
        cur_config = read_config()
        new_profile = {profile_name: config.model_dump()}
        full_config = {**cur_config, **new_profile}
        full_config["default"] = (
            profile_name if default else full_config.get("default", "")
        )
        with open(CONFIG_FILE, "w") as f:
            json.dump(full_config, f)
    except Exception as e:
        StopCommand(
            f"An error occurred while writing new profile to config file - {e}")


def write_token(token, profile):
    tokens = read_token()
    tokens[profile] = token
    try:
        out.vprint(f"writing token to {TOKEN_FILE}, for profile: {profile}")
        with open(TOKEN_FILE, "w") as f:
            json.dump(tokens, f)
    except Exception as e:
        StopCommand(f"Unable to write tmp token to: {TOKEN_FILE} - {e}")


def get_profile_configuration(profile=None, override_config_path=None):
    current_configuration = read_config(override_config_path)
    if not profile:
        out.warning("Profile was not provided, using default profile")
        profile = current_configuration.get("default")
        if profile:
            out.ok(f"Default profile found, using {profile} profile")
        else:
            raise StopCommand(
                "Default profile wasn't configured, please specify a profile"
            )
    try:
        profile_config = ProfileConfig(
            **current_configuration.get(profile, {}))
        if not profile_config:
            out.error(f"profile {CliOutput.bold(profile)} was not found")
            out.warning(
                "use "
                + {CliOutput.bold("'clarity profile-setup'")}
                + "command to set it up"
            )
    except Exception as e:
        # is_valid_config = all([True if key in profile_config else False for key in ['client_id', 'client_secret', 'token_endpoint', 'scope']])
        # if not is_valid_config:
        out.vprint(f"Error parsing config - {e}")
        out.warning(
            "use "
            + {CliOutput.bold("'clarity profile-setup'")}
            + "command to set it up"
        )
        raise StopCommand(
            "Profile configuration is not valid, please reconfigure or use another profile"
        )
    return profile_config, profile


def create_step(step_to_upload: dict, domain: str, headers: dict) -> str:
    create_url = f"{domain}/{STEP_CREATE}"
    response = requests.post(create_url, headers=headers, json=step_to_upload)
    if response.status_code == 400:
        out.vprint(response.text)
        out.warning(
            "Step already exists, please bump version to create a new step")
        return response.json().get("step_id"), False
    elif response.status_code != 200:
        out.vprint(response.text)
        raise StopCommand("Failed to create step")
    out.vprint(f"Created step: {response.json()['step_id']}")
    out.ok("Step created successfully")
    return response.json()["step_id"], True


def update_step(step_id: str, step_to_upload: dict, domain: str, headers: dict) -> str:
    update_url = f"{domain}/{SPECIFIC_STEP.format(step_id=step_id)}"
    response = requests.put(update_url, headers=headers, json=step_to_upload)
    if response.status_code != 200:
        out.vprint(response.text)
        raise StopCommand("Failed to update step")
    out.vprint(f"Updated step: {step_id}")
    out.ok("Step updated successfully")


def zip_and_upload_step(
    step_to_upload: dict, package_dir: str, url_to_upload: str, pyc: bool
) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(
            temp_dir,
            f"{step_to_upload['step_name']}-{step_to_upload['step_version']}.zip",
        )
        # Create the zip file
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_f:
            out.vprint(f"Zipping package to: {zip_path}")
            for root, dirs, files in os.walk(package_dir):
                # Skip any directory containing 'venv' in its path
                if "venv" in root:
                    continue
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, package_dir)
                    if pyc and file_path.endswith(".py"):
                        # Compile to pyc and write that instead
                        pyc_path = file_path + "c"  # py_compile adds 'c' to create .pyc
                        py_compile.compile(file_path, cfile=pyc_path)
                        zip_f.write(pyc_path, arcname + "c")
                    else:
                        zip_f.write(file_path, arcname)

        with open(zip_path, "rb") as f:
            # For S3 presigned URLs, we need to send the file directly in the body
            # without using multipart form data
            response = requests.put(
                url_to_upload,
                data=f.read(),  # Read the file contents instead of passing file object
            )

        # Check if the upload was successful
        if response.status_code not in (200, 201):
            out.vprint(
                f"Got status code {response.status_code}: {response.text}")
            raise StopCommand("Upload new zip file failed")


def get_upload_url(
    step_id: str, domain: str, headers: dict, is_override: bool = False
) -> str:
    get_upload_url = f"{domain}/{STEP_UPLOAD.format(step_id=step_id)}"
    if is_override:
        get_upload_url = f"{get_upload_url}?override=true"
    response = requests.get(get_upload_url, headers=headers)
    if response.status_code == 400:
        response_type = response.json().get("type")
        out.vprint(response.text)
        if response_type:
            out.vprint(f"response type: {response_type}")
            return {"type": response_type, "url": None}
        else:
            raise StopCommand("Failed to get upload url")
    elif response.status_code != 200:
        out.vprint(response.text)
        raise StopCommand("Failed to get upload url")
    return {"type": "success", "url": response.json()["presinged_url"]}


def validate_python_version(python_version: str) -> str:
    if not python_version:
        raise StopCommand("No python version found in pyproject.toml")
    spec = SpecifierSet(python_version)
    if Version(SUPPORTED_PYTHON_VERSION) not in spec:
        raise StopCommand(
            f"Cyclarity currently doesn't support this python version {python_version}, please use: {SUPPORTED_PYTHON_VERSION}"
        )
    return python_version


def validate_step_metadata(step_to_upload: dict) -> dict:
    out.vprint("Validating step metadata")
    if not step_to_upload.get("step_name"):
        step_to_upload["step_name"] = input.ask_for_text_input(
            "Please enter the step name"
        )
    if not step_to_upload.get("step_version"):
        step_to_upload["step_version"] = input.ask_for_text_input(
            "Please enter the step version"
        )
    if not step_to_upload.get("description"):
        step_to_upload["description"] = input.ask_for_text_input(
            "Please enter the step description", default="", optional=True
        )
    if not step_to_upload.get("tags"):
        step_to_upload["tags"] = input.ask_for_text_input(
            "Do you want to add tags to the step? (comma separated, e.g. tag1,tag2,tag3)",
            default="",
            optional=True,
        )
        final_tags = [
            tag.strip().upper()
            for tag in step_to_upload["tags"].split(",")
            if tag.strip()
        ]
        out.vprint(f"Final tags: {final_tags}")
        step_to_upload["tags"] = final_tags
    return step_to_upload


def add_entrypoint_and_running_env(
    step_to_upload: dict,
    clarity_section: dict,
    default_entrypoint: str,
    default_running_env: str,
) -> dict:
    entrypoint = default_entrypoint or clarity_section.get("entrypoint")
    if not entrypoint:
        entrypoint = input.ask_for_text_input(
            "Please enter the runnable class entrypoint separated by dots(e.g. src.main.my_class)",
            default="",
        )
    else:
        approved = input.ask_for_confirmation(
            f"found entrypoint in pyproject.toml, using: {entrypoint}"
        )
        if not approved:
            entrypoint = input.ask_for_text_input(
                "Please enter the runnable class entrypoint separated by dots(e.g. src.main.my_class)",
                default="",
            )
    step_to_upload["execution_config"]["entrypoint"] = entrypoint
    running_env = default_running_env or clarity_section.get("running_env", "")
    if running_env not in RunningEnv.__members__.keys():
        out.warning(
            f"Invalid running environment {running_env}, please use one of: {list(RunningEnv.__members__.keys())}"
        )
        running_env_input = input.ask_for_input_from_list(
            "Please enter the running environment",
            options=RunningEnv.__members__.keys(),
        )
    else:
        running_env_input = running_env  # for toml file
    running_env = RunningEnv[running_env_input].value
    step_to_upload["execution_config"]["running_env"] = running_env
    clarity_section["entrypoint"] = entrypoint
    clarity_section["running_env"] = running_env_input


def create_step_metadata_from_poetry_v2(
    pyproject_data: dict,
    clarity_section: dict,
    default_entrypoint: str,
    default_running_env: str,
) -> dict:
    out.vprint("Creating step metadata from poetry v2")
    project_metadata = pyproject_data.get("project", {})
    step_to_upload = {
        "step_name": project_metadata.get("name"),
        "step_version": project_metadata.get("version"),
        "description": project_metadata.get("description", ""),
        "step_type": "EB_Component",
        "step_subtype": "Action",
        "tags": project_metadata.get("keywords", []),
        "execution_config": {"entrypoint": "", "running_env": "batch"},
        "zip_schema_file": None,
        "icon_file": None,
    }
    step_to_upload = validate_step_metadata(step_to_upload)
    add_entrypoint_and_running_env(
        step_to_upload, clarity_section, default_entrypoint, default_running_env
    )
    # Extract running environment from dependencies and python version
    python_version = project_metadata.get("requires-python")
    validate_python_version(python_version)
    return step_to_upload, clarity_section


def create_step_metadata_from_poetry_v1(
    pyproject_data: dict,
    clarity_section: dict,
    default_entrypoint: str,
    default_running_env: str,
) -> dict:
    out.vprint("Creating step metadata from poetry v1")
    poetry_section: dict = pyproject_data.get("tool", {}).get("poetry", {})
    clarity_section = pyproject_data.get("tool", {}).get("cyclarity", {})
    if not poetry_section:
        raise StopCommand("No [tool.poetry] section found in pyproject.toml")
    step_name = clarity_section.get("pretty_name")
    if not step_name:
        step_name = poetry_section.get("name")
    step_to_upload = {
        "step_name": step_name,
        "step_version": poetry_section.get("version"),
        "description": poetry_section.get("description", ""),
        "step_type": "EB_Component",
        "step_subtype": "Action",
        "tags": poetry_section.get("keywords", []),
        "execution_config": {"entrypoint": "", "running_env": "batch"},
        "zip_schema_file": None,
        "icon_file": None,
    }
    step_to_upload = validate_step_metadata(step_to_upload)
    add_entrypoint_and_running_env(
        step_to_upload, clarity_section, default_entrypoint, default_running_env
    )

    # Extract running environment from dependencies and python version
    # Handle poetry v1 version specifiers like ^3.10, ~3.10, >=3.10, etc
    python_version = (
        poetry_section.get("dependencies", {})
        .get("python", "")
        .replace("^", ">=")
        .replace("~", ">=")
    )
    validate_python_version(python_version)
    return step_to_upload, clarity_section


def update_version_in_toml(pyproject_data: dict, step_to_upload: dict) -> dict:
    if "project" in pyproject_data:
        pyproject_data["project"]["version"] = step_to_upload["step_version"]
    elif "tool" in pyproject_data and "poetry" in pyproject_data["tool"]:
        pyproject_data["tool"]["poetry"]["version"] = step_to_upload["step_version"]
    return pyproject_data


def handle_new_version(
    step_to_upload: dict, step_id: str, domain: str, headers: dict, pyproject_data: dict
) -> str:
    try:
        version = Version(step_to_upload["step_version"])
        new_version = f"{version.major}.{version.minor}.{version.micro + 1}"
        out.ok(
            f"Bumped version from {step_to_upload['step_version']} to {new_version}")
        step_to_upload["step_version"] = new_version
        # Create new step with bumped version
        step_id, _ = out.run_sync_function(
            "Creating step with new version",
            create_step,
            step_to_upload=step_to_upload,
            domain=domain,
            headers=headers,
        )
        if not step_id:
            raise StopCommand("Couldn't create new component version")
        pyproject_data = update_version_in_toml(pyproject_data, step_to_upload)
        return step_id, pyproject_data
    except ValueError:
        raise StopCommand(
            f"Invalid version format: {step_to_upload['step_version']}. Version must follow semantic versioning"
        )


def get_step_to_upload(
    pyproject_data: dict,
    clarity_section: dict,
    default_entrypoint: str,
    default_running_env: str,
) -> tuple[dict, dict]:
    # Check if the TOML has v2 format by looking for specific v2 fields
    is_v2 = "project" in pyproject_data
    if is_v2:
        step_to_upload, clarity_section = create_step_metadata_from_poetry_v2(
            pyproject_data, clarity_section, default_entrypoint, default_running_env
        )
    else:
        step_to_upload, clarity_section = create_step_metadata_from_poetry_v1(
            pyproject_data, clarity_section, default_entrypoint, default_running_env
        )
    return step_to_upload, clarity_section


def handle_upload_url_options(
    step_id: str,
    domain: str,
    headers: dict,
    step_to_upload: dict,
    pyproject_data: dict,
    is_override: bool = False,
) -> tuple[str, str]:
    url_to_upload = out.run_sync_function(
        "Getting url to upload component",
        get_upload_url,
        step_id=step_id,
        domain=domain,
        headers=headers,
        is_override=is_override,
    )
    if url_to_upload.get("type") == "success":
        pass
    elif url_to_upload.get("type") == "override":
        out.warning(
            "Step is in use by expert builder flows, please select Override to update the content or bump version to create a new step"
        )
        answer = input.ask_for_confirmation(
            "Do you want to override the step?")
        if answer:
            url_to_upload = out.run_sync_function(
                "Getting url to upload component",
                get_upload_url,
                step_id=step_id,
                domain=domain,
                headers=headers,
                is_override=True,
            )
        else:
            input.ask_for_confirmation(
                "Do you want to bump the step version?", hard_stop=True
            )
            step_id, pyproject_data = handle_new_version(
                step_to_upload, step_id, domain, headers, pyproject_data
            )
            url_to_upload = out.run_sync_function(
                "Getting url to upload component",
                get_upload_url,
                step_id=step_id,
                domain=domain,
                headers=headers,
            )

    elif url_to_upload.get("type") == "bump":
        out.warning(
            "Step is in use by deployed flows, please bump version to create a new step"
        )
        input.ask_for_confirmation(
            "Do you want to bump the step version?", hard_stop=True
        )
        step_id, pyproject_data = handle_new_version(
            step_to_upload, step_id, domain, headers, pyproject_data
        )
        url_to_upload = out.run_sync_function(
            "Getting url to upload component",
            get_upload_url,
            step_id=step_id,
            domain=domain,
            headers=headers,
        )
    return url_to_upload, step_id, pyproject_data


def check_component_status(step_id: str, domain: str, headers: dict) -> str:
    while True:
        update_url = f"{domain}/{SPECIFIC_STEP.format(step_id=step_id)}"
        response = requests.get(update_url, headers=headers)
        if response.status_code != 200:
            out.vprint(response.text)
            raise StopCommand("Failed to check component status")
        else:
            full_status = response.json().get("deploy_metadata")
            status = full_status.get("compilation_status", "RUNNING")
            error_message = full_status.get("error_message")
            if status == "RUNNING":
                out.vprint("Component is being parsed, please wait...")
                time.sleep(1)
            elif status == "SUCCESS" and not error_message:
                out.ok("Component parsed successfully")
                return full_status
            elif status == "SUCCESS" and error_message:
                out.error(
                    out.bold(
                        "Component parsing failed, check the error message below")
                )
                out.error(error_message)
                raise StopCommand("Component parsing failed")
            else:
                out.error(
                    out.bold(
                        "Component parsing failed, check the error message below")
                )
                out.error(error_message) if error_message else out.error(
                    "Please contact system administrator"
                )
                raise StopCommand("Component parsing failed")


def parse_and_upload_poetry_package(
    package_dir: str,
    workspace_id: str,
    domain: str,
    auth_token: str,
    default_entrypoint: str,
    default_running_env: str,
    pyc: bool,
) -> str:
    """
    Parse a Poetry package, extract key parameters, zip the package, and upload it to a server.

    Args:
        package_dir: Path to the Poetry package directory
        workspace_id: ID of the workspace to upload to
        domain: Domain URL for the server
        auth_token: Authentication token for the API

    Returns:
        str: The ID of the created or updated step
    """
    headers = {"Authorization": f"Bearer {auth_token}",
               "workspace": workspace_id}
    # Ensure the package directory exists
    package_path = Path(package_dir)
    if not package_path.exists() or not package_path.is_dir():
        raise StopCommand(
            f"Package directory {package_dir} does not exist or is not a directory"
        )

    # Find and parse the pyproject.toml file
    pyproject_path = package_path / "pyproject.toml"
    if not pyproject_path.exists():
        raise StopCommand(f"pyproject.toml not found in {package_dir}")

    # Parse the TOML file
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomli.load(f)

    clarity_section = pyproject_data.get("tool", {}).get("cyclarity", {})

    step_to_upload, clarity_section = get_step_to_upload(
        pyproject_data, clarity_section, default_entrypoint, default_running_env
    )

    out.vprint("Creating step")
    step_id, success = out.run_sync_function(
        "Creating step",
        create_step,
        step_to_upload=step_to_upload,
        domain=domain,
        headers=headers,
    )
    if not success:
        answer = input.ask_for_confirmation(
            "Could not create step, would you like to bump the version?"
        )
        if answer:
            step_id, pyproject_data = handle_new_version(
                step_to_upload, step_id, domain, headers, pyproject_data
            )
        else:
            input.ask_for_confirmation(
                "would you like to override the component?", hard_stop=True
            )
    if not step_id:
        raise StopCommand(
            "Couldn't create/update step, please check your project name and version in pyproject.toml file"
        )

    if "tool" not in pyproject_data:
        pyproject_data["tool"] = {}
    pyproject_data["tool"]["cyclarity"] = clarity_section

    # Write back to pyproject.toml
    out.vprint(f"Updating pyproject.toml with step_id: {step_id}")
    with open(pyproject_path, "w") as f:
        # Format the TOML data with proper indentation
        toml_str = tomli_w.dumps(pyproject_data)
        f.write(toml_str)
    upload_response_data, new_step_id, pyproject_data = handle_upload_url_options(
        step_id,
        domain,
        headers,
        step_to_upload,
        pyproject_data,
        is_override=(not success),
    )
    if new_step_id != step_id:
        out.vprint(f"Updating pyproject.toml with step_id: {new_step_id}")
        with open(pyproject_path, "w") as f:
            # Format the TOML data with proper indentation
            toml_str = tomli_w.dumps(pyproject_data)
            f.write(toml_str)
    url_to_upload = upload_response_data.get("url")
    out.run_sync_function(
        "Zipping and uploading component",
        zip_and_upload_step,
        step_to_upload=step_to_upload,
        package_dir=package_dir,
        url_to_upload=url_to_upload,
        pyc=pyc,
    )
    out.ok("Uploaded new zip file successfully")
    out.run_sync_function(
        "Server is parsing component",
        check_component_status,
        step_id=step_id,
        domain=domain,
        headers=headers,
    )
    return step_id


def trigger_report_generation(token, workspace_id, domain, report_type, execution_id, project_id, execution_counter, test_ids, result_types):
    """Trigger report generation for an execution"""
    headers = {"Authorization": f"Bearer {token}", "workspace": workspace_id}
    url = f"{domain}/{REPORT_TRIGGER_PATH.format(report_type=report_type, execution_id=execution_id, project_id=project_id, execution_counter=execution_counter, test_ids=test_ids, result_types=result_types)}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return True
    else:
        out.vprint("Error triggering report generation")
        out.vprint(response.text)
        raise StopCommand("Couldn't trigger report generation")


def check_report_status_and_get_url(token, workspace_id, domain, execution_id, project_id, execution_counter, test_ids="", report_type=None):
    report_type = "PDFLINK" if report_type == "PDFDATA" else "CSVLINK"
    """Check report status and get presigned URL if completed"""
    headers = {"Authorization": f"Bearer {token}", "workspace": workspace_id}
    url = f"{domain}/{REPORT_STATUS_PATH.format(report_type=report_type, execution_id=execution_id, project_id=project_id, execution_counter=execution_counter, test_ids=test_ids)}"
    response = requests.get(url, headers=headers)

    # Return the response in the same format as your backend
    if response.status_code == 200:
        try:
            body = response.json()
            return {
                'status_code': 200,
                'body': body
            }
        except Exception:
            # If response is not JSON, treat as error
            return {
                'status_code': 500,
                'body': {'message': 'Invalid response format from server'}
            }
    elif response.status_code == 400:
        try:
            body = response.json()
            return {
                'status_code': 400,
                'body': body
            }
        except Exception:
            return {
                'status_code': 400,
                'body': {'message': 'Report generation has failed'}
            }
    else:
        out.vprint("Error checking report status")
        out.vprint(response.text)
        return {
            'status_code': response.status_code,
            'body': {'message': f'Server error: {response.status_code}'}
        }
