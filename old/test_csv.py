import os
import pandas as pd
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

from langchain_experimental.agents import create_pandas_dataframe_agent, create_csv_agent
from langchain.agents.agent_types import AgentType
import pandas as pd

os.environ["OPENAI_API_KEY"] = "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"

df = pd.read_csv("/workspaces/FinGPT/data/July 23 Graphs.xlsx_Posted Sales Invoice Lines.csv")

pd_agent = create_pandas_dataframe_agent(OpenAI(temperature=0), 
                         df, 
                         verbose=True)

pd_agent.run("What is survival rate of onboarded passenger?")