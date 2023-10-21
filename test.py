import json
import pathlib

from dotenv import load_dotenv

import openai
from langchain.llms import OpenAI
from langchain.docstore import Wikipedia
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.agents.react.base import DocstoreExplorer
from langchain.agents import load_tools
from langchain.tools import StructuredTool


load_dotenv(dotenv_path=pathlib.Path('.env'))

llm = OpenAI(temperature=0) #gpt-3.5-turbo-16k # model_name="gpt-3.5-turbo"

react = initialize_agent([], llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

react.