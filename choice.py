import os
import csv
import sqlite3
import random
import kanji
from utils import is_kanji
from colorama import init, Fore, Back, Style

DB_NAME = "kanji_learning.db"

def add_confusing_choice(kanji_id, candidate_character):
    candidate_kanji_id = kanji.get_kanji_id(candidate_character)
    if candidate_kanji_id is None:
        candidate_kanji_id = kanji.add_kanji(candidate_character)
    
    # 重複チェック（confusing_choices）
    if exist_confusing_choice(kanji_id, candidate_kanji_id):
        print(Fore.YELLOW + "⚠️ 既にその混同候補は登録されています")
        return

    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    # 追加（confusing_choices）
    cur.execute("INSERT INTO confusing_choices (kanji_id, candidate_kanji_id) VALUES (?, ?)", (kanji_id, candidate_kanji_id))
    conn.commit()
    conn.close()
    print(Fore.LIGHTGREEN_EX + f"✅ 混同候補 「{kanji.get_character(kanji_id)}」→「{candidate_character}」 を登録しました")

def delete_confusing_choice(confusing_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("DELETE FROM confusing_choices WHERE id=?", (confusing_id,))
    conn.commit()
    conn.close()

def list_confusing_choices():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("""
        SELECT confusing_choices.id, k1.character, k2.character
        FROM confusing_choices
        JOIN kanji k1 ON confusing_choices.kanji_id = k1.id
        JOIN kanji k2 ON confusing_choices.candidate_kanji_id = k2.id
        ORDER BY confusing_choices.id
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_confusing_choice(confusing_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("SELECT kanji_id, candidate_kanji_id FROM confusing_choices WHERE id = ?", (confusing_id,))
    row = cur.fetchone()
    conn.close()
    return row

def get_confusing_choices(kanji_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("""
        SELECT confusing_choices.id, k.character
        FROM confusing_choices
        JOIN kanji k ON confusing_choices.candidate_kanji_id = k.id
        WHERE confusing_choices.kanji_id = ?
        ORDER BY confusing_choices.id
    """, (kanji_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def exist_confusing_choice(kanji_id, candidate_kanji_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("SELECT EXISTS (SELECT 1 FROM confusing_choices WHERE kanji_id = ? AND candidate_kanji_id = ?)", (kanji_id, candidate_kanji_id))
    is_exist = (cur.fetchone()[0] == 1)
    conn.close()
    return is_exist

def import_confusing_choices_from_csv(csv_path, reverse=False):
    if not os.path.exists(csv_path):
        print(Fore.LIGHTRED_EX + "❌ ファイルが存在しません")
        return

    count = 0
    skipped = 0

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader) # ヘッダーをスキップ
        for lineno, row in enumerate(reader, start=2):
            if len(row) < 2:
                print(Fore.YELLOW + f"⚠️ {lineno}行目: データ不正（混同候補が1つも存在しません）")
                skipped += 1
                continue

            correct = row[0].strip()

            if not correct or len(correct) != 1 or not is_kanji(correct):
                print(Fore.YELLOW + f"⚠️ {lineno}行目: 正解は1文字の漢字でなければなりません")
                skipped += 1
                continue

            kanji_id = kanji.get_kanji_id(correct)
            if not kanji_id: # その漢字が存在しない場合は kanji テーブルに新規登録
                kanji_id = kanji.add_kanji(correct)

            for candidate in row[1:]: # 可変長の混同候補を 1 個以上追加
                candidate = candidate.strip()
                if not candidate or len(candidate) != 1 or not is_kanji(candidate):
                    print(Fore.YELLOW + f"⚠️ {lineno}行目: 無効な混同候補「{candidate}」")
                    skipped += 1
                    continue

                candidate_id = kanji.get_kanji_id(candidate)
                if not candidate_id: # その混同候補が kanji テーブルに存在しない場合は新規登録
                    candidate_id = kanji.add_kanji(candidate)

                # confusing_choices に追加
                if not exist_confusing_choice(kanji_id, candidate_id):
                    add_confusing_choice(kanji_id, candidate)
                    count += 1
                else:
                    print(Fore.YELLOW + f"⚠️ {lineno}行目: 「{correct}」→「{candidate}」は既に存在します")
                    skipped += 1

                if reverse:
                    if not exist_confusing_choice(candidate_id, kanji_id):
                        add_confusing_choice(candidate_id, correct)
                        count += 1
                    else:
                        print(Fore.YELLOW + f"⚠️ {lineno}行目: 逆方向「{candidate}」→「{correct}」は既に存在します")
                        skipped += 1

    print(Fore.LIGHTGREEN_EX + f"✅ インポート完了: {count}件追加、{skipped}件スキップ")

def generate_choices(user_id, correct_kanji_id, num_choices=4):
    if num_choices < 2:
        print(Fore.YELLOW + "⚠️ 選択肢の個数は 2 以上である必要があります")
        return
    
    choices = []
    # 正解の漢字を追加
    choices.append(correct_kanji_id)

    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # その漢字を対象とした問題の直近の不正解時に間違えて選んだ漢字を取得
    cur.execute("""
        SELECT selected_kanji_id
        FROM history h
        JOIN problems p ON h.problem_id = p.id
        WHERE h.user_id = ? AND p.kanji_id = ? AND h.is_correct = 0 AND selected_kanji_id IS NOT NULL
        ORDER BY h.id DESC
        LIMIT 1
    """, (user_id, correct_kanji_id))
    row = cur.fetchone()
    if row:
        choices.append(row[0])

    # 正解漢字に対する混同候補を取得
    cur.execute("SELECT candidate_kanji_id FROM confusing_choices WHERE kanji_id = ?", (correct_kanji_id,))
    confusing_ids = [row[0] for row in cur.fetchall()]
    random.shuffle(confusing_ids)
    for kid in confusing_ids:
        if len(choices) >= num_choices:
            break
        if kid not in choices:
            choices.append(kid)

    # 補充候補を追加（kanji テーブルからランダムに）
    cur.execute("SELECT id FROM kanji WHERE id != ?", (correct_kanji_id,))
    all_kanji_ids = [row[0] for row in cur.fetchall()]
    random.shuffle(all_kanji_ids)
    for kid in all_kanji_ids:
        if len(choices) >= num_choices:
            break
        if kid not in choices:
            choices.append(kid)

    conn.close()

    # 選択肢をシャッフル
    random.shuffle(choices)
    return choices