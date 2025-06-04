#built-in imports
from langchain.agents import AgentExecutor
from langchain_core.agents import create_tool_calling_agent

#custom imports
from tools.__init__ import all_tools
from llm_utils.llm_client import llm_client
from message_template.template_ import template_

llm = llm_client()
tools = all_tools()
template_final = template_()

agent = create_tool_calling_agent(llm, tools,template_final)

agent_executor = AgentExecutor(
    agent = agent, 
    tools = tools,
    early_stopping_method= "generate",
    return_intermediate_steps= False,
    handle_parsing_errors= True,
    verbose= True
    )
