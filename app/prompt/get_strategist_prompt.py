from langchain.prompts import PromptTemplate

strategist_template = PromptTemplate(
    input_variables=["idea"],
    template="""
You are a Product Strategist.

User Idea:
{idea}

Provide:
- Market positioning
- Target users
- High-level strategy
"""
)