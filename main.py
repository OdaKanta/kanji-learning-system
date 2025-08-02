import warnings

# pkg_resourcesの警告だけ非表示
warnings.filterwarnings("ignore", message="pkg_resources is deprecated*")

from datetime import datetime
import user
import kanji
import problem
import choice
import history
import learning
import admin
from utils import is_kanji, input_int, input_nonempty, input_password, input_kanji, get_display_width, left_align_display, right_align_display, center_display, render_progress_bar, display_kanji_table
from colorama import init, Fore, Back, Style
init(autoreset=True)

user_settings = {}

def main_menu():
    print(Fore.LIGHTCYAN_EX + "ℹ️ 正常に起動しました")
    title = "かんじマスター"
    total_width = 50
    title_width = get_display_width(title)
    print()
    print(Fore.LIGHTRED_EX + Back.RED + " " * total_width)
    print(Fore.LIGHTRED_EX + Back.RED + " " * 2 + Back.LIGHTYELLOW_EX + " " * (total_width-4) + Back.RED + " " * 2)
    print(Fore.LIGHTRED_EX + Back.RED + " " * 2 + Back.LIGHTYELLOW_EX + center_display(title, total_width-4) + Back.RED + " " * 2)
    print(Fore.LIGHTRED_EX + Back.RED + " " * 2 + Back.LIGHTYELLOW_EX + " " * (total_width-4) + Back.RED + " " * 2)
    print(Fore.LIGHTRED_EX + Back.RED + " " * total_width)
    while True:
        print("\n" + Back.WHITE + Fore.BLACK + "    メインメニュー    ")
        print("[1]" + Fore.LIGHTGREEN_EX  + " 🔰 新規登録")
        print("[2]" + Fore.LIGHTYELLOW_EX + " 🔓 ログイン")
        print("[3]" + Fore.LIGHTWHITE_EX  + " ⚙️ 管理者メニュー")
        print("[0]" + Fore.LIGHTRED_EX    + " 🚪 終了")
        choice_num = input_int(Fore.LIGHTCYAN_EX + "番号を選んでください: " + Fore.RESET)

        if choice_num == 1:
            register()
        elif choice_num == 2:
            user_id = login()
            if user_id:
                user_session(user_id)
        elif choice_num == 3:
            admin.admin_menu()
        elif choice_num == 0:
            print(Fore.LIGHTYELLOW_EX + "👋 終了します")
            break
        else:
            print(Fore.LIGHTRED_EX + "❌ 無効な選択です")

def configure_settings(user_id):
    max_count = problem.count_all_problems()
    print(f"\n=== 設定 ===\n現在の問題数: {max_count}")
    print(f"現在の出題数: {user_settings[user_id]['problem_num']} 問")

    while True:
        val = input_int(f"新しい出題数（1〜{max(max_count, 1)}）を入力: ")
        if val is None:
            print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
            return
        elif 1 <= val <= max(max_count, 1):
            user_settings[user_id]["problem_num"] = val
            print(Fore.LIGHTGREEN_EX + f"✅ 出題数を {val} 問に変更しました")
            return
        else:
            print(Fore.LIGHTRED_EX + "❌ 無効な数値です")

def user_session(user_id):
    history.show_dashboard(user_id)
    print()
    print(Back.WHITE + Fore.LIGHTBLACK_EX + " " * 37)
    print(Back.WHITE + Fore.LIGHTBLACK_EX + f"  🎉 ようこそ！ {Fore.LIGHTBLUE_EX + user_id + Fore.LIGHTBLACK_EX} さん".ljust(38) + " ")
    print(Back.WHITE + Fore.LIGHTBLACK_EX + " " * 37)
    if user_id not in user_settings:
        user_settings[user_id] = {"problem_num": 10} # デフォルト

    while True:
        history.show_score_summary(user_id)

        print("\n" + Back.WHITE + Fore.BLACK + "   ユーザーメニュー   ")
        print("[1]" + Fore.MAGENTA + Style.BRIGHT + " 🧠 問題演習")
        print("[2]" + Fore.CYAN                   + " 📚 学習履歴")
        print("[3]" + Fore.LIGHTWHITE_EX          + " ⚙️ 設定")
        print("[0]" + Fore.LIGHTRED_EX            + " 🚪 ログアウト")
        choice_num = input_int(Fore.LIGHTCYAN_EX + "番号を選んでください: " + Fore.RESET)

        if choice_num == 1:
            max_count = problem.count_all_problems()
            problem_num = user_settings[user_id]["problem_num"]

            # 実際の問題数を上限として再チェック
            if problem_num > max_count:
                print(Fore.LIGHTYELLOW_EX + f"⚠️ 現在の問題数は {max_count} 件です（設定を自動調整しました）")
                problem_num = max_count
                user_settings[user_id]["problem_num"] = max_count

            learning.learning_session(user_id, problem_num)

        elif choice_num == 2:
            history_menu(user_id)
        elif choice_num == 3:
            configure_settings(user_id)
        elif choice_num == 0:
            print(Fore.LIGHTYELLOW_EX + "👋 ログアウトします")
            break
        else:
            print(Fore.LIGHTRED_EX + "❌ 無効な選択です")

def register():
    username = input_nonempty("ユーザ名: ")
    if username is None:
        print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
        return

    if user.exist_user(username):
        print(Fore.LIGHTRED_EX + "❌ このユーザ名は既に登録されています")
        return

    password = input_password("パスワード(英字8文字以上): ")
    if password is None:
        print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
        return

    if len(password) < 8 or not password.isascii():
        print(Fore.LIGHTRED_EX + "❌ パスワードは英字8文字以上で設定してください")
        return

    user.register_user(username, password)
    print(Fore.LIGHTGREEN_EX + "✅ 登録完了")
    user_session(username)

