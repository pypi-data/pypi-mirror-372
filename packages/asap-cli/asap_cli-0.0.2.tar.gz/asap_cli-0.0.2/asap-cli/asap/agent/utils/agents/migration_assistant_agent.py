from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from asap.agent.utils.agents.config import AgentConfig
from asap.agent.utils.general.ui import with_animation

_ = load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    is_complete: bool

checkpointer = InMemorySaver()

class MigrationAssistantAgent:
    def __init__(self, config: AgentConfig):
        self.system = config.system
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_openai)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges(
            "llm", 
            self.should_continue,
            {
                "action": "action",
                "end": END
            }
        )
        graph.add_conditional_edges(
            "action",
            self.check_completion,
            {
                "continue": "llm",
                "end": END
            }
        )
        graph.set_entry_point("llm")
        self.graph = graph.compile(checkpointer=checkpointer)
        self.tools = {t.name: t for t in config.tools}
        self.model = config.model.bind_tools(config.tools)

    @with_animation("Thinking...")
    def call_openai(self, state: AgentState):
        messages = state['messages']
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        return {'messages': [message], 'is_complete': state.get('is_complete', False)}

    def should_continue(self, state: AgentState):
        """Decide whether to take action or end"""
        if state.get('is_complete', False):
            return "end"
        
        result = state['messages'][-1]
        if hasattr(result, 'tool_calls') and len(result.tool_calls) > 0:
            return "action"
        return "end"

    def check_completion(self, state: AgentState):
        """Check if we should continue or end after taking action"""
        if state.get('is_complete', False):
            return "end"
        return "continue"

    def take_action(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        is_complete = False

        for t in tool_calls:
            if t['name'] == 'sql_print':
                sql_query = t['args']['sql_query']
                print(f"\n=== SQL CONVERSION RESULT ===")
                print(f"Converted SQL Query:\n{sql_query}\n")

                approval = input("Do you want to proceed with this SQL query? (y/n): ").strip().lower()

                if approval in ['y', 'yes']:
                    result = f"User approved the SQL query. Final result:\n{sql_query}\n\n🎉 CONVERSION COMPLETED SUCCESSFULLY!"
                    print("\n✅ SQL query approved and printed!")
                    print("🎉 Conversion process completed!")
                    is_complete = True
                    results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=result))

                else:
                    print("\n❌ SQL query was not approved.")
                    feedback = input("\nPlease provide feedback on what needs to be changed or improved:\n> ").strip()

                    if feedback:
                        print(f"\n📝 Feedback received: {feedback}")
                        print("🔄 Processing your feedback...")

                        # Add as ToolMessage so the tool call is "completed"
                        results.append(ToolMessage(
                            tool_call_id=t['id'],
                            name=t['name'],
                            content=f"User provided feedback: '{feedback}'. Please update the SQL query accordingly."
                        ))

                        # ALSO feed this into the LLM as a HumanMessage
                        results.append(HumanMessage(content=feedback))

                    else:
                        print("\n❓ No specific feedback provided.")
                        results.append(ToolMessage(
                            tool_call_id=t['id'],
                            name=t['name'],
                            content="User declined approval but provided no specific feedback. Please ask for clarification."
                        ))
                        results.append(HumanMessage(content="The query needs changes, but the user didn't specify what. Ask for clarification."))

            else:
                # Handle other tools normally
                print(f"Calling: {t}")
                result = self.tools[t['name']].invoke(t['args'])
                results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))

        if not is_complete:
            pass 
            #print("Back to the model!")

        return {
            'messages': results,
            'is_complete': is_complete
        }