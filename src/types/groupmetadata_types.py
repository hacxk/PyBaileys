from typing import Optional, List, Dict, Literal
from dataclasses import dataclass
from models.sock_models import Contact

# Define GroupParticipant
@dataclass
class GroupParticipant(Contact):
    isAdmin: Optional[bool] = None
    isSuperAdmin: Optional[bool] = None
    admin: Optional[Literal['admin', 'superadmin']] = None  # 'admin' | 'superadmin' | None

# Define ParticipantAction
ParticipantAction = Literal['add', 'remove', 'promote', 'demote', 'modify']

# Define RequestJoinAction
RequestJoinAction = Literal['created', 'revoked', 'rejected']

# Define RequestJoinMethod
RequestJoinMethod = Literal['invite_link', 'linked_group_join', 'non_admin_add', None]

@dataclass
class GroupMetadata:
    id: str
    owner: Optional[str] = None
    subject: str
    subjectOwner: Optional[str] = None
    subjectTime: Optional[int] = None
    creation: Optional[int] = None
    desc: Optional[str] = None
    descOwner: Optional[str] = None
    descId: Optional[str] = None
    linkedParent: Optional[str] = None
    restrict: Optional[bool] = None
    announce: Optional[bool] = None
    memberAddMode: Optional[bool] = None
    joinApprovalMode: Optional[bool] = None
    isCommunity: Optional[bool] = None
    isCommunityAnnounce: Optional[bool] = None
    size: Optional[int] = None
    participants: List[GroupParticipant]
    ephemeralDuration: Optional[int] = None
    inviteCode: Optional[str] = None
    author: Optional[str] = None

@dataclass
class WAGroupCreateResponse:
    status: int
    gid: Optional[str] = None
    participants: Optional[Dict[str, Dict]] = None

@dataclass
class GroupModificationResponse:
    status: int
    participants: Optional[Dict[str, Dict]] = None
