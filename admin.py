import user
import kanji
import problem
import choice
import history
from utils import input_int, input_nonempty, input_kanji, get_display_width, left_align_display, right_align_display, center_display, parse_ids
import reset_database
from history import REQUIREMENT_SENTENCE
from colorama import init, Fore, Back, Style

def admin_menu():
    while True:
        print("\n" + Back.WHITE + Fore.BLACK + "    管理者メニュー    ")
        print("[1]" + Fore.LIGHTMAGENTA_EX + " 🈶 漢字管理")
        print("[2]" + Fore.RED             + " ❓ 問題管理")
        print("[3]" + Fore.BLUE            + " 🔀 混同候補管理")
        print("[4]" + Fore.LIGHTBLUE_EX    + " 🙍‍♂ ユーザー管理")
        print("[5]" + Fore.YELLOW          + " 🏆 トロフィー管理")
        print("[9]" + Fore.LIGHTRED_EX     + " 🔄 データベースリセット")
        print("[0]" + Fore.LIGHTRED_EX + " 🔙 戻る")
        choice_num = input_int("番号を選んでください: ")
        
        if choice_num == 1:
            kanji_management()
        elif choice_num == 2:
            problem_management()
        elif choice_num == 3:
            confusing_management()
        elif choice_num == 4:
            user_management()
        elif choice_num == 5:
            trophy_management()
        elif choice_num == 9:
            confirm = input_nonempty(Fore.LIGHTRED_EX + "\n🚨 本当にリセットしますか？(yes/no): ")
            if confirm is None:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
            if confirm.lower() == "yes":
                reset_database.reset_tables()
            else:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
        elif choice_num == 0:
            break
        else:
            print(Fore.LIGHTRED_EX + "❌ 無効な選択です")

def kanji_management():
    while True:
        print("\n" + Back.WHITE + Fore.BLACK + "     漢字管理     ")
        print("[1]" + Fore.CYAN            + " 📋 一覧")
        #print("[2]" + Fore.LIGHTMAGENTA_EX + " ➕ 追加")
        #print("[4]" + Fore.RED             + " 🗑️ 削除")
        #print("[9]" + Fore.LIGHTYELLOW_EX  + " 📂 CSVインポート")
        print("[0]" + Fore.LIGHTRED_EX     + " 🔙 戻る")
        choice_num = input_int("番号を選んでください: ")

        if choice_num == 1:
            rows = kanji.list_kanji()
            if rows:
                max_id_width = max(get_display_width(str(r[0])) for r in rows)
                max_kanji_width = max(get_display_width(r[1]) for r in rows)

                max_id_width = max(max_id_width, get_display_width("ID"))
                max_kanji_width = max(max_kanji_width, get_display_width("漢字"))

                print(center_display("= 登録漢字一覧 =", max_id_width + max_kanji_width + 4))
                print(
                    center_display("ID", max_id_width) + " | " +
                    center_display("漢字", max_kanji_width),
                )
                print("-" * (max_id_width) + "-+-" + "-" * (max_kanji_width))
                for r in rows:
                    print(
                        right_align_display(str(r[0]), max_id_width) + " | " +
                        center_display(r[1], max_kanji_width),
                    )
                print("総漢字数:", len(rows))
            else:
                print(Fore.YELLOW + "⚠️ 登録された漢字がありません")

        # elif choice_num == 2:
            # k = input_kanji("登録する漢字: ")
            # if k is None:
                # print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                # continue

            # if kanji.kanji_exist(k):
                # print(Fore.YELLOW + "⚠️ すでに登録されています")
            # else:
                # kanji.add_kanji(k)
                # print(Fore.LIGHTGREEN_EX + "✅ 登録しました")

        # elif choice_num == 4:
            # raw = input("削除する漢字ID（カンマ区切りや範囲指定可）: ").strip()
            # if raw == "":
                # print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                # continue

            # delete_ids = parse_ids(raw)
            # if not delete_ids:
                # print(Fore.YELLOW + "⚠️ 削除対象が指定されていません")
                # continue

            # count_deleted = 0
            # for kid in delete_ids:
                # result = kanji.get_character(kid)
                # if not result:
                    # print(Fore.YELLOW + f"⚠️ 漢字ID {kid} は存在しません")
                    # continue
                # kanji.delete_kanji(kid)
                # print(Fore.LIGHTWHITE_EX + f"🗑 漢字「{result[0]}」を削除しました")
                # count_deleted += 1

            # if count_deleted == 0:
                # print(Fore.YELLOW + "⚠️ 削除された漢字はありません")
            # else:
                # print(Fore.LIGHTWHITE_EX + f"🗑 合計 {count_deleted} 件の漢字を削除しました")

        # elif choice_num == 9:
            # csv_path = input_nonempty("CSVファイルパス: ")
            # if csv_path is None:
                # continue
            # kanji.import_kanji_from_csv(csv_path)

        elif choice_num == 0:
            break
        else:
            print(Fore.LIGHTRED_EX + "❌ 無効な選択です")

