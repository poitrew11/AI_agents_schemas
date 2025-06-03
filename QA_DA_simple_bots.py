import os
import sys
sys.path.append(r"C:\Users\elka1\OneDrive\Desktop\tg-test\ai_agent_project\agent_env\Lib\site-packages")
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts import PromptTemplate
load_dotenv()
llm = ChatOpenAI(model = "gpt-4o-mini", max_tokens = 1000, temperature = 0)
store = {}

def get_chat_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant"),
    MessagesPlaceholder(variable_name = "history"),
    ("human", "{input}")
])

chain = prompt | llm

chat_with_history = RunnableWithMessageHistory(
    chain,
    get_chat_history,
    input_messages_key = "input",
    history_messages_key = "history"
)





'''
There will be another bor shcemas for QA
'''





llm = ChatOpenAI(model = 'gpt-4o-mini', max_tokens = 2000, temperature = 0)

template = """
You are a helpful AI assistant. Your task is to answer the user's question to the best of your ability.

User's question: {question}

Please provide a clear and concise answer:
"""

prompt = PromptTemplate(template = template, input_variables = ['question'])
qa_chain = prompt | llm
def get_answer(question):
    input_variables = {"question": question}
    response = qa_chain.invoke(input_variables).content
    return response

'''
Next will be AI-agent for DA
'''

import pandas as pd
import numpy as np
from langchain_experimental.agents.agent_toolkids import create_pandas_dataframe_agent
from langchain.agents import AgentType
from datetime import timedelta, datetime
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
np.random.seed(42)
df = 'your_df'

agent = create_pandas_dataframe_agent(
    ChatOpenAI(model="gpt-4o", temperature=0),
    df,
    verbose=True,
    allow_dangerous_code=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
)
print("Data Analysis Agent is ready. You can now ask questions about the data.")




def ask_agent(question):
    """Function to ask questions to the agent and display the response"""
    response = agent.run({
        "input": question,
        "agent_scratchpad": f"Human: {question}\nAI: To answer this question, I need to use Python to analyze the dataframe. I'll use the python_repl_ast tool.\n\nAction: python_repl_ast\nAction Input: ",
    })
    print(f"Question: {question}")
    print(f"Answer: {response}")
    print("---")
