# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Agent-to-Agent (A2A) communication protocol for research coordination."""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class MessageType(Enum):
    """Types of A2A messages."""

    RESEARCH_REQUEST = "research_request"
    RESEARCH_RESULTS = "research_results"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    VALIDATION_REQUEST = "validation_request"
    VALIDATION_RESPONSE = "validation_response"


class MessagePriority(Enum):
    """Message priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class A2AMessage:
    """Message structure for Agent-to-Agent communication."""

    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    receiver: str = ""
    message_type: MessageType = MessageType.RESEARCH_REQUEST
    priority: MessagePriority = MessagePriority.NORMAL
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    correlation_id: Optional[str] = None  # For tracking request-response pairs
    timeout_seconds: int = 300

    def to_dict(self) -> Dict:
        """Convert message to dictionary."""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "timeout_seconds": self.timeout_seconds
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "A2AMessage":
        """Create message from dictionary."""
        return cls(
            message_id=data.get("message_id", str(uuid.uuid4())),
            sender=data.get("sender", ""),
            receiver=data.get("receiver", ""),
            message_type=MessageType(data.get("message_type", "research_request")),
            priority=MessagePriority(data.get("priority", "normal")),
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            correlation_id=data.get("correlation_id"),
            timeout_seconds=data.get("timeout_seconds", 300)
        )


class ResearchCoordinationProtocol:
    """
    Agent-to-Agent (A2A) Protocol for research coordination.

    Implements message-based communication between agents in the
    MedResearch AI system, enabling distributed research workflows.
    """

    def __init__(self):
        """Initialize A2A protocol."""
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.pending_responses: Dict[str, A2AMessage] = {}
        self.message_handlers: Dict[str, List] = {}
        self.message_log: List[A2AMessage] = []

    async def send_message(self, message: A2AMessage) -> str:
        """
        Send a message to another agent.

        Args:
            message: A2AMessage to send

        Returns:
            Message ID
        """
        # Log the message
        self.message_log.append(message)

        # Add to queue
        await self.message_queue.put(message)

        # If expecting response, track correlation
        if message.correlation_id is None and message.message_type in [
            MessageType.RESEARCH_REQUEST,
            MessageType.VALIDATION_REQUEST
        ]:
            message.correlation_id = message.message_id

        return message.message_id

    async def send_research_request(
        self,
        from_agent: str,
        to_agent: str,
        query: str,
        **kwargs
    ) -> str:
        """
        Send research request to another agent.

        Args:
            from_agent: Sender agent name
            to_agent: Receiver agent name
            query: Research query
            **kwargs: Additional parameters

        Returns:
            Message ID
        """
        message = A2AMessage(
            sender=from_agent,
            receiver=to_agent,
            message_type=MessageType.RESEARCH_REQUEST,
            priority=MessagePriority.HIGH,
            payload={
                "query": query,
                **kwargs
            }
        )

        return await self.send_message(message)

    async def send_research_results(
        self,
        from_agent: str,
        to_agent: str,
        results: Dict,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Send research results to another agent.

        Args:
            from_agent: Sender agent name
            to_agent: Receiver agent name
            results: Research results
            correlation_id: ID of original request

        Returns:
            Message ID
        """
        message = A2AMessage(
            sender=from_agent,
            receiver=to_agent,
            message_type=MessageType.RESEARCH_RESULTS,
            priority=MessagePriority.NORMAL,
            payload=results,
            correlation_id=correlation_id
        )

        return await self.send_message(message)

    async def send_status_update(
        self,
        from_agent: str,
        to_agent: str,
        status: str,
        progress: Dict
    ) -> str:
        """
        Send status update to another agent.

        Args:
            from_agent: Sender agent name
            to_agent: Receiver agent name
            status: Current status
            progress: Progress information

        Returns:
            Message ID
        """
        message = A2AMessage(
            sender=from_agent,
            receiver=to_agent,
            message_type=MessageType.STATUS_UPDATE,
            priority=MessagePriority.LOW,
            payload={
                "status": status,
                "progress": progress
            }
        )

        return await self.send_message(message)

    async def receive_message(self, timeout: Optional[int] = None) -> Optional[A2AMessage]:
        """
        Receive next message from queue.

        Args:
            timeout: Timeout in seconds

        Returns:
            A2AMessage if available, None if timeout
        """
        try:
            if timeout:
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=timeout
                )
            else:
                message = await self.message_queue.get()

            return message
        except asyncio.TimeoutError:
            return None

    async def wait_for_response(
        self,
        correlation_id: str,
        timeout: int = 300
    ) -> Optional[A2AMessage]:
        """
        Wait for a response to a previous message.

        Args:
            correlation_id: ID of original message
            timeout: Timeout in seconds

        Returns:
            Response message if received, None if timeout
        """
        start_time = asyncio.get_event_loop().time()

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                return None

            message = await self.receive_message(timeout=1)
            if message and message.correlation_id == correlation_id:
                return message

    def register_handler(self, message_type: MessageType, handler):
        """
        Register a handler for a message type.

        Args:
            message_type: Type of message to handle
            handler: Async function to handle messages
        """
        if message_type.value not in self.message_handlers:
            self.message_handlers[message_type.value] = []

        self.message_handlers[message_type.value].append(handler)

    async def process_messages(self):
        """
        Process messages from queue using registered handlers.

        This should run as a background task.
        """
        while True:
            message = await self.receive_message()
            if message:
                handlers = self.message_handlers.get(message.message_type.value, [])
                for handler in handlers:
                    try:
                        await handler(message)
                    except Exception as e:
                        print(f"Error in message handler: {e}")

    def get_message_log(
        self,
        sender: Optional[str] = None,
        receiver: Optional[str] = None,
        limit: int = 100
    ) -> List[A2AMessage]:
        """
        Get message log with optional filtering.

        Args:
            sender: Filter by sender
            receiver: Filter by receiver
            limit: Maximum messages to return

        Returns:
            List of messages
        """
        messages = self.message_log

        if sender:
            messages = [m for m in messages if m.sender == sender]
        if receiver:
            messages = [m for m in messages if m.receiver == receiver]

        return messages[-limit:]

    def get_statistics(self) -> Dict:
        """
        Get protocol statistics.

        Returns:
            Dictionary with statistics
        """
        if not self.message_log:
            return {
                "total_messages": 0,
                "by_type": {},
                "by_sender": {},
                "by_receiver": {}
            }

        by_type = {}
        by_sender = {}
        by_receiver = {}

        for msg in self.message_log:
            # Count by type
            msg_type = msg.message_type.value
            by_type[msg_type] = by_type.get(msg_type, 0) + 1

            # Count by sender
            by_sender[msg.sender] = by_sender.get(msg.sender, 0) + 1

            # Count by receiver
            by_receiver[msg.receiver] = by_receiver.get(msg.receiver, 0) + 1

        return {
            "total_messages": len(self.message_log),
            "by_type": by_type,
            "by_sender": by_sender,
            "by_receiver": by_receiver
        }