def problem_management():
    while True:
        print("\n" + Back.WHITE + Fore.BLACK + "     問題管理     ")
        print("[1]" + Fore.CYAN            + " 📋 一覧")
        print("[2]" + Fore.LIGHTMAGENTA_EX + " ➕ 追加")
        print("[3]" + Fore.GREEN           + " ✏️ 編集")
        print("[4]" + Fore.RED             + " 🗑️ 削除")
        print("[9]" + Fore.LIGHTYELLOW_EX  + " 📂 CSVインポート")
        print("[0]" + Fore.LIGHTRED_EX     + " 🔙 戻る")
        choice_num = input_int("番号を選んでください: ")
        
        if choice_num == 1:
            rows = problem.list_problems()
            if rows:

                # 各列の最大幅を算出（日本語対応）
                max_id_width = max(get_display_width(str(r[0])) for r in rows)
                max_q_width = max(get_display_width(r[1]) for r in rows)
                max_a_width = max(get_display_width(r[2]) for r in rows)

                # ヘッダーと比較して十分な幅を確保
                max_id_width = max(max_id_width, get_display_width("ID"))
                max_q_width = max(max_q_width, get_display_width("問題文"))
                max_a_width = max(max_a_width, get_display_width("正解"))

                # 表示
                print(center_display("=== 問題一覧 ===", max_id_width + max_q_width + max_a_width + 4))
                print(
                    center_display("ID", max_id_width) + " | " +
                    center_display("問題文", max_q_width) + " | " +
                    center_display("正解", max_a_width),
                )
                print("-" * (max_id_width) + "-+-" + "-" * (max_q_width) + "-+-" + "-" * (max_a_width))

                for r in rows:
                    print(
                        right_align_display(str(r[0]), max_id_width) + " | " +
                        left_align_display(r[1], max_q_width) + " | " +
                        center_display(r[2], max_a_width),
                    )
                print("総問題数:", len(rows))
            else:
                print(Fore.YELLOW + "⚠️ 問題がありません")
        elif choice_num == 2:
            q=input_nonempty("問題文: ")
            if q is None:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                continue
            a=input_kanji("正解漢字: ")
            if a is None:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                continue
            kanji_id = kanji.get_kanji_id(a)
            if not kanji_id:
                kanji_id = kanji.add_kanji(a)
            problem.add_problem(kanji_id,q)
            print(Fore.LIGHTGREEN_EX + "✅ 問題を追加しました")
        elif choice_num == 3:
            pid=input_int("問題ID: ")
            if pid is None:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                continue
            row=problem.get_problem(pid)
            if not row:
                print(Fore.LIGHTRED_EX + "❌ 問題が存在しません")
                continue
            print(f"現在の問題文: {row[1]}")
            print(f"現在の正解: {row[2]}")
            q=input_nonempty("新しい問題文: ")
            if q is None:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                continue
            a=input_kanji("新しい正解漢字: ")
            if a is None:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                continue
            kanji_id = kanji.get_kanji_id(a)
            if not kanji_id:
                kanji_id = kanji.add_kanji(a)
            problem.edit_problem(pid,kanji_id,q)
            print(Fore.LIGHTGREEN_EX + "✅ 問題を更新しました")
        elif choice_num == 4:
            raw = input("削除する問題ID（カンマ区切りや範囲指定可）: ").strip()
            if raw == "":
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                continue

            delete_ids = parse_ids(raw)
            if not delete_ids:
                print(Fore.YELLOW + "⚠️ 削除対象が指定されていません")
                continue

            count_deleted = 0
            for pid in delete_ids:
                row = problem.get_problem(pid)
                if not row:
                    print(Fore.YELLOW + f"⚠️ 問題ID {pid} は存在しません")
                    continue
                problem.delete_problem(pid)
                print(Fore.LIGHTWHITE_EX  + f"🗑 問題ID {pid} を削除しました")
                count_deleted += 1

            if count_deleted == 0:
                print(Fore.YELLOW + "⚠️ 削除された問題はありません")
            else:
                print(Fore.LIGHTWHITE_EX + f"🗑 合計 {count_deleted} 件の問題を削除しました")

        elif choice_num == 9:
            csv_path = input_nonempty("CSVファイルパス: ")
            if csv_path is None:
                continue
            problem.import_problems_from_csv(csv_path)
        elif choice_num == 0 :
            break
        else:
            print(Fore.LIGHTRED_EX + "❌ 無効な選択です")

