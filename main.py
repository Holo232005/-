import sys
import psycopg2
import hashlib
from PySide6.QtCore import QDate, Qt, QSize  # Добавлены Qt и QSize
from PySide6.QtGui import QIcon  # QIcon импортируется отсюда
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, \
    QTableWidget, QTableWidgetItem, QComboBox, QHBoxLayout, QTabWidget, QWidget, QFormLayout, QDateEdit

# Настройки подключения к БД
DB_CONFIG = {
    "host": "localhost",
    "dbname": "sportschool",
    "user": "sportschool",
    "password": "1234"
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход в систему")
        self.setGeometry(200, 200, 400, 300)
        self.setWindowIcon(QIcon('icon.png'))  # Иконка приложения

        # Стили CSS
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton {
                padding: 10px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.label_title = QLabel("Авторизация")
        self.label_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.label_title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label_title)

        self.label_login = QLabel("Логин")
        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText("Введите логин")
        self.layout.addWidget(self.label_login)
        self.layout.addWidget(self.input_login)

        self.label_password = QLabel("Пароль")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText("Введите пароль")
        self.layout.addWidget(self.label_password)
        self.layout.addWidget(self.input_password)

        self.btn_login = QPushButton("Войти")
        self.btn_login.setIcon(QIcon.fromTheme("system-lock-screen"))
        self.btn_login.setIconSize(QSize(24, 24))
        self.btn_login.clicked.connect(self.authenticate)
        self.layout.addWidget(self.btn_login)

        self.setLayout(self.layout)

    def authenticate(self):
        login = self.input_login.text()
        password = self.input_password.text()
        hashed_password = hash_password(password)

        try:
            connection = psycopg2.connect(**DB_CONFIG)
            cursor = connection.cursor()

            query = "SELECT id, role, password_hash FROM users WHERE username = %s AND password_hash = %s"
            cursor.execute(query, (login, hashed_password))
            result = cursor.fetchone()

            if result:
                id, role, _ = result
                QMessageBox.information(self, "Успех", f"Вход выполнен как {role}")
                self.open_dashboard(role, id)
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            print(f"Ошибка: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    def open_dashboard(self, role, id):
        if role == "administration":
            self.admin_window = AdminWindow()
            self.admin_window.show()
        elif role == "coacher":
            self.coach_window = CoachWindow(id)  # Передаем ID пользователя
            self.coach_window.show()
        elif role == "student":
            self.student_window = StudentWindow()
            self.student_window.show()

#УПРАВЛЕНИЕ АДМИНОМ
class AdminWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Административная панель")
        self.setGeometry(100, 100, 1024, 768)
        self.setWindowIcon(QIcon('admin_icon.png'))
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ccc;
                background: white;
            }
            QTabBar::tab {
                background: #eaeaea;
                padding: 10px;
                border: 1px solid #ccc;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #007bff;
                color: white;
            }
            QTableWidget {
                gridline-color: #ccc;
                alternate-background-color: #f9f9f9;
            }
        """)
        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Toolbar с кнопками
        toolbar = QHBoxLayout()
        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.setIcon(QIcon.fromTheme("view-refresh"))
        self.btn_refresh.setStyleSheet("padding: 8px;")
        self.btn_logout = QPushButton("Выход")
        self.btn_logout.setIcon(QIcon.fromTheme("system-log-out"))
        self.btn_logout.setStyleSheet("padding: 8px;")

        # Подключаем кнопки к методам
        self.btn_refresh.clicked.connect(self.refresh_data)  # Обновление данных
        self.btn_logout.clicked.connect(self.logout)  # Выход из системы

        toolbar.addWidget(self.btn_refresh)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_logout)
        self.layout.addLayout(toolbar)
        self.setLayout(self.layout)

        self.load_tables()

    def logout(self):
        """Метод для выхода из системы"""
        self.close()  # Закрываем текущее окно
        self.login_window = LoginWindow()
        self.login_window.show()

    def refresh_data(self):
        """Метод для обновления данных во всех вкладках"""
        try:
            # Перезагружаем данные во всех вкладках
            self.load_tables()
            QMessageBox.information(self, "Обновление", "Данные успешно обновлены!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении данных: {str(e)}")

    def load_tables(self):
        try:
            # Сохраняем текущую активную вкладку
            current_index = self.tabs.currentIndex()
            current_tab_text = self.tabs.tabText(current_index) if current_index != -1 else None

            # Удаляем все существующие вкладки, кроме первой
            while self.tabs.count() > 1:
                self.tabs.removeTab(1)

            # Словарь переводов
            table_translations = {
                "users": "Пользователи",
                "students": "Студенты",
                "coaches": "Тренеры",
                "schedule": "Расписание",
                "inventory_movements": "Движение инвентаря",
                "competitions": "Соревнования"
            }

            connection = psycopg2.connect(**DB_CONFIG)
            cursor = connection.cursor()
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]
                # Используем перевод, если он есть, иначе оригинальное название
                tab_name = table_translations.get(table_name, table_name)
                self.add_table_tab(table_name, tab_name)

            # Восстанавливаем активную вкладку
            if current_tab_text:
                for i in range(self.tabs.count()):
                    if self.tabs.tabText(i) == current_tab_text:
                        self.tabs.setCurrentIndex(i)
                        break

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    def add_table_tab(self, table_name, display_name):
        # Проверяем, существует ли уже вкладка с таким именем
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == display_name:
                # Если вкладка уже существует, просто обновляем данные
                current_tab = self.tabs.widget(i)
                table_view = current_tab.findChild(QTableWidget)
                if table_view:
                    self.load_table_data(table_name, table_view)
                return

        # Если вкладки нет, создаем новую
        table_widget = QWidget()
        layout = QVBoxLayout()
        table_view = QTableWidget()
        layout.addWidget(table_view)

        btn_add = QPushButton("Добавить запись")
        btn_edit = QPushButton("Редактировать запись")
        btn_delete = QPushButton("Удалить запись")

        btn_add.clicked.connect(lambda: self.add_record(table_name))
        btn_edit.clicked.connect(lambda: self.edit_record(table_name, table_view))
        btn_delete.clicked.connect(lambda: self.delete_record(table_name, table_view))

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_delete)
        layout.addLayout(btn_layout)

        self.load_table_data(table_name, table_view)
        table_widget.setLayout(layout)

        # Используем display_name для заголовка вкладки
        self.tabs.addTab(table_widget, display_name)

    def load_table_data(self, table_name, table_view):
        try:
            connection = psycopg2.connect(**DB_CONFIG)
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            colnames = [desc[0] for desc in cursor.description]

            # Очищаем таблицу перед загрузкой новых данных
            table_view.clearContents()
            table_view.setRowCount(0)

            table_view.setColumnCount(len(colnames))
            table_view.setHorizontalHeaderLabels(colnames)
            for row, record in enumerate(data):
                table_view.insertRow(row)
                for col, value in enumerate(record):
                    table_view.setItem(row, col, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cursor.close()
            connection.close()

    def add_record(self, table_name):
        try:
            connection = psycopg2.connect(**DB_CONFIG)
            cursor = connection.cursor()

            # Получаем список столбцов, исключая автоинкрементные
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s 
                AND (column_default IS NULL OR column_name NOT IN ('id'))
                ORDER BY ordinal_position
            """, (table_name,))
            columns = [col[0] for col in cursor.fetchall()]

            # Для inventory_movements получаем связанные данные
            if table_name == "inventory_movements":
                cursor.execute("SELECT id, name FROM inventory")
                inventory_items = cursor.fetchall()

                cursor.execute("SELECT id, full_name FROM students")
                students = cursor.fetchall()

                cursor.execute("SELECT id, full_name FROM coaches")
                coaches = cursor.fetchall()

            # Создаем диалог
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Добавить запись в {table_name}")
            layout = QFormLayout()
            inputs = {}

            for column in columns:
                if column == "movement_type":
                    combo = QComboBox()
                    combo.addItems(["issued", "returned", "transferred"])
                    inputs[column] = combo
                    layout.addRow(column, combo)

                elif column == "inventory_id":
                    combo = QComboBox()
                    for item_id, name in inventory_items:
                        combo.addItem(f"{name} (ID: {item_id})", item_id)
                    inputs[column] = combo
                    layout.addRow(column, combo)

                elif column == "student_id":
                    combo = QComboBox()
                    combo.addItem("Не выбрано", None)
                    for student_id, name in students:
                        combo.addItem(f"{name} (ID: {student_id})", student_id)
                    inputs[column] = combo
                    layout.addRow(column, combo)

                elif column == "coach_id":
                    combo = QComboBox()
                    combo.addItem("Не выбрано", None)
                    for coach_id, name in coaches:
                        combo.addItem(f"{name} (ID: {coach_id})", coach_id)
                    inputs[column] = combo
                    layout.addRow(column, combo)

                elif column.endswith("_date"):
                    date_edit = QDateEdit(calendarPopup=True)
                    date_edit.setDate(QDate.currentDate())
                    inputs[column] = date_edit
                    layout.addRow(column, date_edit)

                else:
                    line_edit = QLineEdit()
                    inputs[column] = line_edit
                    layout.addRow(column, line_edit)

            btn_save = QPushButton("Сохранить")
            btn_save.clicked.connect(lambda: self.save_record(table_name, inputs, dialog))
            layout.addWidget(btn_save)

            dialog.setLayout(layout)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    def save_record(self, table_name, inputs, dialog):
        try:
            connection = psycopg2.connect(**DB_CONFIG)
            cursor = connection.cursor()
            columns = []
            values = []
            for column, widget in inputs.items():
                if isinstance(widget, QLineEdit):
                    value = widget.text()
                elif isinstance(widget, QDateEdit):
                    value = widget.date().toString("yyyy-MM-dd")
                elif isinstance(widget, QComboBox):
                    value = widget.currentData()  # Для ComboBox с userData
                    if value is None:  # Если нет userData, берем текст
                        value = widget.currentText()
                # Пропускаем пустые значения для необязательных полей
                if value or column in ['student_id', 'coach_id', 'inventory_id', 'movement_type']:
                    columns.append(column)
                    values.append(value)
            # Формируем SQL-запрос
            placeholders = ["%s"] * len(values)
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(query, values)
            connection.commit()
            QMessageBox.information(dialog, "Успех", "Запись успешно добавлена!")
            dialog.close()
            # Обновляем только текущую таблицу
            current_tab = self.tabs.currentWidget()
            if current_tab:
                table_view = current_tab.findChild(QTableWidget)
                if table_view:
                    self.load_table_data(table_name, table_view)
        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Ошибка сохранения: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    def edit_record(self, table_name, table_view):
        QMessageBox.information(self, "Редактирование", f"Функция редактирования записи в {table_name}")

    def delete_record(self, table_name, table_view):
        selected_row = table_view.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления.")
            return

        record_id = table_view.item(selected_row, 0).text()  # Предполагаем, что ID в первом столбце
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить запись {record_id} из {table_name}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                connection = psycopg2.connect(**DB_CONFIG)
                cursor = connection.cursor()
                query = f"DELETE FROM {table_name} WHERE id = %s"
                cursor.execute(query, (record_id,))
                connection.commit()
                QMessageBox.information(self, "Успех", "Запись удалена успешно.")

                # Обновляем данные в текущей таблице
                self.load_table_data(table_name, table_view)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {str(e)}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'connection' in locals():
                    connection.close()

    def setup_user_tab(self):
        layout = QVBoxLayout()
        self.user_table = QTableWidget()
        layout.addWidget(self.user_table)

        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_delete = QPushButton("Удалить")

        self.btn_add.clicked.connect(self.add_user)
        self.btn_edit.clicked.connect(self.edit_user)
        self.btn_delete.clicked.connect(self.delete_user)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)

        self.user_tab.setLayout(layout)
        self.load_users()

    def load_users(self):
        try:
            connection = psycopg2.connect(**DB_CONFIG)
            cursor = connection.cursor()
            cursor.execute("SELECT id, username, role FROM users")
            users = cursor.fetchall()

            self.user_table.setRowCount(len(users))
            self.user_table.setColumnCount(3)
            self.user_table.setHorizontalHeaderLabels(["ID", "Логин", "Роль"])

            for row, user in enumerate(users):
                for col, data in enumerate(user):
                    self.user_table.setItem(row, col, QTableWidgetItem(str(data)))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cursor.close()
            connection.close()

    def add_record(self, table_name):
        try:
            connection = psycopg2.connect(**DB_CONFIG)
            cursor = connection.cursor()

            # Получаем список всех столбцов таблицы
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, (table_name,))
            all_columns = [col[0] for col in cursor.fetchall()]

            # Получаем следующий доступный ID
            cursor.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {table_name}")
            next_id = cursor.fetchone()[0]

            # Создаём диалоговое окно для ввода данных
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Добавить запись в {table_name}")
            layout = QFormLayout()
            inputs = {}

            # Добавляем поле ID (только для отображения)
            id_label = QLabel("ID (автоматически):")
            id_value = QLabel(str(next_id))
            layout.addRow(id_label, id_value)

            for column in all_columns:
                if column == "id":
                    continue  # Пропускаем поле ID, так как оно уже обработано

                if column.endswith("_at") or column.endswith("_date"):
                    # Обработка полей даты
                    input_field = QDateEdit(calendarPopup=True)
                    input_field.setDate(QDate.currentDate())
                else:
                    # Для остальных полей обычный QLineEdit
                    input_field = QLineEdit()

                inputs[column] = input_field
                layout.addRow(column, input_field)

            btn_save = QPushButton("Сохранить")
            btn_save.clicked.connect(lambda: self.save_record(table_name, inputs, dialog))
            layout.addWidget(btn_save)

            dialog.setLayout(layout)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    def save_record(self, table_name, inputs, dialog):
        try:
            connection = psycopg2.connect(**DB_CONFIG)
            cursor = connection.cursor()
            columns = []
            values = []
            for column, widget in inputs.items():
                if isinstance(widget, QLineEdit):
                    value = widget.text()
                elif isinstance(widget, QDateEdit):
                    value = widget.date().toString("yyyy-MM-dd")
                elif isinstance(widget, QComboBox):
                    value = widget.currentData()  # Для ComboBox с userData
                    if value is None:  # Если нет userData, берем текст
                        value = widget.currentText()
                # Пропускаем пустые значения для необязательных полей
                if value or column in ['student_id', 'coach_id', 'inventory_id', 'movement_type']:
                    columns.append(column)
                    values.append(value)
            # Формируем SQL-запрос
            placeholders = ["%s"] * len(values)
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(query, values)
            connection.commit()
            QMessageBox.information(dialog, "Успех", "Запись успешно добавлена!")
            dialog.close()
            # Обновляем только текущую таблицу
            current_tab = self.tabs.currentWidget()
            if current_tab:
                table_view = current_tab.findChild(QTableWidget)
                if table_view:
                    self.load_table_data(table_name, table_view)
        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Ошибка сохранения: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    def save_record(self, table_name, inputs, dialog):
        try:
            connection = psycopg2.connect(**DB_CONFIG)
            cursor = connection.cursor()

            columns = []
            values = []

            for column, widget in inputs.items():
                if isinstance(widget, QLineEdit):
                    value = widget.text()
                elif isinstance(widget, QDateEdit):
                    value = widget.date().toString("yyyy-MM-dd")
                elif isinstance(widget, QComboBox):
                    if widget.currentData():  # Если есть userData (для ID)
                        value = widget.currentData()
                    else:
                        value = widget.currentText()  # Для обычных ComboBox

                # Для числовых полей проверяем, что значение не пустое
                if column.endswith('_id') and not value:
                    QMessageBox.warning(dialog, "Ошибка", f"Поле {column} обязательно для заполнения!")
                    return

                columns.append(column)
                values.append(value)

            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(values))})"
            cursor.execute(query, values)
            connection.commit()

            QMessageBox.information(dialog, "Успех", "Запись успешно добавлена!")
            dialog.close()
            self.load_tables()  # Обновляем все таблицы

        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Ошибка при сохранении: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    def edit_record(self, table_name, table_view):
        selected_row = table_view.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования!")
            return

        try:
            connection = psycopg2.connect(**DB_CONFIG)
            cursor = connection.cursor()
            # Получаем список столбцов таблицы
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = %s", (table_name,))
            columns = [col[0] for col in cursor.fetchall()]
            if not columns:
                QMessageBox.warning(self, "Ошибка", "Не удалось получить столбцы таблицы!")
                return

            # Получаем текущие значения записи
            values = [table_view.item(selected_row, col).text() for col in range(len(columns))]

            # Создаём диалоговое окно для редактирования данных
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Редактировать запись в {table_name}")
            layout = QFormLayout()
            inputs = {}
            for column, value in zip(columns, values):
                input_field = QLineEdit()
                input_field.setText(value)
                inputs[column] = input_field
                layout.addRow(column, input_field)

            btn_save = QPushButton("Сохранить изменения")
            btn_save.clicked.connect(
                lambda: self.save_edited_record(table_name, columns, values[0], inputs, dialog, table_view))
            layout.addWidget(btn_save)
            dialog.setLayout(layout)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    def save_edited_record(self, table_name, columns, record_id, inputs, dialog, table_view):
        try:
            connection = psycopg2.connect(**DB_CONFIG)
            cursor = connection.cursor()
            set_clause = ', '.join([f"{col} = %s" for col in columns[1:]])
            values = [inputs[col].text() for col in columns[1:]]
            values.append(record_id)
            query = f"UPDATE {table_name} SET {set_clause} WHERE {columns[0]} = %s"
            cursor.execute(query, values)
            connection.commit()
            QMessageBox.information(self, "Успех", "Запись обновлена!")
            dialog.close()

            # Обновляем данные в текущей таблице
            self.load_table_data(table_name, table_view)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    def add_user(self):
        self.add_record("users")

    def edit_user(self, table_view):
        self.edit_record("users", table_view)

    def delete_user(self, table_view):
        selected_row = table_view.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления!")
            return

        user_id = table_view.item(selected_row, 0).text()
        try:
            connection = psycopg2.connect(**DB_CONFIG)
            cursor = connection.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            connection.commit()

            QMessageBox.information(self, "Удаление", "Пользователь удалён!")
            self.load_tables()  # Перезагрузить данные

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

