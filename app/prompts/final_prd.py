"""Final PRD Prompt Template"""

from langchain.prompts import PromptTemplate

final_prd_template = PromptTemplate(
    input_variables=[
        "user_input", 
        "strategist_output", 
        "market_research", 
        "prd_draft",
        "tech_architecture",
        "ux_design",
        "qa_strategy"
    ],
    template="""
You are a Senior Technical Product Manager with 15+ years of experience in enterprise software.

## ALL COLLECTED INPUTS:

### Original Idea:
{user_input}

### Strategic Analysis (Strategist):
{strategist_output}

### Market Research:
{market_research}

### Feature Draft (PRD Draft):
{prd_draft}

### Technical Architecture:
{tech_architecture}

### UX Design:
{ux_design}

### QA Strategy:
{qa_strategy}

---

## YOUR TASK:
Synthesize ALL inputs above into a single, comprehensive, and actionable Product Requirements Document (PRD).

## IMPORTANT RULES:
1. **Resolve Conflicts**: If different agents have conflicting information, use the most recent or most detailed
2. **Don't Add New Info**: Only use information from the inputs above
3. **Be Specific**: Include actual numbers, timelines, and measurable targets
4. **Prioritize**: Clearly mark P0 (must-have), P1 (should-have), P2 (nice-to-have)
5. **Be Actionable**: Engineers should be able to start coding from this PRD

---

## OUTPUT FORMAT (Return ONLY valid JSON):

{{
    "product_name": "Name derived from idea and strategy",
    "executive_summary": {{
        "vision": "One-line product vision",
        "problem_statement": "What problem does this solve?",
        "target_users": ["User persona 1", "User persona 2"]
    }},
    
    "features": [
        {{
            "id": "F1",
            "name": "Feature name",
            "description": "Detailed description",
            "priority": "P0/P1/P2",
            "effort": "High/Medium/Low",
            "dependencies": ["F2", "external_api"],
            "acceptance_criteria": ["Criteria 1", "Criteria 2"]
        }}
    ],
    
    "technical_specifications": {{
        "backend_apis": [
            {{
                "endpoint": "/api/v1/resource",
                "method": "GET/POST/PUT/DELETE",
                "description": "What it does",
                "request": {{"param": "type"}},
                "response": {{"result": "type"}}
            }}
        ],
        "database_schema": [
            {{
                "table": "users",
                "columns": [
                    {{"name": "id", "type": "UUID", "constraints": "primary_key"}},
                    {{"name": "email", "type": "VARCHAR(255)", "constraints": "unique, not_null"}}
                ]
            }}
        ],
        "tech_stack": {{
            "backend": ["FastAPI", "PostgreSQL", "Redis"],
            "frontend": ["React", "Tailwind"],
            "infrastructure": ["Docker", "AWS ECS"]
        }},
        "security_requirements": ["Authentication via JWT", "Rate limiting", "Data encryption at rest"]
    }},
    
    "user_experience": {{
        "user_flows": [
            {{
                "flow_name": "User Onboarding",
                "steps": ["Sign up", "Verify email", "Complete profile", "Dashboard"]
            }}
        ],
        "key_screens": ["Login", "Dashboard", "Settings"],
        "design_constraints": ["Mobile responsive", "Dark mode support"]
    }},
    
    "success_metrics": [
        {{
            "metric": "User Adoption",
            "target": "10,000 users in Q1",
            "measurement": "Daily active users"
        }},
        {{
            "metric": "Engagement",
            "target": "30 minutes/day",
            "measurement": "Average session duration"
        }},
        {{
            "metric": "Revenue",
            "target": "$50,000 MRR",
            "measurement": "Monthly recurring revenue"
        }}
    ],
    
    "timeline": {{
        "phase_1_mvp": {{
            "duration": "6 weeks",
            "features": ["F1", "F2"],
            "milestones": ["Database setup", "API development", "MVP launch"]
        }},
        "phase_2": {{
            "duration": "8 weeks",
            "features": ["F3", "F4", "F5"],
            "milestones": ["Advanced features", "Optimization", "Beta release"]
        }},
        "phase_3": {{
            "duration": "4 weeks",
            "features": ["F6", "F7"],
            "milestones": ["Scale", "Analytics", "Public launch"]
        }}
    }},
    
    "risks_and_mitigations": [
        {{
            "risk": "Technical: API rate limits",
            "impact": "High",
            "mitigation": "Implement caching and queue system"
        }},
        {{
            "risk": "Business: Competitor launch",
            "impact": "Medium",
            "mitigation": "Focus on unique differentiator: AI personalization"
        }}
    ],
    
    "dependencies": [
        {{
            "dependency": "Payment gateway integration",
            "owner": "Finance team",
            "deadline": "Week 4"
        }},
        {{
            "dependency": "Third-party API access",
            "owner": "External vendor",
            "deadline": "Week 2"
        }}
    ],
    
    "open_questions": [
        "What is the exact pricing model?",
        "Do we need SOC2 compliance in phase 1?"
    ]
}}
"""
)