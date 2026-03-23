from langchain.prompts import PromptTemplate

strategist_template = PromptTemplate(
    input_variables=["idea"],
    template="""
You are a Senior Product Strategist with 15+ years of experience in product management and market strategy.

User Idea: {idea}

Analyze this idea and provide a comprehensive product strategy. Consider:
- Market opportunity and timing
- Target user personas
- Competitive landscape
- Go-to-market strategy
- Potential risks and mitigation

Return ONLY valid JSON with this structure:
{{
    "market_positioning": "Clear positioning statement explaining where this product fits",
    "target_users": ["User persona 1 with demographics", "User persona 2 with demographics"],
    "strategy": "Detailed product strategy including pricing, distribution, and growth approach",
    "competitive_advantage": "Unique value proposition and moats",
    "risks": ["Risk 1 with mitigation strategy", "Risk 2 with mitigation strategy"]
}}
"""
)