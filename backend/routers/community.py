from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func, text
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from database import get_db
from models import User, Challenge, ChallengeParticipation, Friendship, Message, Post, PostLike, PostComment
from auth import get_current_user

router = APIRouter(prefix="/api/community", tags=["community"])


class LeaderboardUser(BaseModel):
    rank: int
    name: str
    points: int
    workouts: int
    avatar: str
    trend: str = "same"

    class Config:
        from_attributes = True


class ChallengeResponse(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    participants: int
    progress: int
    target: int
    unit: str
    reward: int
    timeLeft: str
    joined: bool

    class Config:
        from_attributes = True


class FriendResponse(BaseModel):
    id: int
    name: str
    status: Optional[str]
    avatar: str
    online: bool
    unread_count: int = 0

    class Config:
        from_attributes = True


class SuggestedUserResponse(BaseModel):
    id: int
    name: str
    bio: Optional[str]
    avatar: str
    level: int
    mutualFriends: int

    class Config:
        from_attributes = True


class FriendRequestResponse(BaseModel):
    id: int
    user_id: int
    username: str
    avatar: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    recipient_id: int
    content: str


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    sender_name: str
    recipient_id: int
    recipient_name: str
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ChallengeCreate(BaseModel):
    name: str
    description: str
    icon: str
    target: int
    unit: str
    reward_points: int
    end_date: datetime



@router.get("/leaderboard/weekly", response_model=List[LeaderboardUser])
async def get_weekly_leaderboard(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weekly leaderboard."""
    users = db.query(User).order_by(desc(User.workouts_this_week), desc(User.points)).limit(limit).all()

    return [
        LeaderboardUser(
            rank=idx + 1,
            name=user.username,
            points=user.points,
            workouts=user.workouts_this_week,
            avatar=user.username[:2].upper(),
            trend="up" if idx % 2 == 0 else "same"
        )
        for idx, user in enumerate(users)
    ]


@router.get("/leaderboard/monthly", response_model=List[LeaderboardUser])
async def get_monthly_leaderboard(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly leaderboard."""
    users = db.query(User).order_by(desc(User.workouts_this_month), desc(User.points)).limit(limit).all()

    return [
        LeaderboardUser(
            rank=idx + 1,
            name=user.username,
            points=user.points,
            workouts=user.workouts_this_month,
            avatar=user.username[:2].upper(),
            trend="up"
        )
        for idx, user in enumerate(users)
    ]



@router.get("/challenges", response_model=List[ChallengeResponse])
async def get_challenges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active challenges."""
    now = datetime.utcnow()
    challenges = db.query(Challenge).filter(Challenge.end_date > now).all()

    result = []
    for challenge in challenges:
        # Count participants
        participants_count = db.query(ChallengeParticipation).filter(
            ChallengeParticipation.challenge_id == challenge.id
        ).count()

        # Check if user joined and get progress
        user_participation = None
        if current_user:
            user_participation = db.query(ChallengeParticipation).filter(
                and_(
                    ChallengeParticipation.challenge_id == challenge.id,
                    ChallengeParticipation.user_id == current_user.id
                )
            ).first()

        # Calculate time left
        days_left = (challenge.end_date - now).days
        if days_left == 0:
            time_left = "Ends today"
        elif days_left < 0:
            time_left = "Starts tomorrow"
        else:
            time_left = f"{days_left} days left"

        result.append(ChallengeResponse(
            id=challenge.id,
            name=challenge.name,
            description=challenge.description,
            icon=challenge.icon,
            participants=participants_count,
            progress=user_participation.progress if user_participation else 0,
            target=challenge.target,
            unit=challenge.unit,
            reward=challenge.reward_points,
            timeLeft=time_left,
            joined=user_participation is not None
        ))

    return result


@router.post("/challenges/create")
async def create_challenge(
    challenge_data: ChallengeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new challenge."""
    # Fix sequence if needed (PostgreSQL auto-increment issue)
    try:
        db.execute(text(
            "SELECT setval(pg_get_serial_sequence('challenges', 'id'), "
            "COALESCE((SELECT MAX(id) FROM challenges), 1), true);"
        ))
        db.commit()
    except Exception as seq_err:
        print(f"Warning: Could not fix sequence: {seq_err}")
        db.rollback()

    challenge = Challenge(
        name=challenge_data.name,
        description=challenge_data.description,
        icon=challenge_data.icon,
        target=challenge_data.target,
        unit=challenge_data.unit,
        reward_points=challenge_data.reward_points,
        start_date=datetime.now(timezone.utc),
        end_date=challenge_data.end_date
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    return {"message": "Challenge created successfully", "challenge_id": challenge.id}


@router.post("/challenges/{challenge_id}/join")
async def join_challenge(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a challenge."""
    # Fix sequence if needed (PostgreSQL auto-increment issue)
    try:
        db.execute(text(
            "SELECT setval(pg_get_serial_sequence('challenge_participations', 'id'), "
            "COALESCE((SELECT MAX(id) FROM challenge_participations), 1), true);"
        ))
        db.commit()
    except Exception as seq_err:
        print(f"Warning: Could not fix sequence: {seq_err}")
        db.rollback()

    # Check if challenge exists
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    # Check if already joined
    existing = db.query(ChallengeParticipation).filter(
        and_(
            ChallengeParticipation.challenge_id == challenge_id,
            ChallengeParticipation.user_id == current_user.id
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already joined this challenge")

    # Create participation
    participation = ChallengeParticipation(
        user_id=current_user.id,
        challenge_id=challenge_id,
        progress=0
    )
    db.add(participation)

    # Award points for joining a challenge
    POINTS_PER_JOIN = 20
    current_user.points += POINTS_PER_JOIN

    # Calculate new level (100 points per level)
    new_level = (current_user.points // 100) + 1
    current_user.level = new_level

    db.commit()

    return {
        "message": "Successfully joined challenge",
        "points_earned": POINTS_PER_JOIN,
        "total_points": current_user.points,
        "level": current_user.level
    }


class ChallengeProgressUpdate(BaseModel):
    progress: int


@router.patch("/challenges/{challenge_id}/progress")
async def update_challenge_progress(
    challenge_id: int,
    progress_data: ChallengeProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update progress for a challenge."""
    # Get user's participation
    participation = db.query(ChallengeParticipation).filter(
        and_(
            ChallengeParticipation.challenge_id == challenge_id,
            ChallengeParticipation.user_id == current_user.id
        )
    ).first()

    if not participation:
        raise HTTPException(
            status_code=404,
            detail="You haven't joined this challenge"
        )

    # Get challenge to check target
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    # Update progress
    participation.progress = progress_data.progress

    # Check if completed
    if progress_data.progress >= challenge.target and not participation.completed:
        participation.completed = True
        participation.completed_at = datetime.now(timezone.utc)

        # Award points to user
        current_user.points += challenge.reward_points

    db.commit()

    return {
        "message": "Progress updated successfully",
        "progress": participation.progress,
        "completed": participation.completed
    }


@router.get("/friends", response_model=List[FriendResponse])
async def get_friends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's friends list."""
    # Get accepted friendships
    friendships = db.query(Friendship).filter(
        and_(
            or_(
                Friendship.user_id == current_user.id,
                Friendship.friend_id == current_user.id
            ),
            Friendship.status == "accepted"
        )
    ).all()

    friends = []
    for friendship in friendships:
        friend = None
        if friendship.user_id == current_user.id:
            friend = friendship.friend
        else:
            friend = friendship.user

        # Count unread messages from this friend
        unread_count = db.query(Message).filter(
            and_(
                Message.sender_id == friend.id,
                Message.recipient_id == current_user.id,
                Message.is_read == False
            )
        ).count()

        friends.append(FriendResponse(
            id=friend.id,
            name=friend.username,
            status=friend.status or "Active",
            avatar=friend.username[:2].upper(),
            online=friend.is_online,
            unread_count=unread_count
        ))

    return friends


@router.post("/friends/{user_id}/add")
async def add_friend(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send friend request."""
    # Fix sequence if needed (PostgreSQL auto-increment issue)
    try:
        db.execute(text(
            "SELECT setval(pg_get_serial_sequence('friendships', 'id'), "
            "COALESCE((SELECT MAX(id) FROM friendships), 1), true);"
        ))
        db.commit()
    except Exception as seq_err:
        print(f"Warning: Could not fix sequence: {seq_err}")
        db.rollback()

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot add yourself as friend")

    # Check if user exists
    friend = db.query(User).filter(User.id == user_id).first()
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if friendship already exists
    existing = db.query(Friendship).filter(
        or_(
            and_(Friendship.user_id == current_user.id, Friendship.friend_id == user_id),
            and_(Friendship.user_id == user_id, Friendship.friend_id == current_user.id)
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Friendship already exists")

    # Create friendship
    friendship = Friendship(
        user_id=current_user.id,
        friend_id=user_id,
        status="pending"
    )
    db.add(friendship)
    db.commit()

    return {"message": "Friend request sent"}


@router.get("/friends/requests", response_model=List[FriendRequestResponse])
async def get_friend_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending friend requests."""
    requests = db.query(Friendship).filter(
        and_(
            Friendship.friend_id == current_user.id,
            Friendship.status == "pending"
        )
    ).all()

    return [
        FriendRequestResponse(
            id=req.id,
            user_id=req.user.id,
            username=req.user.username,
            avatar=req.user.username[:2].upper(),
            created_at=req.created_at
        )
        for req in requests
    ]


@router.post("/friends/{friendship_id}/accept")
async def accept_friend_request(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    friendship = db.query(Friendship).filter(Friendship.id == friendship_id).first()

    if not friendship:
        raise HTTPException(status_code=404, detail="Friend request not found")

    if friendship.friend_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to accept this request")

    friendship.status = "accepted"
    db.commit()

    return {"message": "Friend request accepted"}


@router.post("/friends/{friendship_id}/reject")
async def reject_friend_request(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a friend request."""
    friendship = db.query(Friendship).filter(Friendship.id == friendship_id).first()

    if not friendship:
        raise HTTPException(status_code=404, detail="Friend request not found")

    if friendship.friend_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to reject this request")

    db.delete(friendship)
    db.commit()

    return {"message": "Friend request rejected"}



@router.post("/messages/send")
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to another user."""
    # Check if recipient exists
    recipient = db.query(User).filter(User.id == message_data.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    # Check if users are friends
    friendship = db.query(Friendship).filter(
        and_(
            or_(
                and_(Friendship.user_id == current_user.id, Friendship.friend_id == message_data.recipient_id),
                and_(Friendship.user_id == message_data.recipient_id, Friendship.friend_id == current_user.id)
            ),
            Friendship.status == "accepted"
        )
    ).first()

    if not friendship:
        raise HTTPException(status_code=403, detail="You can only send messages to friends")

    # Create message
    message = Message(
        sender_id=current_user.id,
        recipient_id=message_data.recipient_id,
        content=message_data.content
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    return {"message": "Message sent successfully", "message_id": message.id}


@router.get("/messages/unread/count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread messages."""
    count = db.query(Message).filter(
        and_(
            Message.recipient_id == current_user.id,
            Message.is_read == False
        )
    ).count()

    return {"unread_count": count}


@router.get("/messages/{friend_id}", response_model=List[MessageResponse])
async def get_conversation(
    friend_id: int,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation with a friend."""
    # Check if users are friends
    friendship = db.query(Friendship).filter(
        and_(
            or_(
                and_(Friendship.user_id == current_user.id, Friendship.friend_id == friend_id),
                and_(Friendship.user_id == friend_id, Friendship.friend_id == current_user.id)
            ),
            Friendship.status == "accepted"
        )
    ).first()

    if not friendship:
        raise HTTPException(status_code=403, detail="You can only view messages with friends")

    # Get messages between users
    messages = db.query(Message).filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.recipient_id == friend_id),
            and_(Message.sender_id == friend_id, Message.recipient_id == current_user.id)
        )
    ).order_by(Message.created_at.desc()).limit(limit).all()

    # Mark messages from friend as read
    db.query(Message).filter(
        and_(
            Message.sender_id == friend_id,
            Message.recipient_id == current_user.id,
            Message.is_read == False
        )
    ).update({"is_read": True})
    db.commit()

    return [
        MessageResponse(
            id=msg.id,
            sender_id=msg.sender_id,
            sender_name=msg.sender.username,
            recipient_id=msg.recipient_id,
            recipient_name=msg.recipient.username,
            content=msg.content,
            is_read=msg.is_read,
            created_at=msg.created_at
        )
        for msg in reversed(messages)
    ]



@router.get("/suggested", response_model=List[SuggestedUserResponse])
async def get_suggested_users(
    current_user: User = Depends(get_current_user),
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """Get suggested users to connect with."""
    # Get users not already friends
    existing_friend_ids = db.query(Friendship.friend_id).filter(
        Friendship.user_id == current_user.id
    ).union(
        db.query(Friendship.user_id).filter(Friendship.friend_id == current_user.id)
    ).all()

    existing_friend_ids = [f[0] for f in existing_friend_ids]
    existing_friend_ids.append(current_user.id)  # Exclude self

    # Get random users with similar level
    suggested = db.query(User).filter(
        User.id.notin_(existing_friend_ids)
    ).order_by(func.random()).limit(limit).all()

    result = []
    for user in suggested:
        # Count mutual friends (simplified)
        mutual_count = 0

        result.append(SuggestedUserResponse(
            id=user.id,
            name=user.username,
            bio=user.status or "Fitness enthusiast",
            avatar=user.username[:2].upper(),
            level=user.level,
            mutualFriends=mutual_count
        ))

    return result



class PostCreate(BaseModel):
    content: str

class PostResponse(BaseModel):
    id: int
    user_id: int
    username: str
    avatar: str
    content: str
    likes_count: int
    comments_count: int
    is_liked: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: int
    user_id: int
    username: str
    avatar: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/posts", response_model=List[PostResponse])
async def get_posts(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent posts from friends and self."""
    # Get friend IDs
    friend_ids = db.query(Friendship.friend_id).filter(
        and_(Friendship.user_id == current_user.id, Friendship.status == "accepted")
    ).union(
        db.query(Friendship.user_id).filter(
            and_(Friendship.friend_id == current_user.id, Friendship.status == "accepted")
        )
    ).all()

    friend_ids = [f[0] for f in friend_ids]
    friend_ids.append(current_user.id)  # Include own posts

    # Get posts
    posts = db.query(Post).filter(
        Post.user_id.in_(friend_ids)
    ).order_by(desc(Post.created_at)).offset(offset).limit(limit).all()

    result = []
    for post in posts:
        likes_count = db.query(PostLike).filter(PostLike.post_id == post.id).count()
        comments_count = db.query(PostComment).filter(PostComment.post_id == post.id).count()
        is_liked = db.query(PostLike).filter(
            and_(PostLike.post_id == post.id, PostLike.user_id == current_user.id)
        ).first() is not None

        result.append(PostResponse(
            id=post.id,
            user_id=post.user_id,
            username=post.user.username,
            avatar=post.user.username[:2].upper(),
            content=post.content,
            likes_count=likes_count,
            comments_count=comments_count,
            is_liked=is_liked,
            created_at=post.created_at
        ))

    return result


@router.post("/posts")
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not post_data.content.strip():
        raise HTTPException(status_code=400, detail="Post content cannot be empty")

    post = Post(
        user_id=current_user.id,
        content=post_data.content.strip()
    )
    db.add(post)

    # Award points for creating a post
    POINTS_PER_POST = 5
    current_user.points += POINTS_PER_POST

    # Calculate new level (100 points per level)
    new_level = (current_user.points // 100) + 1
    current_user.level = new_level

    db.commit()
    db.refresh(post)

    return {
        "message": "Post created successfully",
        "post_id": post.id,
        "points_earned": POINTS_PER_POST,
        "total_points": current_user.points,
        "level": current_user.level
    }


@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check if already liked
    existing_like = db.query(PostLike).filter(
        and_(PostLike.post_id == post_id, PostLike.user_id == current_user.id)
    ).first()

    if existing_like:
        # Unlike
        db.delete(existing_like)
        db.commit()
        return {"message": "Post unliked", "liked": False}
    else:
        # Like
        like = PostLike(post_id=post_id, user_id=current_user.id)
        db.add(like)
        db.commit()
        return {"message": "Post liked", "liked": True}


@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
async def get_post_comments(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comments for a post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comments = db.query(PostComment).filter(
        PostComment.post_id == post_id
    ).order_by(PostComment.created_at).all()

    return [
        CommentResponse(
            id=comment.id,
            user_id=comment.user_id,
            username=comment.user.username,
            avatar=comment.user.username[:2].upper(),
            content=comment.content,
            created_at=comment.created_at
        )
        for comment in comments
    ]


@router.post("/posts/{post_id}/comments")
async def add_comment(
    post_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if not comment_data.content.strip():
        raise HTTPException(status_code=400, detail="Comment content cannot be empty")

    comment = PostComment(
        post_id=post_id,
        user_id=current_user.id,
        content=comment_data.content.strip()
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {"message": "Comment added successfully", "comment_id": comment.id}


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a post (only own posts)."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    db.delete(post)
    db.commit()

    return {"message": "Post deleted successfully"}



class UserSearchResponse(BaseModel):
    id: int
    username: str
    avatar: str
    level: int
    is_friend: bool
    has_pending_request: bool

    class Config:
        from_attributes = True


@router.get("/users/search", response_model=List[UserSearchResponse])
async def search_users(
    query: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if not query or len(query) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")

    # Search users
    users = db.query(User).filter(
        and_(
            User.username.ilike(f"%{query}%"),
            User.id != current_user.id  # Exclude self
        )
    ).limit(limit).all()

    # Get friend IDs
    friend_ids = db.query(Friendship.friend_id).filter(
        and_(Friendship.user_id == current_user.id, Friendship.status == "accepted")
    ).union(
        db.query(Friendship.user_id).filter(
            and_(Friendship.friend_id == current_user.id, Friendship.status == "accepted")
        )
    ).all()
    friend_ids = [f[0] for f in friend_ids]

    # Get pending request IDs
    pending_ids = db.query(Friendship.friend_id).filter(
        and_(Friendship.user_id == current_user.id, Friendship.status == "pending")
    ).all()
    pending_ids = [f[0] for f in pending_ids]

    result = []
    for user in users:
        result.append(UserSearchResponse(
            id=user.id,
            username=user.username,
            avatar=user.username[:2].upper(),
            level=user.level,
            is_friend=user.id in friend_ids,
            has_pending_request=user.id in pending_ids
        ))

    return result
