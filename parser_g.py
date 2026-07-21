import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

import random

# --- НЕЗМІННІ НАЛАШТУВАННЯ ФІЛЬТРІВ ІДГУ ---
COURSES = ["1 курс", "2 курс", "3 курс", "4 курс"]
FORMS = ["Денна", "Заочна"]
FACULTIES = ["НПВ", "ПФ", "ФУАІД", "ФУІФ"]

# Травневий діапазон дат
DATE_START = "01.05.2026"
DATE_END = "08.05.2026"

URL = "https://idgu.edu.ua/rozklad"


def setup_driver():
    """Ініціалізація вікна браузера Chrome у фоновому (тихому) режимі"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # Тихий режим
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def switch_to_schedule_iframe(driver):
    """Пошук та перемикання всередину фрейму розкладу"""
    driver.switch_to.default_content()
    if driver.find_elements(By.CLASS_NAME, "ait-schedlfind-fac"):
        return True
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for index, iframe in enumerate(iframes):
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(index)
            if driver.find_elements(By.CLASS_NAME, "ait-schedlfind-fac"):
                return True
        except:
            continue
    driver.switch_to.default_content()
    return False


def get_all_university_groups():
    """ЕТАП 1: Швидкий збір усіх груп за одну сесію браузера"""
    driver = setup_driver()
    wait = WebDriverWait(driver, 5)
    all_extracted_groups = []

    try:
        print("⏳ Відкриваємо сайт розкладу ІДГУ для збору груп...")
        driver.get(URL)
        time.sleep(3.5)

        if not switch_to_schedule_iframe(driver):
            print("   ❌ Не вдалося знайти фрейм розкладу.")
            return []

        fac_element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "ait-schedlfind-fac")))
        form_element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "ait-schedlfind-edu")))
        course_element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "ait-schedlfind-cour")))
        group_element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "ait-schedlfind-sg")))

        select_fac = Select(fac_element)
        select_form = Select(form_element)
        select_course = Select(course_element)
        select_group = Select(group_element)

        for faculty in FACULTIES:
            target_fac = next(
                (opt.text for opt in select_fac.options if faculty.strip().lower() in opt.text.strip().lower()), None)
            if not target_fac:
                continue
            select_fac.select_by_visible_text(target_fac)
            time.sleep(0.4)

            for form in FORMS:
                target_form = next(
                    (opt.text for opt in select_form.options if form.strip().lower() == opt.text.strip().lower()), None)
                if not target_form:
                    continue
                select_form.select_by_visible_text(target_form)
                time.sleep(0.4)

                for course in COURSES:
                    target_course = next((opt.text for opt in select_course.options if
                                          course.strip().lower() in opt.text.strip().lower()), None)
                    if not target_course:
                        continue

                    select_course.select_by_visible_text(target_course)
                    time.sleep(0.8)  # Мінімальне стабільне очікування оновлення списку

                    found_in_iteration = 0
                    for option in select_group.options:
                        g_text = option.text.strip()
                        if g_text and "виберіть" not in g_text.lower() and "обрати" not in g_text.lower() and "---" not in g_text:
                            all_extracted_groups.append({
                                "faculty": faculty, "form": form, "course": course, "group_name": g_text
                            })
                            found_in_iteration += 1

    except Exception as e:
        print(f"   ⚠️ Помилка під час парсингу груп: {str(e)[:60]}")
    finally:
        driver.quit()

    return all_extracted_groups


def parse_all_schedules_optimized(groups_list):
    """
    ЕТАП 2 (МАКСИМАЛЬНО СПРОЩЕНИЙ): Працює в одній сесії браузера.
    Обирає групи НАПРЯМУ з випадаючого списку .ait-schedlfind-sg без повного переклікування
    попередніх фільтрів, що повністю усуває помилку 'element not interactable'.
    """
    driver = setup_driver()
    wait = WebDriverWait(driver, 5)
    final_schedule_rows = []

    try:
        print("⏳ Відкриваємо сайт ІДГУ для експрес-збору розкладу...")
        driver.get(URL)
        time.sleep(5.0)  # Даємо 5 секунд на повне завантаження всіх скриптів АСУ ВНЗ

        if not switch_to_schedule_iframe(driver):
            print("   ❌ Не вдалося знайти фрейм розкладу на другому етапі.")
            return []

        # Активуємо випадаючі списки (просто знаходимо їх на сторінці)
        group_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ait-schedlfind-sg")))
        select_group = Select(group_element)

        total_groups = len(groups_list)
        print(f"🚀 Починаємо прямий збір розкладу для {total_groups} груп...")

        # Послідовно йдемо прямо по списку знайдених груп
        for idx, group_info in enumerate(groups_list):
            faculty = group_info["faculty"]
            form = group_info["form"]
            course = group_info["course"]
            group_name = group_info["group_name"]

            print(f"⏳ [{idx + 1}/{total_groups}] Отримуємо розклад групи {group_name} ({faculty})...")

            try:
                # На кожній ітерації заново знаходимо селект груп та кнопку, щоб уникнути застарілих елементів
                switch_to_schedule_iframe(driver)
                grp_el = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ait-schedlfind-sg")))
                sel_group = Select(grp_el)

                # 🔥 ПРЯМИЙ ВИБІР: обираємо групу строго за текстом із готового списку Етапу 1
                group_found = False
                for option in sel_group.options:
                    if group_name.strip().lower() == option.text.strip().lower():
                        sel_group.select_by_visible_text(option.text)
                        group_found = True
                        break

                if not group_found:
                    # Якщо група не доступна в поточному DOM, спробуємо вибрати її нативно
                    try:
                        sel_group.select_by_visible_text(group_name)
                    except:
                        print(f"   ⚠️ Групу {group_name} тимчасово не видно в списку сайту. Пропускаємо...")
                        continue

                time.sleep(0.5)  # Коротка стабільна пауза

                # Натискаємо кнопку «Вивести»
                search_btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//input[@type='button' or @type='submit' or @value='Вивести'] | //button")))
                search_btn.click()

                # Очікуємо завантаження та рендерингу таблиці пар (2.5 секунди)
                time.sleep(2.5)

                # --- ЗЧИТУЄМО ТАБЛИЦЮ РОЗКЛАДУ ГРУПИ ---
                schedule_container = driver.find_element(By.CLASS_NAME, "ait-schedl")
                rows = schedule_container.find_elements(By.XPATH, ".//tr[td] | .//div[contains(@class, 'schedl-row')]")

                current_day = ""
                found_lessons = 0

                for row in rows:
                    cols = row.find_elements(By.XPATH, "./td | ./div[contains(@class, 'cell')]")
                    texts = [c.text.strip() for c in cols if c.text.strip() is not None]

                    # 7 колонок, як на вашому фото ТЗ
                    if len(texts) == 7:
                        if texts:
                            current_day = texts.replace('\n', ' ')

                        day_val, time_val, contingent_val, discipline_val, type_val, auditory_val, teacher_val = texts
                        final_schedule_rows.append({
                            "Факультет": faculty, "Форма навчання": form, "Курс": course, "Група": group_name,
                            "День": day_val if day_val else current_day, "Час навчання": time_val,
                            "Контингент": contingent_val,
                            "Дисципліна": discipline_val, "Тип заняття": type_val, "Аудиторія": auditory_val,
                            "Викладач": teacher_val
                        })
                        found_lessons += 1

                    # 6 колонок (день об'єднаний з попереднім рядком)
                    elif len(texts) == 6:
                        time_val, contingent_val, discipline_val, type_val, auditory_val, teacher_val = texts
                        final_schedule_rows.append({
                            "Факультет": faculty, "Форма навчання": form, "Курс": course, "Група": group_name,
                            "День": current_day, "Час навчання": time_val, "Контингент": contingent_val,
                            "Дисципліна": discipline_val, "Тип заняття": type_val, "Аудиторія": auditory_val,
                            "Викладач": teacher_val
                        })
                        found_lessons += 1

                if found_lessons > 0:
                    print(f"   ↳ ✅ Зчитано рядків розкладу: {found_lessons}")
                else:
                    final_schedule_rows.append({
                        "Факультет": faculty, "Форма навчання": form, "Курс": course, "Група": group_name,
                        "День": "Немає занять", "Час навчання": "-", "Контингент": group_name,
                        "Дисципліна": "На цей період розклад відсутній", "Тип заняття": "-", "Аудиторія": "-",
                        "Викладач": "-"
                    })
                    print("   ↳ ❌ Розклад відсутній.")

            except Exception as inner_e:
                print(f"   ⚠️ Збій під час обробки групи {group_name}: {str(inner_e)[:40]}")
                final_schedule_rows.append({
                    "Факультет": faculty, "Форма навчання": form, "Курс": course, "Група": group_name,
                    "День": "Помилка", "Час навчання": "-", "Контингент": group_name,
                    "Дисципліна": "Не вдалося зчитати дані рядка", "Тип заняття": "-", "Аудиторія": "-", "Викладач": "-"
                })

    except Exception as e:
        print(f"   ❌ Критична помилка другого етапу: {str(e)[:60]}")
    finally:
        driver.quit()

    return final_schedule_rows


# # --- ГОЛОВНИЙ ЦИКЛ ЗАПУСКУ ---
if __name__ == "__main__":  # 🔥 ВИПРАВЛЕНО: додано подвійні підкреслення
    start_time = time.time()

    # 1. ЕТАП 1: Швидкий збір назв груп
    groups_list = get_all_university_groups()
    print(f"\n📊 ЕТАП 1 ЗАВЕРШЕНО. Усього в ІДГУ знайдено груп: {len(groups_list)}")

    if not groups_list:
        print("❌ Не знайдено жодної групи для аналізу розкладу. Вихід.")
        exit()

    # 2. ЕТАП 2: Новий надшвидкий збір розкладу по дереву фільтрів
    print("\n🚀 ЕТАП 2: Послідовний експрес-збір розкладу для кожної групи...")
    final_rows = parse_all_schedules_optimized(groups_list)

    # 3. Експорт результатів у Excel-таблицю
    if final_rows:
        df = pd.DataFrame(final_rows)
        filename = "idgu_full_schedule.xlsx"

        # Вибудовуємо колонки точно як на фото вашого ТЗ
        column_order = [
            "Факультет", "Форма навчання", "Курс", "Група",
            "День", "Час навчання", "Контингент", "Дисципліна", "Тип заняття", "Аудиторія", "Викладач"
        ]
        df = df[column_order]
        df.to_excel(filename, index=False)

        execution_time = time.time() - start_time
        print(f"\n🎉 ВСЕ ЗАВЕРШЕНО ЗА {int(execution_time)} СЕКУНД!")
        print(f"📦 Створено підсумковий Excel-файл з точними колонками: {filename}")
    else:
        print("\n❌ Дані для збереження відсутні.")
