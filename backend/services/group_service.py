"""
Group Service
Manages paper groups for multi-document queries
"""
import os
import json
import uuid
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from ..models.schemas import PaperGroup, GroupCreate, GroupUpdate


class GroupService:
    """
    Service for managing paper groups
    Uses simple JSON file storage for group metadata
    """
    
    def __init__(self, storage_path: str = "data/groups.json"):
        self.storage_path = storage_path
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Create storage directory and file if they don't exist"""
        storage_dir = Path(self.storage_path).parent
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        if not os.path.exists(self.storage_path):
            self._save_groups([])
    
    def _load_groups(self) -> List[dict]:
        """Load groups from JSON file"""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_groups(self, groups: List[dict]):
        """Save groups to JSON file"""
        with open(self.storage_path, 'w') as f:
            json.dump(groups, f, indent=2, default=str)
    
    def _find_group_index(self, group_id: str) -> Optional[int]:
        """Find index of group by ID"""
        groups = self._load_groups()
        for i, group in enumerate(groups):
            if group.get('group_id') == group_id:
                return i
        return None
    
    async def create_group(self, group_data: GroupCreate) -> PaperGroup:
        """Create a new paper group"""
        groups = self._load_groups()
        
        # Generate unique ID
        group_id = str(uuid.uuid4())
        
        # Create group
        new_group = {
            "group_id": group_id,
            "name": group_data.name,
            "description": group_data.description,
            "paper_ids": group_data.paper_ids,
            "created_date": datetime.now().isoformat()
        }
        
        groups.append(new_group)
        self._save_groups(groups)
        
        return PaperGroup(**new_group)
    
    async def get_all_groups(self) -> List[PaperGroup]:
        """Get all groups"""
        groups = self._load_groups()
        return [PaperGroup(**g) for g in groups]
    
    async def get_group(self, group_id: str) -> Optional[PaperGroup]:
        """Get a specific group by ID"""
        idx = self._find_group_index(group_id)
        if idx is None:
            return None
        
        groups = self._load_groups()
        return PaperGroup(**groups[idx])
    
    async def update_group(self, group_id: str, updates: GroupUpdate) -> Optional[PaperGroup]:
        """Update a group"""
        idx = self._find_group_index(group_id)
        if idx is None:
            return None
        
        groups = self._load_groups()
        group = groups[idx]
        
        # Update basic fields
        if updates.name is not None:
            group['name'] = updates.name
        if updates.description is not None:
            group['description'] = updates.description
        
        # Handle paper additions/removals
        paper_ids = set(group.get('paper_ids', []))
        
        if updates.add_papers:
            paper_ids.update(updates.add_papers)
        
        if updates.remove_papers:
            paper_ids.difference_update(updates.remove_papers)
        
        group['paper_ids'] = list(paper_ids)
        
        self._save_groups(groups)
        return PaperGroup(**group)
    
    async def delete_group(self, group_id: str) -> bool:
        """Delete a group"""
        idx = self._find_group_index(group_id)
        if idx is None:
            return False
        
        groups = self._load_groups()
        groups.pop(idx)
        self._save_groups(groups)
        
        return True
    
    async def add_papers_to_group(self, group_id: str, paper_ids: List[str]) -> Optional[PaperGroup]:
        """Add papers to a group"""
        return await self.update_group(
            group_id,
            GroupUpdate(add_papers=paper_ids)
        )
    
    async def remove_papers_from_group(self, group_id: str, paper_ids: List[str]) -> Optional[PaperGroup]:
        """Remove papers from a group"""
        return await self.update_group(
            group_id,
            GroupUpdate(remove_papers=paper_ids)
        )
    
    async def get_groups_for_paper(self, paper_id: str) -> List[PaperGroup]:
        """Get all groups that contain a specific paper"""
        groups = self._load_groups()
        return [
            PaperGroup(**g)
            for g in groups
            if paper_id in g.get('paper_ids', [])
        ]


# Singleton instance
_group_service = None


def get_group_service() -> GroupService:
    """Get or create group service singleton"""
    global _group_service
    if _group_service is None:
        _group_service = GroupService()
    return _group_service
