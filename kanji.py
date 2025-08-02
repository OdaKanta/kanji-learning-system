import os
import csv
import sqlite3
import choice
import sound
from utils import is_kanji
from colorama import init, Fore, Back, Style

DB_NAME = "kanji_learning.db"
REQUIRED_STREAK_COUNT_FOR_CLEAR = 3

def list_kanji():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("SELECT id, character FROM kanji ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_character(kanji_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("SELECT character FROM kanji WHERE id = ?", (kanji_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def get_kanji_id(character):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("SELECT id FROM kanji WHERE character = ?", (character,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def add_kanji(character):
    if not character or len(character)!=1 or not is_kanji(character):
        raise ValueError(Fore.YELLOW + "⚠️ 追加する漢字は1文字でなければなりません")
    
    # すでに存在する場合は登録しない
    kanji_id = get_kanji_id(character)
    if kanji_id is not None:
        print(Fore.YELLOW + f"⚠️ 漢字「{character}」は既に存在します")
        return kanji_id

    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("INSERT INTO kanji (character) VALUES (?)", (character,))
    kanji_id = cur.lastrowid
    conn.commit()
    conn.close()
    return kanji_id

def delete_kanji(kanji_id):
    character = get_character(kanji_id)

    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    if exist_kanji(kanji_id):
        try:
            cur.execute("DELETE FROM kanji WHERE id = ?", (kanji_id,))
            print(Fore.LIGHTWHITE_EX  + f"🗑 漢字「{character}」を削除しました")
        except sqlite3.IntegrityError:
            print(Fore.YELLOW + f"⚠️ 漢字「{character}」は他のテーブルから参照されているため削除できません")
    else:
        print(Fore.YELLOW + f"⚠️ 漢字ID {kanji_id} は存在しません")
    conn.commit()
    conn.close()

def exist_kanji(kanji_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("SELECT EXISTS (SELECT 1 FROM kanji WHERE id = ?)", (kanji_id,))
    is_exist = cur.fetchone()[0] == 1
    conn.close()
    return is_exist

def mark_kanji_cleared_if_qualified(user_id, kanji_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # この漢字に関係するすべての問題IDを取得
    cur.execute("SELECT id FROM problems WHERE kanji_id = ?", (kanji_id,))
    problem_ids = [r[0] for r in cur.fetchall()]

    if not problem_ids:
        conn.close()
        return

    # ユーザーが回答した履歴（新しい順）を取得
    cur.execute(f"""
        SELECT is_correct FROM history
        WHERE user_id = ? AND problem_id IN ({','.join(['?'] * len(problem_ids))})
        ORDER BY id DESC
    """, [user_id] + problem_ids)
    recent = cur.fetchall()

    # 直近 REQUIRED_STREAK_COUNT_FOR_CLEAR 回連続で正解しているか判定
    if len(recent) >= REQUIRED_STREAK_COUNT_FOR_CLEAR and all(r[0] == 1 for r in recent[:REQUIRED_STREAK_COUNT_FOR_CLEAR]):
        cur.execute("UPDATE kanji_status SET is_cleared = 1 WHERE user_id = ? AND kanji_id = ?", (user_id, kanji_id))
        conn.commit()
        character = get_character(kanji_id)
        print(Fore.LIGHTRED_EX + Back.LIGHTYELLOW_EX + f"🎉 漢字「{character}」をクリアしました！")
        sound.play_sound("audio/clear.mp3")

    conn.close()

def import_kanji_from_csv(csv_path):
    if not os.path.exists(csv_path):
        print(Fore.LIGHTRED_EX + "❌ ファイルが存在しません")
        return

    count = 0
    skipped = 0

    with open(csv_path, encoding="utf-8") as f:
        reader = list(csv.reader(f))
        total = len(reader) - 1  # ヘッダー除く行数
        if total <= 0:
            print(Fore.YELLOW + "⚠️ インポート対象がありません")
            return

        headers = reader[0]
        data_rows = reader[1:]

        for idx, row in enumerate(data_rows, start=2):
            if len(row) < 1:
                print(Fore.YELLOW + f"\n⚠️ {idx}行目: データ不正（漢字が空）")
                skipped += 1
            else:
                character = row[0].strip()

                if not character or len(character) != 1 or not is_kanji(character):
                    print(Fore.YELLOW + f"\n⚠️ {idx}行目: 無効な漢字「{character}」")
                    skipped += 1
                elif get_kanji_id(character) is not None:
                    print(Fore.YELLOW + f"\n⚠️ {idx}行目: 漢字「{character}」は既に存在します")
                    skipped += 1
                else:
                    kanji_id = add_kanji(character)
                    count += 1

                    for candidate in row[1:]:  # 混同候補の処理
                        candidate = candidate.strip()
                        if not candidate or len(candidate) != 1 or not is_kanji(candidate):
                            print(Fore.YELLOW + f"\n⚠️ {idx}行目: 無効な混同候補「{candidate}」")
                            skipped += 1
                            continue

                        candidate_kanji_id = kanji.get_kanji_id(candidate)
                        if not candidate_kanji_id:
                            candidate_kanji_id = kanji.add_kanji(candidate)

                        if not choice.exist_confusing_choice(kanji_id, candidate_kanji_id):
                            choice.add_confusing_choice(kanji_id, candidate)
                        else:
                            print(Fore.YELLOW + f"\n⚠️ {idx}行目: 「{character}」→「{candidate}」 は既に存在します")
                            skipped += 1

            # 進捗バー表示
            current = count + skipped
            rate = current / total
            bar = render_progress_bar(rate)
            print(f"\r📦 {bar} {current} / {total} 件", end="", flush=True)

    print(Fore.LIGHTGREEN_EX + f"\n✅ インポート完了: {count}件追加、{skipped}件スキップ")

def list_cleared_kanji(user_id):
    # そのユーザーがクリア済の漢字を一覧取得
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("""
        SELECT kanji_id
        FROM kanji_status
        WHERE user_id = ? AND is_cleared = 1
        ORDER BY kanji_id
    """, (user_id,))
    kanji_ids = [row[0] for row in cur.fetchall()]
    conn.close()
    return kanji_ids

def list_uncleared_kanji(user_id):
    # そのユーザーが未クリアの漢字（未出題含む）を一覧取得
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("""
        SELECT k.id
        FROM kanji k
        LEFT JOIN kanji_status ks ON k.id = ks.kanji_id AND ks.user_id = ?
        WHERE COALESCE(ks.is_cleared, 0) = 0
    """, (user_id,))
    kanji_ids = [row[0] for row in cur.fetchall()]
    conn.close()
    return kanji_ids

def count_cleared_kanji(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM kanji_status WHERE user_id = ? AND is_cleared = 1", (user_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count

def get_clear_rate(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # 総漢字数
    cur.execute("SELECT COUNT(*) FROM kanji")
    total = cur.fetchone()[0]

    if total == 0:
        conn.close()
        return None

    # クリア済の漢字数
    cleared = count_cleared_kanji(user_id)

    conn.close()
    return cleared / total