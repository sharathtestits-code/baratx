"""Bookmarks, block/mute/report, DMs, hashtag lookup, early issues — mounted from main."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload

from app import email as email_service, models, schemas
from app.database import get_db

logger = logging.getLogger("baratx.extra")

router = APIRouter()

EARLY_ISSUE_CAP = 1000
WHATSAPP_CHANNEL = "https://whatsapp.com/channel/0029VbDMIgqHQbS9tfQo6u2o"
WHATSAPP_COMMUNITY = "https://chat.whatsapp.com/EV3Uj35EXrHImZ6MZxGAtU?mode=gi_t"


def _blocked_ids(db: Session, user_id: str) -> set[str]:
    rows = (
        db.query(models.Block.blocked_id)
        .filter(models.Block.blocker_id == user_id)
        .all()
    )
    blocked_me = (
        db.query(models.Block.blocker_id)
        .filter(models.Block.blocked_id == user_id)
        .all()
    )
    return {r[0] for r in rows} | {r[0] for r in blocked_me}


def _is_blocked_pair(db: Session, a_id: str, b_id: str) -> bool:
    return (
        db.query(models.Block)
        .filter(
            or_(
                and_(models.Block.blocker_id == a_id, models.Block.blocked_id == b_id),
                and_(models.Block.blocker_id == b_id, models.Block.blocked_id == a_id),
            )
        )
        .first()
        is not None
    )


def register_extra_routes(app, *, get_current_user, get_current_user_optional, serialize_user, serialize_post, create_notification):
    """Attach routes that need main.py helpers via closure."""

    @router.post("/posts/{post_id}/bookmark", response_model=schemas.PostOut)
    def bookmark_post(
        post_id: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        post = db.query(models.Post).filter(models.Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        existing = (
            db.query(models.Bookmark)
            .filter(models.Bookmark.user_id == current_user.id, models.Bookmark.post_id == post_id)
            .first()
        )
        if not existing:
            db.add(models.Bookmark(user_id=current_user.id, post_id=post_id))
            db.commit()
            db.refresh(post)
        return serialize_post(post, current_user)

    @router.delete("/posts/{post_id}/bookmark", response_model=schemas.PostOut)
    def unbookmark_post(
        post_id: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        post = db.query(models.Post).filter(models.Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        existing = (
            db.query(models.Bookmark)
            .filter(models.Bookmark.user_id == current_user.id, models.Bookmark.post_id == post_id)
            .first()
        )
        if existing:
            db.delete(existing)
            db.commit()
            db.refresh(post)
        return serialize_post(post, current_user)

    @router.get("/bookmarks", response_model=list[schemas.PostOut])
    def list_bookmarks(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        rows = (
            db.query(models.Bookmark)
            .filter(models.Bookmark.user_id == current_user.id)
            .order_by(models.Bookmark.created_at.desc())
            .limit(100)
            .all()
        )
        return [serialize_post(r.post, current_user) for r in rows if r.post]

    @router.post("/users/{username}/block", response_model=schemas.MessageResponse)
    def block_user(
        username: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        target = db.query(models.User).filter(models.User.username == username).first()
        if not target:
            raise HTTPException(status_code=404, detail="User not found")
        if target.id == current_user.id:
            raise HTTPException(status_code=400, detail="You can't block yourself")
        existing = (
            db.query(models.Block)
            .filter(models.Block.blocker_id == current_user.id, models.Block.blocked_id == target.id)
            .first()
        )
        if not existing:
            db.add(models.Block(blocker_id=current_user.id, blocked_id=target.id))
            # also remove follow relationships both ways
            db.query(models.Follow).filter(
                or_(
                    and_(models.Follow.follower_id == current_user.id, models.Follow.followed_id == target.id),
                    and_(models.Follow.follower_id == target.id, models.Follow.followed_id == current_user.id),
                )
            ).delete(synchronize_session=False)
            db.commit()
        return schemas.MessageResponse(message=f"Blocked @{username}")

    @router.delete("/users/{username}/block", response_model=schemas.MessageResponse)
    def unblock_user(
        username: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        target = db.query(models.User).filter(models.User.username == username).first()
        if not target:
            raise HTTPException(status_code=404, detail="User not found")
        existing = (
            db.query(models.Block)
            .filter(models.Block.blocker_id == current_user.id, models.Block.blocked_id == target.id)
            .first()
        )
        if existing:
            db.delete(existing)
            db.commit()
        return schemas.MessageResponse(message=f"Unblocked @{username}")

    @router.post("/users/{username}/mute", response_model=schemas.MessageResponse)
    def mute_user(
        username: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        target = db.query(models.User).filter(models.User.username == username).first()
        if not target:
            raise HTTPException(status_code=404, detail="User not found")
        if target.id == current_user.id:
            raise HTTPException(status_code=400, detail="You can't mute yourself")
        existing = (
            db.query(models.Mute)
            .filter(models.Mute.muter_id == current_user.id, models.Mute.muted_id == target.id)
            .first()
        )
        if not existing:
            db.add(models.Mute(muter_id=current_user.id, muted_id=target.id))
            db.commit()
        return schemas.MessageResponse(message=f"Muted @{username}")

    @router.delete("/users/{username}/mute", response_model=schemas.MessageResponse)
    def unmute_user(
        username: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        target = db.query(models.User).filter(models.User.username == username).first()
        if not target:
            raise HTTPException(status_code=404, detail="User not found")
        existing = (
            db.query(models.Mute)
            .filter(models.Mute.muter_id == current_user.id, models.Mute.muted_id == target.id)
            .first()
        )
        if existing:
            db.delete(existing)
            db.commit()
        return schemas.MessageResponse(message=f"Unmuted @{username}")

    @router.post("/reports", response_model=schemas.MessageResponse)
    def create_report(
        payload: schemas.ReportCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        if not payload.target_username and not payload.target_post_id:
            raise HTTPException(status_code=400, detail="Provide a user or post to report")
        target_user_id = None
        if payload.target_username:
            u = db.query(models.User).filter(models.User.username == payload.target_username).first()
            if not u:
                raise HTTPException(status_code=404, detail="User not found")
            target_user_id = u.id
        if payload.target_post_id:
            p = db.query(models.Post).filter(models.Post.id == payload.target_post_id).first()
            if not p:
                raise HTTPException(status_code=404, detail="Post not found")
        db.add(
            models.Report(
                reporter_id=current_user.id,
                target_user_id=target_user_id,
                target_post_id=payload.target_post_id,
                reason=payload.reason,
                details=payload.details or "",
            )
        )
        db.flush()
        msg = "Report submitted. Thanks for helping keep BarathX safe."
        if target_user_id:
            from app import moderation as mod

            target = db.query(models.User).filter(models.User.id == target_user_id).first()
            if target:
                msg = mod.apply_report_auto_mod(
                    db,
                    target=target,
                    reason=payload.reason,
                    details=payload.details or "",
                    purge_fn=mod.purge_user,
                )
        db.commit()
        # Ops email on every report / bug log.
        try:
            email_service.send_ops_alert_email(
                subject=f"[BarathX] Report: {payload.reason[:60]}",
                summary=payload.reason,
                details=payload.details or "",
                reporter=f"@{current_user.username}",
                kind="report",
            )
        except Exception:
            logger.exception("Report alert email failed")
        return schemas.MessageResponse(message=msg)

    @router.get("/hashtags/{tag}", response_model=list[schemas.PostOut])
    def hashtag_posts(
        tag: str,
        db: Session = Depends(get_db),
        current_user: Optional[models.User] = Depends(get_current_user_optional),
    ):
        clean = tag.lstrip("#").lower().strip()
        if len(clean) < 2:
            return []
        ht = db.query(models.Hashtag).filter(models.Hashtag.tag == clean).first()
        if not ht:
            return []
        links = (
            db.query(models.PostHashtag)
            .filter(models.PostHashtag.hashtag_id == ht.id)
            .order_by(models.PostHashtag.id.desc())
            .limit(50)
            .all()
        )
        posts = []
        for link in links:
            post = db.query(models.Post).filter(models.Post.id == link.post_id).first()
            if post:
                posts.append(serialize_post(post, current_user))
        return posts

    @router.get("/messages", response_model=list[schemas.ConversationOut])
    def list_conversations(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        msgs = (
            db.query(models.DirectMessage)
            .options(
                joinedload(models.DirectMessage.sender),
                joinedload(models.DirectMessage.recipient),
            )
            .filter(
                or_(
                    models.DirectMessage.sender_id == current_user.id,
                    models.DirectMessage.recipient_id == current_user.id,
                )
            )
            .order_by(models.DirectMessage.created_at.desc())
            .limit(500)
            .all()
        )
        blocked = _blocked_ids(db, current_user.id)
        latest_by_peer: dict[str, models.DirectMessage] = {}
        unread_by_peer: dict[str, int] = {}
        for m in msgs:
            peer = m.recipient_id if m.sender_id == current_user.id else m.sender_id
            if peer in blocked:
                continue
            if peer not in latest_by_peer:
                latest_by_peer[peer] = m
            if m.recipient_id == current_user.id and not m.is_read:
                unread_by_peer[peer] = unread_by_peer.get(peer, 0) + 1

        out = []
        for peer_id, last in latest_by_peer.items():
            peer = db.query(models.User).filter(models.User.id == peer_id).first()
            if not peer:
                continue
            out.append(
                schemas.ConversationOut(
                    user=schemas.AuthorOut.model_validate(peer),
                    last_message=schemas.MessageOut(
                        id=last.id,
                        text=last.text,
                        created_at=last.created_at,
                        is_read=last.is_read,
                        sender=schemas.AuthorOut.model_validate(last.sender),
                        recipient=schemas.AuthorOut.model_validate(last.recipient),
                    ),
                    unread_count=unread_by_peer.get(peer_id, 0),
                )
            )
        return out

    @router.get("/messages/{username}", response_model=list[schemas.MessageOut])
    def get_thread(
        username: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        peer = db.query(models.User).filter(models.User.username == username).first()
        if not peer:
            raise HTTPException(status_code=404, detail="User not found")
        if _is_blocked_pair(db, current_user.id, peer.id):
            raise HTTPException(status_code=403, detail="Conversation unavailable")
        rows = (
            db.query(models.DirectMessage)
            .filter(
                or_(
                    and_(
                        models.DirectMessage.sender_id == current_user.id,
                        models.DirectMessage.recipient_id == peer.id,
                    ),
                    and_(
                        models.DirectMessage.sender_id == peer.id,
                        models.DirectMessage.recipient_id == current_user.id,
                    ),
                )
            )
            .order_by(models.DirectMessage.created_at.asc())
            .limit(200)
            .all()
        )
        # mark inbound as read
        changed = False
        for m in rows:
            if m.recipient_id == current_user.id and not m.is_read:
                m.is_read = True
                changed = True
        if changed:
            db.commit()
        return [
            schemas.MessageOut(
                id=m.id,
                text=m.text,
                created_at=m.created_at,
                is_read=m.is_read,
                sender=schemas.AuthorOut.model_validate(m.sender),
                recipient=schemas.AuthorOut.model_validate(m.recipient),
            )
            for m in rows
        ]

    @router.post("/messages/{username}", response_model=schemas.MessageOut)
    def send_message(
        username: str,
        payload: schemas.MessageCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        peer = db.query(models.User).filter(models.User.username == username).first()
        if not peer:
            raise HTTPException(status_code=404, detail="User not found")
        if peer.id == current_user.id:
            raise HTTPException(status_code=400, detail="You can't message yourself")
        if _is_blocked_pair(db, current_user.id, peer.id):
            raise HTTPException(status_code=403, detail="Conversation unavailable")
        msg = models.DirectMessage(
            sender_id=current_user.id,
            recipient_id=peer.id,
            text=payload.text,
        )
        db.add(msg)
        create_notification(
            db,
            recipient_id=peer.id,
            actor_id=current_user.id,
            kind="message",
        )
        db.commit()
        db.refresh(msg)
        return schemas.MessageOut(
            id=msg.id,
            text=msg.text,
            created_at=msg.created_at,
            is_read=msg.is_read,
            sender=schemas.AuthorOut.model_validate(msg.sender),
            recipient=schemas.AuthorOut.model_validate(msg.recipient),
        )

    def _early_rank(db: Session, user: models.User) -> int:
        """1-based join order among non-official accounts (first 1000 = early circle)."""
        earlier = (
            db.query(func.count(models.User.id))
            .filter(
                models.User.is_official.is_(False),
                or_(
                    models.User.created_at < user.created_at,
                    and_(
                        models.User.created_at == user.created_at,
                        models.User.id <= user.id,
                    ),
                ),
            )
            .scalar()
        )
        return int(earlier or 0)

    def _author_out(user: models.User) -> schemas.AuthorOut:
        badge = (getattr(user, "badge", None) or "none").strip().lower()
        if badge not in ("none", "gold", "blue"):
            badge = "none"
        return schemas.AuthorOut(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            badge=badge,
            is_official=bool(getattr(user, "is_official", False) or badge == "blue"),
        )

    @router.get("/early-issues/meta", response_model=schemas.EarlyIssuesMetaOut)
    def early_issues_meta(
        current_user: Optional[models.User] = Depends(get_current_user_optional),
        db: Session = Depends(get_db),
    ):
        is_early = False
        rank = None
        if current_user and not getattr(current_user, "is_official", False):
            rank = _early_rank(db, current_user)
            is_early = rank <= EARLY_ISSUE_CAP
        return schemas.EarlyIssuesMetaOut(
            early_cap=EARLY_ISSUE_CAP,
            is_early_member=is_early,
            early_rank=rank,
            whatsapp_community=WHATSAPP_COMMUNITY,
            whatsapp_channel=WHATSAPP_CHANNEL,
            message=(
                "First 1000 members can post bugs and concerns here. "
                "Everyone can join WhatsApp Community / Channel to talk it through."
            ),
        )

    @router.get("/early-issues", response_model=list[schemas.ProductIssueOut])
    def list_early_issues(
        limit: int = 40,
        db: Session = Depends(get_db),
        current_user: Optional[models.User] = Depends(get_current_user_optional),
    ):
        limit = max(1, min(limit, 100))
        rows = (
            db.query(models.ProductIssue)
            .options(joinedload(models.ProductIssue.author))
            .order_by(models.ProductIssue.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            schemas.ProductIssueOut(
                id=r.id,
                text=r.text,
                kind=r.kind,
                created_at=r.created_at,
                author=_author_out(r.author),
            )
            for r in rows
            if r.author
        ]

    @router.post("/early-issues", response_model=schemas.ProductIssueOut)
    def create_early_issue(
        payload: schemas.ProductIssueCreate,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        if getattr(current_user, "is_official", False):
            raise HTTPException(status_code=400, detail="Official accounts use ops tools for bugs")
        rank = _early_rank(db, current_user)
        if rank > EARLY_ISSUE_CAP:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Early issues board is for the first 1000 members. "
                    "Join WhatsApp Community to share concerns, or report a post from ···."
                ),
            )
        issue = models.ProductIssue(
            author_id=current_user.id,
            kind=payload.kind,
            text=payload.text,
            created_at=datetime.now(timezone.utc),
        )
        db.add(issue)
        db.commit()
        db.refresh(issue)
        try:
            email_service.send_ops_alert_email(
                subject=f"[BarathX] Early issue ({payload.kind}) from @{current_user.username}",
                summary=payload.text[:200],
                details=payload.text,
                reporter=f"@{current_user.username} (early #{rank})",
                kind=payload.kind,
            )
        except Exception:
            logger.exception("Early issue alert email failed")
        return schemas.ProductIssueOut(
            id=issue.id,
            text=issue.text,
            kind=issue.kind,
            created_at=issue.created_at,
            author=_author_out(current_user),
        )

    app.include_router(router)
