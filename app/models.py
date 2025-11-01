"""
Pydantic models for A2A protocol and Telex integration
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import uuid4

# ===== A2A Core Models =====

class MessagePart(BaseModel):
    kind: Literal["text", "data", "file"]
    text: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    file_url: Optional[str] = None

class A2AMessage(BaseModel):
    kind: Literal["message"] = "message"
    role: Literal["user", "agent", "system"]
    parts: List[MessagePart]
    messageId: str = Field(default_factory=lambda: str(uuid4()))
    taskId: Optional[str] = None
    contextId: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TaskStatus(BaseModel):
    state: Literal["working", "completed", "input-required", "failed", "submitted", "canceled", "rejected", "auth-required", "unknown"]
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    message: Optional[A2AMessage] = None

class Artifact(BaseModel):
    artifactId: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    parts: List[MessagePart]

class TaskResult(BaseModel):
    id: str
    contextId: str
    status: TaskStatus
    artifacts: List[Artifact] = []
    history: List[A2AMessage] = []
    kind: Literal["task"] = "task"

# ===== JSON-RPC Models =====

class MessageParams(BaseModel):
    message: A2AMessage
    configuration: Optional[Dict[str, Any]] = None

class ExecuteParams(BaseModel):
    contextId: Optional[str] = None
    taskId: Optional[str] = None
    messages: List[A2AMessage]

class JSONRPCRequest(BaseModel):
    jsonrpc: Literal["2.0"]
    id: Union[str, int]
    method: str
    params: Union[MessageParams, ExecuteParams]

class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None

class JSONRPCResponse(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: Union[str, int, None]
    result: Optional[TaskResult] = None
    error: Optional[JSONRPCError] = None

# ===== Agent Card Models =====

class Provider(BaseModel):
    organization: str
    url: str

class Capabilities(BaseModel):
    streaming: bool
    pushNotifications: bool
    stateTransitionHistory: bool

class SkillExample(BaseModel):
    input: Dict[str, Any]
    output: Dict[str, Any]

class Skill(BaseModel):
    id: str
    name: str
    description: str
    inputModes: List[str]
    outputModes: List[str]
    examples: List[SkillExample]

class AgentCard(BaseModel):
    name: str
    description: str
    url: str
    provider: Provider
    version: str
    documentationUrl: Optional[str] = None
    capabilities: Capabilities
    defaultInputModes: List[str]
    defaultOutputModes: List[str]
    skills: List[Skill]
    supportsAuthenticatedExtendedCard: bool = False
