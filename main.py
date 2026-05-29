import sys
import re
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, QTime, QUrl
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
from datetime import datetime

class UniversityKiosk(QWidget):
    def __init__(self):
        super().__init__()

        # Налаштування для IT Box: на весь екран, без рамок, поверх інших вікон
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.showFullScreen()

        # ---- НАЛАШТУВАННЯ РЕЖИМУ КІОСКУ ----
        self.showFullScreen()  # Розгортає програму на весь екран

        # За бажанням: блокуємо зміну розмірів вікна користувачем
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Задаємо темну тему, щоб очі студентів не втомлювалися, а кнопки були великими
        self.setStyleSheet("""
            QWidget {
                background-color: #0f172A; /* Темно-сірий фон */
                color: #FFFFFF;
                font-family: 'Open Sans', Arial, sans-serif;
            }
            QPushButton {
                background-color: #1F2937; /* Світліший сірий для кнопок */
                border: 2px solid #374151;
                border-radius: 15px;
                padding: 20px;
                font-size: 22px;
                font-weight: bold;
                min-height: 60px;
            }
            QPushButton:pressed {
                background-color: #3B82F6; /* Синє підсвічування при натисканні пальцем */
                border-color: #60A5FA;
            }
        """)
        # Головний контейнер (ділить екран на "Ліво" і "Право")
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # ---------------- ЛІВА ПАНЕЛЬ (МЕНЮ) ----------------
        left_menu = QVBoxLayout()
        left_menu.setSpacing(15)

        # ---------------- БЛОК ГОДИННИКА І ДАТИ ----------------
        self.time_label = QLabel(self)
        self.time_label.setFont(QFont("Open Sans", 36, QFont.Weight.Bold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("color: #3B82F6; margin-bottom: 0px;")

        self.date_label = QLabel(self)
        self.date_label.setFont(QFont("Open Sans", 16))
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet("color: #9CA3AF; margin-bottom: 25px;")

        # Додаємо годинник та дату на самий верх лівого меню
        left_menu.addWidget(self.time_label)
        left_menu.addWidget(self.date_label)

        # Створюємо таймер для оновлення часу щосекунди
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)  # Пов'язуємо з функцією оновлення
        timer.start(1000)  # Інтервал 1000 мілісекунд (1 секунда)

        # Викликаємо функцію одразу, щоб годинник з'явився без затримки в 1 секунду
        self.update_clock()

        # Створюємо великі тач-кнопки
        self.btn_home = QPushButton("🏠 Головна", self)
        self.btn_schedule = QPushButton("📅 Розклад занять", self)
        self.btn_map = QPushButton("🗺️ Карта корпусів", self)
        self.btn_university_structure = QPushButton("🏛️ Структура уніврситету", self)
        self.btn_contacts = QPushButton("📞 Контакти", self)

        # Кнопка виходу (Тимчасова! Щоб ви могли закрити програму під час тестів)
        self.btn_exit = QPushButton("❌ Вихід (Тест)", self)
        self.btn_exit.setStyleSheet("background-color: #991B1B; border: none;")

        # Додаємо кнопки в ліве меню
        left_menu.addWidget(self.btn_home)
        left_menu.addWidget(self.btn_university_structure)
        left_menu.addWidget(self.btn_map)
        left_menu.addWidget(self.btn_schedule)
        left_menu.addWidget(self.btn_contacts)
        left_menu.addStretch()  # Штовхає кнопку виходу до самого низу
        left_menu.addWidget(self.btn_exit)



        # ---------------- ПРАВА ПАНЕЛЬ (СТОРІНКИ) ----------------
        # QStackedWidget — це "стопка" сторінок. Показується тільки одна.
        self.pages_container = QStackedWidget(self)
        self.pages_container.setStyleSheet("background-color: #1F2937; border-radius: 20px; padding: 40px;")

        # Створюємо сторінки
        self.page_home = self.create_page_content(
            "Вітаємо в Ізмаїлькому Державному Гуманітарному Університеті!\n\nОберіть потрібний розділ меню ліворуч, щоб отримати інформацію.")
        self.page_schedule = self.create_schedule_page()
        self.page_university_structure = self.create_info_sidebar_page()
        self.page_map = self.create_interactive_map_page()
        self.page_contacts = self.create_page_content(
            "Контакти університету:\n\n📞 Приймальна комісія: 38 (094) 9989607, 38 (068) 0313992\n📧 Email: vstupidgu@gmail.com, idgu@ukr.net\n📍 Адреса: вул. Іллі Ріпина, 12")

        # Додаємо сторінки в наш контейнер (вони отримують індекси 0, 1, 2, 3, 4)
        self.pages_container.addWidget(self.page_home)  # Індекс 0
        self.pages_container.addWidget(self.page_university_structure)   # Індекс 1
        self.pages_container.addWidget(self.page_map)  # Індекс 2
        self.pages_container.addWidget(self.page_schedule)  # Індекс 3
        self.pages_container.addWidget(self.page_contacts)  # Індекс 4

        # ---------------- ЗБИРАЄМО ВСЕ РАЗОМ ----------------
        # Пропорція 1 до 4: ліва панель займає менше місця, права — більше
        main_layout.addLayout(left_menu, 1)
        main_layout.addWidget(self.pages_container, 4)

        # ---------------- ЛОГІКА НА КЛІКИ (ТАЧІ) ----------------
        # Прив'язуємо кнопки до перемикання сторінок за індексами
        self.btn_home.clicked.connect(lambda: self.pages_container.setCurrentIndex(0))
        self.btn_university_structure.clicked.connect(lambda: self.pages_container.setCurrentIndex(1))
        self.btn_map.clicked.connect(lambda: self.pages_container.setCurrentIndex(2))
        self.btn_schedule.clicked.connect(lambda: self.pages_container.setCurrentIndex(3))
        self.btn_contacts.clicked.connect(lambda: self.pages_container.setCurrentIndex(4))
        self.btn_exit.clicked.connect(self.close)  # Закриття програми

    def update_clock(self):
        """Функція, яка викликається щосекунди для оновлення часу та дати"""
        # Отримуємо поточний час та форматуємо його (Години:Хвилини:Секунди)
        current_time = QTime.currentTime().toString("HH:mm:ss")
        self.time_label.setText(current_time)

        # Отримуємо поточну дату українською мовою
        # Оскільки в Windows локалі можуть відрізнятися, зробимо простий словник для місяців
        months = {
            1: "січня", 2: "лютого", 3: "березня", 4: "квітня", 5: "травня", 6: "червня",
            7: "липня", 8: "серпня", 9: "вересня", 10: "жовтня", 11: "листопада", 12: "грудня"
        }
        now = datetime.now()
        current_date = f"{now.day} {months[now.month]} {now.year}"
        self.date_label.setText(current_date)

    def create_schedule_page(self):
        """
        Завантажує оригінальну сторінку розкладу ІДГУ
        та адаптує її під інтерфейс тач-кіоску без парсингу.
        """
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)  # Максимум простору для сайту

        # Створюємо вбудований браузер
        self.schedule_web = QWebEngineView()

        # Використовуємо ваше точне посилання на розклад ІДГУ
        self.schedule_url_str = "https://idgu.edu.ua/rozklad"
        self.schedule_web.setUrl(QUrl(self.schedule_url_str))

        # Збільшуємо масштаб сторінки на 35%, щоб посилання на факультети
        # та таблиці розкладу були великими і зручними для натискання пальцями
        self.schedule_web.setZoomFactor(1.35)

        # Підключаємо захист кіоску: фільтруємо всі кліки по посиланнях
        self.schedule_web.page().acceptNavigationRequest = self.filter_schedule_links

        # Після повного завантаження сторінки робимо скролбар зручним для тачу
        self.schedule_web.loadFinished.connect(self.optimize_schedule_view)

        layout.addWidget(self.schedule_web)
        return page

    def filter_schedule_links(self, url, nav_type, is_main_frame):
        """Блокує перехід на сторонні ресурси, дозволяючи лише сайт ІДГУ"""
        if url.toString() == "about:blank":
            return True

        # Дозволяємо переходи ТІЛЬКИ в межах офіційного сайту та піддоменів ІДГУ
        allowed_domain = "idgu.edu.ua"

        if allowed_domain in url.host():
            return True  # Студент може вільно переходити по розкладу факультетів

        print(f"🔒 Кіоск заблокував зовнішній перехід: {url.toString()}")
        return False  # Сторонній сайт не відкриється

    def optimize_schedule_view(self, success):
        """Очищає сторінку, адаптує календар та замінює кольори сайту (зокрема #ddd) під тему кіоску"""
        if success:
            # Встановлюємо темний фон для самого віджета браузера, поки сторінка рендериться
            self.schedule_web.setStyleSheet("background-color: #1F2937;")

            # 1. Застосовуємо стилі скролбару, ховаємо меню та ПЕРЕФАРБОВУЄМО сайт
            base_css = """
                let style = document.createElement('style');
                style.innerHTML = `
                    /* Товсті скролбари для тач-панелі */
                    ::-webkit-scrollbar { width: 28px !important; height: 28px !important; }
                    ::-webkit-scrollbar-thumb { background: #3B82F6 !important; border-radius: 14px !important; }
                    ::-webkit-scrollbar-track { background: #1F2937 !important; }

                    /* Повністю ховаємо непотрібні блоки та меню .nav_m */
                    #masthead, footer, .top-header, .navigation-bar, 
                    #mega-menu-wrap-primary-menu, .nav_m, .mobile-menu, .menu-toggle { 
                        display: none !important; 
                        visibility: hidden !important;
                    }

                    /* === СТИЛІЗАЦІЯ ПІД ТЕМНУ ТЕМУ КІОСКУ === */
                    /* Перефарбовуємо головний фон сторінки та блоки */
                    body, html, #page, #content, .site-content, .main-content-inner {
                        background-color: #1F2937 !important; /* Колір вашої правої панелі */
                        color: #FFFFFF !important;
                    }

                    /* Робимо весь текст на сторінці білим або світло-сірим */
                    p, span, h1, h2, h3, h4, h5, h6, a, td, th, li {
                        color: #FFFFFF !important;
                    }

                    /* Стилізуємо посилання, щоб вони виділялися */
                    a {
                        color: #60A5FA !important; 
                        text-decoration: none !important;
                    }
                    a:hover, a:active {
                        color: #3B82F6 !important;
                    }

                    /* Таблиці розкладу: робимо темний фон для клітинок */
                    table, tr, td, th {
                        background-color: #111827 !important; /* Трохи темніший для контрасту таблиць */
                        border: 1px solid #1F2937 !important; /* ЗАМІНА #ddd НА #1F2937 ДЛЯ МЕЖ */
                        color: #FFFFFF !important;
                    }

                    /* Глобальна заміна світлих меж та фонів, де міг бути колір #ddd */
                    div, table, td, th, tr, input, select, .ui-widget-content {
                        border-color: #1F2937 !important; /* Заміна кольору ліній */
                    }

                    /* Поля вибору дати / вводу */
                    input, select {
                        background-color: #374151 !important;
                        color: #FFFFFF !important;
                        border: 2px solid #1F2937 !important; /* ЗАМІНА МЕЖІ ПОЛІВ НА #1F2937 */
                        border-radius: 8px !important;
                        padding: 10px !important;
                        font-size: 18px !important;
                    }

                    /* Спеціальні стилі для календаря, коли він СТАЄ видимим */
                    .kiosk-datepicker-active {
                        position: fixed !important;
                        top: 20% !important;
                        left: 50% !important;
                        transform: translateX(-50%) !important;
                        z-index: 999999 !important;
                        background: #0f172A !important; /* Темний фон для вікна календаря */
                        border: 3px solid #3B82F6 !important;
                        border-radius: 15px !important;
                        padding: 20px !important;
                        box-shadow: 0px 10px 30px rgba(0,0,0,0.7) !important;
                        width: 80% !important;
                        max-width: 600px !important;
                    }

                    .kiosk-datepicker-active table {
                        width: 100% !important;
                        font-size: 24px !important;
                        border: 1px solid #1F2937 !important;
                    }

                    .kiosk-datepicker-active .ui-datepicker-header {
                        background: #1F2937 !important;
                        border: none !important;
                    }

                    .kiosk-datepicker-active .ui-datepicker-prev,
                    .kiosk-datepicker-active .ui-datepicker-next {
                        padding: 10px !important;
                        background: #374151 !important;
                        border-radius: 8px !important;
                    }
                `;
                document.head.appendChild(style);
            """
            self.schedule_web.page().runJavaScript(base_css)

            # 2. Розумний спостерігач для календаря (залишається без змін)
            js_observer = """
                function adaptDatePicker() {
                    let datePicker = document.querySelector("#ui-datepicker-div");
                    if (datePicker) {
                        if (datePicker.style.display === 'block') {
                            datePicker.classList.add("kiosk-datepicker-active");
                        } else {
                            datePicker.classList.remove("kiosk-datepicker-active");
                        }
                    }
                }

                let observer = new MutationObserver(function(mutations) {
                    mutations.forEach(function(mutation) {
                        if (mutation.attributeName === "style") {
                            adaptDatePicker();
                        }
                    });
                });

                let checkExist = setInterval(function() {
                    let datePicker = document.querySelector("#ui-datepicker-div");
                    if (datePicker) {
                        observer.observe(datePicker, { attributes: true });
                        adaptDatePicker();
                        clearInterval(checkExist);
                    }
                    document.querySelectorAll('.nav_m, .mobile-navigation').forEach(el => el.remove());
                }, 200);
            """
            self.schedule_web.page().runJavaScript(js_observer)

    def create_page_content(self, text):
        """Допоміжна функція для швидкого створення текстових сторінок"""
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 24))
        label.setWordWrap(True)  # Автоматичне перенесення тексту на новий рядок
        label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        return label

    def keyPressEvent(self, event):
        """Дозволяє закрити повноекранний режим кнопкою Esc на клавіатурі"""
        from PyQt6.QtCore import Qt  # переконайтеся, що імпортували Qt
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def create_interactive_map_page(self):
        """Варіант із кнопками, де виправлено баг нескінченного дублювання"""
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("ПЛАН НАВЧАЛЬНОГО КОРПУСУ")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet("color: #3B82F6; margin-bottom: 20px;")
        layout.addWidget(title)

        floor_buttons_layout = QHBoxLayout()
        floor_buttons_layout.setSpacing(15)
        layout.addLayout(floor_buttons_layout)

        self.map_image_label = QLabel()
        self.map_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_image_label.setStyleSheet(
            "background-color: #111827; border: 2px dashed #374151; border-radius: 15px; margin-top: 20px;")
        layout.addWidget(self.map_image_label, 1)

        self.map_description = QLabel()
        self.map_description.setFont(QFont("Segoe UI", 18))
        self.map_description.setWordWrap(True)
        self.map_description.setStyleSheet("color: #9CA3AF; margin-top: 15px;")
        layout.addWidget(self.map_description)

        floor_btn_style = """
                  QPushButton { background-color: #374151; color: white; border: 2px solid #4B5563; border-radius: 10px; padding: 15px; font-size: 20px; }
                  QPushButton:checked { background-color: #3B82F6; border-color: #60A5FA; }
           """

        floors_data = [
            (1, "floor1.jpg", "1 ПОВЕРХ: Приймальна комісія, Гардероб, Медпункт.", "1 Поверх"),
            (2, "floor2.jpg", "2 ПОВЕРХ: Адміністрація, Кафедра вищої математики.", "2 Поверх"),
            (3, "floor3.jpg", "3 ПОВЕРХ: Деканат, Аудиторії лекційні (301-305).", "3 Поверх"),
            (4, "floor4.jpg", "4 ПОВЕРХ: Аудиторії лекційні (401-405), Кафедри.", "4 Поверх"),
            (5, "floor5.jpg", "5 ПОВЕРХ: Читальний зал, Комп'ютерні класи (501-505).", "5 Поверх"),
            (6, "floor1_it.jpg", "КОРПУС ЦНІТ: Центр новітніх інформаційних технологій.", "1 Поверх, ЦНІТ"),
            (7, "floor2_sport.jpg", "СПОРТИВНИЙ КОМПЛЕКС: Спортивний зал, роздягальні.", "2 Поверх, Спортзал")
        ]

        self.floor_buttons = []

        def create_info_sidebar_page(self):
            """Варіант, де кнопки меню розміщені зліва, а вся текстова інформація — справа"""
            page = QWidget()
            # Головний маркап сторінки — тепер вертикальний тільки для загального заголовка
            main_layout = QVBoxLayout(page)

            # 1. Головний заголовок сторінки (вгорі)
            title = QLabel("ІНФОРМАЦІЙНИЙ РОЗДІЛ")
            title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
            title.setStyleSheet("color: #3B82F6; margin-bottom: 20px;")
            main_layout.addWidget(title)

            # 2. Створюємо горизонтальний контейнер для розділення: Ліво / Право
            content_layout = QHBoxLayout()
            content_layout.setSpacing(30)  # Відступ між кнопками та текстом
            main_layout.addLayout(content_layout)

            # --- ЛІВА ПАНЕЛЬ (КНОПКИ) ---
            left_buttons_layout = QVBoxLayout()
            left_buttons_layout.setSpacing(15)
            # Вирівнюємо кнопки по верхньому краю, щоб вони не розтягувалися на всю висоту
            left_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            content_layout.addLayout(left_buttons_layout)

            # --- ПРАВА ПАНЕЛЬ (ІНФОРМАЦІЯ) ---
            right_info_layout = QVBoxLayout()
            right_info_layout.setSpacing(15)
            content_layout.addLayout(right_info_layout, 1)  # Пріоритет розтягування (1) віддаємо інформації

            # Віджети для правої панелі (Головний текст та Опис нижче)
            self.info_main_text = QLabel("Оберіть розділ зліва для перегляду деталей.")
            self.info_main_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.info_main_text.setWordWrap(True)
            self.info_main_text.setFont(QFont("Segoe UI", 20))
            self.info_main_text.setStyleSheet(
                "background-color: #111827; border: 2px dashed #374151; "
                "border-radius: 15px; padding: 20px; color: white;"
            )
            right_info_layout.addWidget(self.info_main_text, 1)

            self.info_description = QLabel()
            self.info_description.setFont(QFont("Segoe UI", 18))
            self.info_description.setWordWrap(True)
            self.info_description.setStyleSheet("color: #9CA3AF; margin-top: 10px;")
            right_info_layout.addWidget(self.info_description)

            # Стиль для вертикальних кнопок зліва
            sidebar_btn_style = """
                QPushButton { 
                    background-color: #374151; 
                    color: white; 
                    border: 2px solid #4B5563; 
                    border-radius: 10px; 
                    padding: 15px 25px; 
                    font-size: 18px; 
                    text-align: left; /* Текст на кнопках буде вирівняний по лівому краю */
                    min-width: 250px;  /* Фіксована ширина для акуратності */
                }
                QPushButton:checked { 
                    background-color: #3B82F6; 
                    border-color: #60A5FA; 
                }
            """

            # Дані для ваших нових кнопок (Індекс, Головний текст, Додатковий опис, Назва кнопки)
            info_sections_data = [
                (
                    1,
                    "Інформація про факультети та спеціальності університету...",
                    "Додатково: Терміни навчання та ліцензійні обсяги.",
                    "Факультети",
                ),
                (
                    2,
                    "Правила прийому 2026: Сертифікати НМТ, пільги, етапи вступу...",
                    "Додатково: Контакти приймальної комісії.",
                    "Приймальна комісія",
                ),
                (
                    3,
                    "Вартість навчання на контрактній основі за всіма напрямками...",
                    "Додатково: Можливості оплати по семестрах.",
                    "Вартість навчання",
                ),
                (
                    4,
                    "Студентське самоврядування, гуртки, секції та дозвілля...",
                    "Додатково: Розклад роботи спортивних секцій.",
                    "Студентське життя",
                ),
            ]

            self.info_buttons = []

            # Створення кнопок у циклі (динамічно, без дублювання та багів)
            for index, main_txt, desc_txt, btn_title in info_sections_data:
                btn = QPushButton(btn_title)
                btn.setStyleSheet(sidebar_btn_style)
                btn.setCheckable(True)

                # Логіка кліку (оновлення текстових блоків справа)
                btn.clicked.connect(
                    lambda checked, mt=main_txt, dt=desc_txt, b=btn: self.on_info_button_clicked(
                        mt, dt, b
                    )
                )

                left_buttons_layout.addWidget(btn)
                self.info_buttons.append(btn)

            return page

        # Допоміжний метод для обробки кліків (скидає активність інших кнопок і міняє текст)
        def on_info_button_clicked(self, main_text, desc_text, clicked_button):
            # Вимикаємо підсвічування на всіх інших кнопках цієї сторінки
            for btn in self.info_buttons:
                btn.setChecked(False)

            # Вмикаємо підсвічування тільки на натиснутій
            clicked_button.setChecked(True)

            # Оновлюємо інформацію на панелі справа
            self.info_main_text.setText(main_text)
            self.info_description.setText(desc_text)

        def show_floor(floor_num, img_path, description_text):
            # Тільки міняємо стани вже існуючих кнопок
            for index, btn in enumerate(self.floor_buttons):
                btn.setChecked(index + 1 == floor_num)

            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(800, 550, Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                self.map_image_label.setPixmap(scaled_pixmap)
            else:
                self.map_image_label.setText(f"[ Картинку {img_path} не знайдено ]")
            self.map_description.setText(description_text)

        # ЦИКЛ НАЗОВНІ ФУНКЦІЇ — Створює кнопки всього ОДИН раз при ініціалізації
        for floor_num, img, desc, btn_text in floors_data:
            btn = QPushButton(btn_text)
            btn.setStyleSheet(floor_btn_style)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, f=floor_num, i=img, d=desc: show_floor(f, i, d))
            floor_buttons_layout.addWidget(btn)
            self.floor_buttons.append(btn)

        show_floor(1, "floor1.jpg", "1 ПОВЕРХ: Приймальна комісія, Гардероб, Медпункт.")
        return page

if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiosk = UniversityKiosk()
    kiosk.show()
    sys.exit(app.exec())
