from typing import Dict, Any
import asyncio
import boto3
from botocore.config import Config
from langchain_aws import ChatBedrockConverse
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from asap.agent.utils.agents.config import AgentConfig
from asap.agent.utils.agents.migration_assistant_agent import MigrationAssistantAgent
from asap.agent.utils.agents.tools.general.llamagers import BedrockLLamager
from asap.agent.utils.general.ui import with_animation
from asap.agent.utils.agents.tools.translate.translate_tools import translateSQL
from asap.agent.utils.agents.tools.debug.debug_tool import DebugSQLFunction
from asap.agent.utils.agents.tools.general.prompts import MIGRATION_ASSISTANT
from langchain_core.messages import HumanMessage, AIMessage

RESET = '\033[0m'
CYAN = '\033[96m'

class AgentFactory:

    def __init__(self):
        self.llamager = BedrockLLamager.instance("reasoning")
        model = self.llamager.get_model()
        MigrationCheckpointer = InMemorySaver()
        prompt = MIGRATION_ASSISTANT


        # Only store the last 4 messages (user + AI)
        self.conversation_history = []

        config = AgentConfig(model, [translateSQL, DebugSQLFunction], MigrationCheckpointer, prompt)
        self.agent = MigrationAssistantAgent(config)

    def _trim_history(self):
        """Keep only the last 4 messages."""
        if len(self.conversation_history) > 4:
            self.conversation_history = self.conversation_history[-4:]

    
    # @with_animation("Thinking...")
    # async def run(self, user_input: str, thread_id: str):
    #     # Add new user message
    #     self.conversation_history.append(HumanMessage(content=user_input))
    #     self._trim_history()
        
    #     #print(f"[BedrockLLamager] 📌 Current active model: {self.llamager._active_profile}")
        
    #     thread = {"configurable": {"thread_id": thread_id}}
    #     initial_state = {"messages": self.conversation_history, "is_complete": False}

    #     ai_response_text = None
        
    #     async for event in self.agent.graph.astream(initial_state, thread):
    #         for v in event.values():
    #             if 'messages' in v and v['messages']:
    #                 last_message = v['messages'][-1]
    #                 if hasattr(last_message, 'content') and last_message.content:
    #                     ai_response_text = last_message.content
    #                     print(f"{CYAN}aws-proserv:~$ {RESET}Migration Assistant: ")
    #                     print(ai_response_text)

    #     # Save AI response
    #     if ai_response_text:
    #         self.conversation_history.append(AIMessage(content=ai_response_text))
    #         self._trim_history()

        

    #     return ai_response_text
    
    
    def run(self, user_input: str, thread_id: str):
        # Add new user message
        self.conversation_history.append(HumanMessage(content=user_input))
        self._trim_history()

        thread = {"configurable": {"thread_id": thread_id}}
        initial_state = {"messages": self.conversation_history, "is_complete": False}

        ai_response_text = None

        # 🚀 Use sync streaming
        for event in self.agent.graph.stream(initial_state, thread):
            for v in event.values():
                if "messages" in v and v["messages"]:
                    last_message = v["messages"][-1]
                    if hasattr(last_message, "content") and last_message.content:
                        ai_response_text = last_message.content
                        print(f"{CYAN}aws-proserv:~$ {RESET}Migration Assistant: ")
                        print(ai_response_text)

        # Save AI response
        if ai_response_text:
            self.conversation_history.append(AIMessage(content=ai_response_text))
            self._trim_history()

        return ai_response_text




# class AgentFactory:

#     def __init__(self, type: str) :
        
#         model = BedrockLLamager.instance().get_model()
    
#         MigrationCheckpointer = InMemorySaver()  

#         prompt = MIGRATION_ASSISTANT
        
#         config = AgentConfig(model, [translateSQL], MigrationCheckpointer, prompt)
#         self.agent = MigrationAssistantAgent(config)

#     async def run(self, query: str, thread_id: str): 
        
#         messages = [HumanMessage(content=query)]
#         thread = {"configurable": {"thread_id": thread_id}}
#         initial_state = {"messages": messages, "is_complete": False}

#         async for event in self.agent.graph.astream(initial_state, thread):
#             for v in event.values():
#                 if 'messages' in v and v['messages']:
#                     last_message = v['messages'][-1]
#                     if hasattr(last_message, 'content') and last_message.content:
#                         print(last_message.content)
                

