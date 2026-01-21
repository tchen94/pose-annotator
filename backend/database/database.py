import os
import psycopg2
import secrets
from psycopg2.extras import RealDictCursor, Json
from contextlib import contextmanager

# Render's DATABASE_URL environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

@contextmanager
def get_db_connection():
    """Context manager for database connection."""
    if not DATABASE_URL:
        raise Exception("DATABASE_URL environment variable is not set.")
    
    conn = psycopg2.connect(DATABASE_URL)

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initialize the database with required tables."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Create the sessions table for Annotation
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS annotation_sessions (
                           id SERIAL PRIMARY KEY,
                           frame_set_id TEXT NOT NULL UNIQUE,
                           video_id TEXT NOT NULL,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           orig_width INTEGER,
                           orig_height INTEGER,
                           render_width INTEGER,
                           render_height INTEGER,
                           total_frames INTEGER DEFAULT 0,
                           annotated_frames INTEGER DEFAULT 0,
                           last_frame_annotated INTEGER DEFAULT 0,
                           status TEXT DEFAULT 'in_progress'
                        )
            """)

            # Create frame annotations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS frame_annotations (
                           id SERIAL PRIMARY KEY,
                           frame_set_id TEXT NOT NULL,
                           frame_num INTEGER NOT NULL,
                           annotations JSONB NOT NULL,
                           is_completed BOOLEAN DEFAULT FALSE,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           UNIQUE(frame_set_id, frame_num),
                           FOREIGN KEY (frame_set_id)
                                REFERENCES annotation_sessions(frame_set_id)
                                ON DELETE CASCADE
                )
            """)

            # Create the user-token table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_tokens (
                    id SERIAL PRIMARY KEY,
                    token TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)

            # Additional step to add user_token column to annotation_sessions if not exists
            cursor.execute("""
                ALTER TABLE annotation_sessions
                ADD COLUMN IF NOT EXISTS user_token TEXT
            """)

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_frame_set
                ON frame_annotations(frame_set_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_annotations
                ON frame_annotations USING GIN (annotations)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_status
                ON annotation_sessions(status)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_updated
                ON annotation_sessions(updated_at DESC)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_token
                ON annotation_sessions(user_token)
            """)

            conn.commit()
            print("Database initialized successfully.")
            return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False
    
def save_annotation_session(frame_set_id: str, video_id: str, orig_width: int,
                            orig_height: int,render_width: int, render_height: int,
                            total_frames: int, last_frame_annotated: int = 0, user_token: str = None):
    """Create or update annotation session."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO annotation_sessions
                (frame_set_id, video_id, orig_width, orig_height, render_width, 
                       render_height, total_frames, last_frame_annotated, user_token)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (frame_set_id)
            DO UPDATE SET
                updated_at = CURRENT_TIMESTAMP,
                orig_width = EXCLUDED.orig_width,
                orig_height = EXCLUDED.orig_height,
                render_width = EXCLUDED.render_width,
                render_height = EXCLUDED.render_height,
                total_frames = EXCLUDED.total_frames,
                last_frame_annotated = EXCLUDED.last_frame_annotated,
                user_token = EXCLUDED.user_token
            """, (frame_set_id, video_id, orig_width, orig_height, render_width,
                  render_height, total_frames, last_frame_annotated, user_token))
        
def save_frame_annotation(frame_set_id: str, frame_num: int, annotations: dict, is_completed: bool):
    """Save or update a single frame's annotations."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO frame_annotations
                (frame_set_id, frame_num, annotations, is_completed)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (frame_set_id, frame_num)
            DO UPDATE SET
                annotations = EXCLUDED.annotations,
                is_completed = EXCLUDED.is_completed,
                updated_at = CURRENT_TIMESTAMP
        """, (frame_set_id, frame_num, Json(annotations), is_completed))
    
        #update sessions's updated_at timestamp
        cursor.execute("""
            UPDATE annotation_sessions
            SET updated_at = CURRENT_TIMESTAMP
            WHERE frame_set_id = %s
        """, (frame_set_id,))

def update_session_progress(frame_set_id: str):
    """Update the session's progress"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE annotation_sessions
            SET annotated_frames = (
                SELECT COUNT(*) FROM frame_annotations
                WHERE frame_set_id = %s AND is_completed = TRUE
            ),
            status = CASE
                WHEN (
                       SELECT COUNT(*) FROM frame_annotations
                       WHERE frame_set_id = %s AND is_completed = TRUE
                       ) >= total_frames THEN 'completed'
                ELSE 'in_progress'
            END,
            updated_at = CURRENT_TIMESTAMP
            WHERE frame_set_id = %s
    """, (frame_set_id, frame_set_id, frame_set_id))
        
def load_annotation_session(frame_set_id: str):
    """Load all annotations for a frame set."""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Grab session info
        cursor.execute("""
            SELECT * FROM annotation_sessions
            WHERE frame_set_id = %s
        """, (frame_set_id,))
        session = cursor.fetchone()

        if not session:
            return None

        # Grab all frame annotations
        cursor.execute("""
            SELECT frame_num, annotations, is_completed FROM frame_annotations
            WHERE frame_set_id = %s
            ORDER BY frame_num
        """, (frame_set_id,))
        frames = cursor.fetchall()

        return {
            "session": dict(session),
            "frames": [dict(frame) for frame in frames]
        }
    
def list_annotation_sessions(limit: int = 50, user_token: str = None):
    """List all annotation sessions."""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        if user_token:
            cursor.execute("""
                SELECT
                     frame_set_id, video_id, created_at, updated_at,
                     total_frames, annotated_frames, status,
                     ROUND(
                         (annotated_frames::FLOAT / NULLIF(total_frames, 0) * 100)::numeric, 2
                     ) AS progress_percentage
                FROM annotation_sessions
                WHERE user_token = %s
                ORDER BY updated_at DESC
                LIMIT %s
            """, (user_token, limit))
        else:
            cursor.execute("""
                SELECT
                    frame_set_id, video_id, created_at, updated_at,
                    total_frames, annotated_frames, status,
                    ROUND(
                        (annotated_frames::FLOAT / NULLIF(total_frames, 0) * 100)::numeric, 2
                    ) AS progress_percentage
                FROM annotation_sessions
                ORDER BY updated_at DESC
                LIMIT %s
            """, (limit,))

        sessions = cursor.fetchall()
        return [dict(session) for session in sessions]

def delete_annotation_session(frame_set_id: str):
    """Delete an annotation session and all its frame annotations."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM annotation_sessions
            WHERE frame_set_id = %s
        """, (frame_set_id,))
        return cursor.rowcount > 0

# =============== USER TOKEN MANAGEMENT ===============

def create_user_token() -> str:
    """ Creates a unique user token. """
    token = secrets.token_urlsafe(32)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_tokens (token, created_at)
            VALUES (%s, CURRENT_TIMESTAMP)
        """, (token,))

    return token

def validate_user_token(token: str) -> bool:
    """ Validates if the given user token is active. """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT is_active FROM user_tokens
            WHERE token = %s
        """, (token,))

        result = cursor.fetchone()
        return result is not None and result[0]
