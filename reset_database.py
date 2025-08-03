import sqlite3
from colorama import init, Fore, Back, Style

DB_NAME = "kanji_learning.db"

def reset_tables():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    print(Fore.LIGHTYELLOW_EX + "⚠️ 既存テーブルを削除中...")
    cur.executescript("""
        DROP TABLE IF EXISTS achieved_trophies;
        DROP TABLE IF EXISTS trophies;
        DROP TABLE IF EXISTS history;
        DROP TABLE IF EXISTS problems;
        DROP TABLE IF EXISTS confusing_choices;
        DROP TABLE IF EXISTS kanji_status;
        DROP TABLE IF EXISTS kanji;
        DROP TABLE IF EXISTS users;
    """)

    print("🗑️ テーブル削除完了。新しい構成で再作成します...")

    # ユーザーテーブル
    cur.execute("""
        CREATE TABLE users (
            user_id TEXT PRIMARY KEY,
            password_hash BLOB NOT NULL,
            created_at TEXT NOT NULL,
            total_score INTEGER NOT NULL DEFAULT 0
        );
    """)

    # 漢字テーブル
    cur.execute("""
        CREATE TABLE kanji (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character TEXT NOT NULL UNIQUE
        );
    """)

    # 漢字状態テーブル
    cur.execute("""
        CREATE TABLE kanji_status (
            user_id TEXT NOT NULL,
            kanji_id INTEGER NOT NULL,
            is_cleared INTEGER NOT NULL CHECK (is_cleared IN (0,1)) DEFAULT 0,
            PRIMARY KEY (user_id, kanji_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (kanji_id) REFERENCES kanji(id) ON DELETE CASCADE
        );
    """)

    # 問題テーブル
    cur.execute("""
        CREATE TABLE problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kanji_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            FOREIGN KEY (kanji_id) REFERENCES kanji(id) ON DELETE RESTRICT
        );
    """)

    # 混同候補テーブル
    cur.execute("""
        CREATE TABLE confusing_choices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kanji_id INTEGER NOT NULL,
            candidate_kanji_id INTEGER NOT NULL,
            FOREIGN KEY (kanji_id) REFERENCES kanji(id) ON DELETE RESTRICT,
            FOREIGN KEY (candidate_kanji_id) REFERENCES kanji(id) ON DELETE RESTRICT,
            UNIQUE (kanji_id, candidate_kanji_id)
        );
    """)

    # 回答履歴テーブル
    cur.execute("""
        CREATE TABLE history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            problem_id INTEGER NOT NULL,
            is_correct INTEGER NOT NULL CHECK (is_correct IN (0,1)),
            selected_kanji_id INTEGER,
            answered_at TEXT NOT NULL,
            score INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE,
            FOREIGN KEY (selected_kanji_id) REFERENCES kanji(id) ON DELETE CASCADE
        );
    """)

    # トロフィーテーブル
    cur.execute("""
        CREATE TABLE trophies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requirement_type TEXT NOT NULL,
            requirement_value INTEGER,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            score INTEGER NOT NULL DEFAULT 0,
            is_visible INTEGER NOT NULL CHECK (is_visible IN (0,1)),
            UNIQUE (requirement_type, requirement_value)
        );
    """)

    # 獲得トロフィーテーブル
    cur.execute("""
        CREATE TABLE achieved_trophies (
            user_id TEXT NOT NULL,
            trophy_id INTEGER NOT NULL,
            achieved_at TEXT NOT NULL,
            PRIMARY KEY (user_id, trophy_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (trophy_id) REFERENCES trophies(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()
    print(Fore.LIGHTGREEN_EX + "✅ 新しいテーブル構成で再作成完了しました。")

if __name__ == "__main__":
    reset_tables()