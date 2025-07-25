from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/chat", summary="Chat with the model")
async def chat():
    """
    Endpoint to chat with the model.
    This is a placeholder for the chat functionality.
    """
    raise HTTPException(status_code=501, detail="Chat functionality not implemented yet.")
