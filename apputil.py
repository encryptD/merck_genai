from ast import Dict, List
from http.client import REQUESTED_RANGE_NOT_SATISFIABLE
import os
import json
from decouple import config
from flask import Flask, request
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI,OpenAI
from langchain.prompts import PromptTemplate
from langchain.agents.structured_chat.base import create_structured_chat_agent,StructuredChatAgent
from langchain.agents import AgentExecutor,Tool,BaseSingleActionAgent,BaseMultiActionAgent
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent import RunnableAgent,RunnableMultiActionAgent
from langchain.tools import BaseTool,tool,StructuredTool
from langchain_core.runnables import Runnable
from langchain import hub
from hdbcli import dbapi
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from gen_ai_hub.proxy.core.credentials import fetch_credentials
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase

from typing import (
    Any,
    AsyncIterator,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)
# from langchain_openai import OpenAI
from langchain.prompts.chat import (
        AIMessagePromptTemplate,
        ChatPromptTemplate,
        HumanMessagePromptTemplate,
        SystemMessagePromptTemplate,
    )
question = "Get the top 1 material for batch T045485 from table zgscm_prtcl_id_rt"
_hdb_usr = config('HDB_USER')
_hdb_pass = config('HDB_PASS')
_hdb_server = config('HDB_SERVER')
engine = create_engine(f'hana://{_hdb_usr}:{_hdb_pass}@{_hdb_server}')
def getTools():
    tools = [ Tool(
                    name = "df1",
                    func=  mybatch , 
                    description="useful for when you need to answer questions about no of table entries"
                ),
                Tool(
                    name = "df2",
                    func= mycus
                    ,
                    description="useful for when you need to search for Customer name against a customer no"
                )

            ]
    return tools
@tool
def mybatch(kk):
    ''' For Count or Table Entries related information refer this'''
    return """DEV_GCS_MOBILE_APP"""+"."+""+kk+""
@tool
def mycus()->int:
    ''' For Customer related information refer this'''
    return 0
LLM_DEPLOYMENT_ID = 'd35ff937f518fe8b'
# _client_id = config("AICORE_CLIENT_ID")
# _auth_url = config("AICORE_AUTH_URL")
# _client_secret = config("AICORE_CLIENT_SECRET")
# _base_url = config("AICORE_BASE_URL")
# _resource_group = config("AICORE_RESOURCE_GROUP")
# Define which model to use
#chat_llm = ChatOpenAI(deployment_id=LLM_DEPLOYMENT_ID)
proxy_client = get_proxy_client('gen-ai-hub')

#agent.invoke({"input": question})


def query(question):
    db = SQLDatabase(engine=engine,schema='DEV_GCS_MOBILE_APP')
   # print(f'{db.get_table_info()}')    
    llm = ChatOpenAI(proxy_model_name='gpt-35-turbo', proxy_client=proxy_client,temperature=0)
    _prompt_ = prompt = hub.pull("hwchase17/structured-chat-agent")
    global _agent
#_agent = Runnable[BaseSingleActionAgent, BaseMultiActionAgent]
    tools = getTools()
    _agent =  create_structured_chat_agent(llm,tools[:1],_prompt_)
    agent_exec = AgentExecutor(agent=_agent,handle_parsing_errors=True,verbose=True,tools=tools[:1])

    sql_agent = agent = create_sql_agent(llm=llm,agent_type='tool-calling',verbose=True,extra_tools=tools,db=db)
    return sql_agent.invoke({"input":question})