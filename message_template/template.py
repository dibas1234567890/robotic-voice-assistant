from langchain_core.prompts import(SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, PromptTemplate)

from prompts.system_prompt import system_prompt

def template():

    system_message = SystemMessagePromptTemplate(prompt= PromptTemplate(input_variables=["context","chat_history"], template = system_prompt))

    human_message = HumanMessagePromptTemplate(prompt= PromptTemplate(input_variable =["user_input"], template = "{user_input}"))

    prompt_template =  ChatPromptTemplate.from_messages([system_message, human_message])

    return prompt_template