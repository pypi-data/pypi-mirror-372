from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, RootModel, field_validator


class Role(Enum):
    """Defines the roles in a conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """Represents a single message in a conversation."""

    role: Role = Field(..., description="Role of the message sender (user or assistant)")
    content: str = Field(..., description="Content of the message")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: Role) -> Role:
        """Validate that role is either 'user', 'assistant' or 'system'."""
        if v not in (Role.USER, Role.ASSISTANT, Role.SYSTEM):
            raise ValueError(f"Role must be either {Role.USER}, {Role.ASSISTANT} or {Role.SYSTEM}")
        return v

    def model_dump(self, **kwargs) -> dict[str, str]:
        """Return a dictionary with string values for role."""
        result = super().model_dump(**kwargs)
        result["role"] = self.role.value
        return result


class ConversationMetadata(BaseModel):
    """Represents metadata for a conversation."""

    model: str = Field(..., description="The LLM model used (e.g., 'ollama:gemma3:4b')")
    api_base: str = Field(..., description="The API endpoint used")
    start_time: datetime = Field(..., description="When the conversation started")
    message_count: int = Field(default=0, description="Number of messages in the conversation")


class Conversation(BaseModel):
    """Represents a conversation containing multiple messages and metadata."""

    metadata: ConversationMetadata = Field(..., description="Conversation metadata")
    messages: list[Message] = Field(..., description="List of messages in the conversation")

    def model_dump(self, **kwargs) -> dict:
        """Custom serialization to ensure proper role formatting."""
        result = super().model_dump(**kwargs)
        # Ensure messages use custom serialization
        result["messages"] = [msg.model_dump() for msg in self.messages]
        return result


class HistoryFile(RootModel[dict[str, Conversation]]):
    """Represents the structure of the history file.

    The root of the JSON file is a dictionary mapping UUIDs to Conversation objects.
    Format: {uuid1: Conversation, uuid2: Conversation, ...}
    """

    @field_validator("root")
    @classmethod
    def validate_conversations(cls, v: dict[str, Conversation]) -> dict[str, Conversation]:
        """Validate that all keys are valid UUIDs and all conversations are valid."""
        for uuid_str in v.keys():
            try:
                UUID(uuid_str)
            except ValueError as e:
                raise ValueError(f"Invalid UUID format: {uuid_str}") from e
        return v

    def model_dump(self, **kwargs) -> dict:
        """Custom serialization to ensure proper conversation formatting."""
        result = {}
        for uuid_str, conversation in self.root.items():
            result[uuid_str] = conversation.model_dump(**kwargs)
        return result
