from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from schemas.message import MessageCreate, MessageOut
from models import User, Message

from typing import List, Optional, Dict
from main import  get_current_user
from deps import get_db

router = APIRouter(
    tags=["Chain"],
)


@router.post("/post_chain", response_model=List[MessageOut])
async def post_messages(
    chain: List[MessageCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stored_messages = []
    for msg in chain:
        message = Message(
            from_agent=msg.from_agent,
            chain_id=msg.chain_id,
            user_id=current_user.id,
            to_agent=msg.to_agent,
            message=msg.message,
            args=[arg.dict() for arg in msg.args],
        )
        db.add(message)
        stored_messages.append(message)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving messages.",
        )
    for message in stored_messages:
        db.refresh(message)

    return stored_messages


@router.get("/chains", response_model=Dict[str, List[MessageOut]])
async def get_messages(
    chain_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Message).filter(Message.user_id == current_user.id)
    if chain_id is not None:
        query = query.filter(Message.chain_id == chain_id)

    messages = query.all()
    response = {}
    for message in messages:
        if message.chain_id in response:
            if isinstance(response[message.chain_id], list):
                response[message.chain_id].append(MessageOut.from_orm(message))
            else:
                response[message.chain_id] = [
                    response[message.chain_id],
                    MessageOut.from_orm(message),
                ]
        else:
            response[message.chain_id] = MessageOut.from_orm(message)
    return response


@router.delete("/chains/{chain_id}", response_model=Dict[str, str])
async def delete_chain(
    chain_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    messages_to_delete = (
        db.query(Message)
        .filter(Message.chain_id == chain_id, Message.user_id == current_user.id)
        .all()
    )

    if not messages_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chain not found or you do not have permission to delete this chain.",
        )

    try:
        for message in messages_to_delete:
            db.delete(message)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the chain.",
        )

    return {
        "detail": f"Successfully deleted {len(messages_to_delete)} messages in chain '{chain_id}'."
    }