#РОЛЬ ТРЕНЕРА
class CoachWindow(QDialog):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id  # Сохраняем ID текущего пользователя
        self.setWindowTitle("Панель тренера")
        self.setGeometry(200, 200, 1024, 768)
        self.setWindowIcon(QIcon('coach_icon.png'))  # Иконка окна

        # Стили CSS
        self.setStyleSheet("""
            QDialog {
                background-color: #f9f9f9;
            }
            QPushButton {
                padding: 10px;
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QTableWidget {
                gridline-color: #ddd;
                alternate-background-color: #fafafa;
            }
        """)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Toolbar с кнопками
        toolbar = QHBoxLayout()
        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.setIcon(QIcon.fromTheme("view-refresh"))
        self.btn_refresh.setStyleSheet("padding: 8px; background-color: #007bff;")

        self.btn_logout = QPushButton("Выход")
        self.btn_logout.setIcon(QIcon.fromTheme("system-log-out"))
        self.btn_logout.setStyleSheet("padding: 8px; background-color: #dc3545;")

        toolbar.addWidget(self.btn_refresh)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_logout)

        self.layout.addLayout(toolbar)

        # Кнопки функционала
        self.btn_schedule = QPushButton("Моё расписание")
        self.btn_schedule.setIcon(QIcon.fromTheme("x-office-calendar"))
        self.btn_schedule.clicked.connect(self.view_schedule)
        self.layout.addWidget(self.btn_schedule)

        self.btn_students = QPushButton("Мои ученики")
        self.btn_students.setIcon(QIcon.fromTheme("system-users"))
        self.btn_students.clicked.connect(self.view_students)
        self.layout.addWidget(self.btn_students)

        self.btn_inventory = QPushButton("Инвентарь")
        self.btn_inventory.setIcon(QIcon.fromTheme("package-x-generic"))
        self.btn_inventory.clicked.connect(self.view_inventory)
        self.layout.addWidget(self.btn_inventory)

        self.btn_competitions = QPushButton("Соревнования")
        self.btn_competitions.setIcon(QIcon.fromTheme("trophy-gold"))
        self.btn_competitions.clicked.connect(self.view_competitions)
        self.layout.addWidget(self.btn_competitions)

        # Новая кнопка для записи занятия
        self.btn_add_class = QPushButton("Записать занятие")
        self.btn_add_class.setIcon(QIcon.fromTheme("list-add"))
        self.btn_add_class.clicked.connect(self.add_class)
        self.layout.addWidget(self.btn_add_class)

        self.setLayout(self.layout)

        # Подключение кнопок выхода
        self.btn_logout.clicked.connect(self.logout)
        self.btn_refresh.clicked.connect(self.refresh_data)

    def refresh_data(self):
        QMessageBox.information(self, "Обновление", "Данные обновлены!")
        # Здесь можно добавить логику обновления данных

    def logout(self):
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()

    def add_class(self):
        """Добавление нового занятия для выбранного студента"""
        try:
            connection = psycopg2.connect(**DB_CONFIG)
            cursor = connection.cursor()
            # Получаем список студентов
            cursor.execute("SELECT id, full_name FROM students")
            students = cursor.fetchall()
            # Получаем список тренеров
            cursor.execute("""
                SELECT c.id, u.username 
                FROM coaches c
                JOIN users u ON c.user_id = u.id
            """)
            coaches = cursor.fetchall()
            if not students or not coaches:
                QMessageBox.warning(self, "Ошибка", "Нет доступных студентов или тренеров!")
                return

            # Создаем диалоговое окно
            dialog = QDialog(self)
            dialog.setWindowTitle("Добавить занятие")
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #fff;
                }
                QLabel {
                    font-size: 14px;
                }
                QComboBox, QDateEdit {
                    padding: 8px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }
            """)
            layout = QFormLayout()

            # Студент
            self.student_combo = QComboBox()
            for student_id, full_name in students:
                self.student_combo.addItem(full_name, student_id)
            layout.addRow("Студент:", self.student_combo)

            # Тренер
            self.coach_combo = QComboBox()
            for coach_id, username in coaches:
                self.coach_combo.addItem(username, coach_id)
            layout.addRow("Тренер:", self.coach_combo)

            # Дата
            self.date_edit = QDateEdit()
            self.date_edit.setCalendarPopup(True)
            self.date_edit.setDisplayFormat("yyyy-MM-dd")
            self.date_edit.setDate(QDate.currentDate())
            layout.addRow("Дата:", self.date_edit)

            # Время
            self.time_combo = QComboBox()
            time_slots = ["08:00:00", "10:00:00", "12:00:00", "14:00:00", "16:00:00", "18:00:00"]
            self.time_combo.addItems(time_slots)
            layout.addRow("Время:", self.time_combo)

            # Место
            self.location_combo = QComboBox()
            cursor.execute("SELECT DISTINCT location FROM schedule WHERE location IS NOT NULL")
            locations = cursor.fetchall()
            for loc in locations:
                self.location_combo.addItem(loc[0])
            layout.addRow("Место:", self.location_combo)

            # Сохранить
            btn_save = QPushButton("Сохранить")
            btn_save.setIcon(QIcon.fromTheme("document-save"))
            btn_save.setStyleSheet("background-color: #28a745;")
            btn_save.clicked.connect(lambda: self.save_class(dialog))
            layout.addWidget(btn_save)

            dialog.setLayout(layout)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    def save_class(self, dialog):
        """Сохранение занятия в базу данных"""
        try:
            connection = psycopg2.connect(**DB_CONFIG)
            cursor = connection.cursor()

            student_id = self.student_combo.currentData()
            coach_id = self.coach_combo.currentData()
            date_part = self.date_edit.date().toString("yyyy-MM-dd")
            time_part = self.time_combo.currentText()
            class_date = f"{date_part} {time_part}"
            location = self.location_combo.currentText()

            query = """
            INSERT INTO schedule (student_id, coach_id, class_date, location)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (student_id, coach_id, class_date, location))
            connection.commit()

            QMessageBox.information(self, "Успех", "Занятие успешно добавлено!")
            dialog.close()
            self.view_schedule()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    # Остальные существующие методы класса CoachWindow
    def view_schedule(self):
        self.show_table("SELECT * FROM schedule")

    def view_students(self):
        self.show_table("SELECT * FROM students")

    def view_inventory(self):
        self.show_table("SELECT * FROM inventory_movements")

    def view_competitions(self):
        self.show_table("SELECT * FROM competitions")

    def show_table(self, query):
        try:
            connection = psycopg2.connect(host="localhost", dbname="sportschool", user="sportschool", password="1234")
            cursor = connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            # Удаляем предыдущие таблицы перед добавлением новой
            for i in reversed(range(self.layout.count())):
                widget = self.layout.itemAt(i).widget()
                if isinstance(widget, QTableWidget):
                    widget.setParent(None)

            table_widget = QTableWidget()
            table_widget.setRowCount(len(data))
            table_widget.setColumnCount(len(columns))
            table_widget.setHorizontalHeaderLabels(columns)

            for row_idx, row_data in enumerate(data):
                for col_idx, value in enumerate(row_data):
                    table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

            self.layout.addWidget(table_widget)

        except Exception as e:
            print("Ошибка загрузки данных:", str(e))
        finally:
            cursor.close()
            connection.close()



