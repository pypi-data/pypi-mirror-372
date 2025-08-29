from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from enum import Enum
from pydantic import BaseModel

SUPPORTED_PYTHON_VERSION = "3.10"
# Define the base directory for storing configuration
CONFIG_DIR = Path.home() / '.clarity'
CONFIG_FILE = CONFIG_DIR / 'config.json'
TOKEN_FILE = CONFIG_DIR / 'token.json'

EXECUTION_VIEW_PATH = 'testing/executions/view?executionId={execution_id}&projectId={project_id}'
ALL_EXECUTIONS_VIEW_PATH = 'inv-api/testing/executions/handler?project_id={project_id}&page_size=25&sort_key=execution_counter&sort_type=DESC'
SPECIFIC_EXECUTION_VIEW_PATH = 'inv-api/testing/executions/handler?execution_id={execution_id}&project_id={project_id}'
ALL_PROJECTS_VIEW_PATH = 'inv-api/testing/projects'
DEVICES_LIST = 'inv-api/devices/status'
TEST_LIST = 'inv-api/testing/catalog'
PLAN_LIST = 'inv-api/plan/catalog'
STEP_CREATE = 'inv-api/testing/steps'
STEP_UPLOAD = 'inv-api/testing/steps/{step_id}/upload'
SPECIFIC_STEP = 'inv-api/testing/steps/{step_id}'
GET_EXECUTION_FINDINGS = 'inv-api/testing/executions/history?type=FINDING&execution_id={execution_id}'
REPORT_TRIGGER_PATH = 'inv-api/testing/executions/report?type={report_type}&executionId={execution_id}&project_id={project_id}&execution_counter={execution_counter}&testIds={test_ids}&resultTypes=Finding'
REPORT_STATUS_PATH = 'inv-api/testing/executions/report?type={report_type}&executionId={execution_id}&project_id={project_id}&execution_counter={execution_counter}&testIds={test_ids}'


class RunningEnv(Enum):
    CLOUD = "batch"
    IOT = "iot_device"


class ThemeColors(Enum):
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    CYAN = "cyan"
    WHITE = "white"
    RED = "red"


@dataclass
class TableColumn:
    name: str
    color: Optional[ThemeColors] = ThemeColors.WHITE


class ProfileConfig(BaseModel):
    client_id: str
    client_secret: str
    token_endpoint: str
    scope: str
    project: Optional[str] = ""
    workspace: Optional[str] = ""
    agent: Optional[str] = ""
    domain: str


class InputTypes(Enum):
    integer = int
    string = str
    boolean = bool
