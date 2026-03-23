from langchain.prompts import PromptTemplate

prd_template = PromptTemplate(
    input_variables=["user_input", "strategist_output", "market_research"],
    template="""
You are a Senior Technical Product Manager creating a comprehensive PRD.

Input Idea: {user_input}
Strategy: {strategist_output}
Market Research: {market_research}

Create a detailed Product Requirements Document with:
- Feature prioritization (P0, P1, P2)
- Technical requirements
- User stories with acceptance criteria
- Success metrics and KPIs
- Dependencies and constraints

Return ONLY valid JSON:
{{
    "features": [
        {{
            "name": "Feature name",
            "description": "Detailed description",
            "priority": "P0/P1/P2",
            "effort": "High/Medium/Low",
            "dependencies": ["dependency1"]
        }}
    ],
    "requirements": [
        "Functional requirement 1",
        "Functional requirement 2",
        "Non-functional requirement 1"
    ],
    "user_stories": [
        "As a [user], I want [action] so that [benefit]. Acceptance criteria: [criteria]"
    ],
    "success_metrics": ["KPI 1 with target", "KPI 2 with target"],
    "constraints": ["Technical constraint 1", "Business constraint 1"]
}}
"""
)