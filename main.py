import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, QTime, QUrl
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
from datetime import datetime

import json

from PyQt6.QtCore import QObject, QEvent

class GlobalTouchFilter(QObject):
    def __init__(self, kiosk_instance):
        super().__init__()
        self.kiosk = kiosk_instance

    def eventFilter(self, obj, event):
        # Перехоплюємо натискання миші, тач-події або прокрутку (скрол)
        if event.type() in [QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease,
                            QEvent.Type.TouchBegin, QEvent.Type.TouchUpdate]:
            # Щоразу, коли відбувається дотик — скидаємо таймер кіоску
            if hasattr(self.kiosk, 'inactivity_timer'):
                self.kiosk.inactivity_timer.start()
        return super().eventFilter(obj, event)



class UniversityKiosk(QWidget):
    def __init__(self):
        super().__init__()

        # Налаштування для IT Box: без рамок
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

        # АВТОМАТИЧНО ОТРИМУЄМО РОЗМІР ВАШОГО МОНІТОРА:
        screen = QApplication.primaryScreen().geometry()
        self.setFixedSize(screen.width(), screen.height())  # Жорстко фіксуємо під екран

        self.showFullScreen()  # Запускаємо в чистому повноекранному режимі

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
        # Додаємо ім'я для зв'язку зі style.qss
        self.time_label.setObjectName("ClockTime")

        self.date_label = QLabel(self)
        self.date_label.setFont(QFont("Open Sans", 16))
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Додаємо ім'я для зв'язку зі style.qss
        self.date_label.setObjectName("ClockDate")

        # Додаємо годинник та дату на самий верх лівого меню
        left_menu.addWidget(self.time_label)
        left_menu.addWidget(self.date_label)

        # Створюємо таймер для оновлення часу щосекунди
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)

        # Викликаємо функцію одразу, щоб годинник з'явився без затримки в 1 секунду
        self.update_clock()

        # ---------------- СТВОРЮЄМО ВЕЛИКІ ТАЧ-КНОПКИ ----------------
        self.btn_home = QPushButton("🏠 Головна", self)
        # ПРИВ'ЯЗУЄМО ДО ГЛОБАЛЬНОГО СТИЛЮ QPushButton (через базовий селектор або ім'я)
        self.btn_home.setObjectName("MainMenuButton")

        self.btn_schedule = QPushButton("📅 Розклад", self)
        self.btn_schedule.setObjectName("MainMenuButton")

        self.btn_map = QPushButton("🗺️ Карта корпусів", self)
        self.btn_map.setObjectName("MainMenuButton")

        self.btn_university_structure = QPushButton("🏛️ Структура унівeрситету", self)
        self.btn_university_structure.setObjectName("MainMenuButton")

        self.btn_contacts = QPushButton("📞 Контакти", self)
        self.btn_contacts.setObjectName("MainMenuButton")

        # Кнопка виходу (Тимчасова! Щоб ви могли закрити програму під час тестів)
        # self.btn_exit = QPushButton("❌ Вихід (Тест)", self)
        # Додаємо ім'я для зв'язку з ExitTestButton у qss
        # self.btn_exit.setObjectName("ExitTestButton")

        # Додаємо кнопки в ліве меню
        left_menu.addWidget(self.btn_home)
        left_menu.addWidget(self.btn_university_structure)
        left_menu.addWidget(self.btn_map)
        left_menu.addWidget(self.btn_schedule)
        left_menu.addWidget(self.btn_contacts)
        left_menu.addStretch()  # Штовхає кнопку виходу до самого низу
        # left_menu.addWidget(self.btn_exit)

        # ---------------- ПРАВА ПАНЕЛЬ (СТОРІНКИ) ----------------
        # QStackedWidget — це "стопка" сторінок. Показується тільки одна.
        self.pages_container = QStackedWidget(self)
       # self.pages_container.setStyleSheet("background-color: #1F2937; border-radius: 20px; padding: 40px;")

        # Створюємо сторінки
        self.page_home = self.create_home_page()
        self.page_schedule = self.create_schedule_page()
        self.page_university_structure = self.create_info_sidebar_page()
        self.page_map = self.create_interactive_map_page()
        # Замените старую строку на вызов новой функции:
        self.page_contacts = self.create_contacts_page()

        # Додаємо сторінки в наш контейнер (вони отримують індекси 0, 1, 2, 3, 4)
        self.pages_container.addWidget(self.page_home)  # Індекс 0
        self.pages_container.addWidget(self.page_university_structure)   # Індекс 1
        self.pages_container.addWidget(self.page_map)  # Індекс 2
        self.pages_container.addWidget(self.page_schedule)  # Індекс 3
        self.pages_container.addWidget(self.page_contacts)  # Індекс 4

        # ---------------- ЗБИРАЄМО ВСЕ РАЗОМ ----------------
        # Пропорція 1 до 4: ліва панель займає менше місця, права — більше
        main_layout.addLayout(left_menu, 1)
        main_layout.addWidget(self.pages_container, 2)

        # ---------------- ЛОГІКА НА КЛІКИ (ТАЧІ) ----------------
        # Прив'язуємо кнопки до перемикання сторінок за індексами
        self.btn_home.clicked.connect(lambda: self.pages_container.setCurrentIndex(0))
        self.btn_university_structure.clicked.connect(lambda: self.pages_container.setCurrentIndex(1))
        self.btn_map.clicked.connect(lambda: self.pages_container.setCurrentIndex(2))
        self.btn_schedule.clicked.connect(lambda: self.pages_container.setCurrentIndex(3))
        self.btn_contacts.clicked.connect(lambda: self.pages_container.setCurrentIndex(4))
        #self.btn_exit.clicked.connect(self.close)  # Закриття програми

        # ---------------- ТАЙМЕР БЕЗДІЯЛЬНОСТІ ----------------
        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setInterval(90000)  # 90000 мілісекунд = 90 секунд
        self.inactivity_timer.timeout.connect(self.return_to_home)
        self.inactivity_timer.start()

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
        """ Завантажує оригінальну сторінку розкладу ІДГУ та адаптує її під інтерфейс тач-кіоску без парсингу."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)  # Максимум простору для сайту

        # Створюємо вбудований браузер
        self.schedule_web = QWebEngineView()
        self.schedule_web.setObjectName("ScheduleBrowser")  # Прив'язка до QSS

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
        # Очищає сторінку, адаптує календар
        if success:
            # Рядок setStyleSheet ВИДАЛЕНО — тепер фон підтягується зі style.qss автоматично

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

    def create_home_page(self):
        """Створює головну сторінку з ідеальним системним центруванням."""
        page = QWidget()

        # Головний вертикальний макет для всієї сторінки
        layout = QVBoxLayout(page)

        # Важливо: усуваємо розтягування сетки, змушуючи елементи групуватися строго по центру
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(25)

        # 1. ЕЛЕМЕНТ ДЛЯ ВІДОБРАЖЕННЯ ЛОГОТИПУ
        # 1. ЕЛЕМЕНТ ДЛЯ ВІДОБРАЖЕННЯ ЛОГОТИПУ
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Визначаємо шлях до папки з .exe
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        logo_path = os.path.join(base_dir, "logo.png")
        pixmap = QPixmap(logo_path)

        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(
                350, 350,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            logo_label.setText("[ Логотип університету не знайдено ]")
            logo_label.setObjectName("LogoErrorLabel")

        # 2. ГОЛОВНИЙ ВІТАЛЬНИЙ ЗАГОЛОВОК
        welcome_title = QLabel("Вітаємо в Ізмаїльському державному гуманітарному університеті!")
        welcome_title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_title.setWordWrap(True)
        welcome_title.setObjectName("WelcomeTitle")
        welcome_title.setFixedWidth(750)  # Задаємо ТІЛЬКИ ширину, висота підлаштується автоматично

        # 3. ІНСТРУКЦІЯ ДЛЯ СТУДЕНТА
        welcome_hint = QLabel("Оберіть потрібний розділ меню ліворуч, щоб отримати інформацію.")
        welcome_hint.setFont(QFont("Segoe UI", 20))
        welcome_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_hint.setWordWrap(True)
        welcome_hint.setObjectName("WelcomeHint")
        welcome_hint.setFixedWidth(750)  # Задаємо ТІЛЬКИ ширину

        # Додаємо елементи і явно вказуємо Qt вирівнювати їх по центру всередині контейнера
        layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_hint, alignment=Qt.AlignmentFlag.AlignCenter)

        return page

    def keyPressEvent(self, event):
        """Дозволяє закрити повноекранний режим кнопкою Esc на клавіатурі"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def return_to_home(self):
        """Спрацьовує, коли таймер добігає кінця."""
        # Перевіряємо, чи кіоск зараз НЕ на головній сторінці (індекс 0)
        if self.pages_container.currentIndex() != 0:
            self.pages_container.setCurrentIndex(0) # Скидаємо сторінку на головну
            print("⏳ Екран автоматично скинуто на головну сторінку.")

    def create_interactive_map_page(self):
        """Створює сторінку інтерактивної мапи з JSON-даними."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 20, 25, 20)

        # Название страницы (привязка к стилю QLabel#MapTitle)
        title = QLabel("🗺 ПЛАН НАВЧАЛЬНОГО КОРПУСУ")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setObjectName("MapTitle")
        layout.addWidget(title)

        # ВИПРАВЛЕНО: Присвоюємо правильний ObjectName для рамки карти
        self.map_image_label = QLabel()
        self.map_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_image_label.setObjectName("MapImageContainer")  # Зв'язок з QSS!

        # ВИПРАВЛЕНО: Присвоюємо правильний ObjectName для нижнього опису
        self.map_description = QLabel()
        self.map_description.setObjectName("MapDescription")  # Зв'язок з QSS!
        self.map_description.setWordWrap(True)
        self.map_description.setFont(QFont("Segoe UI", 18))

        # Горизонтальний макет кнопок з фіксованими відступами
        floor_buttons_layout = QHBoxLayout()
        floor_buttons_layout.setSpacing(15)  # Розсуває кнопки в коді
        floor_buttons_layout.setContentsMargins(0, 10, 0, 15)

        self.floor_buttons = []
        self.map_data_store = {}

        # --- Завантаження даних ---
        try:
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))

            json_path = os.path.join(base_dir, "data.json")

            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    floors_source = json.load(f).get("floors_data", [])

                    for item in floors_source:
                        btn = QPushButton(item.get("name", "Поверх"))
                        btn.setObjectName("FloorButton")
                        btn.setCheckable(True)

                        self.map_data_store[btn.text()] = {
                            "image": os.path.join(base_dir, item.get("image_path", "")),
                            "description": item.get("description", "")
                        }
                        btn.clicked.connect(self.show_floor)
                        floor_buttons_layout.addWidget(btn)
                        self.floor_buttons.append(btn)

            layout.addLayout(floor_buttons_layout)
            layout.addWidget(self.map_image_label, 1)
            layout.addWidget(self.map_description)

            # ВИПРАВЛЕНО КРАШ РОЗМІРУ: Завантажуємо карту першого поверху БЕЗ передчасного кліку
            if self.floor_buttons:
                first_btn = self.floor_buttons[0]
                first_btn.setChecked(True)

                data = self.map_data_store.get(first_btn.text(), {})
                self.map_description.setText(data.get("description", ""))

                img_path = data.get("image", "")
                if img_path and os.path.exists(img_path):
                    pixmap = QPixmap(img_path)
                    # Фіксований безпечний розмір для першого рендеру табло (1200х650)
                    self.map_image_label.setPixmap(pixmap.scaled(
                        1200, 650,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    ))

        except Exception as e:
            self.map_description.setText(f"Помилка: {e}")

        return page

    def show_floor(self):
        """Оновлює картинку та опис на основі натиснутої кнопки."""
        clicked_btn = self.sender()
        if not clicked_btn: return

        for btn in self.floor_buttons:
            btn.blockSignals(True)
            btn.setChecked(btn == clicked_btn)
            btn.blockSignals(False)

        data = self.map_data_store.get(clicked_btn.text(), {})
        self.map_description.setText(data.get("description", ""))

        import os
        img_path = data.get("image", "")
        if img_path and os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            # Використовуємо якісне SmoothTransformation для чіткості кабінетів
            scaled = pixmap.scaled(
                self.map_image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.map_image_label.setPixmap(scaled)

    def create_info_sidebar_page(self):
        """Створює сторінку інформації з бічним меню."""
        page = QWidget()
        main_layout = QVBoxLayout(page)

        # 1. ЗАГОЛОВОК СТОРІНКИ
        title = QLabel("🏛 ІНФОРМАЦІЯ ПО СТРУКТУРІ УНІВЕРСИТЕТУ")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setObjectName("StructureTitle")
        main_layout.addWidget(title)

        # 2. ГОЛОВНИЙ ГОРИЗОНТАЛЬНИЙ КОНТЕЙНЕР
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        main_layout.addLayout(content_layout)

        # --- ЛІВА ПАНЕЛЬ (КНОПКИ) ---
        self.left_buttons_layout = QVBoxLayout()
        self.left_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.left_buttons_layout.addSpacing(30)
        content_layout.addLayout(self.left_buttons_layout)

        # --- ПРАВА ПАНЕЛЬ (ІНФОРМАЦІЯ) ---
        right_info_layout = QVBoxLayout()
        content_layout.addLayout(right_info_layout, 1)

        # Створюємо початковий текст
        self.info_main_text = QLabel("Оберіть розділ зліва для перегляду деталей.")
        self.info_main_text.setWordWrap(True)
        self.info_main_text.setObjectName("InfoMainText")

        # СТАВИТЬ ПОЧАТКОВИЙ НАПИС ПО ЦЕНТРУ
        self.info_main_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Додаємо унікальну мітку стилю для початкового стану
        self.info_main_text.setProperty("state", "welcome")

        self.info_main_text.setTextFormat(Qt.TextFormat.RichText)

        # Оновлюємо стилі в реальному часі
       # self.info_main_text.style().unpolish(self.info_main_text)
       # self.info_main_text.style().polish(self.info_main_text)
       # self.info_main_text.setText(data.get("main_text", ""))

        right_info_layout.addWidget(self.info_main_text, 1)

        self.info_description = QLabel()
        self.info_description.setFont(QFont("Segoe UI", 18))
        self.info_description.setWordWrap(True)
        self.info_description.setObjectName("InfoDescription")
        self.info_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_info_layout.addWidget(self.info_description)

        # --- ДИНАМІЧНЕ ЗАВАНТАЖЕННЯ З JSON ---
        try:
            # ВИПРАВЛЕННЯ: Кажемо програмі дивитися в папку з файлом .exe, а не в Temp
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))

            json_path = os.path.join(base_dir, "structure_data.json")

            # Ініціалізуємо змінні заздалегідь на випадок помилки
            self.sidebar_data = {}
            self.info_buttons_list = []

            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)  # Змінено назву на json_data, щоб не плутати

                for item in json_data:
                    title_text = item.get("title", "Без назви")
                    main_text = item.get("main_text", "")
                    additional_info = item.get("additional_info") if item.get(
                        "additional_info") is not None else item.get("description", "")

                    btn = QPushButton(title_text)
                    btn.setCheckable(True)
                    btn.setObjectName("SidebarButton")

                    self.sidebar_data[title_text] = {
                        "main_text": main_text,
                        "additional_info": additional_info
                    }
                    btn.clicked.connect(self._safe_sidebar_click_handler)
                    self.left_buttons_layout.addWidget(btn)
                    self.info_buttons_list.append(btn)

        except Exception as e:
            # Якщо виникла помилка, виводимо її на екран, а замість тексту факультетів ставимо пусті рядки
            self.info_main_text.setText(f"Помилка завантаження файлу JSON: {e}")
            self.info_description.setText("")
            print(f"Помилка з JSON: {e}")

        return page

    def _safe_sidebar_click_handler(self):
        """Обробник кліку із динамічним вирівнюванням тексту."""
        clicked_btn = self.sender()
        if not clicked_btn:
            return

        clicked_btn.blockSignals(True)
        for btn in getattr(self, 'info_buttons_list', []):
            if btn != clicked_btn:
                btn.setChecked(False)
        clicked_btn.setChecked(True)
        clicked_btn.blockSignals(False)

        btn_text = clicked_btn.text()
        data = self.sidebar_data.get(btn_text, {})

        # КОЛИ ВИБРАНО ФАКУЛЬТЕТ: Змінюємо вирівнювання на ЛІВИЙ КРАЙ
        self.info_main_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Скидаємо початковий стан стилю, щоб увімкнувся стандартний вигляд тексту факультету
        self.info_main_text.setProperty("state", "normal")

        # Примусово кажемо QLabel розпізнавати HTML
        self.info_main_text.setTextFormat(Qt.TextFormat.RichText)

        # Оновлюємо стилі в реальному часі
        self.info_main_text.style().unpolish(self.info_main_text)
        self.info_main_text.style().polish(self.info_main_text)

        # Отримуємо чистий текст із JSON
        raw_text = data.get("main_text", "")

        # Створюємо глобальні стилі для HTML тексту всередині QLabel
        # Встановлюємо гарні інтервали списку та базовий шрифт
        html_css = """
                <style>
                    body { 
                        color: #FFFFFF; 
                        font-size: 18px; 
                        font-family: 'Segoe UI', Arial, sans-serif; 
                        
                    }
                    ul { 
                        font-size: 16px;
                        margin-top: 2px;   /* Відступ від верхнього тексту до початку списку */
                        margin-bottom: 2px;/* Відступ від кінця списку до наступного тексту */
                        margin-left: 20px;  /* Відступ списку зліва */
                        padding-left: 0px;
                    }
                    li { 
                        margin-bottom: 0px;  /* МІНІМАЛЬНИЙ ВІДСТУП МІЖ ПУНКТАМИ (зменшіть до 0px, якщо треба ще щільніше) */
                        margin-top: 0px;     /* Прибираємо верхній відступ кожного пункту */
                        line-height: 80%;   /* Компактний інтервал всередині самого пункту, якщо текст переноситься */
                    }
                </style>
                """

        # Об'єднуємо стилі з текстом та виводимо в один прийом
        self.info_main_text.setText(html_css + raw_text)

        # Для додаткового тексту також увімкнемо RichText про всяк випадок
        self.info_description.setTextFormat(Qt.TextFormat.RichText)
        self.info_description.setText(data.get("additional_info", ""))

    def on_info_button_clicked(self, main_text, desc_text, clicked_button):
        """Обробляє кліки по кнопках інформаційного розділу."""
        for btn in self.info_buttons:
            btn.setChecked(False)
        clicked_button.setChecked(True)

        self.info_main_text.setText(main_text)
        self.info_main_text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.info_description.setText(desc_text)

    def create_contacts_page(self):
        """Створює сучасну сторінку контактів, завантажуючи дані з JSON."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 1. Заголовок сторінки
        self.contacts_title = QLabel("📞 КОНТАКТИ УНІВЕРСИТЕТУ")
        self.contacts_title.setObjectName("ContactsTitle")
        layout.addWidget(self.contacts_title)

        # Контейнер для інформаційних блоків
        info_layout = QVBoxLayout()
        info_layout.setSpacing(25)

        self.lbl_admission = QLabel()
        self.lbl_email = QLabel()
        self.lbl_address = QLabel()

        # Значения по умолчанию на случай, если JSON пустой или отсутствует
        admission_default = "<b>Приймальна комісія:</b> +38 (094) 998-96-07, +38 (068) 031-39-92"
        email_default = "<b>Email:</b> vstupidgu@gmail.com, idgu@ukr.net"
        address_default = "<b>Адреса:</b> вул. Іллі Ріпина, 12"

        # --- ЗАВАНТАЖЕННЯ З JSON ---
        try:
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))

            json_path = os.path.join(base_dir, "data.json")

            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f).get("contacts", {})
                    self.contacts_title.setText(data.get("title", "📞 КОНТАКТИ УНІВЕРСИТЕТУ"))
                    self.lbl_admission.setText(data.get("admission_committee", admission_default))
                    self.lbl_email.setText(data.get("email", email_default))
                    self.lbl_address.setText(data.get("address", address_default))
            else:
                self.lbl_admission.setText(admission_default)
                self.lbl_email.setText(email_default)
                self.lbl_address.setText(address_default)
        except Exception as e:
            self.lbl_admission.setText(admission_default)
            self.lbl_email.setText(email_default)
            self.lbl_address.setText(address_default)

        # Налаштування стилів та розтягування плашок
        for lbl in [self.lbl_admission, self.lbl_email, self.lbl_address]:
            lbl.setWordWrap(True)
            lbl.setObjectName("ContactInfoLine")

            # ВИПРАВЛЕНО: QHBoxLayout теперь заставляет плашку растягиваться по горизонтали
            row = QHBoxLayout()
            row.addWidget(lbl, 1)  # Параметр 1 заставляет QLabel занимать всю ширину
            info_layout.addLayout(row)

        layout.addLayout(info_layout)
        return page

    def _create_contact_row(self, label_widget):
        """Допоміжний метод для створення рядка інформації."""
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row.addWidget(label_widget)
        return row


if __name__ == "__main__":
    import sys
    import os
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    try:
        # ПРАВИЛЬНЕ ВИЗНАЧЕННЯ ПАПКИ ДЛЯ .EXE ТА С КРИПТІВ:
        if getattr(sys, 'frozen', False):
            # Якщо програма запущена як зібраний .exe файл
            current_dir = os.path.dirname(sys.executable)
        else:
            # Якщо програма запущена як звичайний скрипт в PyCharm
            current_dir = os.path.dirname(os.path.abspath(__file__))

        qss_path = os.path.join(current_dir, "style.qss")
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"=== ПОМИЛКА ЗАВАНТАЖЕННЯ СТИЛІВ: {e} ===")

    kiosk = UniversityKiosk()

    # --- НОВИЙ НАДІЙНИЙ КОД: Підключаємо глобальний тач-фільтр ---
    touch_filter = GlobalTouchFilter(kiosk)
    app.installEventFilter(touch_filter)
    # -------------------------------------------------------------

    kiosk.show()
    sys.exit(app.exec())
