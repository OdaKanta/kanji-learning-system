import time
import pwinput
import threading
import queue
from wcwidth import wcswidth
import kanji
from colorama import init, Fore, Back, Style

def is_kanji(char):
    return '\u4e00' <= char <= '\u9fff'

def input_int(prompt):
    while True:
        val = input(prompt).strip()
        if val == "" or val is None:
            print(Fore.LIGHTRED_EX + "❌ 入力が空です")
            return None
        try:
            return int(val)
        except ValueError:
            print(Fore.LIGHTRED_EX + "❌ 数字を入力してください")

def input_answer(prompt, timeout):
    q = queue.Queue()

    def get_input():
        try:
            val = input(prompt)
            q.put((val, time.time()))
        except:
            q.put((None, time.time()))

    thread = threading.Thread(target=get_input)
    thread.daemon = True
    start_time = time.time()
    thread.start()

    update_interval = 0.1 # ゲージ更新間隔（秒）

    while True:
        elapsed = time.time() - start_time
        remaining = timeout - elapsed

        if not q.empty():
            val, end_time = q.get()
            elapsed_time = end_time - start_time
            val = val.strip() if val else ""
            if val == "":
                print(Fore.LIGHTRED_EX + "\n❌ 入力が空です")
                return None, elapsed_time
            try:
                return int(val), elapsed_time
            except ValueError:
                print(Fore.LIGHTRED_EX + "\n❌ 数字を入力してください")
                return None, elapsed_time

        if remaining <= 0:
            print("\r" + Fore.LIGHTRED_EX + "⏰ 時間切れです！" + " " * 30)
            return None, 0.0

        gauge = render_time_gauge(elapsed, timeout)
        remaining_display = f"{remaining:.1f}"
        print(f"\r⏳ {gauge} | 答えを入力: ", end="", flush=True)

        time.sleep(update_interval)

def input_nonempty(prompt):
    while True:
        val = input(prompt).strip()
        if val == "":
            print(Fore.LIGHTRED_EX + "❌ 入力が空です")
            return None
        else:
            return val

def input_password(prompt):
    while True:
        val = pwinput.pwinput(prompt, mask = "●").strip()
        if val == "":
            print(Fore.LIGHTRED_EX + "❌ 入力が空です")
            return None
        else:
            return val

def input_kanji(prompt):
    while True:
        val = input(prompt).strip()
        if val == "":
            print(Fore.LIGHTRED_EX + "❌ 入力が空です")
            return None
        elif len(val) != 1 or not is_kanji(val):
            print(Fore.LIGHTRED_EX + f"❌ 漢字を1文字だけ入力してください")
        else:
            return val

def get_display_width(text):
    return wcswidth(text)

def left_align_display(text, total_width):
    display_width = get_display_width(text)
    pad_right = max(total_width - display_width, 0)
    return text + ' ' * pad_right

def right_align_display(text, total_width):
    display_width = wcswidth(text)
    pad_left = max(total_width - display_width, 0)
    return ' ' * pad_left + text
    
def center_display(text, total_width):
    display_width = wcswidth(text)
    pad_total = max(total_width - display_width, 0)
    pad_left = pad_total // 2
    pad_right = pad_total - pad_left
    return ' ' * pad_left + text + ' ' * pad_right

def parse_ids(text):
    ids = set()
    parts = text.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                ids.update(range(start, end + 1))
            except ValueError:
                print(Fore.LIGHTRED_EX + f"❌ 範囲指定の形式が不正です: {part}")
        else:
            try:
                ids.add(int(part))
            except ValueError:
                print(Fore.LIGHTRED_EX + f"❌ IDが整数ではありません: {part}")
    return sorted(ids)

def render_progress_bar(rate, bar_length=30, filled_char="█", empty_char="─"):
    rate = min(max(rate, 0.0), 1.0)

    color_styles = [
        (0.90, Fore.LIGHTGREEN_EX + Style.BRIGHT),   # 明るい緑
        (0.75, Fore.GREEN + Style.NORMAL),           # 緑
        (0.60, Fore.YELLOW + Style.NORMAL),          # 黄色
        (0.45, Fore.LIGHTYELLOW_EX + Style.NORMAL),  # 明るい黄
        (0.30, Fore.LIGHTRED_EX + Style.NORMAL),     # 明るい赤
        (0.00, Fore.RED + Style.NORMAL),             # 赤
    ]
    color = next(style for threshold, style in color_styles if rate >= threshold)

    filled_length = int(round(bar_length * rate))
    empty_length = bar_length - filled_length

    bar = filled_char * filled_length
    empty = empty_char * empty_length
    percent = f"{rate * 100:.1f}%"

    return f"[{color}{bar}{Style.RESET_ALL}{empty}] {color}{percent}{Style.RESET_ALL}"

def render_time_gauge(elapsed, total, length=15, filled_char="■"):
    used = int(length * elapsed / total)
    remain = length - used
    return "[" + filled_char * remain + " " * used + f"] {total - elapsed:.1f} 秒"

def display_kanji_table(kanji_ids, columns=20):
    if not kanji_ids:
        print("（データなし）")
        return

    # 各 ID に対応する文字を取得
    characters = [kanji.get_character(kid) for kid in kanji_ids]

    col_width = 4  # 全角1文字に対応した幅（罫線込みで見やすく）
    cell_w = col_width
    border_piece = "─" * cell_w
    border = "+" + "+".join([border_piece] * columns) + "+"

    # 行ごとに分割
    print(Fore.BLACK + Back.LIGHTWHITE_EX + border)
    for i in range(0, len(characters), columns):
        row = characters[i:i + columns]
        padded = row + [""] * (columns - len(row))  # 列数が不足しても空白で補完
        line = "|" + "|".join(center_display(c, cell_w) for c in padded) + "|"
        print(Fore.BLACK + Back.LIGHTWHITE_EX + line)
        print(Fore.BLACK + Back.LIGHTWHITE_EX + border)