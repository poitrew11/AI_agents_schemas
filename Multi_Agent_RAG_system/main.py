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
