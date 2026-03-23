from langchain.prompts import PromptTemplate

tech_architect_template = PromptTemplate(
    input_variables=["prd_output", "strategist_output"],
    template="""
You are a Senior Solutions Architect designing scalable, maintainable systems.

PRD: {prd_output}
Strategy: {strategist_output}

Design a comprehensive technical architecture including:
- Technology stack selection
- System architecture diagram (described in text)
- API design and endpoints
- Database schema
- Security architecture
- Scalability considerations
- Deployment strategy

Return ONLY valid JSON:
{{
    "tech_stack": {{
        "frontend": ["React", "Next.js", "Tailwind"],
        "backend": ["Python/FastAPI", "PostgreSQL", "Redis"],
        "infrastructure": ["AWS", "Docker", "Kubernetes"],
        "monitoring": ["Datadog", "Sentry"]
    }},
    "system_design": "Detailed description of microservices, communication patterns, data flow",
    "api_endpoints": [
        {{
            "method": "POST",
            "endpoint": "/api/v1/resource",
            "description": "Purpose",
            "request": {{}},
            "response": {{}}
        }}
    ],
    "database_schema": [
        {{
            "table": "users",
            "columns": ["id", "name", "email", "created_at"],
            "relationships": ["has_many: orders"]
        }}
    ],
    "security_considerations": ["Auth strategy", "Data encryption", "Compliance"],
    "scalability_plan": "Horizontal scaling strategy, caching, CDN"
}}
"""
)