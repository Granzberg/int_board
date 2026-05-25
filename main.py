## python
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, QTime
from PyQt6.QtGui import QPixmap, QFont
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
                font-family: 'Segoe UI', Arial, sans-serif;
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
        self.time_label.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("color: #3B82F6; margin-bottom: 0px;")

        self.date_label = QLabel(self)
        self.date_label.setFont(QFont("Segoe UI", 16))
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
        self.btn_news = QPushButton("Новини", self)
        self.btn_contacts = QPushButton("📞 Контакти", self)

        # Кнопка виходу (Тимчасова! Щоб ви могли закрити програму під час тестів)
        self.btn_exit = QPushButton("❌ Вихід (Тест)", self)
        self.btn_exit.setStyleSheet("background-color: #991B1B; border: none;")

        # Додаємо кнопки в ліве меню
        left_menu.addWidget(self.btn_home)
        left_menu.addWidget(self.btn_schedule)
        left_menu.addWidget(self.btn_map)
        left_menu.addWidget(self.btn_news)
        left_menu.addWidget(self.btn_contacts)
        left_menu.addStretch()  # Штовхає кнопку виходу до самого низу
        left_menu.addWidget(self.btn_exit)



        # ---------------- ПРАВА ПАНЕЛЬ (СТОРІНКИ) ----------------
        # QStackedWidget — це "стопка" сторінок. Показується тільки одна.
        self.pages_container = QStackedWidget(self)
        self.pages_container.setStyleSheet("background-color: #1F2937; border-radius: 20px; padding: 40px;")

        # Створюємо сторінки
        self.page_home = self.create_page_content(
            "Вітаємо в Ізмаїлький Державни Гуманітарний Університет!\n\nОберіть потрібний розділ меню ліворуч, щоб отримати інформацію.\n\nСьогодні: 22 травня 2026 року.")
        self.page_schedule = self.create_page_content(
            "Розклад занять:\n\n1 пара: 08:30 - 10:05\n2 пара: 10:20 - 11:55\n3 пара: 12:10 - 13:45\n\nДля перегляду груп підійдіть до деканату.")
        self.page_map = self.create_interactive_map_page()

        self.page_contacts = self.create_page_content(
            "Контакти університету:\n\n📞 Приймальна комісія: +38 (044) 123-45-67\n📧 Email: info@university.edu.ua\n📍 Адреса: вул. Університетська, 1")

        # Додаємо сторінки в наш контейнер (вони отримують індекси 0, 1, 2, 3)
        self.pages_container.addWidget(self.page_home)  # Індекс 0
        self.pages_container.addWidget(self.page_schedule)  # Індекс 1
        self.pages_container.addWidget(self.page_map)  # Індекс 2
        self.pages_container.addWidget(self.page_contacts)  # Індекс 3

        # ---------------- ЗБИРАЄМО ВСЕ РАЗОМ ----------------
        # Пропорція 1 до 3: ліва панель займає менше місця, права — більше
        main_layout.addLayout(left_menu, 1)
        main_layout.addWidget(self.pages_container, 3)

        # ---------------- ЛОГІКА НА КЛІКИ (ТАЧІ) ----------------
        # Прив'язуємо кнопки до перемикання сторінок за індексами
        self.btn_home.clicked.connect(lambda: self.pages_container.setCurrentIndex(0))
        self.btn_schedule.clicked.connect(lambda: self.pages_container.setCurrentIndex(1))
        self.btn_map.clicked.connect(lambda: self.pages_container.setCurrentIndex(2))
        self.btn_contacts.clicked.connect(lambda: self.pages_container.setCurrentIndex(3))
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