def confusing_management():
    while True:
        print("\n" + Back.WHITE + Fore.BLACK + "   混同候補管理   ")
        print("[1]" + Fore.CYAN             + " 📋 一覧")
        print("[2]" + Fore.LIGHTMAGENTA_EX  + " ➕ 追加")
        print("[4]" + Fore.RED              + " 🗑️ 削除")
        print("[5]" + Fore.CYAN + Style.DIM + " 🔍 検索")
        print("[9]"                         + Fore.LIGHTYELLOW_EX + " 📂 CSVインポート")
        print("[0]"                         + Fore.LIGHTRED_EX + " 🔙 戻る")
        choice_num = input_int("番号を選んでください: ")
        
        if choice_num == 1:
            rows = choice.list_confusing_choices()
            if rows:
                # 幅整形
                max_id_width = max(get_display_width(str(r[0])) for r in rows)
                max_correct_width = max(get_display_width(r[1]) for r in rows)
                max_candidate_width = max(get_display_width(r[2]) for r in rows)

                max_id_width = max(max_id_width, get_display_width("ID"))
                max_correct_width = max(max_correct_width, get_display_width("正答"))
                max_candidate_width = max(max_candidate_width, get_display_width("候補"))

                print(center_display("= 混同候補一覧 =", max_id_width + max_correct_width + max_candidate_width + 4))
                print(
                    center_display("ID", max_id_width) + " | " +
                    center_display("正答", max_correct_width) + " | " +
                    center_display("候補", max_candidate_width),
                )
                print("-" * (max_id_width) + "-+-" + "-" * (max_correct_width) + "-+-" + "-" * (max_candidate_width))
                for r in rows:
                    print(
                        right_align_display(str(r[0]), max_id_width) + " | " +
                        center_display(r[1], max_correct_width) + " | " +
                        center_display(r[2], max_candidate_width),
                    )
            else:
                print(Fore.YELLOW + "⚠️ 混同候補がありません")

        elif choice_num == 2:
            # 追加時に「正答漢字 → kanji_id 取得」
            character = input_kanji("正答漢字: ")
            if character is None:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                continue

            candidate = input_kanji("混同候補漢字: ")
            if candidate is None:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                continue

            kanji_id = kanji.get_kanji_id(character)
            choice.add_confusing_choice(kanji_id, candidate)
            print(Fore.LIGHTGREEN_EX + "✅ 混同候補を追加しました")

        elif choice_num == 4:
            raw = input("削除する混同候補ID（カンマ区切りや範囲指定可）: ").strip()
            if raw == "":
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                continue

            delete_ids = parse_ids(raw)
            if not delete_ids:
                print("削除対象が指定されていません")
                continue

            count_deleted = 0
            for cid in delete_ids:
                if choice.get_confusing_choice(cid) is None:
                    print(Fore.YELLOW + f"⚠️ 混同候補ID {cid} は存在しません")
                    continue
                choice.delete_confusing_choice(cid)
                print(Fore.LIGHTGREEN_EX + f"✅ 混同候補ID {cid} を削除しました")
                count_deleted += 1

            if count_deleted == 0:
                print(Fore.YELLOW + "⚠️ 削除された混同候補はありません")
            else:
                print(Fore.LIGHTWHITE_EX  + f"🗑 合計 {count_deleted} 件の混同候補を削除しました")

        elif choice_num == 5:
            character = input_kanji("正答漢字（候補を検索）: ")
            if character is None:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                continue

            result = kanji.get_kanji_id(character)
            if not result:
                print(Fore.LIGHTRED_EX + "❌ 指定された漢字は kanji テーブルに存在しません")
                continue

            kanji_id = result[0]
            rows = choice.get_confusing_choices(kanji_id)
            if rows:
                max_id_width = max(get_display_width(str(r[0])) for r in rows)
                max_candidate_width = max(get_display_width(r[1]) for r in rows)

                max_id_width = max(max_id_width, get_display_width("ID"))
                max_candidate_width = max(max_candidate_width, get_display_width("候補"))

                print(center_display("= 混同候補検索結果 =", max_id_width + max_candidate_width + 4))
                print(
                    center_display("ID", max_id_width) + " | " +
                    center_display("候補", max_candidate_width),
                )
                print("-" * (max_id_width) + "-+-" + "-" * (max_candidate_width))
                for r in rows:
                    print(
                        right_align_display(str(r[0]), max_id_width) + " | " +
                        center_display(r[1], max_candidate_width),
                    )
            else:
                print(Fore.YELLOW + "⚠️ 混同候補がありません")

        elif choice_num == 9:
            csv_path = input_nonempty("CSVファイルパス: ")
            if csv_path is None:
                continue
            reverse = input("逆方向登録も行いますか？（y/N）").lower() == "y"
            choice.import_confusing_choices_from_csv(csv_path, reverse)

        elif choice_num == 0:
            break
        else:
            print(Fore.LIGHTRED_EX + "❌ 無効な選択です")

