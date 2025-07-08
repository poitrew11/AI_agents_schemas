from pydantic import BaseModel, Field
from typing import Optional
from main import llm
from database_sql import db
from langchain_core.messages import SystemMessage
import ast
from langgraph.types import interrupt
class UserInput(BaseModel):
    identifier: str = Field(description = "Identifier, which can be a customer ID, email, or phone number.")

structured_llm = llm.with_structured_output(schema = UserInput)
structured_system_prompt = """You are a customer service representative responsible for extracting customer identifier.\n 
Only extract the customer's account information from the message history. 
If they haven't provided the information yet, return an empty string for the file"""

def get_customer_id_from_identifier(identifier: str) -> Optional[int]:

    if identifier.isdigit():
        return int(identifier)
    
    elif identifier[0] == "+":
        query = f"SELECT CustomerId FROM Customer WHERE Phone = '{identifier}';"
        result = db.run(query)
        formatted_result = ast.literal_eval(result)
        if formatted_result:
            return formatted_result[0][0]
        
    elif "@" in identifier:
        query = f"SELECT CustomerId FROM Customer WHERE Email = '{identifier}';"
        result = db.run(query)
        formatted_result = ast.literal_eval(result)
        if formatted_result:
            return formatted_result[0][0]
        
    return None

def verify_info(state, config):
    if state.get("customer_id") is None:
        system_instructions = """You are a music store agent, where you are trying to verify the customer identity 
        as the first step of the customer support process. 
        Only after their account is verified, you would be able to support them on resolving the issue. 
        In order to verify their identity, one of their customer ID, email, or phone number needs to be provided.
        If the customer has not provided the information yet, please ask them for it.
        If they have provided the identifier but cannot be found, please ask them to revise it."""

        user_input = state["messages"][-1]
        parser_info = structured_llm.invoke([SystemMessage(content = structured_system_prompt)] + [user_input])
        identifier = parser_info.identifier
        customer_id = ""
        if (identifier):
            customer_id = get_customer_id_from_identifier(identifier)
    
        if customer_id != "":
            intent_message = SystemMessage(
                content= f"Thank you for providing your information! I was able to verify your account with customer id {customer_id}."
            )
            return {
                  "customer_id": customer_id,
                  "messages" : [intent_message]
                  }
        else:
          response = llm.invoke([SystemMessage(content=system_instructions)]+state['messages'])
          return {"messages": [response]}

    else: 
        pass

def human_input(state, config):
    user_input = interrupt("Please provide input.")
    

    return {"messages": [user_input]}

def should_interrupt(state, config):
    if state.get("customer_id") is not None:
        return "continue"
    else:
        return "interrupt"