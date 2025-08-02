import user
import problem
import choice
import history
import sound
import kanji
from utils import input_answer
import pygame
import time
import math
from colorama import init, Fore, Back, Style

def learning_session(user_id, problems_num, time_limit=5):
    if problem.count_all_problems() == 0:
        print(Fore.YELLOW + "⚠️ 問題プールが空です")
        return

    problems = problem.get_priority_problems(user_id, problems_num)
    if not problems:
        print(Fore.YELLOW + "⚠️ すべての漢字をクリアしているので出題対象がありません")
        return
    
    print("=== 演習開始 ===")
    print(Fore.RED + Back.WHITE + f"⏱  回答制限時間: {time_limit} 秒")
    all_correct = True
    total_score = 0
    combo_count = 0
    for i, prob in enumerate(problems, 1):
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pid, correct_kanji_id, qtext = prob
        choices = choice.generate_choices(user_id, correct_kanji_id)
        characters = [kanji.get_character(kid) for kid in choices]

        print(f"\n【第{i}問】")
        print(Fore.BLACK + Back.WHITE + f"問題: {qtext}")
        for idx, c in enumerate(characters, 1):
            print(f"[{idx}] {c}")

        sound.play_sound("audio/question.mp3")
        ans, elapsed_time = input_answer("", time_limit)

        if ans is None:
            selected = None
            is_correct = 0
            all_correct = False
            combo_count = 0
            score = 0
            sound.play_sound("audio/wrong.mp3")
        else:
            try:
                selected = choices[int(ans) - 1]
            except IndexError:
                print(Fore.YELLOW + "⚠️ 無効な番号です")
                selected = None
                is_correct = 0
                all_correct = False
                combo_count = 0
                score = 0

            is_correct = (selected == correct_kanji_id)
            if is_correct:
                remaining_time = time_limit - elapsed_time
                combo_count += 1
                consecutive_count = history.consec_count(user_id, correct_kanji_id) + 1 # この段階ではまだ history テーブルにこの問題の回答ログが記録されていないので +1 する
                problems_ago =  history.problems_ago(user_id, correct_kanji_id) or 1
                score = calc_score(remaining_time, combo_count, consecutive_count, problems_ago)
                total_score += score
                combo = f" {combo_count} コンボ" if combo_count > 1 else ""
                print(Fore.LIGHTRED_EX + "⭕ 正解！" + Fore.LIGHTYELLOW_EX + combo)
                print(Fore.LIGHTCYAN_EX + f"💎 スコア +{score}" + Fore.RESET + f"（回答所要時間: {elapsed_time:.1f} 秒）")
                sound.play_sound("audio/correct.mp3")
            else:
                all_correct = False
                combo_count = 0
                score = 0
                print("Fore.LIGHTRED_EX + ❌ 不正解")
                print(f"正解: 「{kanji.get_character(correct_kanji_id)}」")
                sound.play_sound("audio/wrong.mp3")

        history.record_answer(user_id, pid, is_correct, selected, score)
        user.update_total_score(user_id, score)
    print("=== 演習終了 ===")
    if all_correct:
        print("💯" + Fore.LIGHTWHITE_EX + Back.LIGHTRED_EX + " 全問正解！")
    print(Fore.LIGHTYELLOW_EX + f"✨ 今回の合計獲得スコア: {total_score}")

    trophies = history.check_trophies(user_id)
    if trophies:
        for name, description, requirement, score in trophies:
            print("\n" + "🏆 " + Fore.LIGHTWHITE_EX + Back.YELLOW + "新しいトロフィーを獲得！" + Style.RESET_ALL + Fore.LIGHTCYAN_EX + f"   💎 スコア +{score}")
            print("📜" + Fore.YELLOW + f" {name}" + Style.RESET_ALL + Fore.LIGHTBLACK_EX + f" ~ {description} ~")
            print(Fore.LIGHTRED_EX + f"🎯 {requirement}")
            sound.play_sound("audio/bonus.mp3")

def calc_score(remaining_time, combo_count, consecutive_count, problems_ago):
    return int((remaining_time + consecutive_count * 5 + math.log2(problems_ago)) * (1 + combo_count * 0.1))