"""
API routes for paper group management
"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from ..models.schemas import (
    PaperGroup,
    GroupCreate,
    GroupUpdate,
    GroupListResponse,
    GroupDeleteResponse
)
from ..services.group_service import get_group_service

router = APIRouter()


@router.post("/groups", response_model=PaperGroup, status_code=status.HTTP_201_CREATED)
async def create_group(group_data: GroupCreate):
    """
    Create a new paper group
    
    Groups allow you to organize multiple papers and query across them
    """
    group_service = get_group_service()
    group = await group_service.create_group(group_data)
    return group


@router.get("/groups", response_model=GroupListResponse)
async def list_groups():
    """
    Get all paper groups
    """
    group_service = get_group_service()
    groups = await group_service.get_all_groups()
    return GroupListResponse(groups=groups, total=len(groups))


@router.get("/groups/{group_id}", response_model=PaperGroup)
async def get_group(group_id: str):
    """
    Get a specific group by ID
    """
    group_service = get_group_service()
    group = await group_service.get_group(group_id)
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group {group_id} not found"
        )
    
    return group


@router.put("/groups/{group_id}", response_model=PaperGroup)
async def update_group(group_id: str, updates: GroupUpdate):
    """
    Update a group (name, description, papers)
    """
    group_service = get_group_service()
    group = await group_service.update_group(group_id, updates)
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group {group_id} not found"
        )
    
    return group


@router.delete("/groups/{group_id}", response_model=GroupDeleteResponse)
async def delete_group(group_id: str):
    """
    Delete a group
    
    Note: This does NOT delete the papers, only the group
    """
    group_service = get_group_service()
    success = await group_service.delete_group(group_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group {group_id} not found"
        )
    
    return GroupDeleteResponse(
        success=True,
        group_id=group_id,
        message="Group deleted successfully"
    )


@router.post("/groups/{group_id}/papers", response_model=PaperGroup)
async def add_papers_to_group(group_id: str, paper_ids: List[str]):
    """
    Add papers to a group
    """
    group_service = get_group_service()
    group = await group_service.add_papers_to_group(group_id, paper_ids)
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group {group_id} not found"
        )
    
    return group


@router.delete("/groups/{group_id}/papers/{paper_id}", response_model=PaperGroup)
async def remove_paper_from_group(group_id: str, paper_id: str):
    """
    Remove a paper from a group
    """
    group_service = get_group_service()
    group = await group_service.remove_papers_from_group(group_id, [paper_id])
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group {group_id} not found"
        )
    
    return group
