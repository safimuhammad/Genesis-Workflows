from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.components import AbilityCreate, AbilityOut
from models import User, Abilities
from typing import List
from main import get_current_user
from deps import get_db

router = APIRouter(
    tags=["Components"],
)


@router.get("/get_components", response_model=List[AbilityOut])
async def get_workflow_components(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    abilities = db.query(Abilities).all()
    return abilities


@router.post("/post_components", response_model=AbilityOut)
async def post_components(
    ability_data: AbilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fetch_ability = (
        db.query(Abilities)
        .filter(ability_data.tool_name == Abilities.tool_name)
        .first()
    )
    if fetch_ability is not None:
        raise HTTPException(status_code=409, detail="Ability already exists.")
    db_ability = Abilities(
        tool_name=ability_data.tool_name,
        description=ability_data.description,
        args=[arg.dict() for arg in ability_data.args],
        output=[out.dict() for out in ability_data.output],
    )
    db.add(db_ability)
    db.commit()
    db.refresh(db_ability)
    return db_ability
