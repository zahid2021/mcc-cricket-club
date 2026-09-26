from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import safe_decode
from app.db.session import get_db
from app.models import User, AccountStatus

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if not creds or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = safe_decode(creds.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.get(User, payload.get("sub"))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please login again")
    if user.account_status != AccountStatus.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive")
    return user


def require_permissions(*codes: str):
    def _dep(user: User = Depends(get_current_user)) -> User:
        owned: set[str] = set()
        for role in user.roles:
            for perm in role.permissions:
                owned.add(perm.code)
        missing = [c for c in codes if c not in owned]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {', '.join(missing)}",
            )
        return user

    return _dep


def user_permission_codes(user: User) -> list[str]:
    codes: set[str] = set()
    for role in user.roles:
        for perm in role.permissions:
            codes.add(perm.code)
    return sorted(codes)


def primary_role_code(user: User) -> str:
    priority = [
        "super_admin",
        "club_admin",
        "team_manager",
        "captain",
        "vice_captain",
        "coach",
        "scorer",
        "sponsor_manager",
        "sponsor",
        "player",
        "viewer",
    ]
    codes = {r.code for r in user.roles}
    for p in priority:
        if p in codes:
            return p
    return "viewer"
