from datetime import datetime
from uuid import uuid4
from uagents import Agent, Protocol, Context
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)
import asyncio
import sys


def run_agent_chat(agent2_address=None, initial_text=None):
    # Ask user to enter recipient agent address and message if not provided
    if not agent2_address:
        agent2_address = input("Enter the recipient agent address: ").strip()
    if not initial_text:
        initial_text = input("Enter the message to send: ").strip()

    # Initialize agent1
    agent = Agent(
        name="chat-agent",
        seed="chat-agent",
        port=8000,
        mailbox=True
    )

    # Initialize chat protocol
    chat_proto = Protocol(spec=chat_protocol_spec)

    # Startup handler to send the initial message
    @agent.on_event("startup")
    async def startup_handler(ctx: Context):
        ctx.logger.info(f"My name is {ctx.agent.name} and my address is {ctx.agent.address}")
        initial_message = ChatMessage(
            timestamp=datetime.utcnow(),
            msg_id=uuid4(),
            content=[TextContent(type="text",
                                 text=initial_text
            )
            ]
        )
        await ctx.send(agent2_address, initial_message)
        ctx.logger.info(f"Sent message to {agent2_address}: {initial_text}")

    # Message handler
    @chat_proto.on_message(ChatMessage)
    async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
        for item in msg.content:
            if isinstance(item, TextContent):
                ctx.logger.info(f"Received message from {sender}: {item.text}")
        ack = ChatAcknowledgement(
            timestamp=datetime.utcnow(),
            acknowledged_msg_id=msg.msg_id
        )
        await ctx.send(sender, ack)
        # Auto-exit after first response
        ctx.logger.info("Exiting agent chat after first response.")
        sys.exit(0)

    # Acknowledgement handler
    @chat_proto.on_message(ChatAcknowledgement)
    async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
        ctx.logger.info(f"Received acknowledgement from {sender} for message ID: {msg.acknowledged_msg_id}")

    # Include chat protocol
    agent.include(chat_proto, publish_manifest=True)

    agent.run()
