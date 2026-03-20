form langchain_prompts import PromptTemplate



prd_template = PromptTemplate(
    input_variables=["user_input","strategy"],
template = """You are a Product Manager writing a PRD.

Input Idea:
{user_input}

Strategy:
{strategy}

Generate:
- Features
- Requirements
- User stories
"""

)