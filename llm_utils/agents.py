from langchain_core.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from llm import llm_client
from tools.__init__ import all_tools
from message_template.template import template

llm = llm_client()
tools = all_tools()
template_final = template()

agent = create_tool_calling_agent(llm, tools,template_final)

agent_executor = AgentExecutor(agent = agent, tools = tools)
