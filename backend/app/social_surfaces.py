"""Lists, Communities, text Spaces, and settings helpers — mounted from main."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.database import get_db
from app.topics_data import debate_sides_for

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
            is_arena=bool(getattr(c, "is_arena", False)),
            arena_key=getattr(c, "arena_key", None),
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
        # Arenas are debate floors (is_arena=True) — keep them out of Communities list
        # so the two surfaces don't look like duplicate topic systems.
        rows = (
            db.query(models.Community)
            .options(joinedload(models.Community.creator))
            .filter(models.Community.is_arena == False)  # noqa: E712
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
        if not bool(getattr(current_user, "has_posted_once", False)):
            current_user.has_posted_once = True
        db.add(post)
        db.flush()
        attach_hashtags(db, post, payload.text)
        notify_mentions(db, current_user.id, payload.text, post_id=post.id)
        db.commit()
        db.refresh(post)
        return serialize_post(post, current_user)


    # ---------- Arenas (Sports / Politics / Entertainment / News) ----------

    @router.get("/arenas", response_model=list[schemas.ArenaOut])
    def list_arenas(
        db: Session = Depends(get_db),
        current_user: Optional[models.User] = Depends(get_current_user_optional),
    ):
        from app.topics_data import ACTIVE_ARENA_KEYS

        rows = (
            db.query(models.Community)
            .filter(models.Community.is_arena == True)  # noqa: E712
            .order_by(models.Community.name.asc())
            .all()
        )
        out = []
        for c in rows:
            key = c.arena_key or c.slug
            if key not in ACTIVE_ARENA_KEYS:
                continue
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
            open_debate_count = (
                db.query(models.Space)
                .filter(
                    models.Space.community_id == c.id,
                    models.Space.kind == "debate",
                    models.Space.status == "open",
                )
                .count()
            )
            out.append(
                schemas.ArenaOut(
                    key=key,
                    slug=c.slug,
                    name=c.name,
                    description=c.description or "",
                    member_count=member_count,
                    is_member=is_member,
                    open_debate_count=open_debate_count,
                    community_id=c.id,
                )
            )
        return out

    @router.get("/arenas/{arena_key}", response_model=schemas.ArenaOut)
    def get_arena(
        arena_key: str,
        db: Session = Depends(get_db),
        current_user: Optional[models.User] = Depends(get_current_user_optional),
    ):
        from app.topics_data import ACTIVE_ARENA_KEYS

        if arena_key not in ACTIVE_ARENA_KEYS:
            raise HTTPException(status_code=404, detail="Arena not found")
        c = (
            db.query(models.Community)
            .filter(
                models.Community.is_arena == True,  # noqa: E712
                (models.Community.arena_key == arena_key) | (models.Community.slug == arena_key),
            )
            .first()
        )
        if not c:
            raise HTTPException(status_code=404, detail="Arena not found")
        rows = list_arenas(db=db, current_user=current_user)
        for row in rows:
            if row.key == (c.arena_key or c.slug) or row.slug == c.slug:
                return row
        raise HTTPException(status_code=404, detail="Arena not found")

    @router.post("/arenas/{arena_key}/join", response_model=schemas.ArenaOut)
    def join_arena(
        arena_key: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        from app.topics_data import ACTIVE_ARENA_KEYS

        if arena_key not in ACTIVE_ARENA_KEYS:
            raise HTTPException(status_code=404, detail="Arena not found")
        c = (
            db.query(models.Community)
            .filter(
                models.Community.is_arena == True,  # noqa: E712
                (models.Community.arena_key == arena_key) | (models.Community.slug == arena_key),
            )
            .first()
        )
        if not c:
            raise HTTPException(status_code=404, detail="Arena not found")
        join_community(slug_or_id=c.slug, current_user=current_user, db=db)
        return get_arena(arena_key=c.arena_key or c.slug, db=db, current_user=current_user)

    @router.post("/arenas/join-many", response_model=list[schemas.ArenaOut])
    def join_many_arenas(
        payload: schemas.ArenaJoinMany,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        for key in payload.keys or []:
            key = (key or "").strip().lower()
            if not key:
                continue
            try:
                join_arena(arena_key=key, current_user=current_user, db=db)
            except HTTPException:
                continue
        return list_arenas(db=db, current_user=current_user)

    @router.post("/spaces/{space_id}/stance", response_model=schemas.SpaceOut)
    def set_space_stance(
        space_id: str,
        payload: schemas.StanceCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        s = _get_space(db, space_id)
        if (getattr(s, "kind", None) or "room") != "debate":
            raise HTTPException(status_code=400, detail="Stances are only for debates")
        row = (
            db.query(models.SpaceStance)
            .filter(
                models.SpaceStance.space_id == s.id,
                models.SpaceStance.user_id == current_user.id,
            )
            .first()
        )
        if row:
            row.side = payload.side
        else:
            db.add(
                models.SpaceStance(space_id=s.id, user_id=current_user.id, side=payload.side)
            )
        from app import rewards

        rewards.bump_founding_for_space(db, s.id)
        db.commit()
        db.refresh(s)
        return _space_out(s, current_user, db)

    @router.delete("/spaces/{space_id}/stance", response_model=schemas.SpaceOut)
    def leave_space_stance(
        space_id: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        """Leave the debate conversation (clear For/Against stance)."""
        s = _get_space(db, space_id)
        if (getattr(s, "kind", None) or "room") != "debate":
            raise HTTPException(status_code=400, detail="Stances are only for debates")
        deleted = (
            db.query(models.SpaceStance)
            .filter(
                models.SpaceStance.space_id == s.id,
                models.SpaceStance.user_id == current_user.id,
            )
            .delete(synchronize_session=False)
        )
        if not deleted:
            # Idempotent — already not in the fight
            return _space_out(s, current_user, db)
        db.commit()
        db.refresh(s)
        return _space_out(s, current_user, db)

    # ---------- Text Spaces ----------

    def _space_out(s: models.Space, current_user: Optional[models.User], db: Session) -> schemas.SpaceOut:
        post_count = db.query(models.Post).filter(models.Post.space_id == s.id).count()
        for_count = (
            db.query(models.SpaceStance)
            .filter(models.SpaceStance.space_id == s.id, models.SpaceStance.side == "for")
            .count()
        )
        against_count = (
            db.query(models.SpaceStance)
            .filter(models.SpaceStance.space_id == s.id, models.SpaceStance.side == "against")
            .count()
        )
        my_side = None
        if current_user:
            stance = (
                db.query(models.SpaceStance)
                .filter(
                    models.SpaceStance.space_id == s.id,
                    models.SpaceStance.user_id == current_user.id,
                )
                .first()
            )
            if stance:
                my_side = stance.side
        arena_key = None
        arena_name = None
        community = getattr(s, "community", None)
        if community is None and getattr(s, "community_id", None):
            community = db.query(models.Community).filter(models.Community.id == s.community_id).first()
        if community is not None:
            arena_key = getattr(community, "arena_key", None)
            arena_name = community.name
        topic_id = getattr(s, "topic_id", None)
        topic_key = None
        topic_name = None
        if topic_id:
            topic = getattr(s, "topic", None)
            if topic is None:
                topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
            if topic is not None:
                topic_key = topic.key
                topic_name = topic.name
        return schemas.SpaceOut(
            id=s.id,
            title=s.title,
            status=s.status,
            kind=getattr(s, "kind", None) or "room",
            created_at=s.created_at,
            closes_at=s.closes_at,
            post_count=post_count,
            is_host=bool(current_user and s.host_id == current_user.id),
            host=schemas.AuthorOut.model_validate(s.host) if s.host else None,
            community_id=getattr(s, "community_id", None),
            arena_key=arena_key,
            arena_name=arena_name,
            topic_id=topic_id,
            topic_key=topic_key,
            topic_name=topic_name,
            source_url=getattr(s, "source_url", None),
            side_for_label=getattr(s, "side_for_label", None) or "For",
            side_against_label=getattr(s, "side_against_label", None) or "Against",
            for_count=for_count,
            against_count=against_count,
            my_side=my_side,
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
        kind: Optional[str] = None,
        arena_key: Optional[str] = None,
        topic_key: Optional[str] = None,
        for_you: bool = False,
        db: Session = Depends(get_db),
        current_user: Optional[models.User] = Depends(get_current_user_optional),
    ):
        # Soft refresh unpaid prompts occasionally when debates are listed.
        if kind == "debate" or for_you:
            try:
                from app import topic_ops

                topic_ops.refresh_debate_prompts(db, force=False, per_topic=1, max_topics=8)
            except Exception:  # noqa: BLE001
                pass

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
        if kind in ("room", "debate"):
            q = q.filter(models.Space.kind == kind)
        if arena_key:
            arena = (
                db.query(models.Community)
                .filter(models.Community.arena_key == arena_key)
                .first()
            )
            if arena:
                q = q.filter(models.Space.community_id == arena.id)
            else:
                return []
        if topic_key:
            topic = db.query(models.Topic).filter(models.Topic.key == topic_key).first()
            if topic:
                q = q.filter(models.Space.topic_id == topic.id)
            else:
                return []
        if for_you and current_user:
            interest_ids = [
                r.topic_id
                for r in db.query(models.UserTopicInterest)
                .filter(models.UserTopicInterest.user_id == current_user.id)
                .all()
            ]
            if interest_ids:
                q = q.filter(models.Space.topic_id.in_(interest_ids))
            else:
                # No interests yet — fall back to all open debates
                pass
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
        kind = payload.kind or "room"
        community_id = payload.community_id
        if payload.arena_key:
            from app.topics_data import ACTIVE_ARENA_KEYS

            if payload.arena_key not in ACTIVE_ARENA_KEYS:
                raise HTTPException(status_code=404, detail="Arena not found")
            arena = (
                db.query(models.Community)
                .filter(
                    models.Community.arena_key == payload.arena_key,
                    models.Community.is_arena == True,  # noqa: E712
                )
                .first()
            )
            if not arena:
                raise HTTPException(status_code=404, detail="Arena not found")
            community_id = arena.id
            kind = "debate"
        elif community_id:
            c = db.query(models.Community).filter(models.Community.id == community_id).first()
            if not c:
                raise HTTPException(status_code=404, detail="Community not found")
        default_for, default_against = debate_sides_for(payload.arena_key)
        if payload.arena_key:
            side_for = (payload.side_for_label or default_for).strip()[:40] or default_for
            side_against = (payload.side_against_label or default_against).strip()[:40] or default_against
        else:
            side_for = (payload.side_for_label or "For").strip()[:40] or "For"
            side_against = (payload.side_against_label or "Against").strip()[:40] or "Against"

        topic_id = payload.topic_id
        if topic_id:
            topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
            if not topic:
                raise HTTPException(status_code=400, detail="Topic not found")
            if payload.arena_key and topic.arena_key != payload.arena_key:
                raise HTTPException(status_code=400, detail="Topic does not belong to this arena")

        s = models.Space(
            title=payload.title,
            host_id=current_user.id,
            status="open",
            kind=kind,
            community_id=community_id,
            topic_id=topic_id,
            side_for_label=side_for,
            side_against_label=side_against,
            closes_at=now + timedelta(hours=hours),
        )
        db.add(s)
        db.flush()
        # Founding 100: opening a debate in any active arena qualifies (floor).
        if payload.arena_key:
            from app.topics_data import ACTIVE_ARENA_KEYS
            from app import rewards

            if payload.arena_key in ACTIVE_ARENA_KEYS:
                rewards.try_award(
                    db, user=current_user, kind="debate", space_id=s.id
                )
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
        debate_side = payload.debate_side
        if (getattr(s, "kind", None) or "room") == "debate":
            stance = (
                db.query(models.SpaceStance)
                .filter(
                    models.SpaceStance.space_id == s.id,
                    models.SpaceStance.user_id == current_user.id,
                )
                .first()
            )
            if not stance:
                raise HTTPException(status_code=400, detail="Pick For or Against before posting")
            debate_side = debate_side or stance.side
        post = models.Post(
            author_id=current_user.id,
            text=payload.text,
            space_id=s.id,
            debate_side=debate_side,
        )
        if not bool(getattr(current_user, "has_posted_once", False)):
            current_user.has_posted_once = True
        db.add(post)
        db.flush()
        attach_hashtags(db, post, payload.text)
        notify_mentions(db, current_user.id, payload.text, post_id=post.id)
        from app import rewards

        rewards.bump_founding_for_space(db, s.id)
        db.commit()
        db.refresh(post)
        return serialize_post(post, current_user)

    # ---------- Topics (Path C — unpaid interest feeds) ----------

    def _topic_out(t: models.Topic, db: Session, current_user: Optional[models.User]) -> schemas.TopicOut:
        is_following = False
        if current_user:
            is_following = (
                db.query(models.UserTopicInterest)
                .filter(
                    models.UserTopicInterest.user_id == current_user.id,
                    models.UserTopicInterest.topic_id == t.id,
                )
                .first()
                is not None
            )
        open_debate_count = (
            db.query(models.Space)
            .filter(
                models.Space.topic_id == t.id,
                models.Space.kind == "debate",
                models.Space.status == "open",
            )
            .count()
        )
        return schemas.TopicOut(
            id=t.id,
            arena_key=t.arena_key,
            key=t.key,
            name=t.name,
            blurb=t.blurb or "",
            is_following=is_following,
            open_debate_count=open_debate_count,
        )

    @router.get("/topics", response_model=list[schemas.TopicOut])
    def list_topics(
        arena_key: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: Optional[models.User] = Depends(get_current_user_optional),
    ):
        # Self-heal when code taxonomy is ahead of DB.
        try:
            from app import topic_ops

            if topic_ops.topics_need_seed(db):
                topic_ops.seed_topics(db)
        except Exception:  # noqa: BLE001
            pass
        from app.topics_data import ACTIVE_ARENA_KEYS

        q = db.query(models.Topic).filter(models.Topic.arena_key.in_(ACTIVE_ARENA_KEYS))
        if arena_key:
            if arena_key not in ACTIVE_ARENA_KEYS:
                return []
            q = q.filter(models.Topic.arena_key == arena_key)
        rows = q.order_by(models.Topic.arena_key.asc(), models.Topic.name.asc()).all()
        return [_topic_out(t, db, current_user) for t in rows]

    @router.get("/topics/mine", response_model=list[schemas.TopicOut])
    def my_topics(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        rows = (
            db.query(models.Topic)
            .join(models.UserTopicInterest, models.UserTopicInterest.topic_id == models.Topic.id)
            .filter(models.UserTopicInterest.user_id == current_user.id)
            .order_by(models.Topic.arena_key.asc(), models.Topic.name.asc())
            .all()
        )
        return [_topic_out(t, db, current_user) for t in rows]

    @router.post("/topics/interests", response_model=list[schemas.TopicOut])
    def set_topic_interests(
        payload: schemas.TopicInterestUpdate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        ids = [i for i in (payload.topic_ids or []) if i]
        # Cap at 20 picks for focus
        ids = ids[:20]
        valid = {
            t.id: t
            for t in db.query(models.Topic).filter(models.Topic.id.in_(ids)).all()
        } if ids else {}
        if payload.replace:
            db.query(models.UserTopicInterest).filter(
                models.UserTopicInterest.user_id == current_user.id
            ).delete(synchronize_session=False)
        existing = {
            r.topic_id
            for r in db.query(models.UserTopicInterest)
            .filter(models.UserTopicInterest.user_id == current_user.id)
            .all()
        }
        joined_arenas = {
            r.community_id
            for r in db.query(models.CommunityMember)
            .filter(models.CommunityMember.user_id == current_user.id)
            .all()
        }
        for tid in ids:
            if tid not in valid or tid in existing:
                continue
            db.add(models.UserTopicInterest(user_id=current_user.id, topic_id=tid))
            existing.add(tid)
            # Also join parent arena community when picking a topic
            arena = (
                db.query(models.Community)
                .filter(models.Community.arena_key == valid[tid].arena_key)
                .first()
            )
            if arena and arena.id not in joined_arenas:
                db.add(models.CommunityMember(community_id=arena.id, user_id=current_user.id))
                joined_arenas.add(arena.id)
        db.commit()
        rows = (
            db.query(models.Topic)
            .join(models.UserTopicInterest, models.UserTopicInterest.topic_id == models.Topic.id)
            .filter(models.UserTopicInterest.user_id == current_user.id)
            .order_by(models.Topic.arena_key.asc(), models.Topic.name.asc())
            .all()
        )
        return [_topic_out(t, db, current_user) for t in rows]

    # ---------- Live Talk (audio room under a Space) ----------

    from app import moderation as mod

    def _active_talk_q(db: Session, space_id: str):
        return db.query(models.LiveTalkParticipant).filter(
            models.LiveTalkParticipant.space_id == space_id,
            models.LiveTalkParticipant.left_at.is_(None),
            models.LiveTalkParticipant.removed_at.is_(None),
        )

    def _talk_participant_out(
        row: models.LiveTalkParticipant,
        *,
        current_user: models.User,
        host_id: str,
        pinned_ids: set[str],
    ) -> schemas.LiveTalkParticipantOut:
        u = row.user
        return schemas.LiveTalkParticipantOut(
            user=schemas.AuthorOut.model_validate(u),
            muted=bool(row.muted),
            video_enabled=bool(row.video_enabled),
            joined_at=row.joined_at,
            is_self=u.id == current_user.id,
            is_pinned=u.id in pinned_ids,
            is_host=u.id == host_id,
        )

    def _talk_state(db: Session, space: models.Space, current_user: models.User) -> schemas.LiveTalkStateOut:
        pinned_rows = (
            db.query(models.LiveTalkPin)
            .filter(
                models.LiveTalkPin.space_id == space.id,
                models.LiveTalkPin.viewer_id == current_user.id,
            )
            .all()
        )
        pinned_ids = {r.pinned_user_id for r in pinned_rows}
        rows = (
            _active_talk_q(db, space.id)
            .options(joinedload(models.LiveTalkParticipant.user))
            .order_by(models.LiveTalkParticipant.joined_at.asc())
            .all()
        )
        # Pinned first (viewer preference), then join order
        rows_sorted = sorted(
            rows,
            key=lambda r: (0 if r.user_id in pinned_ids else 1, r.joined_at or datetime.now(timezone.utc)),
        )
        me = next((r for r in rows if r.user_id == current_user.id), None)
        msgs = (
            db.query(models.LiveTalkMessage)
            .options(joinedload(models.LiveTalkMessage.sender))
            .filter(models.LiveTalkMessage.space_id == space.id)
            .order_by(models.LiveTalkMessage.created_at.desc())
            .limit(80)
            .all()
        )
        msgs = list(reversed(msgs))
        pinned_usernames = []
        for pid in pinned_ids:
            u = db.query(models.User).filter(models.User.id == pid).first()
            if u:
                pinned_usernames.append(u.username)
        # Keep recent reactions (last ~30s window, max 24)
        since = datetime.now(timezone.utc) - timedelta(seconds=45)
        reaction_rows = (
            db.query(models.LiveTalkReaction)
            .options(joinedload(models.LiveTalkReaction.user))
            .filter(
                models.LiveTalkReaction.space_id == space.id,
                models.LiveTalkReaction.created_at >= since,
            )
            .order_by(models.LiveTalkReaction.created_at.desc())
            .limit(24)
            .all()
        )
        return schemas.LiveTalkStateOut(
            space_id=space.id,
            max_participants=mod.LIVE_TALK_MAX,
            participant_count=len(rows),
            in_talk=me is not None,
            my_muted=bool(me.muted) if me else True,
            my_video=bool(me.video_enabled) if me else False,
            my_user_id=current_user.id,
            participants=[
                _talk_participant_out(r, current_user=current_user, host_id=space.host_id, pinned_ids=pinned_ids)
                for r in rows_sorted
            ],
            messages=[
                schemas.LiveTalkMessageOut(
                    id=m.id,
                    text=m.text,
                    created_at=m.created_at,
                    sender=schemas.AuthorOut.model_validate(m.sender),
                )
                for m in msgs
            ],
            reactions=[
                schemas.LiveTalkReactionOut(
                    id=r.id,
                    emoji=r.emoji,
                    created_at=r.created_at,
                    user=schemas.AuthorOut.model_validate(r.user),
                )
                for r in reversed(reaction_rows)
            ],
            pinned_usernames=pinned_usernames,
        )

    @router.get("/spaces/{space_id}/talk", response_model=schemas.LiveTalkStateOut)
    def get_live_talk(
        space_id: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        s = _get_space(db, space_id)
        _maybe_auto_close(db, s)
        return _talk_state(db, s, current_user)

    @router.post("/spaces/{space_id}/talk/join", response_model=schemas.LiveTalkStateOut)
    def join_live_talk(
        space_id: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        s = _get_space(db, space_id)
        _maybe_auto_close(db, s)
        if s.status != "open":
            raise HTTPException(status_code=400, detail="This room is closed")
        existing = (
            db.query(models.LiveTalkParticipant)
            .filter(
                models.LiveTalkParticipant.space_id == s.id,
                models.LiveTalkParticipant.user_id == current_user.id,
            )
            .first()
        )
        active_count = _active_talk_q(db, s.id).count()
        if existing and existing.left_at is None and existing.removed_at is None:
            return _talk_state(db, s, current_user)
        if active_count >= mod.LIVE_TALK_MAX and not (
            existing and existing.left_at is None and existing.removed_at is None
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Talk is full ({mod.LIVE_TALK_MAX} people). Try again when a seat opens.",
            )
        now = datetime.now(timezone.utc)
        if existing:
            existing.left_at = None
            existing.removed_at = None
            existing.removed_reason = ""
            existing.muted = True
            existing.video_enabled = False
            existing.joined_at = now
        else:
            db.add(
                models.LiveTalkParticipant(
                    space_id=s.id,
                    user_id=current_user.id,
                    muted=True,
                    video_enabled=False,
                    joined_at=now,
                )
            )
        db.commit()
        return _talk_state(db, s, current_user)

    @router.post("/spaces/{space_id}/talk/leave", response_model=schemas.LiveTalkStateOut)
    def leave_live_talk(
        space_id: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        s = _get_space(db, space_id)
        row = (
            db.query(models.LiveTalkParticipant)
            .filter(
                models.LiveTalkParticipant.space_id == s.id,
                models.LiveTalkParticipant.user_id == current_user.id,
                models.LiveTalkParticipant.left_at.is_(None),
            )
            .first()
        )
        if row:
            row.left_at = datetime.now(timezone.utc)
            row.muted = True
            row.video_enabled = False
            _clear_talk_signals_for_user(db, s.id, current_user.id)
            db.commit()
        return _talk_state(db, s, current_user)

    @router.patch("/spaces/{space_id}/talk/me", response_model=schemas.LiveTalkStateOut)
    def update_live_talk_me(
        space_id: str,
        payload: schemas.LiveTalkStateUpdate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        s = _get_space(db, space_id)
        row = (
            _active_talk_q(db, s.id)
            .filter(models.LiveTalkParticipant.user_id == current_user.id)
            .first()
        )
        if not row:
            raise HTTPException(status_code=400, detail="Join Talk first")
        if payload.muted is not None:
            row.muted = bool(payload.muted)
        if payload.video_enabled is not None:
            row.video_enabled = bool(payload.video_enabled)
        db.commit()
        return _talk_state(db, s, current_user)

    @router.post("/spaces/{space_id}/talk/pin", response_model=schemas.LiveTalkStateOut)
    def pin_live_talk_participant(
        space_id: str,
        payload: schemas.LiveTalkPinBody,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        s = _get_space(db, space_id)
        target = db.query(models.User).filter(models.User.username == payload.username).first()
        if not target:
            raise HTTPException(status_code=404, detail="User not found")
        on_call = (
            _active_talk_q(db, s.id)
            .filter(models.LiveTalkParticipant.user_id == target.id)
            .first()
        )
        if not on_call:
            raise HTTPException(status_code=400, detail="They are not on this Talk")
        exists = (
            db.query(models.LiveTalkPin)
            .filter(
                models.LiveTalkPin.space_id == s.id,
                models.LiveTalkPin.viewer_id == current_user.id,
                models.LiveTalkPin.pinned_user_id == target.id,
            )
            .first()
        )
        if not exists:
            db.add(
                models.LiveTalkPin(
                    space_id=s.id,
                    viewer_id=current_user.id,
                    pinned_user_id=target.id,
                )
            )
            db.commit()
        return _talk_state(db, s, current_user)

    @router.delete("/spaces/{space_id}/talk/pin/{username}", response_model=schemas.LiveTalkStateOut)
    def unpin_live_talk_participant(
        space_id: str,
        username: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        s = _get_space(db, space_id)
        uname = (username or "").strip().lstrip("@").lower()
        target = db.query(models.User).filter(models.User.username == uname).first()
        if not target:
            raise HTTPException(status_code=404, detail="User not found")
        db.query(models.LiveTalkPin).filter(
            models.LiveTalkPin.space_id == s.id,
            models.LiveTalkPin.viewer_id == current_user.id,
            models.LiveTalkPin.pinned_user_id == target.id,
        ).delete(synchronize_session=False)
        db.commit()
        return _talk_state(db, s, current_user)

    @router.get("/spaces/{space_id}/talk/messages", response_model=list[schemas.LiveTalkMessageOut])
    def list_live_talk_messages(
        space_id: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        s = _get_space(db, space_id)
        me = (
            _active_talk_q(db, s.id)
            .filter(models.LiveTalkParticipant.user_id == current_user.id)
            .first()
        )
        if not me:
            raise HTTPException(status_code=403, detail="Join Talk to see in-call messages")
        return _talk_state(db, s, current_user).messages

    @router.post("/spaces/{space_id}/talk/messages", response_model=schemas.LiveTalkStateOut)
    def post_live_talk_message(
        space_id: str,
        payload: schemas.LiveTalkMessageCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        s = _get_space(db, space_id)
        me = (
            _active_talk_q(db, s.id)
            .filter(models.LiveTalkParticipant.user_id == current_user.id)
            .first()
        )
        if not me:
            raise HTTPException(status_code=403, detail="Join Talk to message people on the call")
        blocked = mod.apply_talk_message_moderation(
            db,
            space_id=s.id,
            sender=current_user,
            text=payload.text,
            purge_fn=mod.purge_user,
        )
        if blocked:
            db.commit()
            raise HTTPException(status_code=400, detail=blocked)
        db.add(
            models.LiveTalkMessage(
                space_id=s.id,
                sender_id=current_user.id,
                text=payload.text,
            )
        )
        db.commit()
        return _talk_state(db, s, current_user)

    @router.post("/spaces/{space_id}/talk/reactions", response_model=schemas.LiveTalkStateOut)
    def post_live_talk_reaction(
        space_id: str,
        payload: schemas.LiveTalkReactionCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        s = _get_space(db, space_id)
        me = (
            _active_talk_q(db, s.id)
            .filter(models.LiveTalkParticipant.user_id == current_user.id)
            .first()
        )
        if not me:
            raise HTTPException(status_code=403, detail="Join the conversation to react")
        db.add(
            models.LiveTalkReaction(
                space_id=s.id,
                user_id=current_user.id,
                emoji=payload.emoji,
            )
        )
        db.commit()
        return _talk_state(db, s, current_user)

    @router.post("/spaces/{space_id}/talk/participants/{username}/remove", response_model=schemas.LiveTalkStateOut)
    def remove_live_talk_participant(
        space_id: str,
        username: str,
        payload: schemas.LiveTalkRemoveBody,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        """Host or any caller can remove someone for guideline violations — no admin wait."""
        s = _get_space(db, space_id)
        uname = (username or "").strip().lstrip("@").lower()
        target = db.query(models.User).filter(models.User.username == uname).first()
        if not target:
            raise HTTPException(status_code=404, detail="User not found")
        if target.id == current_user.id:
            raise HTTPException(status_code=400, detail="Leave Talk instead of removing yourself")
        me = (
            _active_talk_q(db, s.id)
            .filter(models.LiveTalkParticipant.user_id == current_user.id)
            .first()
        )
        is_host = s.host_id == current_user.id
        if not is_host and not me:
            raise HTTPException(status_code=403, detail="Join Talk or be the host to remove someone")
        if not is_host and not mod.reason_is_guideline(payload.reason):
            raise HTTPException(
                status_code=400,
                detail="Cite a community guideline reason (harassment, spam, misleading, …)",
            )
        row = (
            _active_talk_q(db, s.id)
            .filter(models.LiveTalkParticipant.user_id == target.id)
            .first()
        )
        now = datetime.now(timezone.utc)
        if row:
            row.removed_at = now
            row.left_at = now
            row.removed_reason = payload.reason[:200]
        db.add(
            models.Report(
                reporter_id=current_user.id,
                target_user_id=target.id,
                reason=payload.reason[:80],
                details=f"Removed from Live Talk in space {s.id}",
            )
        )
        mod.add_strike(
            db,
            user_id=target.id,
            kind="talk_remove",
            detail=payload.reason[:200],
            space_id=s.id,
        )
        mod.maybe_auto_delete_user(db, target, purge_fn=mod.purge_user)
        db.commit()
        return _talk_state(db, s, current_user)

    def _purge_old_talk_signals(db: Session, space_id: str):
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=2)
        db.query(models.LiveTalkSignal).filter(
            models.LiveTalkSignal.space_id == space_id,
            models.LiveTalkSignal.created_at < cutoff,
        ).delete(synchronize_session=False)

    def _clear_talk_signals_for_user(db: Session, space_id: str, user_id: str):
        db.query(models.LiveTalkSignal).filter(
            models.LiveTalkSignal.space_id == space_id,
            or_(
                models.LiveTalkSignal.from_user_id == user_id,
                models.LiveTalkSignal.to_user_id == user_id,
            ),
        ).delete(synchronize_session=False)

    @router.post("/spaces/{space_id}/talk/signals", response_model=schemas.LiveTalkSignalOut)
    def post_live_talk_signal(
        space_id: str,
        payload: schemas.LiveTalkSignalCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        s = _get_space(db, space_id)
        me = (
            _active_talk_q(db, s.id)
            .filter(models.LiveTalkParticipant.user_id == current_user.id)
            .first()
        )
        if not me:
            raise HTTPException(status_code=400, detail="Join the conversation first")
        if payload.to_user_id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot signal yourself")
        peer = (
            _active_talk_q(db, s.id)
            .filter(models.LiveTalkParticipant.user_id == payload.to_user_id)
            .first()
        )
        if not peer:
            raise HTTPException(status_code=404, detail="Peer is not on this call")
        row = models.LiveTalkSignal(
            space_id=s.id,
            from_user_id=current_user.id,
            to_user_id=payload.to_user_id,
            kind=payload.kind,
            payload=payload.payload,
        )
        db.add(row)
        _purge_old_talk_signals(db, s.id)
        db.commit()
        db.refresh(row)
        return schemas.LiveTalkSignalOut(
            id=row.id,
            from_user_id=row.from_user_id,
            to_user_id=row.to_user_id,
            kind=row.kind,
            payload=row.payload,
            created_at=row.created_at,
        )

    @router.get("/spaces/{space_id}/talk/signals", response_model=list[schemas.LiveTalkSignalOut])
    def list_live_talk_signals(
        space_id: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        s = _get_space(db, space_id)
        me = (
            _active_talk_q(db, s.id)
            .filter(models.LiveTalkParticipant.user_id == current_user.id)
            .first()
        )
        if not me:
            return []
        _purge_old_talk_signals(db, s.id)
        rows = (
            db.query(models.LiveTalkSignal)
            .filter(
                models.LiveTalkSignal.space_id == s.id,
                models.LiveTalkSignal.to_user_id == current_user.id,
                models.LiveTalkSignal.delivered.is_(False),
            )
            .order_by(models.LiveTalkSignal.created_at.asc())
            .limit(80)
            .all()
        )
        out = []
        for row in rows:
            row.delivered = True
            out.append(
                schemas.LiveTalkSignalOut(
                    id=row.id,
                    from_user_id=row.from_user_id,
                    to_user_id=row.to_user_id,
                    kind=row.kind,
                    payload=row.payload,
                    created_at=row.created_at,
                )
            )
        db.commit()
        return out

    app.include_router(router)
