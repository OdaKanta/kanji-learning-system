import os
import csv
import random
import sqlite3
import kanji
import history
from utils import is_kanji, render_progress_bar
from kanji import REQUIRED_STREAK_COUNT_FOR_CLEAR
from colorama import init, Fore, Back, Style

DB_NAME = "kanji_learning.db"

def add_problem(kanji_id, question):
    # すでに存在する場合は登録しない
    if exist_problem(kanji_id, question):
        print(Fore.YELLOW + f"⚠️ 同一問題が既に存在します")
        return
    
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO problems (kanji_id, question) VALUES (?, ?)",
        (kanji_id, question)
    )
    conn.commit()
    conn.close()

def edit_problem(problem_id, new_kanji_id, new_question):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute(
        "UPDATE problems SET kanji_id=?, question=? WHERE id=?",
        (new_kanji_id, new_question, problem_id)
    )
    conn.commit()
    conn.close()

def delete_problem(problem_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    #cur.execute("DELETE FROM history WHERE problem_id=?", (problem_id,)) history.problem_id は ON DELETE CASCADE 指定済
    cur.execute("DELETE FROM problems WHERE id=?", (problem_id,))
    conn.commit()
    conn.close()

def get_problem(problem_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("""
        SELECT problems.id, problems.question, kanji.character
        FROM problems
        JOIN kanji ON problems.kanji_id = kanji.id
        WHERE problems.id = ?
    """, (problem_id,))
    row = cur.fetchone()
    conn.close()
    return row

def list_problems():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("""
        SELECT problems.id, problems.question, kanji.character
        FROM problems
        JOIN kanji ON problems.kanji_id = kanji.id
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_priority_problems(user_id, top_n=10):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # 対象ユーザーにおいてクリアしていない漢字IDをリストとして取得（ただし、problems テーブルにその漢字を正答とする問題が存在するものに限る）
    cur.execute("""
        SELECT k.id
        FROM kanji k
        LEFT JOIN kanji_status ks ON k.id = ks.kanji_id AND ks.user_id = ?
        WHERE COALESCE(ks.is_cleared, 0) = 0 AND EXISTS (SELECT 1 FROM problems p WHERE p.kanji_id = k.id)
    """, (user_id,))
    candidate_kanji_ids = [row[0] for row in cur.fetchall()]
    if not candidate_kanji_ids:
        conn.close()
        return []

    # 各漢字の直近の出題から現在に至るまでの経過出題数をカウント（何問前に出題されたか）
    problems_ago = {}
    MAX_PRIORITY = 9999 # 未出題の漢字は「限りなく遠い過去に出題された」とみなして優先度最大にする
    for kid in candidate_kanji_ids:
        problems_ago[kid] = history.problems_ago(user_id, kid) or MAX_PRIORITY

    # 各漢字の直近の連続正解回数を算出（未出題、未正解は0）
    consecutive_count = {}
    for kid in candidate_kanji_ids:
        consecutive_count[kid] = history.consec_count(user_id, kid)

    # 連続正解回数に応じた出題間隔の目安を辞書型で定義
    intervals = {i: top_n * i**2 for i in range(REQUIRED_STREAK_COUNT_FOR_CLEAR + 1)}

    # 各漢字の出題優先度（＝直近の出題以降の経過出題数ー目安となる出題間隔）の計算
    priority = {}
    for kid in candidate_kanji_ids:
        stage = min(consecutive_count[kid], REQUIRED_STREAK_COUNT_FOR_CLEAR)
        priority[kid] = problems_ago[kid] - intervals[stage]

    # 優先度で降順ソートして優先度の高い方から top_n 個の漢字IDを抽出
    sorted_kids = [kid for kid, _ in sorted(priority.items(), key=lambda x: x[1], reverse=True)]
    selected_kanji_ids = sorted_kids[:top_n]

    # 各漢字に対してランダムに1問選出
    problems = []
    for kid in selected_kanji_ids:
        cur.execute("SELECT id, question FROM problems WHERE kanji_id = ?", (kid,))
        rows = cur.fetchall()
        if rows:
            pid, question = random.choice(rows)
            problems.append((pid, kid, question))

    conn.close()
    return problems

def count_all_problems():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM problems")
    count = cur.fetchone()[0]
    conn.close()
    return count

def exist_problem(kanji_id, question):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("SELECT EXISTS (SELECT 1 FROM problems WHERE kanji_id=? AND question=?)", (kanji_id, question))
    is_exist = (cur.fetchone()[0] == 1)
    conn.close()
    return is_exist

def import_problems_from_csv(csv_path):
    if not os.path.exists(csv_path):
        print(Fore.LIGHTRED_EX + "❌ ファイルが存在しません")
        return

    count = 0
    skipped = 0

    with open(csv_path, encoding="utf-8") as f:
        reader = list(csv.reader(f))
        total = len(reader) - 1  # ヘッダーを除いた行数
        if total <= 0:
            print(Fore.YELLOW + "⚠️ インポート対象がありません")
            return

        headers = reader[0]  # 1行目をスキップ
        data_rows = reader[1:]

        for idx, row in enumerate(data_rows, start=2):
            if len(row) < 2:
                print(Fore.YELLOW + f"\n⚠️ {idx}行目: カラム数不足")
                skipped += 1
            else:
                answer = row[0].strip()
                question = row[1].strip()

                if not question or not answer:
                    print(Fore.YELLOW + f"\n⚠️ {idx}行目: 空欄があります")
                    skipped += 1
                elif len(answer) != 1 or not is_kanji(answer):
                    print(Fore.YELLOW + f"\n⚠️ {idx}行目: 正解は1文字の漢字である必要があります")
                    skipped += 1
                else:
                    kanji_id = kanji.get_kanji_id(answer)
                    if not kanji_id:
                        kanji_id = kanji.add_kanji(answer)

                    if exist_problem(kanji_id, question):
                        print(Fore.YELLOW + f"\n⚠️ {idx}行目: 同一問題が既に存在します")
                        skipped += 1
                    else:
                        add_problem(kanji_id, question)
                        count += 1

            # 進捗バーの表示（成功・失敗問わず1行処理ごとに更新）
            current = count + skipped
            rate = current / total
            bar = render_progress_bar(rate)
            print(f"\r📦 {bar} {current} / {total} 件", end="", flush=True)

    print(Fore.LIGHTGREEN_EX + "\n✅ インポート完了: {}件追加、{}件スキップ".format(count, skipped))