#ИНТЕРФЕЙС СТУДЕНТА
class StudentWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Панель студента")
        self.setGeometry(200, 200, 1024, 768)
        self.setWindowIcon(QIcon('student_icon.png'))  # Иконка окна

        # Стили CSS
        self.setStyleSheet("""
            QDialog {
                background-color: #f9f9f9;
            }
            QPushButton {
                padding: 10px;
                background-color: #ffc107;
                color: black;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QTableWidget {
                gridline-color: #ddd;
                alternate-background-color: #fafafa;
            }
        """)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Toolbar с кнопками
        toolbar = QHBoxLayout()
        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.setIcon(QIcon.fromTheme("view-refresh"))
        self.btn_refresh.setStyleSheet("padding: 8px; background-color: #007bff;")

        self.btn_logout = QPushButton("Выход")
        self.btn_logout.setIcon(QIcon.fromTheme("system-log-out"))
        self.btn_logout.setStyleSheet("padding: 8px; background-color: #dc3545;")

        toolbar.addWidget(self.btn_refresh)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_logout)

        self.layout.addLayout(toolbar)

        # Кнопки функционала
        self.btn_schedule = QPushButton("Моё расписание")
        self.btn_schedule.setIcon(QIcon.fromTheme("x-office-calendar"))
        self.btn_schedule.clicked.connect(lambda: self.show_table("schedule"))
        self.layout.addWidget(self.btn_schedule)

        self.btn_coaches = QPushButton("Тренеры")
        self.btn_coaches.setIcon(QIcon.fromTheme("system-users"))
        self.btn_coaches.clicked.connect(lambda: self.show_table("coaches"))
        self.layout.addWidget(self.btn_coaches)

        self.btn_competitions = QPushButton("Соревнования")
        self.btn_competitions.setIcon(QIcon.fromTheme("trophy-gold"))
        self.btn_competitions.clicked.connect(lambda: self.show_table("competitions"))
        self.layout.addWidget(self.btn_competitions)

        self.setLayout(self.layout)

        # Подключение кнопок выхода
        self.btn_logout.clicked.connect(self.logout)
        self.btn_refresh.clicked.connect(self.refresh_data)

    def refresh_data(self):
        QMessageBox.information(self, "Обновление", "Данные обновлены!")
        # Здесь можно добавить логику обновления данных

    def logout(self):
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()

    def show_table(self, table_name):
        query = f"SELECT * FROM {table_name}"
        try:
            connection = psycopg2.connect(host="localhost", dbname="sportschool", user="sportschool", password="1234")
            cursor = connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            if hasattr(self, 'table_widget') and self.table_widget:
                self.layout.removeWidget(self.table_widget)
                self.table_widget.deleteLater()

            self.table_widget = QTableWidget()
            self.table_widget.setRowCount(len(data))
            self.table_widget.setColumnCount(len(columns))
            self.table_widget.setHorizontalHeaderLabels(columns)

            for row_idx, row_data in enumerate(data):
                for col_idx, value in enumerate(row_data):
                    self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

            self.layout.addWidget(self.table_widget)
        except Exception as e:
            print("Ошибка загрузки данных:", str(e))
        finally:
            cursor.close()
            connection.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())