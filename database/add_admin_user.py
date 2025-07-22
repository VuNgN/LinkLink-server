import getpass
import os
import sys

import bcrypt
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
if DB_URL and DB_URL.startswith("postgresql+asyncpg://"):
    DB_URL = DB_URL.replace("postgresql+asyncpg://", "postgresql://", 1)
if not DB_URL:
    print("DATABASE_URL not set in environment.")
    sys.exit(1)


def get_conn():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)


def create_admin():
    username = input("Enter admin username: ").strip()
    email = input("Enter admin email: ").strip()
    password = getpass.getpass("Enter admin password: ").strip()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (username, email, hashed_password, is_active, is_admin, status, created_at, updated_at)
                VALUES (%s, %s, %s, TRUE, TRUE, 'approved', NOW(), NOW())
                ON CONFLICT (username) DO NOTHING
            """,
                (username, email, hashed),
            )
            conn.commit()
    print(f"Admin user '{username}' created (or already exists).")


def list_admins():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT username, email, is_active, status, created_at FROM users WHERE is_admin = TRUE"
            )
            admins = cur.fetchall()
            if not admins:
                print("No admin users found.")
                return
            print("Admin users:")
            for a in admins:
                print(
                    f"- {a['username']} | {a['email']} | active: {a['is_active']} | status: {a['status']} | created: {a['created_at']}"
                )


def remove_admin():
    username = input("Enter admin username to remove: ").strip()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM users WHERE username = %s AND is_admin = TRUE", (username,)
            )
            if cur.rowcount:
                print(f"Admin user '{username}' removed.")
            else:
                print(f"No such admin user '{username}'.")
            conn.commit()


def main():
    if len(sys.argv) < 2:
        print("Usage: add_admin_user.py [create|list|remove]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "create":
        create_admin()
    elif cmd == "list":
        list_admins()
    elif cmd == "remove":
        remove_admin()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
