import os
import csv
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import user
import kanji
import problem
from utils import get_display_width, left_align_display, right_align_display, center_display, render_progress_bar
from colorama import init, Fore, Back, Style

DB_NAME = "kanji_learning.db"

def record_answer(user_id, problem_id, is_correct, selected_kanji_id, score):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # 解答履歴を記録
    cur.execute("""
        INSERT INTO history (user_id, problem_id, is_correct, selected_kanji_id, answered_at, score)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, problem_id, int(is_correct), selected_kanji_id, datetime.now().isoformat(), score))

    # その問題の正答の kanji_id を取得
    character = problem.get_problem(problem_id)[2]
    kanji_id = kanji.get_kanji_id(character)

    # kanji_status に未登録であれば (user_id, kanji_id, 0) を登録
    cur.execute("SELECT EXISTS (SELECT 1 FROM kanji_status WHERE user_id = ? AND kanji_id=?)", (user_id, kanji_id))
    is_exist = (cur.fetchone()[0] == 1)
    if not is_exist:
        cur.execute("INSERT INTO kanji_status (user_id, kanji_id, is_cleared) VALUES (?, ?, 0)", (user_id, kanji_id))

    conn.commit()
    conn.close()

    # 正解だった場合は、対象漢字のクリア判定（直近で3回連続正解かどうか）を行う
    if is_correct:
        kanji.mark_kanji_cleared_if_qualified(user_id, kanji_id)

def count_total_answers(user_id, day=None):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    if day: # 日付指定がある場合
        start = f"{day}T00:00:00"
        end = f"{day}T23:59:59"
        cur.execute("SELECT COUNT(*) FROM history WHERE user_id = ? AND answered_at BETWEEN ? AND ?", (user_id, start, end))
    else: # 日付指定がない場合は全期間
        cur.execute("SELECT COUNT(*) FROM history WHERE user_id = ?", (user_id,))
    total = cur.fetchone()[0]
    conn.close()
    return total if total else 0

def count_correct_answers(user_id, day=None):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    if day: # 日付指定がある場合
        start = f"{day}T00:00:00"
        end = f"{day}T23:59:59"
        cur.execute("SELECT COUNT(*) FROM history WHERE user_id = ? AND is_correct = 1 AND answered_at BETWEEN ? AND ?", (user_id, start, end))
    else: # 日付指定がない場合は全期間
        cur.execute("SELECT COUNT(*) FROM history WHERE user_id = ? AND is_correct = 1", (user_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count if count else 0

def get_total_score(user_id, day=None):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    
    if day: # 日付指定がある場合
        start = f"{day}T00:00:00"
        end = f"{day}T23:59:59"
        cur.execute("SELECT COALESCE(SUM(score), 0) FROM history WHERE user_id = ? AND answered_at BETWEEN ? AND ?", (user_id, start, end))
        history_score = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(t.score), 0) FROM achieved_trophies a JOIN trophies t ON a.trophy_id = t.id WHERE a.user_id = ? AND a.achieved_at BETWEEN ? AND ?", (user_id, start, end))
        trophy_score = cur.fetchone()[0]
        total = history_score + trophy_score
    else: # 日付指定がない場合は全期間
        cur.execute("SELECT total_score FROM users WHERE user_id = ?", (user_id,))
        total = cur.fetchone()[0]
    conn.close()
    return total if total else 0

def get_correct_rate(user_id, day=None):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    if day: # 日付指定がある場合
        start = f"{day}T00:00:00"
        end = f"{day}T23:59:59"
        cur.execute("SELECT COUNT(*) FROM history WHERE user_id = ? AND answered_at BETWEEN ? AND ?", (user_id, start, end))
        total = cur.fetchone()[0]
        if total == 0:
            conn.close()
            return None
        cur.execute("SELECT COUNT(*) FROM history WHERE user_id = ? AND is_correct = 1 AND answered_at BETWEEN ? AND ?", (user_id, start, end))
        correct = cur.fetchone()[0]
    else: # 日付指定がない場合は全期間
        cur.execute("SELECT COUNT(*) FROM history WHERE user_id = ?", (user_id,))
        total = cur.fetchone()[0]
        if total == 0:
            conn.close()
            return None
        cur.execute("SELECT COUNT(*) FROM history WHERE user_id = ? AND is_correct = 1", (user_id,))
        correct = cur.fetchone()[0]
    conn.close()
    return correct / total

def show_score_summary(user_id):
    today = datetime.now().date().isoformat()

    # 今日
    score_today = get_total_score(user_id, today)
    answers_today = count_total_answers(user_id, today)
    correct_today = count_correct_answers(user_id, today)
    rate_today = (correct_today / answers_today * 100) if answers_today else None

    # 累計
    score_total = get_total_score(user_id)
    answers_total = count_total_answers(user_id)
    correct_total = count_correct_answers(user_id)
    rate_total = (correct_total / answers_total * 100) if answers_total else None

    # 幅調整
    label_w = max(get_display_width("（正答率）"), get_display_width("⭕ 正答数"), get_display_width("📌 回答数"), get_display_width("💎 獲得スコア"))
    col_w = max(
        get_display_width(f"{score_today}"),
        get_display_width(f"{answers_today} 問"),
        get_display_width(f"{correct_today} 問"),
        get_display_width(f"（{rate_today:.1f}%）" if rate_today is not None else "---"),
        get_display_width(f"{score_total}"),
        get_display_width(f"{answers_total} 問"),
        get_display_width(f"{correct_total} 問"),
        get_display_width(f"（{rate_total:.1f}%）" if rate_total is not None else "---")
    )
    gap = 1
    total_width = label_w + col_w * 2 + gap * 3

    print()
    print(Fore.LIGHTWHITE_EX + Back.LIGHTBLACK_EX + " " + "-" * (total_width-1) + " ")
    print(Fore.LIGHTWHITE_EX + Back.LIGHTBLACK_EX + " " + " " * (label_w + gap) + center_display("今日", col_w) + " " * gap + center_display("累計", col_w) + " ")

    def line(label, today_str, total_str):
        return (
            center_display(label, label_w) + " " * gap +
            center_display(today_str, col_w) + " " * gap +
            center_display(total_str, col_w)
        )

    print(Fore.LIGHTCYAN_EX + Back.LIGHTBLACK_EX + " " + line("💎 スコア", f"{score_today}", f"{score_total}") + " ")
    print(Fore.LIGHTYELLOW_EX + Back.LIGHTBLACK_EX + " " + line("📌 回答数", f"{answers_today}", f"{answers_total}") + " ")
    print(Fore.LIGHTRED_EX + Back.LIGHTBLACK_EX + " " + line("⭕ 正答数", f"{correct_today}", f"{correct_total}") + " ")
    print(Fore.LIGHTWHITE_EX + Back.LIGHTBLACK_EX + " " + line("（正答率）", f"{rate_today:.1f}%" if rate_today is not None else "---", f"{rate_total:.1f}%" if rate_total is not None else "---") + " ")
    print(Fore.LIGHTWHITE_EX + Back.LIGHTBLACK_EX + " " + "-" * (total_width-1) + " ")

def consec_count(user_id, kanji_id=None):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    
    if kanji_id: # 漢字指定がある場合
        cur.execute("SELECT h.is_correct FROM history h JOIN problems p ON h.problem_id = p.id WHERE h.user_id = ? AND p.kanji_id = ? ORDER BY h.id DESC", (user_id, kanji_id))
    else: # 漢字指定がない場合は全漢字対象
        cur.execute("SELECT is_correct FROM history WHERE user_id = ? ORDER BY id DESC", (user_id,))
    is_correct_history = [row[0] for row in cur.fetchall()]
    conn.close()

    consec = 0
    for is_correct in is_correct_history:
        if is_correct == 1:
            consec += 1 # 連続正解回数をカウント
        else:
            break
    return consec

def problems_ago(user_id, kanji_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    
    # そのユーザーへの出題履歴を最新のものから順に並べて取得
    cur.execute("SELECT p.kanji_id FROM history h JOIN problems p ON h.problem_id = p.id WHERE h.user_id = ? ORDER BY h.id DESC", (user_id,))
    kid_history = [row[0] for row in cur.fetchall()]
    conn.close()

    if kanji_id not in kid_history:
        return None # 未出題の場合
    else:
        # 各漢字の直近の出題から現在に至るまでの経過出題数をカウント（何問前に出題されたか）
        count_ago = 0
        for kid in kid_history:
            count_ago += 1
            if kid == kanji_id:
                break
    return count_ago

def get_most_wrong_kanji(user_id, top_n=5):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # 不正解の kanji_id と character を取得
    cur.execute("""
        SELECT p.kanji_id
        FROM history h
        JOIN problems p ON h.problem_id = p.id
        WHERE h.user_id = ? AND h.is_correct = 0
    """, (user_id,))
    
    kids = [row[0] for row in cur.fetchall()]

    # 出現回数をカウント
    mistake_counts = {}
    for kid in kids:
        if kid not in mistake_counts:
            mistake_counts[kid] = 0
        mistake_counts[kid] += 1

    # 現回数で降順ソートして上位 Top N 個の kanji_id を抽出）
    sorted_kids = sorted(mistake_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    result = []
    for kid, count in sorted_kids:
        result.append((kid, kanji.get_character(kid), count))

    conn.close()
    return result

def show_dashboard(user_id):
    today = datetime.now().date()
    dates = [(today - timedelta(days=i)).isoformat() for i in range(29, -1, -1)]
    scores = [get_total_score(user_id, d) for d in dates]
    rates_raw = [get_correct_rate(user_id, d) for d in dates]

    filtered_dates = []
    filtered_rates = []
    for d, r in zip(dates, rates_raw):
        if r is not None:
            filtered_dates.append(d)
            filtered_rates.append(r * 100)

    font_jp = FontProperties(fname="C:/Windows/Fonts/msgothic.ttc")
    font_en = FontProperties(fname="C:/Windows/Fonts/arial.ttf")

    fig, axs = plt.subplots(1, 2, figsize=(9, 4.5))
    fig.subplots_adjust(wspace=2)

    # 左上にウィンドウを移動（TkAggのみ有効）
    mng = plt.get_current_fig_manager()
    try:
        mng.window.wm_geometry("+0+0")
    except Exception:
        pass

    # === 左図：クリア率円グラフ or メッセージ ===
    clear_rate = kanji.get_clear_rate(user_id)
    if clear_rate is None:
        axs[0].text(0.5, 0.5, "漢字が登録されていません", fontsize=13,
                    ha="center", va="center", transform=axs[0].transAxes, fontproperties=font_jp)
    else:
        wedges, texts, autotexts = axs[0].pie(
            [clear_rate, 1 - clear_rate],
            labels=["クリア", "未クリア"],
            autopct="%.1f%%",
            startangle=90,
            colors=["#66c2a5", "#fc8d62"],
            textprops={'fontproperties': font_en}
        )
        for t in texts:
            t.set_fontproperties(font_jp)
        axs[0].set_title("現在のクリア率", fontsize=14, fontproperties=font_jp)

        # === 苦手な漢字 Top5 を重ねて表示 ===
        mistakes = get_most_wrong_kanji(user_id)
        text_lines = [f"{i+1}. {char}（{count}回）" for i, (_, char, count) in enumerate(mistakes)]
        full_text = "苦手な漢字 Top5\n" + "\n".join(text_lines)
        axs[0].text(-1.0, -1.2, full_text, fontsize=10, fontproperties=font_jp, ha="left", va="top")

    # === 右図：スコア棒グラフ & 正答率折れ線グラフ ===
    ax1 = axs[1]
    ax2 = ax1.twinx()
    ax1.bar(dates, scores, color="#8da0cb", label="スコア")
    ax2.plot(filtered_dates, filtered_rates, color="#fc8d62", marker="o", label="正答率")

    ax1.set_ylabel("スコア", fontsize=11, fontproperties=font_jp)
    ax2.set_ylabel("正答率（%）", fontsize=11, fontproperties=font_jp)
    ax1.set_xticks(dates[::5])
    ax1.set_xticklabels(dates[::5], rotation=45, fontproperties=font_en)
    ax1.set_title("直近30日間のスコアと正答率", fontsize=14, fontproperties=font_jp)
    ax1.set_ylim(0,)
    ax2.set_ylim(0, 100)

    for label in ax1.get_yticklabels() + ax2.get_yticklabels():
        label.set_fontproperties(font_en)

    def on_key(event):
        plt.close()
    fig.canvas.mpl_connect("key_press_event", on_key)

    plt.tight_layout()
    plt.show()

today = datetime.now().date().isoformat()
REQUIREMENT_CHECKERS = {
    "clear_count":    lambda user_id, val: kanji.count_cleared_kanji(user_id) >= val,  # クリア漢字数
    "clear_rate":     lambda user_id, val: kanji.get_clear_rate(user_id) >= val / 100,       # 漢字クリア率
    "all_clear":      lambda user_id, val: kanji.get_clear_rate(user_id) >= 1.0,         # 全漢字クリア
    "consec_count":   lambda user_id, val: consec_count(user_id) >= val,               # 任意の問題での連続正解回数
    "total_answers":  lambda user_id, val: count_total_answers(user_id) >= val,        # 総回答数
    "answers_in_day": lambda user_id, val: count_total_answers(user_id, today) >= val, # 単日の回答数
    "total_score":    lambda user_id, val: get_total_score(user_id) >= val,            # 累計獲得スコア
    "score_in_day":   lambda user_id, val: get_total_score(user_id, today) >= val,     # 単日の獲得スコア
}
REQUIREMENT_SENTENCE = {
    "clear_count":    "クリアした漢字が {val} 個以上",
    "clear_rate":     "全漢字の {val}% をクリア",
    "all_clear":      "すべての漢字をクリア",
    "consec_count":   "任意の問題で {val} 回連続正解",
    "total_answers":  "これまでに {val} 回の回答",
    "answers_in_day": "1日で {val} 回の回答",
    "total_score":    "累計スコアが {val} に到達",
    "score_in_day":   "1日の獲得スコアが {val} に到達",
}

def check_trophies(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # 既に獲得済みのトロフィーIDを取得
    cur.execute("SELECT trophy_id FROM achieved_trophies WHERE user_id = ?", (user_id,))
    already_achieved = [row[0] for row in cur.fetchall()]

    # 全トロフィーを取得
    cur.execute("SELECT id, requirement_type, requirement_value, name, description, score, is_visible FROM trophies")
    all_trophies = cur.fetchall()
    conn.commit()
    conn.close()

    newly_achieved = []
    for tid, rtype, rvalue, name, desc, score, is_visible in all_trophies:
        if tid in already_achieved:
            continue
        checker = REQUIREMENT_CHECKERS[rtype]
        if checker and checker(user_id, rvalue):
            achieve_trophy(user_id, tid)
            user.update_total_score(user_id, score)
            template = REQUIREMENT_SENTENCE[rtype]
            requirement = template.format(val=rvalue)
            newly_achieved.append((name, desc, requirement, score))
    
    return newly_achieved

def list_trophies(user_id=None):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    if user_id: # ユーザーが指定された場合；requirement_type, requirement_value で昇順ソート
        cur.execute("""
            SELECT t.id, t.name, t.description, t.requirement_type, t.requirement_value, t.is_visible,
                   a.trophy_id IS NOT NULL AS is_achieved,
                   a.achieved_at
            FROM trophies t
            LEFT JOIN achieved_trophies a ON t.id = a.trophy_id AND a.user_id = ?
            ORDER BY t.requirement_type ASC, t.requirement_value ASC
        """, (user_id,))
        rows = cur.fetchall()
        conn.close()

        result = []
        for tid, name, desc, rtype, rvalue, is_visible, is_achieved, achieved_at in rows:
            template = REQUIREMENT_SENTENCE[rtype]
            requirement = template.format(val=rvalue)
            result.append({"id": tid, "name": name, "desc": desc, "requirement": requirement, "is_achieved": bool(is_achieved), "achieved_at": achieved_at[:10] if achieved_at else None, "is_visible": bool(is_visible)})
    else: # ユーザーが指定されない場合；trophy_id で昇順に並ぶ（デフォルト）
        cur.execute("SELECT id, name, description, requirement_type, requirement_value, score, is_visible FROM trophies")
        rows = cur.fetchall()
        conn.close()
        
        result = []
        for tid, name, desc, rtype, rvalue, score, is_visible in rows:
            template = REQUIREMENT_SENTENCE[rtype]
            requirement = template.format(val=rvalue)
            result.append({"id": tid, "name": name, "desc": desc, "requirement": requirement, "score": score, "is_visible": bool(is_visible)})
    return result

def add_trophy(name, description, rtype, rvalue, score, is_visible):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("INSERT INTO trophies (name, description, requirement_type, requirement_value, score, is_visible) VALUES (?, ?, ?, ?, ?, ?)", (name, description, rtype, rvalue, score, is_visible))
    conn.commit()
    conn.close()

def get_trophy(tid):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("SELECT * FROM trophies WHERE id = ?", (tid,))
    row = cur.fetchone()
    conn.close()
    return row

def edit_trophy(tid, name, description, rtype, rvalue, score, is_visible):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("UPDATE trophies SET name=?, description=?, requirement_type=?, requirement_value=?, score=?, is_visible=? WHERE id = ?", (name, description, rtype, rvalue, score, is_visible, tid))
    conn.commit()
    conn.close()

def delete_trophy(tid):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("DELETE FROM trophies WHERE id = ?", (tid,))
    conn.commit()
    conn.close()

def exist_trophy(requirement_type, requirement_value):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    if requirement_value is None:
        cur.execute("SELECT EXISTS (SELECT 1 FROM trophies WHERE requirement_type = ? AND requirement_value IS NULL)", (requirement_type,))
    else:
        cur.execute("SELECT EXISTS (SELECT 1 FROM trophies WHERE requirement_type = ? AND requirement_value = ?)", (requirement_type, requirement_value))
    is_exist = (cur.fetchone()[0] == 1)
    conn.close()
    return is_exist

def achieve_trophy(user_id, trophy_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("INSERT INTO achieved_trophies (user_id, trophy_id, achieved_at) VALUES (?, ?, ?)", (user_id, trophy_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def import_trophies_from_csv(csv_path):
    if not os.path.exists(csv_path):
        print("❌ ファイルが存在しません")
        return

    count = 0
    skipped = 0

    with open(csv_path, encoding="utf-8") as f:
        reader = list(csv.reader(f))
        total = len(reader) - 1  # ヘッダーを除いた行数
        if total <= 0:
            print(Fore.YELLOW + "⚠️ インポート対象がありません")
            return

        headers = reader[0]
        data_rows = reader[1:]

        for lineno, row in enumerate(data_rows, start=2):
            if len(row) < 6:
                print(Fore.YELLOW + f"\n⚠️ {lineno}行目: カラム数不足")
                skipped += 1
            else:
                rtype = row[0].strip()
                rvalue = row[1].strip()
                name = row[2].strip()
                desc = row[3].strip()
                score = row[4].strip()
                is_visible = row[5].strip().lower()

                if rtype not in REQUIREMENT_SENTENCE:
                    print(Fore.YELLOW + f"\n⚠️ {lineno}行目: 無効な条件タイプ '{rtype}'")
                    skipped += 1
                    continue

                try:
                    if rtype == "all_clear":
                        rvalue = None
                    else:
                        rvalue = int(rvalue)
                    score = int(score)
                    visible_flag = 1 if is_visible in ["1", "true", "yes", "y"] else 0
                except ValueError:
                    print(Fore.YELLOW + f"\n⚠️ {lineno}行目: 数値項目が無効（rvalue/score）")
                    skipped += 1
                    continue

                if not name or not desc:
                    print(Fore.YELLOW + f"\n⚠️ {lineno}行目: 名前または説明が空です")
                    skipped += 1
                    continue

                if exist_trophy(rtype, rvalue):
                    print(Fore.YELLOW + f"\n⚠️ {lineno}行目: 同一のトロフィーが既に存在します")
                    skipped += 1
                    continue

                add_trophy(name, desc, rtype, rvalue, score, visible_flag)
                count += 1

            # 🎯 進捗バー更新
            current = count + skipped
            rate = current / total
            bar = render_progress_bar(rate)
            print(f"\r📦 {bar} {current} / {total} 件", end="", flush=True)

    print(Fore.LIGHTGREEN_EX + f"\n✅ インポート完了: {count}件追加、{skipped}件スキップ")