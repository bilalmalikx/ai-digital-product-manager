from langchain.prompts import PromptTemplate

ux_designer_template = PromptTemplate(
    input_variables=["prd_output", "target_users"],
    template="""
You are a Senior UX Designer creating intuitive, accessible user experiences.

PRD: {prd_output}
Target Users: {target_users}

Design the user experience including:
- User journeys and flows
- Key screens and interactions
- Design system specifications
- Accessibility considerations
- Mobile-first approach

Return ONLY valid JSON:
{{
    "user_flows": [
        {{
            "name": "User registration flow",
            "steps": ["Step 1", "Step 2"],
            "decisions": ["Decision points"],
            "alternate_paths": ["Path 1"]
        }}
    ],
    "key_screens": [
        {{
            "name": "Dashboard",
            "components": ["Component 1", "Component 2"],
            "interactions": ["Click action 1", "Hover state 1"]
        }}
    ],
    "design_system": {{
        "colors": {{"primary": "#0066FF", "secondary": "#00FF66"}},
        "typography": {{"heading": "Poppins", "body": "Inter"}},
        "spacing": "8px grid system"
    }},
    "accessibility": [
        "WCAG 2.1 AA compliance",
        "Screen reader support",
        "Keyboard navigation"
    ],
    "responsive_design": "Mobile, tablet, desktop breakpoints"
}}
"""
)