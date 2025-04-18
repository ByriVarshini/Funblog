from psycopg2 import connect

# Connection string
DATABASE_URL = "postgresql://postgres:funblog@db.hbmjmbgbuxhygzrdkeuj.supabase.co:5432/postgres"

# SQL commands to create tables
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(20) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""

CREATE_POSTS_TABLE = """
CREATE TABLE IF NOT EXISTS posts (
    post_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    username VARCHAR(20) REFERENCES users(username) ON DELETE CASCADE
);
"""

CREATE_POST_COMMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS post_comments (
    comment_id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(post_id) ON DELETE CASCADE,
    username VARCHAR(20) REFERENCES users(username) ON DELETE CASCADE,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_POST_LIKES_TABLE = """
CREATE TABLE IF NOT EXISTS post_likes (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(post_id) ON DELETE CASCADE,
    username VARCHAR(20) REFERENCES users(username) ON DELETE CASCADE,
    like_status BOOLEAN DEFAULT FALSE
);
"""

def create_tables():
    try:
        # Connect to the database
        conn = connect(DATABASE_URL)
        cursor = conn.cursor()

        # Execute table creation commands
        cursor.execute(CREATE_USERS_TABLE)
        cursor.execute(CREATE_POSTS_TABLE)
        cursor.execute(CREATE_POST_COMMENTS_TABLE)
        cursor.execute(CREATE_POST_LIKES_TABLE)

        # Commit changes
        conn.commit()
        print("Tables created successfully!")

    except Exception as e:
        print("Error creating tables:", e)

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_tables()