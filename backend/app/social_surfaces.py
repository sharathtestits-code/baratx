"""Lists, Communities, text Spaces, and settings helpers — mounted from main."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app import models, schemas, text_parse
from app.database import get_db

router = APIRouter()

SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?$")


def _slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")
    return s[:48] or "community"


def register_social_surfaces(
    app,
    *,
    get_current_user,
    get_current_user_optional,
    serialize_user,
    serialize_post,
    attach_hashtags: Callable,
    notify_mentions: Callable,
):
    # ---------- Settings helpers: mutes / blocks ----------

    @router.get("/users/me/mutes", response_model=list[schemas.UserOut])
    def list_mutes(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        rows = (
            db.query(models.Mute)
            .filter(models.Mute.muter_id == current_user.id)
            .order_by(models.Mute.created_at.desc())
            .all()
        )
        users = []
        for row in rows:
            u = db.query(models.User).filter(models.User.id == row.muted_id).first()
            if u:
                users.append(serialize_user(u, current_user))
        return users

    @router.get("/users/me/blocks", response_model=list[schemas.UserOut])
    def list_blocks(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        rows = (
            db.query(models.Block)
            .filter(models.Block.blocker_id == current_user.id)
            .order_by(models.Block.created_at.desc())
            .all()
        )
        users = []
        for row in rows:
            u = db.query(models.User).filter(models.User.id == row.blocked_id).first()
            if u:
                users.append(serialize_user(u, current_user))
        return users

    # ---------- Lists ----------

    def _list_out(ul: models.UserList, current_user: models.User) -> schemas.UserListOut:
        return schemas.UserListOut(
            id=ul.id,
            name=ul.name,
            description=ul.description or "",
            created_at=ul.created_at,
            member_count=len(ul.members),
            owner=schemas.AuthorOut.model_validate(ul.owner),
            is_owner=ul.owner_id == current_user.id,
        )

    def _get_owned_list(db: Session, list_id: str, user: models.User) -> models.UserList:
        ul = (
            db.query(models.UserList)
            .options(joinedload(models.UserList.members), joinedload(models.UserList.owner))
            .filter(models.UserList.id == list_id)
            .first()
        )
        if not ul:
            raise HTTPException(status_code=404, detail="List not found")
        if ul.owner_id != user.id:
            raise HTTPException(status_code=403, detail="You can only manage your own lists")
        return ul

    @router.get("/lists", response_model=list[schemas.UserListOut])
    def my_lists(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        rows = (
            db.query(models.UserList)
            .options(joinedload(models.UserList.members), joinedload(models.UserList.owner))
            .filter(models.UserList.owner_id == current_user.id)
            .order_by(models.UserList.created_at.desc())
            .all()
        )
        return [_list_out(r, current_user) for r in rows]

    @router.post("/lists", response_model=schemas.UserListOut)
    def create_list(
        payload: schemas.UserListCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        ul = models.UserList(
            owner_id=current_user.id,
            name=payload.name,
            description=payload.description or "",
        )
        db.add(ul)
        db.commit()
        db.refresh(ul)
        ul = (
            db.query(models.UserList)
            .options(joinedload(models.UserList.members), joinedload(models.UserList.owner))
            .filter(models.UserList.id == ul.id)
            .first()
        )
        return _list_out(ul, current_user)

    @router.get("/lists/{list_id}", response_model=schemas.UserListOut)
    def get_list(
        list_id: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        ul = _get_owned_list(db, list_id, current_user)
        return _list_out(ul, current_user)

    @router.patch("/lists/{list_id}", response_model=schemas.UserListOut)
    def update_list(
        list_id: str,
        payload: schemas.UserListUpdate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        ul = _get_owned_list(db, list_id, current_user)
        if payload.name is not None:
            ul.name = payload.name
        if payload.description is not None:
            ul.description = payload.description
        db.commit()
        db.refresh(ul)
        return _list_out(ul, current_user)

    @router.delete("/lists/{list_id}", response_model=schemas.MessageResponse)
    def delete_list(
        list_id: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        ul = _get_owned_list(db, list_id, current_user)
        db.delete(ul)
        db.commit()
        return schemas.MessageResponse(message="List deleted")

    @router.get("/lists/{list_id}/members", response_model=list[schemas.UserOut])
    def list_members(
        list_id: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        ul = _get_owned_list(db, list_id, current_user)
        out = []
        for m in ul.members:
            u = db.query(models.User).filter(models.User.id == m.user_id).first()
            if u:
                out.append(serialize_user(u, current_user))
        return out

    @router.post("/lists/{list_id}/members/{username}", response_model=schemas.MessageResponse)
    def add_list_member(
        list_id: str,
        username: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        ul = _get_owned_list(db, list_id, current_user)
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        exists = (
            db.query(models.ListMember)
            .filter(models.ListMember.list_id == ul.id, models.ListMember.user_id == user.id)
            .first()
        )
        if not exists:
            db.add(models.ListMember(list_id=ul.id, user_id=user.id))
            db.commit()
        return schemas.MessageResponse(message=f"Added @{username}")

    @router.delete("/lists/{list_id}/members/{username}", response_model=schemas.MessageResponse)
    def remove_list_member(
        list_id: str,
        username: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        ul = _get_owned_list(db, list_id, current_user)
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        row = (
            db.query(models.ListMember)
            .filter(models.ListMember.list_id == ul.id, models.ListMember.user_id == user.id)
            .first()
        )
        if row:
            db.delete(row)
            db.commit()
        return schemas.MessageResponse(message=f"Removed @{username}")

    @router.get("/lists/{list_id}/feed", response_model=list[schemas.PostOut])
    def list_feed(
        list_id: str,
        limit: int = 30,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        ul = _get_owned_list(db, list_id, current_user)
        member_ids = [m.user_id for m in ul.members]
        if not member_ids:
            return []
        limit = max(1, min(limit, 50))
        posts = (
            db.query(models.Post)
            .filter(
                models.Post.author_id.in_(member_ids),
                models.Post.community_id.is_(None),
                models.Post.space_id.is_(None),
            )
            .order_by(models.Post.created_at.desc())
            .limit(limit)
            .all()
        )
        return [serialize_post(p, current_user) for p in posts]

    # ---------- Communities ----------

    def _community_out(
        c: models.Community, current_user: Optional[models.User], db: Session
    ) -> schemas.CommunityOut:
        member_count = (
            db.query(models.CommunityMember)
            .filter(models.CommunityMember.community_id == c.id)
            .count()
        )
        is_member = False
        if current_user:
            is_member = (
                db.query(models.CommunityMember)
                .filter(
                    models.CommunityMember.community_id == c.id,
                    models.CommunityMember.user_id == current_user.id,
                )
                .first()
                is not None
            )
        return schemas.CommunityOut(
            id=c.id,
            slug=c.slug,
            name=c.name,
            description=c.description or "",
            created_at=c.created_at,
            member_count=member_count,
            is_member=is_member,
            creator=schemas.AuthorOut.model_validate(c.creator) if c.creator else None,
        )

    def _get_community(db: Session, slug_or_id: str) -> models.Community:
        c = (
            db.query(models.Community)
            .options(joinedload(models.Community.creator))
            .filter((models.Community.slug == slug_or_id) | (models.Community.id == slug_or_id))
            .first()
        )
        if not c:
            raise HTTPException(status_code=404, detail="Community not found")
        return c

    @router.get("/communities", response_model=list[schemas.CommunityOut])
    def list_communities(
        db: Session = Depends(get_db),
        current_user: Optional[models.User] = Depends(get_current_user_optional),
    ):
        rows = (
            db.query(models.Community)
            .options(joinedload(models.Community.creator))
            .order_by(models.Community.created_at.desc())
            .limit(100)
            .all()
        )
        return [_community_out(c, current_user, db) for c in rows]

    @router.post("/communities", response_model=schemas.CommunityOut)
    def create_community(
        payload: schemas.CommunityCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        slug = (payload.slug or _slugify(payload.name)).lower()
        if not SLUG_RE.match(slug):
            raise HTTPException(status_code=400, detail="Invalid slug")
        exists = db.query(models.Community).filter(models.Community.slug == slug).first()
        if exists:
            raise HTTPException(status_code=400, detail="Community slug already taken")
        c = models.Community(
            slug=slug,
            name=payload.name,
            description=payload.description or "",
            created_by=current_user.id,
        )
        db.add(c)
        db.flush()
        db.add(models.CommunityMember(community_id=c.id, user_id=current_user.id))
        db.commit()
        db.refresh(c)
        c = (
            db.query(models.Community)
            .options(joinedload(models.Community.creator))
            .filter(models.Community.id == c.id)
            .first()
        )
        return _community_out(c, current_user, db)

    @router.get("/communities/{slug_or_id}", response_model=schemas.CommunityOut)
    def get_community(
        slug_or_id: str,
        db: Session = Depends(get_db),
        current_user: Optional[models.User] = Depends(get_current_user_optional),
    ):
        c = _get_community(db, slug_or_id)
        return _community_out(c, current_user, db)

    @router.post("/communities/{slug_or_id}/join", response_model=schemas.CommunityOut)
    def join_community(
        slug_or_id: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        c = _get_community(db, slug_or_id)
        exists = (
            db.query(models.CommunityMember)
            .filter(
                models.CommunityMember.community_id == c.id,
                models.CommunityMember.user_id == current_user.id,
            )
            .first()
        )
        if not exists:
            db.add(models.CommunityMember(community_id=c.id, user_id=current_user.id))
            db.commit()
        return _community_out(c, current_user, db)

    @router.post("/communities/{slug_or_id}/leave", response_model=schemas.CommunityOut)
    def leave_community(
        slug_or_id: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        c = _get_community(db, slug_or_id)
        row = (
            db.query(models.CommunityMember)
            .filter(
                models.CommunityMember.community_id == c.id,
                models.CommunityMember.user_id == current_user.id,
            )
            .first()
        )
        if row:
            db.delete(row)
            db.commit()
        return _community_out(c, current_user, db)

    @router.get("/communities/{slug_or_id}/feed", response_model=list[schemas.PostOut])
    def community_feed(
        slug_or_id: str,
        limit: int = 30,
        db: Session = Depends(get_db),
        current_user: Optional[models.User] = Depends(get_current_user_optional),
    ):
        c = _get_community(db, slug_or_id)
        limit = max(1, min(limit, 50))
        posts = (
            db.query(models.Post)
            .filter(models.Post.community_id == c.id)
            .order_by(models.Post.created_at.desc())
            .limit(limit)
            .all()
        )
        return [serialize_post(p, current_user) for p in posts]

    @router.post("/communities/{slug_or_id}/posts", response_model=schemas.PostOut)
    def community_post(
        slug_or_id: str,
        payload: schemas.SurfacePostCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        c = _get_community(db, slug_or_id)
        member = (
            db.query(models.CommunityMember)
            .filter(
                models.CommunityMember.community_id == c.id,
                models.CommunityMember.user_id == current_user.id,
            )
            .first()
        )
        if not member:
            raise HTTPException(status_code=403, detail="Join this community to post")
        post = models.Post(
            author_id=current_user.id,
            text=payload.text,
            community_id=c.id,
        )
        db.add(post)
        db.flush()
        attach_hashtags(db, post, payload.text)
        notify_mentions(db, current_user.id, payload.text, post_id=post.id)
        db.commit()
        db.refresh(post)
        return serialize_post(post, current_user)

    # ---------- Text Spaces ----------

    def _space_out(s: models.Space, current_user: Optional[models.User], db: Session) -> schemas.SpaceOut:
        post_count = db.query(models.Post).filter(models.Post.space_id == s.id).count()
        return schemas.SpaceOut(
            id=s.id,
            title=s.title,
            status=s.status,
            created_at=s.created_at,
            closes_at=s.closes_at,
            post_count=post_count,
            is_host=bool(current_user and s.host_id == current_user.id),
            host=schemas.AuthorOut.model_validate(s.host) if s.host else None,
        )

    def _get_space(db: Session, space_id: str) -> models.Space:
        s = (
            db.query(models.Space)
            .options(joinedload(models.Space.host))
            .filter(models.Space.id == space_id)
            .first()
        )
        if not s:
            raise HTTPException(status_code=404, detail="Space not found")
        return s

    def _maybe_auto_close(db: Session, s: models.Space) -> None:
        if s.status != "open" or not s.closes_at:
            return
        now = datetime.now(timezone.utc)
        closes = s.closes_at
        if closes.tzinfo is None:
            closes = closes.replace(tzinfo=timezone.utc)
        if closes <= now:
            s.status = "closed"
            db.commit()
            db.refresh(s)

    @router.get("/spaces", response_model=list[schemas.SpaceOut])
    def list_spaces(
        status: str = "open",
        db: Session = Depends(get_db),
        current_user: Optional[models.User] = Depends(get_current_user_optional),
    ):
        # Auto-close expired open spaces first.
        open_rows = (
            db.query(models.Space)
            .filter(models.Space.status == "open")
            .limit(100)
            .all()
        )
        for s in open_rows:
            _maybe_auto_close(db, s)

        q = db.query(models.Space).options(joinedload(models.Space.host))
        if status in ("open", "closed"):
            q = q.filter(models.Space.status == status)
        rows = q.order_by(models.Space.created_at.desc()).limit(50).all()
        return [_space_out(s, current_user, db) for s in rows]

    @router.post("/spaces", response_model=schemas.SpaceOut)
    def create_space(
        payload: schemas.SpaceCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        now = datetime.now(timezone.utc)
        hours = payload.duration_hours or 24
        hours = max(1, min(hours, 168))
        s = models.Space(
            title=payload.title,
            host_id=current_user.id,
            status="open",
            closes_at=now + timedelta(hours=hours),
        )
        db.add(s)
        db.commit()
        db.refresh(s)
        s = (
            db.query(models.Space)
            .options(joinedload(models.Space.host))
            .filter(models.Space.id == s.id)
            .first()
        )
        return _space_out(s, current_user, db)

    @router.get("/spaces/{space_id}", response_model=schemas.SpaceOut)
    def get_space(
        space_id: str,
        db: Session = Depends(get_db),
        current_user: Optional[models.User] = Depends(get_current_user_optional),
    ):
        s = _get_space(db, space_id)
        _maybe_auto_close(db, s)
        return _space_out(s, current_user, db)

    @router.post("/spaces/{space_id}/close", response_model=schemas.SpaceOut)
    def close_space(
        space_id: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        s = _get_space(db, space_id)
        if s.host_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only the host can close this Space")
        s.status = "closed"
        s.closes_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(s)
        return _space_out(s, current_user, db)

    @router.get("/spaces/{space_id}/feed", response_model=list[schemas.PostOut])
    def space_feed(
        space_id: str,
        limit: int = 50,
        db: Session = Depends(get_db),
        current_user: Optional[models.User] = Depends(get_current_user_optional),
    ):
        s = _get_space(db, space_id)
        limit = max(1, min(limit, 100))
        posts = (
            db.query(models.Post)
            .filter(models.Post.space_id == s.id)
            .order_by(models.Post.created_at.asc())
            .limit(limit)
            .all()
        )
        return [serialize_post(p, current_user) for p in posts]

    @router.post("/spaces/{space_id}/posts", response_model=schemas.PostOut)
    def space_post(
        space_id: str,
        payload: schemas.SurfacePostCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        s = _get_space(db, space_id)
        _maybe_auto_close(db, s)
        if s.status != "open":
            raise HTTPException(status_code=400, detail="This Space is closed")
        post = models.Post(
            author_id=current_user.id,
            text=payload.text,
            space_id=s.id,
        )
        db.add(post)
        db.flush()
        attach_hashtags(db, post, payload.text)
        notify_mentions(db, current_user.id, payload.text, post_id=post.id)
        db.commit()
        db.refresh(post)
        return serialize_post(post, current_user)

    app.include_router(router)
