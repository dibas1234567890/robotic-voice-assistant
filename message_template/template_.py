#built-in imports
from langchain_core.prompts import(SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, PromptTemplate)

#custom imports
from prompts.system_prompt import system_prompt

def template_():
    """Creates a chat prompt template with a system and a human message.

    Returns:
    ChatPromptTemplate: A chat prompt that combines the system prompt with user input.
    
    """

    system_message = SystemMessagePromptTemplate(
        prompt= PromptTemplate(
            input_variables =["context","chat_history"], 
            template = system_prompt
        )
    )

    human_message = HumanMessagePromptTemplate(
        prompt= PromptTemplate(
            input_variables =["user_input"], 
            template = "{user_input}"
        )
    )

    prompt_template =  ChatPromptTemplate.from_messages([system_message, human_message])

    return prompt_template
