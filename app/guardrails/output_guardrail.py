def filter_agent_output(output: dict) -> dict:
    """Remove sensitive keys from output"""

    sensitive_keys = ["password", "api_key", "secret", "token"]

    def clean(obj):
        if isinstance(obj, dict):
            return {
                k: clean(v)
                for k, v in obj.items()
                if k not in sensitive_keys
            }
        elif isinstance(obj, list):
            return [clean(item) for item in obj]
        return obj

    return clean(output)