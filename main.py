## python
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PyQt6.QtCore import Qt, QTimer, QTime
from PyQt6.QtGui import QPixmap, QFont
from datetime import datetime

class UniversityKiosk(QWidget):
    def __init__(self):
        super().__init__()

        # Налаштування для IT Box: на весь екран, без рамок, поверх інших вікон
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.showFullScreen()

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
            "Вітаємо в Ізмаїлькому Державному Гумонітарному Університеті!\n\nОберіть потрібний розділ меню ліворуч, щоб отримати інформацію.\n\nСьогодні: 22 травня 2026 року.")
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

    def create_interactive_map_page(self):
        """Створює сучасну сторінку з планом єдиного корпусу"""
        page = QWidget()
        layout = QVBoxLayout(page)

        # Заголовок сторінки
        title = QLabel("ПЛАН НАВЧАЛЬНОГО КОРПУСУ")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet("color: #3B82F6; margin-bottom: 20px;")
        layout.addWidget(title)

        # Горизонтальний ряд великих кнопок для вибору поверху
        floor_buttons_layout = QHBoxLayout()
        floor_buttons_layout.setSpacing(15)

        btn_floor1 = QPushButton("1 Поверх")
        btn_floor2 = QPushButton("2 Поверх")
        btn_floor3 = QPushButton("3 Поверх")
        btn_floor4 = QPushButton("4 Поверх")
        btn_floor5 = QPushButton("5 Поверх")
        btn_floor6 = QPushButton("1 Поверх, ЦНІТ")
        btn_floor7 = QPushButton("2 Поверх, Спортзал")

        # Робимо кнопки поверхів трохи іншого стилю, щоб вони виділялися
        floor_btn_style = """
               QPushButton {
                   background-color: #374151;
                   border: 2px solid #4B5563;
                   border-radius: 10px;
                   padding: 15px;
                   font-size: 20px;
               }
               QPushButton:checked {
                   background-color: #3B82F6; /* Колір вибраного поверху */
                   border-color: #60A5FA;
               }
           """
        for btn in [btn_floor1, btn_floor2, btn_floor3, btn_floor4, btn_floor5, btn_floor6, btn_floor7]:
            btn.setStyleSheet(floor_btn_style)
            btn.setCheckable(True)  # Кнопка може залишатися натиснутою
            floor_buttons_layout.addWidget(btn)

        layout.addLayout(floor_buttons_layout)

        # Зона, де буде показуватися картинка плану поверху
        self.map_image_label = QLabel()
        self.map_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_image_label.setStyleSheet(
            "background-color: #111827; border: 2px dashed #374151; border-radius: 15px; margin-top: 20px;")
        layout.addWidget(self.map_image_label, 1)  # Цифра 1 змушує картинку займати весь вільний простір

        # Текстовий опис під картою
        self.map_description = QLabel("Оберіть поверх вище, щоб побачити схему аудиторій.")
        self.map_description.setFont(QFont("Segoe UI", 18))
        self.map_description.setWordWrap(True)
        self.map_description.setStyleSheet("color: #9CA3AF; margin-top: 15px;")
        layout.addWidget(self.map_description)

        # Логіка перемикання карти при натисканні (Тачі)
        def show_floor(floor_num, img_path, description_text):
            # Скидаємо виділення з усіх кнопок і виділяємо потрібну
            btn_floor1.setChecked(floor_num == 1)
            btn_floor2.setChecked(floor_num == 2)
            btn_floor3.setChecked(floor_num == 3)
            btn_floor4.setChecked(floor_num == 4)
            btn_floor5.setChecked(floor_num == 5)
            btn_floor6.setChecked(floor_num == 6)
            btn_floor7.setChecked(floor_num == 7)

            # Завантажуємо та масштабуємо картинку під розмір екрана
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                # Автоматично підганяє розмір картинки, зберігаючи пропорції
                scaled_pixmap = pixmap.scaled(800, 500, Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                self.map_image_label.setPixmap(scaled_pixmap)
            else:
                self.map_image_label.setText(f"[ Картинку {img_path} не знайдено в папці з програмою ]")
                self.map_image_label.setFont(QFont("Segoe UI", 20))

            self.map_description.setText(description_text)

        # Прив'язуємо функції до кнопок
        btn_floor1.clicked.connect(lambda: show_floor(1, "floor1.jpg", "1 ПОВЕРХ: Приймальна комісія,  Гардероб, Медпункт."))
        btn_floor2.clicked.connect(lambda: show_floor(2, "floor2.jpg",
                                                      "2 ПОВЕРХ: Адмністрація, Кафедра вищої математики."))
        btn_floor3.clicked.connect(lambda: show_floor(3, "floor3.jpg",
                                                      "3 ПОВЕРХ: Деканат ,Аудиторії лекційні (301-305)."))
        btn_floor4.clicked.connect(lambda: show_floor(4, "floor4.jpg",
                                                      "3 ПОВЕРХ: Деканат ,Аудиторії лекційні (401-405)."))
        btn_floor5.clicked.connect(lambda: show_floor(5, "floor5.jpg",
                                                      "3 ПОВЕРХ: Деканат ,Аудиторії лекційні (501-505)."))
        btn_floor6.clicked.connect(lambda: show_floor(6, "floor1_it.jpg",
                                                      "3 ПОВЕРХ: ЦНІТ."))
        btn_floor7.clicked.connect(lambda: show_floor(7, "floor2_sport.jpg",
                                                      "3 ПОВЕРХ: Спортивний зал."))

        # Показуємо перший поверх за замовчуванням
        show_floor(1, "floor1.jpg", "1 ПОВЕРХ: Приймальна комісія,  Гардероб, Медпункт.")

        return page


if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiosk = UniversityKiosk()
    kiosk.show()
    sys.exit(app.exec())
