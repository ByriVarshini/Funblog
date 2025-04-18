from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.database import get_db
from app.auth import get_current_user  # Import authentication function
from typing import Any, Dict
import logging  # Add logging

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

class Post(BaseModel):
    title: str
    content: str
    published: bool = True  # Default value

@router.get("/")
def my_feed(db: Any = Depends(get_db), user: Dict = Depends(get_current_user), limit: int = 15, offset: int = 0):
    user_email = user.get("sub")
    if not user_email:
        raise HTTPException(status_code=400, detail="Email not found in token")
    
    # Fetch username of the logged-in user
    db.execute("SELECT username FROM users WHERE email = %s", (user_email,))
    user_record = db.fetchone()
    if not user_record:
        raise HTTPException(status_code=400, detail="User not found")

    username = user_record["username"]

    # Fetch posts along with like, dislike, user's like status, and comment count
    db.execute("""
        SELECT p.post_id, p.title, p.content, p.username, p.created_at, 
               COUNT(CASE WHEN l.like_status = TRUE THEN 1 END) AS likes,
               COUNT(CASE WHEN l.like_status = FALSE THEN 1 END) AS dislikes,
               MAX(CASE WHEN l.username = %s AND l.like_status = TRUE THEN 1 ELSE 0 END) AS user_liked,
               (SELECT COUNT(*) FROM post_comments WHERE post_id = p.post_id) AS comment_count
        FROM posts p
        LEFT JOIN post_likes l ON p.post_id = l.post_id
        WHERE p.username != %s
        GROUP BY p.post_id
        ORDER BY p.created_at DESC  LIMIT %s OFFSET %s
    """, (username, username, limit, offset))
    posts = db.fetchall()
    
    # Add logging to debug post counts
    logging.info(f"Fetched posts: {posts}")

    for post in posts:
        post["like_count"] = post.pop("likes", 0)  # Rename key properly
        post["dislike_count"] = post.pop("dislikes", 0)
        post["user_liked"] = bool(post.pop("user_liked", 0))  # Convert to boolean
        post["comment_count"] = post.pop("comment_count", 0)
    return {"data": posts}

@router.get("/myposts")
def get_my_posts(db: Any = Depends(get_db), user: Dict = Depends(get_current_user)):
    user_email = user.get("sub")  # Extract user email from token
    # Fetch username of the logged-in user
    db.execute("SELECT username FROM users WHERE email = %s", (user_email,))
    user_record = db.fetchone()
    if not user_record:
        raise HTTPException(status_code=400, detail="User not found")

    username = user_record["username"]

    # Fetch posts of the logged-in user
    db.execute("SELECT * FROM posts WHERE username = %s", (username,))
    my_posts = db.fetchall()

    if not my_posts:
        raise HTTPException(status_code=404, detail="No posts found for this user")

    return {"my_posts": my_posts}


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Any = Depends(get_db), user: dict = Depends(get_current_user)):
    user_email = user.get("sub")  # Extract user email from token
    # Fetch username from the database
    db.execute("SELECT username FROM users WHERE email = %s", (user_email,))
    user_record = db.fetchone()
    if not user_record:
        raise HTTPException(status_code=400, detail="User not found")
    username = user_record["username"]  # Use correct column name
    # Insert the post with the username
    db.execute(
        """
        INSERT INTO posts (title, content, published, username) 
        VALUES (%s, %s, %s, %s) RETURNING *
        """,
        (post.title, post.content, post.published, username)
    )
    new_post = db.fetchone()
    db.connection.commit()
    return {"data": new_post}

@router.get("/{id}")
def get_post(id: int, db: Any = Depends(get_db), user: Dict = Depends(get_current_user)):
    user_email = user.get("sub")
    db.execute("SELECT username FROM users WHERE email = %s", (user_email,))
    user_record = db.fetchone()

    if not user_record:
        raise HTTPException(status_code=400, detail="User not found")

    username = user_record["username"]
    
    # Debugging: Print details before querying the database
    #print(f"User: {username}, Post ID: {id}")

    db.execute("SELECT * FROM posts WHERE post_id = %s", (id,))
    post = db.fetchone()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    print(f"Fetched Post: {post}")  # Debug output

    return post

@router.get("/latest")
def getmy_latest_post(db: Any = Depends(get_db), user: Dict = Depends(get_current_user)):
    user_email = user.get("sub")  # Extract user email from token
    # Fetch username of the logged-in user
    db.execute("SELECT username FROM users WHERE email = %s", (user_email,))
    user_record = db.fetchone()
    if not user_record:
        raise HTTPException(status_code=400, detail="User not found")
    username = user_record["username"]
    # Fetch latest post of the logged-in user
    db.execute("SELECT * FROM posts WHERE username = %s ORDER BY post_id DESC LIMIT 1", (username,))
    latest_post = db.fetchone()
    if not latest_post:
        raise HTTPException(status_code=404, detail="No posts found for this user")
    return {"latest_post": latest_post}

@router.get("/{username}")
def get_posts_by_username(username: str, db: Any = Depends(get_db), user: Dict = Depends(get_current_user)):
    # Fetch posts of the given username
    db.execute("SELECT * FROM posts WHERE username = %s", (username,))
    posts = db.fetchall()
    
    if not posts:
        raise HTTPException(status_code=404, detail="No posts found for this user")
    
    return {"data": posts}


