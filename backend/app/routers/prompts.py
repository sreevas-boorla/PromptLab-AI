import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Prompt, PromptVersion
from ..schemas import PromptCreate, PromptUpdate, PromptResponse, PromptVersionResponse, PromptVersionCreate

router = APIRouter(prefix="/api/v1/prompts", tags=["Prompts"])

def _format_version(v: PromptVersion) -> PromptVersionResponse:
    try:
        config = json.loads(v.model_config_json) if v.model_config_json else {}
    except Exception:
        config = {}
    return PromptVersionResponse(
        id=v.id,
        prompt_id=v.prompt_id,
        version_number=v.version_number,
        system_prompt=v.system_prompt,
        user_prompt=v.user_prompt,
        config_settings=config,
        notes=v.notes,
        created_at=v.created_at
    )

def _format_prompt(p: Prompt) -> PromptResponse:
    tags_list = [t.strip() for t in p.tags.split(",") if t.strip()] if p.tags else []
    sorted_versions = sorted(p.versions, key=lambda v: v.version_number, reverse=True)
    latest_v = _format_version(sorted_versions[0]) if sorted_versions else None
    return PromptResponse(
        id=p.id,
        title=p.title,
        description=p.description,
        category=p.category,
        tags=tags_list,
        created_at=p.created_at,
        updated_at=p.updated_at,
        latest_version=latest_v,
        versions_count=len(p.versions)
    )

@router.get("", response_model=List[PromptResponse])
def list_prompts(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Prompt)
    if category:
        query = query.filter(Prompt.category == category)
    if search:
        query = query.filter(Prompt.title.ilike(f"%{search}%") | Prompt.description.ilike(f"%{search}%"))
    
    prompts = query.order_by(Prompt.updated_at.desc()).all()
    
    if tag:
        prompts = [p for p in prompts if tag.lower() in [t.strip().lower() for t in (p.tags or "").split(",")]]
        
    return [_format_prompt(p) for p in prompts]

@router.post("", response_model=PromptResponse)
def create_prompt(req: PromptCreate, db: Session = Depends(get_db)):
    tags_str = ",".join([t.strip() for t in req.tags if t.strip()])
    prompt = Prompt(
        title=req.title,
        description=req.description,
        category=req.category,
        tags=tags_str
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)

    # Initial Version (v1)
    version = PromptVersion(
        prompt_id=prompt.id,
        version_number=1,
        system_prompt=req.initial_version.system_prompt,
        user_prompt=req.initial_version.user_prompt,
        model_config_json=json.dumps(req.initial_version.config_settings),
        notes=req.initial_version.notes or "Initial version"
    )
    db.add(version)
    db.commit()
    db.refresh(prompt)

    return _format_prompt(prompt)

@router.get("/{prompt_id}", response_model=PromptResponse)
def get_prompt(prompt_id: int, db: Session = Depends(get_db)):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return _format_prompt(prompt)

@router.put("/{prompt_id}", response_model=PromptResponse)
def update_prompt(prompt_id: int, req: PromptUpdate, db: Session = Depends(get_db)):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    if req.title is not None:
        prompt.title = req.title
    if req.description is not None:
        prompt.description = req.description
    if req.category is not None:
        prompt.category = req.category
    if req.tags is not None:
        prompt.tags = ",".join([t.strip() for t in req.tags if t.strip()])

    db.commit()
    db.refresh(prompt)
    return _format_prompt(prompt)

@router.delete("/{prompt_id}")
def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    db.delete(prompt)
    db.commit()
    return {"status": "success", "message": f"Prompt {prompt_id} deleted."}

@router.get("/{prompt_id}/versions", response_model=List[PromptVersionResponse])
def list_versions(prompt_id: int, db: Session = Depends(get_db)):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    versions = db.query(PromptVersion).filter(PromptVersion.prompt_id == prompt_id).order_by(PromptVersion.version_number.desc()).all()
    return [_format_version(v) for v in versions]

@router.post("/{prompt_id}/versions", response_model=PromptVersionResponse)
def create_new_version(prompt_id: int, req: PromptVersionCreate, db: Session = Depends(get_db)):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    latest_ver = db.query(PromptVersion).filter(PromptVersion.prompt_id == prompt_id).order_by(PromptVersion.version_number.desc()).first()
    next_ver_num = (latest_ver.version_number + 1) if latest_ver else 1

    new_v = PromptVersion(
        prompt_id=prompt.id,
        version_number=next_ver_num,
        system_prompt=req.system_prompt,
        user_prompt=req.user_prompt,
        model_config_json=json.dumps(req.config_settings),
        notes=req.notes or f"Version {next_ver_num}"
    )
    db.add(new_v)
    db.commit()
    db.refresh(new_v)
    return _format_version(new_v)