def login():
    username = input_nonempty("ユーザ名: ")
    if username is None:
        print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
        return None

    password = input_password("パスワード: ")
    if password is None:
        print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
        return
    if user.login_user(username, password):
        print(Fore.LIGHTGREEN_EX + "✅ ログイン成功")
        return username
    else:
        print(Fore.LIGHTRED_EX + "❌ ログイン失敗")
        return None

def history_menu(user_id):
    while True:
        print("\n" + Back.WHITE + Fore.BLACK + "       学習履歴       ")
        print(Fore.LIGHTGREEN_EX  + "[1] 🟢 クリア済漢字一覧")
        print(Fore.RED            + "[2] 🔴 未クリア漢字一覧")
        print(Fore.YELLOW         + "[3] 🏆 トロフィー一覧")
        print(Fore.LIGHTRED_EX    + "[0] 🔙 戻る")
        choice_num = input_int("番号を選んでください: ")

        if choice_num == 1:
            kanji_ids = kanji.list_cleared_kanji(user_id)
            if kanji_ids:
                print("\n" + Fore.BLACK + Back.LIGHTGREEN_EX + center_display("クリア済漢字一覧", 101))
                display_kanji_table(kanji_ids)
                print("\nクリア済漢字数:", len(kanji_ids))
            elif not kanji.list_kanji():
                print(Fore.LIGHTYELLOW_EX + "⚠️ 漢字が登録されていません")
                continue
            else:
                print(Fore.LIGHTYELLOW_EX + "⚠️ クリア済の漢字がありません")
            rate = kanji.get_clear_rate(user_id)
            print("📊 クリア率 " + render_progress_bar(rate, bar_length=50))
        elif choice_num == 2:
            kanji_ids = kanji.list_uncleared_kanji(user_id)
            if kanji_ids:
                print("\n" + Fore.WHITE + Back.RED + center_display("未クリア漢字一覧", 101))
                display_kanji_table(kanji_ids)
                print("\n未クリア漢字数:", len(kanji_ids))
            elif not kanji.list_kanji():
                print(Fore.LIGHTYELLOW_EX + "⚠️ 漢字が登録されていません")
                continue
            else:
                print(Fore.LIGHTRED_EX + Back.LIGHTYELLOW_EX + "🎉 すべての漢字をクリアしました！")
            rate = kanji.get_clear_rate(user_id)
            print("📊 クリア率 " + render_progress_bar(rate, bar_length=50))
        elif choice_num == 3:
            trophies = history.list_trophies(user_id)
            if not trophies:
                print(Fore.LIGHTYELLOW_EX + "⚠️ トロフィーが登録されていません")
                continue

            # 幅計算
            name_w   = max([get_display_width("名前"),   max((get_display_width(t["name"]) for t in trophies if t["name"] is not None), default=0)])
            desc_w   = max([get_display_width("説明"),   max((get_display_width(t["desc"]) for t in trophies if t["desc"] is not None), default=0)])
            req_w    = max([get_display_width("条件"),   max((get_display_width(t["requirement"]) for t in trophies if t["requirement"] is not None), default=0)])
            status_w =      get_display_width("獲得状況")
            date_w   = max([get_display_width("獲得日"), max((get_display_width(t["achieved_at"]) for t in trophies if t["achieved_at"] is not None), default=0)])

            total_width = name_w + desc_w + req_w + status_w + date_w + 12  # 4本線＋スペース

            print("\n" + Fore.BLACK + Back.YELLOW + center_display(" ", total_width))
            print(       Fore.BLACK + Back.YELLOW + center_display("トロフィー一覧", total_width))
            print(       Fore.BLACK + Back.YELLOW + center_display(" ", total_width))
            print(
                center_display("名前", name_w) + " | " +
                center_display("説明", desc_w) + " | " +
                center_display("条件", req_w) + " | " +
                center_display("獲得状況", status_w) + " | " +
                center_display("獲得日", date_w)
            )
            print("-" * name_w + "-+-" + "-" * desc_w + "-+-" + "-" * req_w + "-+-" + "-" * status_w + "-+-" + "-" * date_w)

            for t in trophies:
                name   = left_align_display(t["name"], name_w) if t["is_achieved"] or t["is_visible"] else "*" * name_w
                desc   = left_align_display(t["desc"], desc_w) if t["is_achieved"] or t["is_visible"]  else "*" * desc_w
                req    = left_align_display(t["requirement"], req_w) if t["is_achieved"] or t["is_visible"] else "*" * req_w
                status = center_display("✅", status_w) if t["is_achieved"] else center_display("🔒", status_w)
                date   = center_display(t["achieved_at"], date_w) if t["is_achieved"] else " " + "-" * (date_w-2) + " "

                # 色の適用
                if t["is_achieved"]:
                    color = Fore.LIGHTGREEN_EX + Style.BRIGHT
                elif t["is_visible"]:
                    color = Fore.YELLOW
                else:
                    color = Fore.LIGHTWHITE_EX + Style.DIM

                print(color + f"{name}" + Style.RESET_ALL + " | " + color + f"{desc}" + Style.RESET_ALL + " | " + color + f"{req}" + Style.RESET_ALL + " | " + color + f"{status}" + Style.RESET_ALL + " | " + color + f"{date}")
        elif choice_num == 0:
            break
        else:
            print(Fore.LIGHTRED_EX + "❌ 無効な選択です")

if __name__=="__main__":
    main_menu()