def user_management():
    while True:
        print("\n" + Back.WHITE + Fore.BLACK + "   ユーザー管理   ")
        print("[4]" + Fore.RED + " 🗑️ 削除")
        print("[0]" + Fore.LIGHTRED_EX + " 🔙 戻る")
        choice_num = input_int("番号を選んでください: ")
        
        if choice_num == 4:
            username = input_nonempty("削除するユーザ名: ")
            if username is None:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                return
            if not user.exist_user(username):
                print(Fore.LIGHTRED_EX + "❌ このユーザーは存在しません")
                return
            confirm = input_nonempty("\n🚨 本当に削除しますか？(yes/no)")
            if confirm is None:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                return
            if confirm.lower() == "yes":
                user.delete_user(username)
                print(Fore.LIGHTGREEN_EX + "✅ ユーザを削除しました")
            else:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")

        elif choice_num == 0:
            break
        else:
            print(Fore.LIGHTRED_EX + "❌ 無効な選択です")

def trophy_management():
    REQUIREMENT_TYPES = list(REQUIREMENT_SENTENCE.keys())

    while True:
        print("\n" + Back.WHITE + Fore.BLACK + "  トロフィー管理  ")
        print("[1]" + Fore.CYAN            + " 📋 一覧")
        print("[2]" + Fore.LIGHTMAGENTA_EX + " ➕ 追加")
        print("[3]" + Fore.GREEN           + " ✏️ 編集")
        print("[4]" + Fore.RED             + " 🗑️ 削除")
        print("[9]" + Fore.LIGHTYELLOW_EX  + " 📂 CSVインポート")
        print("[0]" + Fore.LIGHTRED_EX     + " 🔙 戻る")
        choice_num = input_int("番号を選んでください: ")
        
        if choice_num == 1:
            trophies = history.list_trophies()
            if trophies:
                # 各列の最大幅を計算
                id_w      = max(get_display_width("ID"), max(get_display_width(str(t["id"])) for t in trophies))
                name_w    = max(get_display_width("名前"), max(get_display_width(t["name"]) for t in trophies))
                desc_w    = max(get_display_width("説明"), max(get_display_width(t["desc"]) for t in trophies))
                req_w     = max(get_display_width("条件"), max(get_display_width(t["requirement"]) for t in trophies))
                score_w   = max(get_display_width("スコア"), max(get_display_width(str(t["score"])) for t in trophies))
                visible_w = get_display_width("公開")

                total_width = id_w + name_w + desc_w + req_w + score_w + visible_w + 15

                print(center_display("=== トロフィー一覧 ===", total_width))
                print(
                    center_display("ID", id_w) + " | " +
                    center_display("名前", name_w) + " | " +
                    center_display("説明", desc_w) + " | " +
                    center_display("条件", req_w) + " | " +
                    center_display("スコア", score_w) + " | " +
                    center_display("公開", visible_w)
                )
                print(
                    "-" * id_w + "-+-" +
                    "-" * name_w + "-+-" +
                    "-" * desc_w + "-+-" +
                    "-" * req_w + "-+-" +
                    "-" * score_w + "-+-" +
                    "-" * visible_w
                )

                for t in trophies:
                    visible_text = "○" if t.get("is_visible") else ""
                    print(
                        right_align_display(str(t["id"]), id_w) + " | " +
                        left_align_display(t["name"], name_w) + " | " +
                        left_align_display(t["desc"], desc_w) + " | " +
                        left_align_display(t["requirement"], req_w) + " | " +
                        right_align_display(str(t["score"]), score_w) + " | " +
                        center_display(visible_text, visible_w)
                    )
            else:
                print(Fore.YELLOW + "⚠️ トロフィーがありません")

        elif choice_num == 2:
            name = input_nonempty("トロフィー名: ")
            if name is None:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                continue
            desc = input_nonempty("説明: ")
            if desc is None:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                continue

            print("📌 条件タイプ一覧")
            for idx, rtype in enumerate(REQUIREMENT_TYPES, 1):
                print(f"[{idx}] {rtype} - {REQUIREMENT_SENTENCE[rtype]}")
            sel = input_int("番号を選んでください: ")
            if sel is None:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                continue
            if 1 <= sel <= len(REQUIREMENT_TYPES):
                rtype = REQUIREMENT_TYPES[sel - 1]
            else:
                print(Fore.LIGHTRED_EX + "❌ 無効な番号です")
                continue

            rvalue = input_int("条件値 val（整数）: ")
            if rvalue is None:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                continue
            score = input_int("獲得スコア: ")
            if score is None:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                continue
            is_secret = input("シークレットですか？ (y/N): ").lower() == "y"
            history.add_trophy(name, desc, rtype, rvalue, score, int(not is_secret))
            print(Fore.LIGHTGREEN_EX + "✅ トロフィーを追加しました")

        elif choice_num == 3:
            tid = input_int("トロフィーID: ")
            row = history.get_trophy(tid)
            if not row:
                print(Fore.LIGHTRED_EX + "❌ トロフィーが存在しません")
                continue
            print(f"現在の条件タイプ: {row[1]}")
            print(f"現在の条件値: {row[2]}")
            print(f"現在の名前: {row[3]}")
            print(f"現在の説明: {row[4]}")
            print(f"現在のスコア: {row[5]}")
            print(f"現在の公開設定: {'公開' if row[6] else 'シークレット'}")

            print("📌 条件タイプ一覧")
            for idx, rtype in enumerate(REQUIREMENT_TYPES, 1):
                print(f"[{idx}] {rtype} - {REQUIREMENT_SENTENCE[rtype]}")
            sel = input_int("番号を選んでください: ")
            if sel is None:
                rtype = row[1]
            elif 1 <= sel <= len(REQUIREMENT_TYPES):
                rtype = REQUIREMENT_TYPES[sel - 1]
            else:
                print(Fore.LIGHTRED_EX + "❌ 無効な番号です")
                rtype = row[1]

            rvalue = input_int("新しい条件値 val（整数）: ") or row[2]
            name = input_nonempty("新しい名前: ") or row[3]
            desc = input_nonempty("新しい説明: ") or row[4]
            score = input_int("新しい獲得スコア: ") or row[5]
            is_secret = input("シークレットですか？ (y/N): ").lower() == "y"
            history.edit_trophy(tid, name, desc, rtype, rvalue, score, int(not is_secret))
            print(Fore.LIGHTGREEN_EX + "✅ トロフィーを更新しました")

        elif choice_num == 4:
            raw = input("削除するトロフィーID（カンマ区切りや範囲可）: ").strip()
            if not raw:
                print(Fore.LIGHTCYAN_EX + "ℹ️ キャンセルしました")
                continue
            ids = parse_ids(raw)
            if not ids:
                print(Fore.YELLOW + "⚠️ 無効なID指定です")
                continue
            for tid in ids:
                if history.get_trophy(tid):
                    history.delete_trophy(tid)
                    print(Fore.LIGHTGREEN_EX + f"✅ トロフィーID {tid} を削除しました")
                else:
                    print(Fore.YELLOW + f"⚠️ トロフィーID {tid} は存在しません")

        elif choice_num == 9:
            csv_path = input_nonempty("CSVファイルパス: ")
            if csv_path:
                history.import_trophies_from_csv(csv_path)
        elif choice_num == 0:
            break
        else:
            print(Fore.LIGHTRED_EX + "❌ 無効な選択です")