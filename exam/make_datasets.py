"""
Генерация синтетических учебных датасетов для ноутбуков-ответов на экзаменационные
вопросы (директория exam/). Все данные придуманные (сгенерированы генератором
случайных чисел с фиксированным seed) и используются только для демонстрации
приёмов работы с NumPy/Pandas/файлами — они НЕ являются копией каких-либо реальных
наборов данных или литературных произведений, а лишь имитируют их структуру
(имена файлов подсказаны формулировками билетов: titanic.csv, addres-book-q.xml,
litw-win, countries-of-the-world, sp500hst.txt, себестоимость_в1.xlsx, "Анна Каренина").

Модуль можно запустить как скрипт (создаст все файлы в exam/datasets/) либо
импортировать и вызывать отдельные make_*() функции из ноутбуков.
"""
from __future__ import annotations

import csv
import random
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.dom import minidom

import numpy as np

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "datasets"
DATA_DIR.mkdir(exist_ok=True)

SEED = 20260923


# --------------------------------------------------------------------------- #
# 1. titanic.csv
# --------------------------------------------------------------------------- #
def make_titanic(path: Path = DATA_DIR / "titanic.csv", n: int = 400) -> Path:
    rng = np.random.default_rng(SEED)
    first_names_m = ["Иван", "Пётр", "Алексей", "Николай", "Сергей", "Дмитрий", "George", "William", "John", "James"]
    first_names_f = ["Анна", "Мария", "Ольга", "Елена", "Наталья", "Ирина", "Grace", "Helen", "Alice", "Margaret"]
    last_names = ["Smith", "Brown", "Johnson", "Williams", "Иванов", "Петров", "Соколов", "Кузнецов", "Miller", "Davis"]

    pclass = rng.choice([1, 2, 3], size=n, p=[0.22, 0.28, 0.50])
    sex = rng.choice(["male", "female"], size=n, p=[0.65, 0.35])

    # "истинный" возраст зависит от класса и пола (используется, чтобы потом
    # спрятать часть значений и было что восстанавливать по средним)
    base_age_by_class = {1: 38.0, 2: 30.0, 3: 25.0}
    age_true = np.array([
        max(0.5, rng.normal(base_age_by_class[int(pc)] + (2 if s == "female" else 0), 12.0))
        for pc, s in zip(pclass, sex)
    ]).round(1)

    fare_base = {1: 80.0, 2: 25.0, 3: 12.0}
    fare = np.array([max(4.0, rng.normal(fare_base[int(pc)], fare_base[int(pc)] * 0.4)) for pc in pclass]).round(2)

    survived_p = np.array([
        0.62 if s == "female" else 0.19
        for s in sex
    ])
    survived_p = survived_p + np.where(pclass == 1, 0.15, np.where(pclass == 2, 0.0, -0.1))
    survived_p = np.clip(survived_p, 0.03, 0.97)
    survived = (rng.random(n) < survived_p).astype(int)

    sibsp = rng.choice([0, 1, 2, 3, 4], size=n, p=[0.55, 0.25, 0.12, 0.05, 0.03])
    parch = rng.choice([0, 1, 2, 3], size=n, p=[0.65, 0.20, 0.10, 0.05])

    # прячем часть возрастов (NaN), доля пропусков зависит от класса
    age = age_true.copy().astype(object)
    miss_p = {1: 0.10, 2: 0.18, 3: 0.30}
    for i, pc in enumerate(pclass):
        if rng.random() < miss_p[int(pc)]:
            age[i] = ""  # пропуск

    # изредка пропускаем класс или пол, чтобы отработать условие
    # "не восстанавливать, если неизвестен и класс, и пол"
    pclass_out = pclass.astype(object)
    sex_out = sex.astype(object)
    for i in rng.choice(n, size=max(1, n // 60), replace=False):
        pclass_out[i] = ""
    for i in rng.choice(n, size=max(1, n // 60), replace=False):
        sex_out[i] = ""

    names = []
    for s in sex:
        if s == "male":
            names.append(f"{rng.choice(last_names)}, {rng.choice(first_names_m)}")
        else:
            names.append(f"{rng.choice(last_names)}, {rng.choice(first_names_f)}")

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["PassengerId", "Survived", "Pclass", "Name", "Sex", "Age", "SibSp", "Parch", "Fare"])
        for i in range(n):
            writer.writerow([
                i + 1, int(survived[i]), pclass_out[i], names[i], sex_out[i],
                age[i], int(sibsp[i]), int(parch[i]), fare[i],
            ])
    return path


# --------------------------------------------------------------------------- #
# 2. addres-book-q.xml
# --------------------------------------------------------------------------- #
def make_address_book_xml(path: Path = DATA_DIR / "addres-book-q.xml", n: int = 24) -> Path:
    rng = random.Random(SEED)
    male_names = ["Иван Петров", "Сергей Смирнов", "Алексей Кузнецов", "Дмитрий Попов",
                  "Николай Волков", "Михаил Соколов", "Андрей Морозов", "Виктор Лебедев"]
    female_names = ["Анна Егорова", "Мария Фёдорова", "Ольга Никитина", "Елена Захарова",
                     "Наталья Павлова", "Ирина Семёнова", "Татьяна Голубева", "Светлана Виноградова"]
    companies = ["ООО Ромашка", "АО СтройИнвест", "ЗАО Вектор", "ООО ТехноПром",
                 "ИП Соколов", "ООО Глобус", "АО Меридиан", "ООО Альянс"]

    root = ET.Element("address-book")

    def make_phone(rng_: random.Random) -> str:
        return f"+7-{rng_.randint(900, 999)}-{rng_.randint(100, 999)}-{rng_.randint(10, 99)}-{rng_.randint(10, 99)}"

    for i in range(n):
        is_male = i % 2 == 0
        name = rng.choice(male_names) if is_male else rng.choice(female_names)
        person = ET.SubElement(root, "person", {"gender": "male" if is_male else "female"})
        ET.SubElement(person, "name").text = name
        ET.SubElement(person, "company").text = rng.choice(companies)
        ET.SubElement(person, "work-phone").text = make_phone(rng)
        ET.SubElement(person, "personal-phone").text = make_phone(rng)

    xml_bytes = ET.tostring(root, encoding="utf-8")
    pretty = minidom.parseString(xml_bytes).toprettyxml(indent="  ", encoding="utf-8")
    path.write_bytes(pretty)
    return path


# --------------------------------------------------------------------------- #
# 3. litw-win (частотный список русских слов, кодировка windows-1251 — см. Q16)
# --------------------------------------------------------------------------- #
def make_litw_win(path: Path = DATA_DIR / "litw-win.csv") -> Path:
    rng = random.Random(SEED)
    words = [
        ("и", "cj"), ("в", "pr"), ("не", "pt"), ("на", "pr"), ("я", "spro"),
        ("быть", "v"), ("он", "spro"), ("с", "pr"), ("что", "cj"), ("а", "cj"),
        ("это", "spro"), ("весь", "apro"), ("как", "advpro"), ("она", "spro"),
        ("по", "pr"), ("но", "cj"), ("они", "spro"), ("к", "pr"), ("у", "pr"),
        ("ты", "spro"), ("из", "pr"), ("мы", "spro"), ("за", "pr"), ("то", "cj"),
        ("свой", "apro"), ("человек", "s"), ("который", "apro"), ("год", "s"),
        ("сказать", "v"), ("время", "s"), ("говорить", "v"), ("знать", "v"),
        ("дело", "s"), ("рука", "s"), ("день", "s"), ("глаз", "s"), ("жизнь", "s"),
        ("дом", "s"), ("вода", "s"), ("слово", "s"), ("работа", "s"), ("город", "s"),
        ("случай", "s"), ("друг", "s"), ("сила", "s"), ("голова", "s"), ("сердце", "s"),
        ("голос", "s"), ("мир", "s"), ("земля", "s"),
    ]
    rng.shuffle(words)
    with path.open("w", newline="", encoding="windows-1251") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["rank", "lemma", "pos", "ipm"])
        ipm = 15000.0
        for rank, (lemma, pos) in enumerate(words, start=1):
            ipm *= rng.uniform(0.55, 0.85)
            writer.writerow([rank, lemma, pos, round(ipm, 1)])
    return path


# --------------------------------------------------------------------------- #
# 4. countries-of-the-world.csv
# --------------------------------------------------------------------------- #
def make_countries(path: Path = DATA_DIR / "countries-of-the-world.csv") -> Path:
    rng = np.random.default_rng(SEED)
    countries = [
        ("Russia", "C.W. OF IND. STATES"), ("Germany", "WESTERN EUROPE"), ("France", "WESTERN EUROPE"),
        ("Brazil", "LATIN AMER. & CARIB"), ("China", "ASIA (EX. NEAR EAST)"), ("India", "ASIA (EX. NEAR EAST)"),
        ("Egypt", "NORTHERN AFRICA"), ("Nigeria", "SUB-SAHARAN AFRICA"), ("USA", "NORTHERN AMERICA"),
        ("Canada", "NORTHERN AMERICA"), ("Japan", "ASIA (EX. NEAR EAST)"), ("Australia", "OCEANIA"),
        ("Mexico", "LATIN AMER. & CARIB"), ("Italy", "WESTERN EUROPE"), ("Spain", "WESTERN EUROPE"),
        ("Poland", "EASTERN EUROPE"), ("Turkey", "NEAR EAST"), ("Argentina", "LATIN AMER. & CARIB"),
        ("Kenya", "SUB-SAHARAN AFRICA"), ("Sweden", "WESTERN EUROPE"), ("Norway", "WESTERN EUROPE"),
        ("Ukraine", "C.W. OF IND. STATES"), ("Kazakhstan", "C.W. OF IND. STATES"), ("Vietnam", "ASIA (EX. NEAR EAST)"),
        ("Thailand", "ASIA (EX. NEAR EAST)"), ("South Africa", "SUB-SAHARAN AFRICA"), ("Chile", "LATIN AMER. & CARIB"),
        ("Greece", "WESTERN EUROPE"), ("Portugal", "WESTERN EUROPE"), ("Finland", "WESTERN EUROPE"),
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Country", "Region", "Population", "Area (sq. mi.)", "GDP ($ per capita)",
                          "Literacy (%)", "Birthrate", "Deathrate"])
        for name, region in countries:
            population = int(rng.integers(2_000_000, 1_400_000_000))
            area = int(rng.integers(20_000, 9_000_000))
            gdp = int(rng.integers(700, 65_000))
            literacy = round(float(rng.uniform(55, 99.9)), 1)
            birthrate = round(float(rng.uniform(7, 45)), 2)
            deathrate = round(float(rng.uniform(3, 18)), 2)
            writer.writerow([name, region, population, area, gdp, literacy, birthrate, deathrate])
    return path


# --------------------------------------------------------------------------- #
# 5. sp500hst.txt (без заголовка: Дата,Тикер,Open,High,Low,Close,Volume)
# --------------------------------------------------------------------------- #
def make_sp500hst(path: Path = DATA_DIR / "sp500hst.txt") -> Path:
    rng = np.random.default_rng(SEED)
    tickers = ["AAPL", "MSFT", "GE", "XOM", "KO", "IBM", "JPM", "PFE"]
    start_prices = {"AAPL": 30, "MSFT": 28, "GE": 15, "XOM": 65, "KO": 55, "IBM": 130, "JPM": 40, "PFE": 17}

    # торговые дни 2010 года (пропускаем выходные, без учёта праздников — не принципиально)
    import datetime
    day = datetime.date(2010, 1, 4)
    end = datetime.date(2010, 12, 31)
    dates = []
    while day <= end:
        if day.weekday() < 5:
            dates.append(day)
        day += datetime.timedelta(days=1)

    rows = []
    for t in tickers:
        price = start_prices[t]
        for d in dates:
            ret = rng.normal(0.0003, 0.015)
            price = max(1.0, price * (1 + ret))
            open_ = price * (1 + rng.normal(0, 0.003))
            close = price
            high = max(open_, close) * (1 + abs(rng.normal(0, 0.004)))
            low = min(open_, close) * (1 - abs(rng.normal(0, 0.004)))
            volume = int(rng.integers(1_000_000, 20_000_000))
            rows.append([d.strftime("%Y%m%d"), t, round(open_, 2), round(high, 2),
                         round(low, 2), round(close, 2), volume])

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    return path


# --------------------------------------------------------------------------- #
# 6. себестоимость_в1.xlsx
# --------------------------------------------------------------------------- #
def make_sebestoimost_xlsx(path: Path = DATA_DIR / "себестоимость_в1.xlsx") -> Path:
    import openpyxl

    rng = np.random.default_rng(SEED)
    resources = ["Мука", "Сахар", "Яйца", "Масло", "Молоко", "Соль"]
    recipes = ["Рецептура 1", "Рецептура 2", "Рецептура 3", "Рецептура 4"]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Себестоимость"

    ws.append(["Ресурс", *recipes])
    values = rng.uniform(0.1, 5.0, size=(len(resources), len(recipes))).round(2)
    for res, row in zip(resources, values):
        ws.append([res, *row.tolist()])

    # строка со "средним физическим расходом ресурсов" изначально записана неверно
    # (например, нулями) — именно её должен пересчитать код на Python
    ws.append(["Средний физический расход ресурсов", *[0.0] * len(recipes)])

    wb.save(path)
    return path


# --------------------------------------------------------------------------- #
# 7. синтетический текст в стиле романа с главной героиней "Анна"
# --------------------------------------------------------------------------- #
def make_anna_synthetic_text(path: Path = DATA_DIR / "anna_synthetic.txt") -> Path:
    """
    ВНИМАНИЕ: это НЕ текст романа Л.Н. Толстого «Анна Каренина», а собственный
    сгенерированный текст, который используется как заменитель ради задачи
    билета №19 (частоты словоформ имени персонажа) и билета №14 (топ-200 слов).
    """
    rng = random.Random(SEED)

    name_forms = {
        "nomn": "Анна",
        "gent": "Анны",
        "datv": "Анне",
        "accs": "Анну",
        "ablt": "Анной",
        "loct": "Анне",
    }

    templates = [
        "{Name} вошла в гостиную и посмотрела на часы.",
        "Все заговорили об {Name_loc}, но никто не решался спросить прямо.",
        "Вронский подошёл к {Name_dat} и поклонился.",
        "Кити давно не видела {Name_acc} и обрадовалась встрече.",
        "Письмо от {Name_gen} лежало на столе нераспечатанным.",
        "{Name} долго молчала, глядя в окно на засыпанный снегом сад.",
        "Друзья {Name_gen} собрались вечером в старом доме у реки.",
        "Никто не мог сравниться с {Name_abl} в лёгкости движений.",
        "Разговор с {Name_abl} оставил у Левина странное чувство тревоги.",
        "{Name} написала короткую записку и отправила её с посыльным.",
        "Степан Аркадьич рассказал сестре о делах в конторе.",
        "Поезд медленно подходил к перрону, и пассажиры собирали вещи.",
        "В саду цвели яблони, и воздух был наполнен ароматом весны.",
        "Крестьяне работали в поле от рассвета до заката.",
        "Оркестр заиграл вальс, и гости начали собираться в зале.",
        "Старый слуга принёс самовар и расставил чашки на столе.",
        "За окном шёл дождь, и капли стучали по крыше веранды.",
        "Дети играли во дворе, пока взрослые пили чай на террасе.",
        "Доктор посоветовал больше гулять на свежем воздухе.",
        "Помещик долго считал расходы на постройку новой мельницы.",
    ]

    filler_words = (
        "дом сад окно стол чай вечер утро дорога письмо город река снег "
        "весна осень друг сестра брат слуга разговор мысль чувство душа "
        "свет тень голос улыбка взгляд память надежда тревога радость "
        "поле лес небо солнце луна звезда ветер дождь снегопад мороз "
        "усадьба гостиная зала веранда терраса кабинет библиотека камин "
        "свеча лампа зеркало картина ковёр кресло диван шкаф часы "
        "экипаж коляска лошадь кучер станция перрон вагон купе платформа "
        "платок перчатка шляпа пальто платье букет цветок роза сирень "
        "музыка вальс романс рояль скрипка бал приём гости хозяйка "
        "секретарь управляющий кучер горничная лакей повар кухарка нянька "
        "родственник знакомый сосед помещик крестьянин мужик деревня усадебка "
        "имение контора счёт расход доход урожай мельница амбар конюшня "
        "надежда сомнение тревога волнение спокойствие покой печаль тоска "
        "нежность гордость ревность обида прощение сострадание жалость "
        "утешение слеза улыбка вздох молчание тишина шёпот крик смех "
        "прогулка поездка визит встреча прощание разлука возвращение отъезд "
        "весточка записка телеграмма газета книга роман стихи журнал "
        "зима лето осеннее утро летний вечер весеннее утро зимний день"
    ).split()

    lines = []
    for _ in range(900):
        tpl = rng.choice(templates)
        line = (
            tpl.replace("{Name}", name_forms["nomn"])
            .replace("{Name_loc}", name_forms["loct"])
            .replace("{Name_dat}", name_forms["datv"])
            .replace("{Name_acc}", name_forms["accs"])
            .replace("{Name_gen}", name_forms["gent"])
            .replace("{Name_abl}", name_forms["ablt"])
        )
        if rng.random() < 0.7:
            extra = " ".join(rng.choice(filler_words) for _ in range(rng.randint(3, 7)))
            line = line[:-1] + " " + extra + "."
        lines.append(line)

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def make_all() -> None:
    make_titanic()
    make_address_book_xml()
    make_litw_win()
    make_countries()
    make_sp500hst()
    make_sebestoimost_xlsx()
    make_anna_synthetic_text()
    print(f"Готово. Файлы в {DATA_DIR}:")
    for p in sorted(DATA_DIR.iterdir()):
        print(" -", p.name)


if __name__ == "__main__":
    make_all()
