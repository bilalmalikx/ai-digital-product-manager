from fastapi import HTTPException


def validate_product_idea(idea: str):
    """Validate incoming product idea"""

    if not idea:
        raise HTTPException(
            status_code=400,
            detail="Product idea is required"
        )

    if len(idea) < 10:
        raise HTTPException(
            status_code=400,
            detail="Product idea is too short"
        )

    if len(idea) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Product idea is too long"
        )

    bad_words = ["hate", "kill", "illegal"]

    for word in bad_words:
        if word in idea.lower():
            raise HTTPException(
                status_code=400,
                detail=f"Inappropriate content detected: {word}"
            )

    return True