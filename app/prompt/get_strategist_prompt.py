from langchain.prompts import PromptTemplate

strategist_template = PromptTemplate(
    input_variables=["idea"],
    template="""
You are a Product Strategist.

User Idea:
{idea}

Return ONLY valid JSON:

{
  "market_positioning": "",
  "target_users": [],
  "strategy": ""
}
"""
)