from langchain.prompts import PromptTemplate

prd_template = PromptTemplate(
    input_variables=["user_input", "strategist_output"],
    template="""
You are a Product Manager writing a PRD.

Input Idea:
{user_input}

Strategy:
{strategist_output}

Return ONLY valid JSON:

{
  "features": [],
  "requirements": [],
  "user_stories": []
}
"""
)