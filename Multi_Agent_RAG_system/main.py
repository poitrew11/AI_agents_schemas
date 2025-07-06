from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver #short-term memory
from langgraph.store.memory import InMemoryStore #long-term memory
from typing_extensions import TypedDict
from typing import Annotated, List
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.managed.is_last_step import RemainingSteps
from langchain_core.tools import tool
from langchain_community.utilities.sql_database import SQLDatabase
import ast
from database_sql import create_my_db
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from subagent import invoice_subagent_prompt, invoice_tools
from nodes import music_assistant, music_tool_node, should_continue
from langgraph_supervisor import create_supervisor
from supervisor import supervisor_prompt
from tools import music_tools

load_dotenv(dotenv_path = ".env", override = True)

llm = ChatOpenAI(model = "meta-llama/Llama-3.3-70B-Instruct", temperature = 0)

in_memory_store = InMemoryStore()
checkpointer = MemorySaver()

class State(TypedDict):
    customer_id: str
    messages: Annotated[list[AnyMessage], add_messages] #Add metadata
    loaded_memory:str
    remaining_steps: RemainingSteps

my_engine = create_my_db()
db = SQLDatabase(my_engine)

llm_with_music_tools = llm.bind_tools(music_tools)
music_workflow = StateGraph(State)
music_workflow.add_node("music_assistant", music_assistant)
music_workflow.add_node("music_tool_node", music_tool_node)

music_workflow.add_edge(START, "music_assistant")
music_workflow.add_conditional_edges(
    "music_assistant",
    should_continue,
    {
        "continue": music_tool_node,
        "end": END
    }
)

music_workflow.add_edge("music_tool_node", "music_assistant")

music_catalog_subagent = music_workflow.compile(name="music_catalog_subagent", checkpointer=checkpointer, store = in_memory_store)

invoice_information_subagent = create_react_agent(
    llm,
    tools = invoice_tools,
    prompt = invoice_subagent_prompt,
    name = "invoice_information_subagent",
    state_schema = State,
    checkpointer = checkpointer,
    store = in_memory_store
)

supervisor_prebuilt_workflow = create_supervisor(
    agents = [invoice_information_subagent, music_catalog_subagent],
    model = llm,
    prompt = (supervisor_prompt),
    output_mode = "last_message",
    state_schema = State
)

supervisor_prebuilt = supervisor_prebuilt_workflow.compile(name = "music_catalog_subagent", checkpointer = checkpointer, store = in_memory_store)
