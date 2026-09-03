#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Прогон тестов для решений олимпиадных задач. Windows / macOS / Linux.
Запускать прямо из IDE кнопкой "Run" — всё настраивается константами ниже.

Формат тестов: файл  N  — входные данные, файл  Na  — правильный ответ.
Тесты без файла-ответа запускаются, но помечаются "?" (сверять не с чем).
"""

# ============================ НАСТРОЙКИ ============================

# Папка, где лежат решения (1.py, 2.py, ...) и папка "Тесты".
# macOS/Linux:  "/Users/msikanov/VSCodeProjects/Информатика 8-9закл"
# Windows:      r"C:\Users\msikanov\Desktop\Информатика 8-9закл"   <- буква r обязательна
PROJECT_DIR = "/Users/msikanov/PycharmProjects/ege-informatics/10-11отб"

# Файл решения. Номер задачи берётся из его имени ("5-1.py" -> задача 5),
# по нему ищутся тесты: "Тесты/5", "Тесты/Задача 5" и т. п.
SOLUTION_FILE = "5-2.py"

# Показывать вход / ожидаемый / полученный ответ для упавших тестов.
VERBOSE = True

# Лимит времени на один тест, секунды.
TIMEOUT = 1

# --- Обычно менять не нужно -----------------------------------------

# Своя папка с тестами. Пусто = искать автоматически по номеру задачи:
# "Тесты/<номер>", "Тесты/Задача <номер>"; лишняя вложенность внутри
# (папки распакованных архивов вида "Архив (15)") распознаётся сама.
TESTS_DIR = ""

# Сколько строк показывать в подробностях упавшего теста.
PREVIEW_LINES = 10

# Цветной вывод. Если консоль IDE показывает мусор вида "[32m" — поставьте False.
USE_COLORS = True

# ===================================================================

import os
import re
import subprocess
import sys
import time


def _colors_on():
    if not USE_COLORS or os.environ.get("NO_COLOR"):
        return False
    if os.name == "nt":
        try:
            import ctypes
            k = ctypes.windll.kernel32
            k.SetConsoleMode(k.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    return True


USE_COLOR = _colors_on()


def c(text, code):
    return "\033[%sm%s\033[0m" % (code, text) if USE_COLOR else text


GREEN = lambda s: c(s, "32")
RED = lambda s: c(s, "31")
YELLOW = lambda s: c(s, "33")
GREY = lambda s: c(s, "90")
BOLD = lambda s: c(s, "1")


def read_text(path):
    with open(path, "rb") as f:
        data = f.read()
    for enc in ("utf-8-sig", "utf-8", "cp1251"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", "replace")


def normalize(s):
    """Сравнение без учёта хвостовых пробелов и лишних переводов строк."""
    lines = [ln.rstrip() for ln in s.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def _tests_in_dir(test_dir):
    """Тесты, лежащие непосредственно в каталоге: [(имя, вход, ответ|None), ...]."""
    entries = {}
    try:
        names = os.listdir(test_dir)
    except OSError:
        return []
    for name in names:
        path = os.path.join(test_dir, name)
        if os.path.isfile(path) and not name.startswith("."):
            entries[name] = path

    tests = []
    for name, path in entries.items():
        if re.fullmatch(r"\d+", name):                              # 1, 2, 10 ...
            ans = entries.get(name + "a") or entries.get(name + "а")  # лат. и кир. "а"
            tests.append((name, path, ans))
    tests.sort(key=lambda t: int(t[0]))
    return tests


def find_tests(test_dir):
    """Ищет тесты, пробиваясь через лишнюю вложенность: тесты могут лежать
    не в самой папке задачи, а в распакованном архиве внутри неё
    (например "Тесты/5/Архив (15)/1").

    Берётся тот каталог, где тестов больше всего; при равенстве — самый верхний.
    Возвращает (список_тестов, каталог_где_нашли).
    """
    best_tests, best_dir = [], test_dir
    for root, dirs, _files in os.walk(test_dir):
        dirs[:] = [d for d in sorted(dirs)
                   if not d.startswith(".") and d != "__MACOSX"]
        found = _tests_in_dir(root)          # os.walk идёт сверху вниз,
        if len(found) > len(best_tests):     # поэтому строгое ">" оставляет
            best_tests, best_dir = found, root   # наименее вложенный вариант
    return best_tests, best_dir


def resolve_test_dir(project, task):
    """Каталог с тестами задачи. Понимает разные схемы именования папок."""
    if TESTS_DIR:
        d = TESTS_DIR if os.path.isabs(TESTS_DIR) else os.path.join(project, TESTS_DIR)
        return d if os.path.isdir(d) else None

    roots = []                       # сначала папки "Тесты", потом сам проект
    for name in ("Тесты", "тесты", "Tests", "tests"):
        d = os.path.join(project, name)
        if os.path.isdir(d):
            roots.append(d)
    test_roots = list(roots)
    roots.append(project)

    if task:
        variants = ("Задача " + task, "Задача" + task, "задача " + task,
                    "Task " + task, task)
        for root in roots:
            for name in variants:
                d = os.path.join(root, name)
                if os.path.isdir(d):
                    return d

    # тесты могут лежать прямо в папке "Тесты" без подпапок задач
    for root in test_roots:
        if find_tests(root)[0]:
            return root
    return None


def preview(text):
    lines = text.split("\n")
    out = "\n".join("    " + ln for ln in lines[:PREVIEW_LINES])
    if len(lines) > PREVIEW_LINES:
        out += "\n    ... (ещё %d строк)" % (len(lines) - PREVIEW_LINES)
    return out


def main():
    project = os.path.abspath(os.path.expanduser(PROJECT_DIR)) if PROJECT_DIR \
        else os.path.dirname(os.path.abspath(__file__))

    if not os.path.isdir(project):
        print(RED("Папка проекта не найдена: %s" % project))
        print(GREY("Поправьте PROJECT_DIR в начале файла."))
        return 2

    solution = os.path.join(project, SOLUTION_FILE)
    if not os.path.isfile(solution):
        print(RED("Нет файла решения: %s" % solution))
        return 2

    m = re.match(r"\d+", os.path.basename(SOLUTION_FILE))   # "5-1.py" -> "5"
    task = m.group(0) if m else None

    test_dir = resolve_test_dir(project, task)
    if test_dir is None:
        print(RED("Не найдена папка с тестами для задачи %s в %s" % (task or "?", project)))
        print(GREY("Укажите TESTS_DIR в начале файла."))
        return 2

    tests, tests_root = find_tests(test_dir)
    if not tests:
        print(RED("Тесты не найдены в %s (включая вложенные папки)" % test_dir))
        return 2

    print(BOLD("Решение: %s" % os.path.basename(solution)))
    print(BOLD("Тесты:   %s  (%d шт.)" % (tests_root, len(tests))))
    print("-" * 60)

    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"

    passed = failed = unknown = 0
    fails = []

    for name, inp_path, ans_path in tests:
        stdin_data = read_text(inp_path)
        t0 = time.time()
        try:
            proc = subprocess.run(
                [sys.executable, solution],
                input=stdin_data.encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=TIMEOUT,
                cwd=project,
                env=env,
            )
            elapsed = time.time() - t0
            out = proc.stdout.decode("utf-8", "replace")
            err = proc.stderr.decode("utf-8", "replace")
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            failed += 1
            fails.append((name, "TIMEOUT", stdin_data, "", ""))
            print("%-6s %s  %5.2fs" % (name, RED("ПРЕВЫШЕНО ВРЕМЯ"), time.time() - t0))
            continue

        if rc != 0:
            failed += 1
            fails.append((name, "RUNTIME ERROR", stdin_data, out, err))
            print("%-6s %s  %5.2fs" % (name, RED("ОШИБКА"), elapsed))
            continue

        actual = normalize(out)

        if ans_path is None:
            unknown += 1
            print("%-6s %s  %5.2fs   вывод: %s" % (
                name, YELLOW("?"), elapsed, actual.replace("\n", " | ")[:60]))
            continue

        expected = normalize(read_text(ans_path))
        if actual == expected:
            passed += 1
            print("%-6s %s  %5.2fs" % (name, GREEN("OK"), elapsed))
        else:
            failed += 1
            fails.append((name, "WRONG ANSWER", stdin_data, actual, expected))
            print("%-6s %s  %5.2fs" % (name, RED("НЕВЕРНО"), elapsed))

    print("-" * 60)
    summary = "Пройдено %d из %d" % (passed, passed + failed)
    if unknown:
        summary += "  (+%d без эталона)" % unknown
    print(BOLD(GREEN(summary) if failed == 0 else RED(summary)))

    if fails and VERBOSE:
        for name, kind, stdin_data, actual, extra in fails:
            print()
            print(BOLD("=== Тест %s — %s ===" % (name, kind)))
            print(GREY("Вход:"))
            print(preview(normalize(stdin_data)))
            if kind == "WRONG ANSWER":
                print(GREY("Ожидалось:"))
                print(preview(extra))
                print(GREY("Получено:"))
                print(preview(actual))
            elif kind == "RUNTIME ERROR":
                if actual.strip():
                    print(GREY("Вывод программы:"))
                    print(preview(actual))
                print(GREY("Ошибка:"))
                print(preview(extra.rstrip()))
    elif fails:
        print(GREY("Подробности: поставьте VERBOSE = True в начале файла"))

    return 1 if failed else 0


if __name__ == "__main__":
    main()
