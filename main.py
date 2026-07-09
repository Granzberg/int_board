import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, QTime, QUrl
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
from datetime import datetime

import json

class UniversityKiosk(QWidget):
    def __init__(self):
        super().__init__()

        # Налаштування для IT Box: на весь екран, без рамок, поверх інших вікон
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.showMaximized()

        # За бажанням: блокуємо зміну розмірів вікна користувачем
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

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
        # ЗАМІНА СТИЛЮ НА ІМ'Я ОБ'ЄКТА:
        self.time_label.setObjectName("ClockTime")

        self.date_label = QLabel(self)
        self.date_label.setFont(QFont("Open Sans", 16))
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # ЗАМІНА СТИЛЮ НА ІМ'Я ОБ'ЄКТА:
        self.date_label.setObjectName("ClockDate")

        # Додаємо годинник та дату на самий верх лівого меню
        left_menu.addWidget(self.time_label)
        left_menu.addWidget(self.date_label)

        # Створюємо таймер для оновлення часу щосекунди
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)

        self.update_clock()

        # Створюємо великі тач-кнопки (вони автоматично беруть стиль QPushButton з QSS)
        self.btn_home = QPushButton("🏠 Головна", self)
        self.btn_schedule = QPushButton("📅 Розклад занять", self)
        self.btn_map = QPushButton("🗺️ Карта корпусів", self)
        self.btn_university_structure = QPushButton("🏛️ Структура унівeрситету", self)
        self.btn_contacts = QPushButton("📞 Контакти", self)

        # Кнопка виходу (Тимчасова! Щоб ви могли закрити програму під час тестів)
        self.btn_exit = QPushButton("❌ Вихід (Тест)", self)
        # ЗАМІНА СТИЛЮ НА ІМ'Я ОБ'ЄКТА:
        self.btn_exit.setObjectName("ExitTestButton")

        # Додаємо кнопки в ліве меню
        left_menu.addWidget(self.btn_home)
        left_menu.addWidget(self.btn_university_structure)
        left_menu.addWidget(self.btn_map)
        left_menu.addWidget(self.btn_schedule)
        left_menu.addWidget(self.btn_contacts)
        left_menu.addStretch()
        left_menu.addWidget(self.btn_exit)

        # ---------------- ПРАВА ПАНЕЛЬ (СТОРІНКИ) ----------------
        # QStackedWidget — це "стопка" сторінок. Показується тільки одна.
        self.pages_container = QStackedWidget(self)
        self.pages_container.setStyleSheet("background-color: #1F2937; border-radius: 20px; padding: 40px;")

        # Створюємо сторінки
        self.page_home = self.create_home_page()
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
        """Створює головну сторінку з логотипом університету, великим заголовком та підказкою."""
        page = QWidget()

        # Головний макет сторінки — ГОРИЗОНТАЛЬНИЙ (щоб затиснути вміст по центру)
        main_horizontal_layout = QHBoxLayout(page)

        # Створюємо внутрішній ВЕРТИКАЛЬНИЙ контейнер для елементів
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(25)  # Відступ між логотипом і текстами

        # 1. ЕЛЕМЕНТ ДЛЯ ВІДОБРАЖЕННЯ ЛОГОТИПУ
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap("logo.png")

        if not pixmap.isNull():
            scaled_logo = pixmap.scaled(
                350, 350,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(scaled_logo)
        else:
            logo_label.setText("[ Логотип університету не знайдено ]")
            logo_label.setObjectName("LogoErrorLabel")

        # 2. ГОЛОВНИЙ ВІТАЛЬНИЙ ЗАГОЛОВОК
        welcome_title = QLabel("Вітаємо в Ізмаїльському Державному Гуманітарному Університеті!")
        welcome_title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))  # 28 розмір ідеально збалансований
        welcome_title.setWordWrap(True)
        welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_title.setObjectName("WelcomeTitle")
        welcome_title.setMaximumWidth(750)  # Фіксуємо максимальну ширину тексту

        # 3. ІНСТРУКЦІЯ ДЛЯ СТУДЕНТА
        welcome_hint = QLabel("Оберіть потрібний розділ меню ліворуч, щоб отримати інформацію.")
        welcome_hint.setFont(QFont("Segoe UI", 20))
        welcome_hint.setWordWrap(True)
        welcome_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_hint.setObjectName("WelcomeHint")
        welcome_hint.setMaximumWidth(750)  # Фіксуємо максимальну ширину тексту

        # Додаємо всі елементи у вертикальний контейнер
        layout.addWidget(logo_label)
        layout.addWidget(welcome_title)
        layout.addWidget(welcome_hint)

        # МАГІЯ ВИРІВНЮВАННЯ: затискаємо content_widget пружинами зліва, справа, зверху та знизу
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_horizontal_layout.addStretch(1)  # Ліва пружина
        main_horizontal_layout.addWidget(content_widget)  # Сам блок із логотипом та текстом
        main_horizontal_layout.addStretch(1)  # Права пружина

        return page

    def keyPressEvent(self, event):
        """Дозволяє закрити повноекранний режим кнопкою Esc на клавіатурі"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def mousePressEvent(self, event):
        """Викликається автоматично при кожному кліку/тачу по екрану кіоску."""
        super().mousePressEvent(event)
        # Якщо користувач активний — перезапускаємо таймер заново з позначки 90 сек
        self.inactivity_timer.start()

    def return_to_home(self):
        """Спрацьовує, коли таймер добігає кінця."""
        # Перевіряємо, чи кіоск зараз НЕ на головній сторінці (індекс 0)
        if self.pages_container.currentIndex() != 0:
            self.pages_container.setCurrentIndex(0) # Скидаємо сторінку на головну
            print("⏳ Екран кіоску автоматично скинуто на головну сторінку.")

    def create_interactive_map_page(self):
        """Створює сторінку інтерактивної мапи з кнопками перемикання поверхів."""
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("🗺 ПЛАН НАВЧАЛЬНОГО КОРПУСУ")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        # ЗАМІНА СТИЛЮ НА ІМ'Я ОБ'ЄКТА:
        title.setObjectName("MapTitle")
        layout.addWidget(title)

        # Контейнер для кнопок поверхів (горизонтальний)
        floor_buttons_layout = QHBoxLayout()
        floor_buttons_layout.setSpacing(15)
        layout.addLayout(floor_buttons_layout)

        # Елемент для відображення карти
        self.map_image_label = QLabel()
        self.map_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # ЗАМІНА СТИЛЮ НА ІМ'Я ОБ'ЄКТА:
        self.map_image_label.setObjectName("MapImageContainer")

        layout.addWidget(self.map_image_label, 1)

        # Опис поверху нижче мапи
        self.map_description = QLabel()
        self.map_description.setFont(QFont("Segoe UI", 18))
        self.map_description.setWordWrap(True)
        # ЗАМІНА СТИЛЮ НА ІМ'Я ОБ'ЄКТА:
        self.map_description.setObjectName("MapDescription")
        layout.addWidget(self.map_description)

        floors_data = [
            (1, "floor1.png", "1 ПОВЕРХ: Приймальна комісія, Гардероб, Медпункт.", "1 Поверх"),
            (2, "floor22.png", "2 ПОВЕРХ: Адміністрація, Кафедра вищої математики.", "2 Поверх"),
            (3, "floor32.png", "3 ПОВЕРХ: Деканат, Аудиторії лекційні (301-305).", "3 Поверх"),
            (4, "floor42.png", "4 ПОВЕРХ: Аудиторії лекційні (401-405), Кафедри.", "4 Поверх"),
            (5, "floor52.png", "5 ПОВЕРХ: Читальний зал, Комп'ютерні класи (501-505).", "5 Поверх"),
            (6, "floor1_it2.png", "КОРПУС ЦНІТ: Центр новітніх інформаційних технологій.", "1 Поверх, ЦНІТ"),
            (7, "floor2_sport2.png", "СПОРТИВНИЙ КОМПЛЕКС: Спортивний зал, роздягальні.", "2 Поверх, Спортзал")
        ]
        self.floor_buttons = []

        # ЦИКЛ СТВОРЕННЯ КНОПОК ПОВЕРХІВ
        for index, main_txt, desc_txt, btn_title in floors_data:
            btn = QPushButton(btn_title)

            # ПРИСВОЮЄМО ІМ'Я ОБ'ЄКТА ДЛЯ ПРИВ'ЯЗКИ СТИЛЮ З QSS:
            btn.setObjectName("FloorButton")

            btn.setCheckable(True)
            btn.clicked.connect(
                lambda checked, mt=main_txt, dt=desc_txt, b=btn: self.on_info_button_clicked(mt, dt, b)
            )
            floor_buttons_layout.addWidget(btn)
            self.floor_buttons.append(btn)

        # Ініціалізуємо карту першим поверхом при старті
        self.show_floor(1, "floor1.png", "1 ПОВЕРХ: Приймальна комісія, Гардероб, Медпункт.")

        return page

    def show_floor(self, floor_num, img_path, description_text):
        """Оновлює стан кнопок мапи, завантажує та відображає картинку поверху."""
        # Керуємо станом виділення кнопок поверхів
        for index, btn in enumerate(self.floor_buttons):
            btn.setChecked((index + 1) == floor_num)

        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                800, 550,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.map_image_label.setPixmap(scaled_pixmap)
        else:
            self.map_image_label.setText(f"[ Картинку {img_path} не знайдено ]")

        self.map_description.setText(description_text)

        # === НОВИЙ КОД: Скидаємо таймер бездіяльності при зміні поверху ===
        if hasattr(self, 'inactivity_timer'):
            self.inactivity_timer.start()

    def create_info_sidebar_page(self):
        """Створює сторінку інформації з бічним меню."""
        page = QWidget()
        main_layout = QVBoxLayout(page)

        # 1. ЗАГОЛОВОК СТОРІНКИ
        title = QLabel("🏛 ІНФОРМАЦІЯ ПО СТРУКТУРІ УНІВЕРСИТЕТУ")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setObjectName("StructureTitle")  # Стиль з style.qss
        main_layout.addWidget(title)

        # 2. ГОЛОВНИЙ ГОРИЗОНТАЛЬНИЙ КОНТЕЙНЕР (розділяє ліво і право)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        main_layout.addLayout(content_layout)

        # --- ЛІВА ПАНЕЛЬ (КНОПКИ) ---
        self.left_buttons_layout = QVBoxLayout()  # Робимо self, щоб цикл заповнення кнопок міг його знайти
        self.left_buttons_layout.setSpacing(15)
        self.left_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_layout.addLayout(self.left_buttons_layout)  # ТУТ ВИПРАВЛЕНО: додаємо в content_layout!

        # --- ПРАВА ПАНЕЛЬ (ІНФОРМАЦІЯ) ---
        right_info_layout = QVBoxLayout()
        right_info_layout.setSpacing(15)
        content_layout.addLayout(right_info_layout, 1)

        # Спочатку СТВОРЮЄМО об'єкти, а потім додаємо їх у макет
        self.info_main_text = QLabel("Оберіть розділ зліва для перегляду деталей.")
        self.info_main_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_main_text.setWordWrap(True)
        self.info_main_text.setFont(QFont("Segoe UI", 20))
        self.info_main_text.setObjectName("InfoMainText")  # Стиль з style.qss
        right_info_layout.addWidget(self.info_main_text, 1)

        self.info_description = QLabel()
        self.info_description.setFont(QFont("Segoe UI", 18))
        self.info_description.setWordWrap(True)
        self.info_description.setObjectName("InfoDescription")  # Стиль з style.qss
        right_info_layout.addWidget(self.info_description)


        info_sections_data = [
            (1, "Педагогічний факультет ІДГУ готує фахівців дошкільної, початкової, спеціальної та мистецької освіти.\n"
                "Розташований в головному корпусі за адресою: вул. Рєпіна, 12, м. Ізмаїл, Одеська обл.\nСтруктура факультету:\n"
                "Навчальний процес забезпечують 4 випускові кафедри\n"
                "Кафедра дошкільної та початкової освіти\n"
                "Кафедра загальної педагогіки і спеціальної освіти\n"
                "Кафедра фізичного виховання, спорту та здоров'я людини\n"
                "Кафедра музичного та образотворчого\n\n"
                "Приймальна комісія (телефон): (068) 031-39-92, (094) 998-96-07\n"
                "Електронна пошта для довідок: idgu@ukr.net\n"
                "Офіційний сайт: https://idgu.edu.ua/",
             "Додатково: корпус №1, каб. 104.", "Педагогічний факультет ІДГУ"),
            (2, "Факультет української та іноземної філології (ФУІФ) Ізмаїльського державного гуманітарного університету "
                "готує фахівців за спеціальністю «Філологія». Декан факультету — доцент Татаринов Іван Євгенович.\n"
                "Освітній процес забезпечують профільні кафедри. Основні освітні програми та спеціальності (Бакалавр) "
                "«Філологія (Українська мова і література та англійська мова, переклад включно)»\n"
                "«Філологія (Німецька і англійська мови та літератури, переклад включно)»\n"
                "«Середня освіта (Англійська мова та зарубіжна література)»\n\n"
                "Електронна пошта: fim_idgu@ukr.net\n"
                "Офіційний портал: https://idgu.edu.ua/faculties/fim",
             "Додатково: ауд. 305.", "Факультет української та іноземної філології (ФУІФ)"),
            (3, "На факультеті здійснюється підготовка за рівнями «бакалавр» та «магістр».\n"
                "До структури ФУАІД входять: "
                "Кафедра технологічної освіти та природничих наук\n"
                "Кафедра управління підприємницькою та туристичною діяльністю\n"
                "Кафедра математики, інформатики та інформаційної діяльності\n"
                "Кафедра  історії та методики її навчання\n"
                "Кафедра загальної та практичної психології\n"
                "Кафедра права і соціальної роботи\n\n"
                "Телефон: (04841) 5-32-42.\n"
                "Електронна пошта: labfuaid@gmail.com (технічна підтримка факультету).\n"
                "Сайт факультету: https://fei.idgu.edu.ua/.\n"
                "Telegram-канал деканату: @dekanat_fuaid.\n"
                "Facebook-сторінка: Сторінка live.fuaid.\n"
                "Instagram: @fuaid_live.",
             "Додатково: ауд. 312.", "ФУАІД ІДГУ"),
            (4, "Центр неперервної освіти (ЦНО) ІДГУ здійснює довузівську підготовку, курси підвищення кваліфікації педагогів та надає додаткові платні освітні послуги.\n"
                "Основні напрямки діяльності ЦНО:\n"
                "Довузівська підготовка: навчання громадян України та іноземців для вступу до закладів вищої освіти.\n"
                "Підвищення кваліфікації: спеціальні курси для педагогічних працівників за затвердженим планом-графіком.\n"
                "Додаткові послуги: платні навчальні курси понад обсяги основних освітніх програм.\n\n"
                "Контакти та графік роботи:\n"
                "Телефон: +38 (096) 556-08-83 (дзвінки приймають з 9:30 до 16:00 у робочі дні)\n"
                "Електронна пошта: rioidgu@ukr.net\n"
                "Офіційний вебсайт: cno.idgu.edu.ua\n",
             "Додатково: ауд. 305", "Центр неперервної освіти (ЦНО) ІДГУ"),
            (5, "Одним із найважливіших підрозділів ІДГУ, зорієнтованим на підтримку освітнього та "
                "науково-дослідницького процесу, є бібліотека з багатим зібранням вітчизняної і зарубіжної наукової, навчальної та художньої літератури.",
            "Додатково: ауд. 117", "Бібліотека"),
            (6, " Бухгалтерія опікується фінансовими питаннями вишу, зокрема нарахуванням заробітних плат працівникам та стипендій студентам.\n"
                "Публічна інформація: Детальну інформацію щодо фінансової звітності,"
                " кошторисів та річних планів закупівель університету можна переглянути на сторінці Публічна інформація ІДГУ.\n\n"
                "Адреса: вул. Іллі Рєпіна, 12, м. Ізмаїл, Одеська область, 68610.\n"
                "Email: idgu@ukr.net (загальний для університету).\n"
                "Офіційний сайт: https://idgu.edu.ua/",
             "Аудиторії: 106-109 (1 поверх)", "Бухгалтерія ІДГУ"),
            (7, "Відділ кадрів Ізмаїльського державного гуманітарного університету (ІДГУ)\n"
                "кадрове забезпечення діяльності університету;\n"
                "ведення кадрового діловодства;\n"
                "оформлення прийняття, переведення та звільнення працівників;\n"
                "ведення особових справ працівників;\n"
                "оформлення трудових книжок та електронних кадрових документів;\n"
                "підготовка наказів з кадрових питань;\n"
                "контроль за дотриманням трудового законодавства;\n"
                "ведення обліку кадрів і підготовка статистичної звітності;\n"
                "організація роботи з підвищення кваліфікації та атестації працівників;\n"
                "оформлення документів щодо відпусток, стажу роботи, пенсійного забезпечення та інших кадрових процедур.\n"
                "Для зв'язку з відділом кадрів використовуються загальні контакти університету:\n"
                "електронна пошта: idgu@ukr.net.",
             "Додатково: ауд. 208", "Відділ кадрів (ІДГУ)")
        ]

        self.info_buttons = []

        # Знайдіть цей цикл у методі create_info_sidebar_page:
        for index, main_txt, desc_txt, btn_title in info_sections_data:
            btn = QPushButton(btn_title)

            # ПРИСВОЮЄМО ІМ'Я ОБ'ЄКТА ДЛЯ ПРИВ'ЯЗКИ СТИЛЮ З QSS:
            btn.setObjectName("SidebarButton")

            btn.setCheckable(True)
            btn.clicked.connect(
                lambda checked, mt=main_txt, dt=desc_txt, b=btn: self.on_info_button_clicked(mt, dt, b)
            )
            self.left_buttons_layout.addWidget(btn)
            self.info_buttons.append(btn)

        return page

    def on_info_button_clicked(self, main_text, desc_text, clicked_button):
        """Обробляє кліки по кнопках інформаційного розділу."""
        for btn in self.info_buttons:
            btn.setChecked(False)
        clicked_button.setChecked(True)

        self.info_main_text.setText(main_text)
        self.info_main_text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.info_description.setText(desc_text)


if __name__ == "__main__":
    import sys
    import os
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # АВТОМАТИЧНЕ ТА НАДІЙНЕ ЗЧИТУВАННЯ QSS
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        qss_path = os.path.join(current_dir, "style.qss")

        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
            print("=== СТИЛІ СУКЦЕСИВНО ЗАВАНТАЖЕНО З STYLE.QSS ===")
    except Exception as e:
        print(f"=== ПОМИЛКА ЗАВАНТАЖЕННЯ СТИЛІВ: {e} ===")

    kiosk = UniversityKiosk()
    kiosk.show()
    sys.exit(app.exec())
