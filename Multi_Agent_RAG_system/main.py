from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv(dotenv_path = ".env", override = True)

llm = ChatOpenAI(model = "meta-llama/Llama-3.3-70B-Instruct", temperature = 0)


