def get_strategist_prompt(user_input: str) -> str:
    return f"""
You are a Product Strategist.

User Idea:
{user_input}

Provide:
- Market positioning
- Target users
- High-level strategy
"""