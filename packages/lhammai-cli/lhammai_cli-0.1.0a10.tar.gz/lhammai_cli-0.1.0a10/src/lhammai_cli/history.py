import json
import threading
from datetime import datetime
from uuid import UUID, uuid4

from lhammai_cli.schema import Conversation, ConversationMetadata, HistoryFile, Message, Role
from lhammai_cli.settings import settings
from lhammai_cli.utils import logger

HISTORY_FILE = settings.history_file


class ConversationHistory:
    """Manages conversation history with LLMs, supporting persistence and retrieval."""

    def __init__(self, conversation_uuid: UUID, conversation: Conversation):
        """Initialize the conversation history manager.

        Args:
            conversation_uuid: UUID of the current conversation
            conversation: The current conversation object
        """
        self._lock = threading.Lock()
        self._current_uuid: UUID = conversation_uuid
        self._current_conversation: Conversation = conversation

    @staticmethod
    def init_history() -> None:
        """Initialize the conversation history file."""
        if not HISTORY_FILE.exists() or (HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size == 0):
            with HISTORY_FILE.open("w", encoding="utf-8") as f:
                json.dump({}, f)

    @classmethod
    def clear_all_history(cls) -> None:
        """Clear all conversation history from disk and memory.
        
        Raises:
            FileNotFoundError: If the history file does not exist
        """
        try:
            if HISTORY_FILE.exists():
                HISTORY_FILE.unlink()

            logger.debug("Cleared all conversation history. Creating new history file.")
            cls.init_history()

        except FileNotFoundError:
            logger.warning("History file not found. Initializing new history file.")
            cls.init_history()
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            raise

    @classmethod
    def load_history_from_disk(cls) -> dict[str, Conversation]:
        """Load conversation history from disk.

        Returns:
            Dictionary mapping UUIDs to conversation objects
        
        Raises:
            FileNotFoundError: If the history file does not exist
            json.JSONDecodeError: If the history file is not valid JSON
        """
        try:
            with HISTORY_FILE.open(encoding="utf-8") as f:
                raw_data = json.load(f)
        
            history_file = HistoryFile.model_validate(raw_data)
            return history_file.root

        except FileNotFoundError as e:
            logger.warning("History file not found. Initializing new history file.")
            cls.init_history()
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Could not parse history file: {e}")
            raise json.JSONDecodeError("Failed to parse history file, invalid JSON.", doc=e.doc, pos=e.pos) from e
        except Exception as e:
            logger.error(f"Failed to load history from disk: {e}")
            raise

    @classmethod
    def delete_conversation(cls, conversation_uuid: str) -> bool:
        """Delete a conversation by its UUID.

        Args:
            conversation_uuid: UUID of the conversation to delete

        Returns:
            True if conversation was deleted, False if it didn't exist

        Raises:
            ValueError: If UUID format is invalid
        """
        try:
            UUID(conversation_uuid)
        except ValueError as e:
            raise ValueError(f"Invalid UUID format: {conversation_uuid}") from e

        try:
            history = cls.load_history_from_disk()

            if conversation_uuid not in history:
                return False

            # Remove conversation
            del history[conversation_uuid]

            # Save back to disk using Pydantic serialization
            history_file = HistoryFile(root=history)
            with HISTORY_FILE.open("w", encoding="utf-8") as f:
                json.dump(history_file.model_dump(), f, indent=2, ensure_ascii=False, default=str)

            logger.debug(f"Deleted conversation {conversation_uuid}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete conversation {conversation_uuid}: {e}")
            raise Exception(f"Failed to delete conversation {conversation_uuid}") from e

    @classmethod
    def start_new(cls, model: str, api_base: str) -> "ConversationHistory":
        """Start a new conversation, saving the current one if it exists.

        Args:
            model: The LLM model to use (e.g., 'ollama:gemma3:4b')
            api_base: The API endpoint to use

        Returns:
            The UUID of the new conversation as a string
        """
        uuid = uuid4()
        metadata = ConversationMetadata(model=model, api_base=api_base, start_time=datetime.now(), message_count=0)
        conversation = Conversation(metadata=metadata, messages=[])

        cls.init_history()

        logger.debug(f"Started new conversation {uuid}")

        return cls(conversation_uuid=uuid, conversation=conversation)

    @classmethod
    def load_from_disk(cls, uuid: UUID) -> "ConversationHistory":
        """Load a conversation from disk.

        Args:
            uuid: The UUID of the conversation to load

        Returns:
            The loaded ConversationHistory object
        """
        history = cls.load_history_from_disk()
        if uuid not in history:
            raise ValueError(f"Conversation {uuid} not found in history")

        conversation = history[str(uuid)]
        return cls(conversation_uuid=uuid, conversation=conversation)

    @classmethod
    def list_conversation_uuids(cls) -> list[str]:
        """List all conversation UUIDs.

        Returns:
            List of conversation UUID strings
        """
        history = cls.load_history_from_disk()
        return list(history.keys())

    def add_message(self, role: Role, content: str) -> None:
        """Add a message to the current conversation.

        Args:
            role: The role of the message sender ('user', 'assistant' or 'system')
            content: The content of the message

        Raises:
            ValueError: If role is not 'user', 'assistant' or 'system'
            RuntimeError: If no conversation has been started
        """
        if not self._current_conversation:
            raise RuntimeError("No conversation started. Call `ConversationHistory.start_new()` first.")

        # Validate the message using Pydantic model
        message = Message(role=role, content=content)

        with self._lock:
            self._current_conversation.messages.append(message)
            self._current_conversation.metadata.message_count += 1
            logger.debug(f"Added {role} message to conversation {self._current_uuid}")

    def get_current_conversation(self) -> Conversation:
        """Get the current conversation messages as a list of dictionaries.

        The method returns a copy of the current conversation messages to prevent unintended
        external modifications to the internal state of the conversation object.

        Returns:
            List of message dictionaries with 'role' and 'content' keys, empty list if no conversation
        """
        if not self._current_conversation:
            raise RuntimeError("No conversation started. Call `ConversationHistory.start_new()` first.")

        with self._lock:
            return self._current_conversation.model_copy()

    def get_current_uuid(self) -> UUID:
        """Get the UUID of the current conversation.

        Returns:
            The UUID as a string, or None if no current conversation
        """
        if not self._current_conversation:
            raise RuntimeError("No conversation started. Call `ConversationHistory.start_new()` first.")

        with self._lock:
            return self._current_uuid

    def get_current_metadata(self) -> dict[str, str | int | datetime] | None:
        """Get the metadata of the current conversation.

        Returns:
            Dictionary containing conversation metadata, or None if no current conversation
        """
        if not self._current_conversation:
            raise RuntimeError("No conversation started. Call `ConversationHistory.start_new()` first.")

        with self._lock:
            return self._current_conversation.metadata.model_dump()

    def save_to_disk(self) -> None:
        """Save the current conversation to disk."""
        if not self._current_conversation:
            raise RuntimeError("No conversation started. Call `ConversationHistory.start_new()` first.")

        with self._lock:
            self._save_conversation_to_disk(self._current_uuid, self._current_conversation)

    def _save_conversation_to_disk(self, conversation_uuid: UUID, conversation: Conversation) -> None:
        """Save a specific conversation to disk.

        Args:
            conversation_uuid: UUID of the conversation
            conversation: Conversation object to save
        """
        try:
            # Load existing history
            existing_history = self.load_history_from_disk()

            # Add/update conversation
            existing_history[str(conversation_uuid)] = conversation

            # Save back to disk using Pydantic serialization
            history_file = HistoryFile(root=existing_history)
            with HISTORY_FILE.open("w", encoding="utf-8") as f:
                json.dump(history_file.model_dump(), f, indent=2, ensure_ascii=False, default=str)

            logger.debug(f"Saved conversation {conversation_uuid} to disk")

        except Exception as e:
            logger.error(f"Failed to save conversation to disk: {e}")
            raise
