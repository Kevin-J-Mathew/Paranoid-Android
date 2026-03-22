from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class StorySource(str, Enum):
    JIRA = "jira"
    MANUAL = "manual"
    MOCK = "mock"


class StoryInput(BaseModel):
    story_id: Optional[str] = None
    title: str
    description: str
    acceptance_criteria: Optional[str] = None
    story_type: Optional[str] = "feature"
    source: StorySource = StorySource.MANUAL
    target_url: Optional[str] = None  # Override default target URL


class TestScenario(BaseModel):
    name: str
    description: str
    steps: List[str]
    expected_result: str
    priority: str  # high / medium / low
    test_type: str  # functional / regression / edge_case


class TestResult(BaseModel):
    test_name: str
    status: str  # passed / failed / error / skipped
    duration_ms: float
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    stdout: Optional[str] = None


class RegressionFlag(BaseModel):
    test_name: str
    is_regression: bool
    baseline_pass_rate: Optional[float]
    current_status: str
    severity: str  # critical / warning / none
    explanation: str


class AgentStep(BaseModel):
    agent_name: str
    status: str  # running / completed / failed
    message: str
    timestamp: str
    data: Optional[Dict[str, Any]] = None


class RunRequest(BaseModel):
    story: StoryInput
    run_id: Optional[str] = None


class RunResponse(BaseModel):
    run_id: str
    status: str
    message: str


class FeedbackRequest(BaseModel):
    run_id: str
    test_name: str
    is_false_positive: bool
    notes: Optional[str] = None