@router.delete("/{id}", status_code=200)
def delete_post(id: int, db: Any = Depends(get_db), user: Dict = Depends(get_current_user)):
    user_email = user.get("sub")
    db.execute("SELECT username FROM users WHERE email = %s", (user_email,))
    user_record = db.fetchone()
    if not user_record:
        raise HTTPException(status_code=400, detail="User not found")
    username = user_record["username"]
    # Check if the post belongs to the logged-in user before deleting
    db.execute("DELETE FROM posts WHERE post_id = %s AND username = %s RETURNING *", (id, username))
    deleted_post = db.fetchone()
    if not deleted_post:
        raise HTTPException(status_code=404, detail="Post not found or unauthorized access")
    db.connection.commit()
    return {"message": "Post deleted successfully"}


class PostUpdate(BaseModel):
    title: str
    content: str
    published: bool

@router.put("/{id}")  # Change {username} to {id}
def update_post(
    id: int,  # Accept post ID directly
    post: PostUpdate,  # Ensure request body is validated
    db: Any = Depends(get_db),
    user: Dict = Depends(get_current_user)
):
    user_email = user.get("sub")

    # Fetch the username of the logged-in user
    db.execute("SELECT username FROM users WHERE email = %s", (user_email,))
    user_record = db.fetchone()
    if not user_record:
        raise HTTPException(status_code=400, detail="User not found")

    username = user_record["username"]

    # Check if the post exists and belongs to the logged-in user
    db.execute("SELECT * FROM posts WHERE post_id = %s AND username = %s", (id, username))
    existing_post = db.fetchone()
    if not existing_post:
        raise HTTPException(status_code=404, detail="Post not found or unauthorized access")

    # Update the post
    db.execute(
        """
        UPDATE posts 
        SET title = %s, content = %s, published = %s 
        WHERE post_id = %s AND username = %s 
        RETURNING *
        """,
        (post.title, post.content, post.published, id, username)
    )
    updated_post = db.fetchone()
    db.connection.commit()

    return {"message": "Post updated successfully", "data": updated_post}


    
class Comment(BaseModel):
    post_id: int
    comment: str

@router.post("/comment", status_code=status.HTTP_201_CREATED)
def add_comment(comment: Comment, db: Any = Depends(get_db), user: Dict = Depends(get_current_user)):
    """
    Add a comment to a post.
    """
    user_email = user.get("sub")
    db.execute("SELECT username FROM users WHERE email = %s", (user_email,))
    user_record = db.fetchone()
    if not user_record:
        raise HTTPException(status_code=400, detail="User not found")
    username = user_record["username"]

    # Insert the comment into the new post_comments table
    db.execute(
        """
        INSERT INTO post_comments (post_id, username, comment) 
        VALUES (%s, %s, %s) RETURNING *
        """,
        (comment.post_id, username, comment.comment)
    )
    new_comment = db.fetchone()
    db.connection.commit()

    if not new_comment:
        raise HTTPException(status_code=500, detail="Failed to add comment")

    return {"data": new_comment}

@router.get("/comments/{post_id}")
def get_comments(post_id: int, db: Any = Depends(get_db)):
    """
    Retrieve all comments for a specific post.
    """
    db.execute(
        """
        SELECT username, comment, created_at 
        FROM post_comments 
        WHERE post_id = %s 
        ORDER BY created_at DESC
        """,
        (post_id,)
    )
    comments = db.fetchall()

    if not comments:
        return {"data": []}  # Return an empty list if no comments are found

    return {"data": comments}

@router.post("/{post_id}/like")
def toggle_like(post_id: int, db: Any = Depends(get_db), user: Dict = Depends(get_current_user)):
    user_email = user.get("sub")
    db.execute("SELECT username FROM users WHERE email = %s", (user_email,))
    user_record = db.fetchone()
    if not user_record:
        raise HTTPException(status_code=400, detail="User not found")
    username = user_record["username"]

    # Check if the user has already liked the post
    db.execute("SELECT * FROM post_likes WHERE post_id = %s AND username = %s", (post_id, username))
    like_record = db.fetchone()

    if like_record:
        # If the user has already liked, remove the like
        db.execute("DELETE FROM post_likes WHERE post_id = %s AND username = %s", (post_id, username))
    else:
        # Otherwise, add a like
        db.execute("INSERT INTO post_likes (post_id, username, like_status) VALUES (%s, %s, TRUE)", (post_id, username))

    # Commit the changes
    db.connection.commit()

    # Fetch the updated like count
    db.execute("""
        SELECT COUNT(*) AS likes
        FROM post_likes
        WHERE post_id = %s AND like_status = TRUE
    """, (post_id,))
    like_count = db.fetchone()["likes"]

    return {"likes": like_count}

@router.get("/{post_id}/like_count")
def get_like_count(post_id: int, db: Any = Depends(get_db)):
    """
    Retrieve the total likes count for a specific post.
    """
    try:
        db.execute("""
            SELECT COUNT(*) AS likes
            FROM post_likes
            WHERE post_id = %s AND like_status = TRUE
        """, (post_id,))
        like_count = db.fetchone()
        if not like_count:
            return {"like_count": 0}  # Return 0 if no likes are found
        return {"like_count": like_count["likes"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

@router.get("/{post_id}/likes")
def get_likes(post_id: int, db: Any = Depends(get_db)):
    """Fetch users who liked a given post."""
    db.execute(
        "SELECT username FROM post_likes WHERE post_id = %s AND like_status = TRUE", (post_id,)
    )
    liked_users = [row["username"] for row in db.fetchall()]
    
    return {"liked_users": liked_users}