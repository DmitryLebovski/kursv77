import sys, re
from PyQt6.QtWidgets import (QApplication, 
                            QWidget, 
                            QVBoxLayout,
                            QHBoxLayout, 
                            QLabel, 
                            QLineEdit, 
                            QPushButton, 
                            QTextEdit,
                            QMessageBox, 
                            QTableWidget,
                            QTableWidgetItem, 
                            QDialog, 
                            QComboBox,
                            QCalendarWidget,
                            QFileDialog)
from PyQt6.QtCore import Qt, QFile, QUrl
from PyQt6.QtGui import QDesktopServices
from psycopg2 import Error as DatabaseError
from db import connect

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход")
        layout = QVBoxLayout()

        self.username_label = QLabel("Имя пользователя:")
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Вход")
        self.login_button.clicked.connect(self.authenticate)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def authenticate(self):
        username = self.username_input.text()
        password = self.password_input.text()

        connection = connect(username, password)
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT id FROM head WHERE head_username = %s", (username,))
                user_exists = cursor.fetchone()
                if user_exists:
                    self.openMainWindow("head")
                    return
                else:
                    cursor.execute("SELECT id FROM executor WHERE executor_username = %s", (username,))
                    user_exists = cursor.fetchone()
                    if user_exists:
                        self.openMainWindow("executor")
                        return
                    else:
                        QMessageBox.warning(self, "Ошибка входа", "Такого пользователя не существует")
            except Exception as error:
                print("Ошибка при выполнении SQL запроса:", error)
                QMessageBox.warning(self, "Ошибка БД", "Ошибка при выполнении SQL запроса.")
                cursor.close()
                connection.close()
            finally:
                cursor.close()
                connection.close()
        else:
            QMessageBox.warning(self, "Ошибка входа", "Неверное имя пользователя или пароль.")

    def openMainWindow(self, role):
        self.main_window = MainWindow(self.username_input.text(), self.password_input.text(), role)
        self.main_window.show()
        self.close()

class MainWindow(QWidget):
    def __init__(self, username, password, role):
        super().__init__()
        self.username = username
        self.password = password
        self.role = role
        self.setWindowTitle("Список договоров")
        self.layoutQV = QVBoxLayout()
        self.setFixedWidth(1580)
        self.table = QTableWidget()
        self.table.setFixedHeight(230)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        connection = connect(self.username, self.password)
        if connection:
            cursor = connection.cursor()
            try:
                panel_view = QHBoxLayout()
                panel_view.setAlignment(Qt.AlignmentFlag.AlignLeft)

                update_button = QPushButton("Обновить таблицу")
                update_button.setFixedWidth(180)
                update_button.clicked.connect(self.reloadTable)
                panel_view.addWidget(update_button)

                if self.role == "head":
                    cursor.execute("SELECT id, full_name FROM head WHERE head_username =  %s", (self.username,))
                    self.data = cursor.fetchall()
                    self.full_name_v = self.data[0][1]
                    self.id_head = self.data[0][0]
                    self.welcome_label = QLabel(f"Здравствуйте, {self.full_name_v}!")
                    self.status = QLabel(f"Статус пользователя: Руководитель, Вы имеете полный доступ к договорам.")
                    self.layoutQV.addWidget(self.welcome_label)
                    self.layoutQV.addWidget(self.status)
                    self.setFixedHeight(520)

                    add_button = QPushButton("Добавить договор")
                    add_button.setFixedWidth(180)
                    add_button.clicked.connect(self.add_contract)
                    panel_view.addWidget(add_button)

                    hlayout = QHBoxLayout()
                    hlayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
                    delete_executor_button = QPushButton("Удалить агента")
                    delete_executor_button.setFixedWidth(180)
                    delete_executor_button.clicked.connect(self.delete_executor)
                    hlayout.addWidget(delete_executor_button)

                    add_executor_button = QPushButton("Добавить агента")
                    add_executor_button.setFixedWidth(180)
                    add_executor_button.clicked.connect(self.add_executor)
                    hlayout.addWidget(add_executor_button)
                    self.layoutQV.addLayout(hlayout)

                elif self.role == "executor":
                    cursor.execute("SELECT ex.full_name, ex.head_id FROM executor ex WHERE ex.executor_username = %s", (self.username,))
                    result = cursor.fetchone()
                    if result:
                        full_name_v = result[0]
                        h_id = result[1]
                    else:
                        QMessageBox.warning(self, "Ошибка БД", "Ошибка при подгрузке данных с БД.")
                    cursor.execute("SELECT h.full_name, h.phone_number, h.email FROM head h WHERE h.id = %s", (h_id,))
                    result = cursor.fetchone()
                    if result:
                        h_name = result[0]
                        h_pn = result[1]
                        h_mail = result[2]
                    else:
                        QMessageBox.warning(self, "Ошибка БД", "Ошибка при подгрузке данных с БД.")
                    self.welcome_label1 = QLabel(f"Здравствуйте, {full_name_v}!")
                    self.welcome_label2 = QLabel(f"Вы были добавлены в систему руководителем: {h_name}")
                    self.welcome_label3 = QLabel(f"Доступные данные руководителя: {h_pn}, {h_mail}")

                    self.status = QLabel(f"Статус пользователя: Агент, Вы можете редактировать разрешенную информацию только в течении статуса 'Создано'.")
                    self.status_add = QLabel(f"Как только статус договора будет изменен Руководителем - дальнейшее редактирование недоступно.")
                    self.layoutQV.addWidget(self.welcome_label1)
                    self.layoutQV.addWidget(self.welcome_label2)
                    self.layoutQV.addWidget(self.welcome_label3)
                    self.layoutQV.addWidget(self.status)
                    self.layoutQV.addWidget(self.status_add)
                    self.setFixedHeight(550)

                self.layoutQV.addLayout(panel_view)


                hlayout = QHBoxLayout()
                hlayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
                self.filter_column_combo = QComboBox()
                self.filter_column_combo.setFixedWidth(180)
                self.filter_column_combo.addItems([
                    "Номер договора", "Статус", "Наименование договора",
                    "ФИО руководителя", "ФИО агента", "Компания",
                    "Дата заключения", "Срок действия"
                ])

                hlayout.addWidget(self.filter_column_combo)
                self.filter_value_input = QLineEdit()
                self.filter_value_input.setFixedWidth(180)
                hlayout.addWidget(self.filter_value_input)

                filter_button = QPushButton("Найти")
                filter_button.setFixedWidth(180)
                filter_button.clicked.connect(self.filterTable)
                hlayout.addWidget(filter_button)
                self.layoutQV.addLayout(hlayout)
            except Exception as error:
                print("Ошибка при подгрузке данных с PostgreSQL:", error)
                QMessageBox.warning(self, "Ошибка БД", "Ошибка при подгрузке данных с БД.")
            finally:
                cursor.close()
                connection.close()

        self.reloadTable()
        self.layoutQV.addWidget(self.table)
        self.setLayout(self.layoutQV)

        self.logout_button = QPushButton("Завершить работу")
        self.logout_button.clicked.connect(self.logout)
        self.layoutQV.addWidget(self.logout_button)

    def logout(self):
        login_window = LoginWindow()
        login_window.show()
        self.close()

    def reloadTable(self):
        connection = connect(self.username, self.password)
        if connection:
            cursor = connection.cursor()
            try:
                if self.role == "head":
                    cursor.execute("SELECT * FROM contract_view")
                elif self.role == "executor":
                    cursor.execute("SELECT * FROM contract_view_executor(%s)", (self.username,))
                records = cursor.fetchall()

                if not records:
                    QMessageBox.information(self, "Пусто", "Записи отсутствуют.")
                    self.table.setRowCount(0)
                    return

            except Exception as error:
                print("Ошибка при подгрузке данных с PostgreSQL:", error)
                QMessageBox.warning(self, "Ошибка БД", "Ошибка при подгрузке данных с БД.")
                return
            finally:
                cursor.close()
                connection.close()

            self.table.setRowCount(len(records))
            self.table.setColumnCount(len(records[0]))
            headers = ["Номер договора", "Статус", "Наименование договора", "ФИО руководителя",
                       "ФИО агента", "Компания", "Дата заключения", "Срок действия", "Полная информация"]
            if self.role == "head":
                self.table.setColumnCount(len(records[0]) + 1)
                headers.append("Удалить договор")
            self.table.setHorizontalHeaderLabels(headers)

            for i, row in enumerate(records):
                for j, value in enumerate(row[1:]):
                    self.table.setItem(i, j, QTableWidgetItem(str(value)))
                open_button = QPushButton("Открыть")
                open_button.clicked.connect(lambda _, i=i: self.openContract(records[i][0]))
                self.table.setCellWidget(i, len(row) - 1, open_button)

                if self.role == "head":
                    delete_button = QPushButton("Удалить")
                    delete_button.clicked.connect(lambda _, i=i: self.confirm_delete(records[i][0]))
                    self.table.setCellWidget(i, len(row), delete_button)
            self.table.resizeColumnsToContents()

    def filterTable(self):
        column = self.filter_column_combo.currentText()
        value = self.filter_value_input.text()

        column_mapping = {
            "Номер договора": "contract_n",
            "Статус": "status",
            "Наименование договора": "agr_obj",
            "ФИО руководителя": "head_name",
            "ФИО агента": "executor_name",
            "Компания": "company_n",
            "Дата заключения": "conc_d",
            "Срок действия": "agr_d"
        }
        column_name = column_mapping.get(column)

        if not value:
            QMessageBox.warning(self, "Ошибка", "Введите значение для поиска.")
            return

        connection = connect(self.username, self.password)
        if connection:
            cursor = connection.cursor()
            try:
                
                cursor.execute("SELECT full_name FROM executor ex WHERE ex.executor_username = %s", (self.username,))
                ex_fullname = cursor.fetchall()

                if column_name in ["conc_d", "agr_d"]:
                    query = f"SELECT * FROM contract_view WHERE TO_CHAR({column_name}, 'YYYY-MM-DD') ILIKE %s"
                else:
                    query = f"SELECT * FROM contract_view WHERE {column_name} ILIKE %s"
                            
                if self.role == "head":
                    cursor.execute(query, ('%' + value + '%',))
                elif self.role == "executor":
                    query += " AND executor_name = %s"
                    cursor.execute(query, ('%' + value + '%', ex_fullname))

                records = cursor.fetchall()

                if not records:
                    QMessageBox.information(self, "Пусто", "Записи отсутствуют.")
                    return

                self.table.setRowCount(len(records))
                self.table.setColumnCount(len(records[0]))
                headers = ["Номер договора", "Статус", "Наименование договора", "ФИО руководителя",
                        "ФИО агента", "Компания(не обязательно)", "Дата заключения", "Срок действия", "Полная информация"]
                if self.role == "head":
                    self.table.setColumnCount(len(records[0]) + 1)
                    headers.append("Удалить договор")
                self.table.setHorizontalHeaderLabels(headers)

                for i, row in enumerate(records):
                    for j, value in enumerate(row[1:]):
                        self.table.setItem(i, j, QTableWidgetItem(str(value)))
                    open_button = QPushButton("Открыть")
                    open_button.clicked.connect(lambda _, i=i: self.openContract(records[i][0]))
                    self.table.setCellWidget(i, len(row) - 1, open_button)

                    if self.role == "head":
                        delete_button = QPushButton("Удалить")
                        delete_button.clicked.connect(lambda _, i=i: self.confirm_delete(records[i][0]))
                        self.table.setCellWidget(i, len(row), delete_button)
                self.table.resizeColumnsToContents()

            except Exception as error:
                print("Ошибка при подгрузке данных с PostgreSQL:", error)
                QMessageBox.warning(self, "Ошибка БД", "Ошибка при подгрузке данных с БД.")
            finally:
                cursor.close()
                connection.close()


    def confirm_delete(self, contract_id):
        confirm_dialog = QMessageBox.question(self, "Подтверждение удаления",
                                              "Вы уверены, что хотите удалить договор?",
                                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm_dialog == QMessageBox.StandardButton.Yes:
            self.delete_contract(contract_id)

    def delete_contract(self, contract_id):
        connection = connect(self.username, self.password)
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT delete_contract(%s);", (contract_id,))
                connection.commit()
                self.reloadTable()
                QMessageBox.information(self, "Успех", "Договор успешно удален.")
            except Exception as error:
                print("Ошибка при подгрузке данных с PostgreSQL:", error)
                QMessageBox.warning(self, "Ошибка БД", "Ошибка при удалении данных из БД.")
            finally:
                cursor.close()
                connection.close()

    def openContract(self, contract_id):
        headers = ["Номер договора",
                   "Наименование договора",
                   "ФИО руководителя",
                   "Номер телефона руководителя(не обязательно)",
                   "Почта руководителя",
                   "ФИО агента",
                   "Номер телефона агента(не обязательно)",
                   "Почта агента",
                   "Позиция агента",
                   "Компания(не обязательно)",
                   "Дата заключения",
                   "Срок действия",
                   "Скан документа",
                   "Дополнительные условия"]
        contract_window = ContractWindow(self, self.username, self.password, self.role, contract_id, headers)
        contract_window.exec()

    def add_contract(self):
        headers = ["Номер договора",
                   "Наименование договора",
                   "ФИО руководителя",
                   "Номер телефона руководителя(не обязательно)",
                   "Почта руководителя",
                   "ФИО агента",
                   "Номер телефона агента(не обязательно)",
                   "Почта агента",
                   "Позиция агента",
                   "Компания(не обязательно)",
                   "Дата заключения",
                   "Срок действия",
                   "Скан документа",
                   "Дополнительные условия"]
        add_window = AddContractWindow(self, self.username, self.password, headers)
        add_window.exec()

    def delete_executor(self):
        self.executors_window = ChangeExecutorDialog(self, self.username, self.password, 'delete')
        self.executors_window.exec()

    def add_executor(self):
        self.executors_window = AddExecutorWindow(self.username, self.password, self.id_head)
        self.executors_window.exec()

class AddExecutorWindow(QDialog):
    def __init__(self, username, password, head_id):
        super().__init__()
        self.setWindowTitle("Добавление агента")
        self.setGeometry(0, 0, 500, 300)
        layout = QVBoxLayout()
        self.username = username
        self.password = password
        self.head_id = head_id

        headers = ["ФИО агента",
                   "Номер телефона агента(не обязательно)",
                   "Почта агента",
                   "Позиция агента",
                   "Компания(не обязательно)",
                   "Имя пользователя"]

        self.fields = {}  

        for header in headers:
            label = QLabel(header)
            line_edit = QLineEdit()
            h_layout = QHBoxLayout()
            h_layout.addWidget(label)
            h_layout.addWidget(line_edit)
            layout.addLayout(h_layout)
            self.fields[header] = line_edit
        save_button = QPushButton("Добавить")
        save_button.clicked.connect(self.save_executor)
        layout.addWidget(save_button)
        self.setLayout(layout)

    def validate_fields(self):
        for header, widget in self.fields.items():
            if isinstance(widget, QLineEdit):
                if not widget.text() and header in ["ФИО Руководителя", "ФИО агента"]:
                    QMessageBox.warning(self, "Пустое поле", f"Поле '{header}' не должно быть пустым.")
                    return False
                        
                
                if not widget.text() and header not in ["Номер телефона агента(не обязательно)", "Компания(не обязательно)"]:
                    QMessageBox.warning(self, "Пустое поле", f"Поле '{header}' не должно быть пустым.")
                    return False
                                    
                if widget.text() and header == "Номер телефона агента(не обязательно)":
                    phone_number = widget.text()
                    if not re.match(r'^\+\d{1}\(\d{3}\)\d{3}-\d{2}-\d{2}$', phone_number):
                        QMessageBox.warning(self, "Неверный формат номера телефона", "Номер телефона должен быть в формате +X(XXX)XXX-XX-XX.")
                        return False
        return True
    
    def save_executor(self):
        if self.validate_fields():
            connection = connect(self.username, self.password)
            if connection:
                cursor = connection.cursor()
                try:
                        cursor.execute("SELECT full_name, id FROM head WHERE head_username =  %s", (self.username,))
                        self.full_name_v = cursor.fetchone()[0]
                        
                        
                        add_executor = "SELECT * FROM insert_user(%s, %s, %s, %s, %s, %s, %s);"    
                        cursor.execute(add_executor, (
                            self.fields["ФИО агента"].text(),
                            self.fields["Номер телефона агента(не обязательно)"].text(),
                            self.fields["Почта агента"].text(),
                            self.fields["Компания(не обязательно)"].text(),
                            self.fields["Позиция агента"].text(),
                            self.fields["Имя пользователя"].text(),
                            self.head_id
                        ))
                        connection.commit()
                        QMessageBox.information(self, "Успех", f"Руководитель '{self.full_name_v}' успешно добавил своего агента.")
                except DatabaseError as db_error:
                    print("Ошибка при обновлении данных в PostgreSQL:", db_error)
                    QMessageBox.warning(self, "Ошибка БД", f"Добавление агента. {db_error.pgerror.split('CONTEXT:')[0].strip()}")
                    connection.rollback()
                except Exception as error:
                    print("Неожиданная ошибка:", error)
                    QMessageBox.warning(self, "Ошибка", f"Произошла ошибка: {error}")
                    connection.rollback()
                else:
                    connection.commit()
                finally:
                    cursor.close()
                    connection.close()
                    super().accept()
            self.close()
        

class AddContractWindow(QDialog):
    def __init__(self, main_window, username, password, headers):
        super().__init__()
        self.setWindowTitle("Добавление договора")
        self.setGeometry(0, 0, 500, 900)
        layout = QVBoxLayout()
        self.username = username
        self.password = password
        self.main_window = main_window

        connection = connect(self.username, self.password)
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT id, full_name, phone_number, email FROM head WHERE head_username = %s", (self.username,))
                self.data = cursor.fetchall()
            except Exception as error:
                print("Ошибка при подгрузке данных с PostgreSQL:", error)
                QMessageBox.warning(self, "Ошибка БД", "Данные руководителя. Ошибка при подгрузке данных с БД.")
                cursor.close()
                connection.close()
            finally:
                cursor.close()
                connection.close()
            self.close()

        self.fields = {}  

        for header in headers:
            label = QLabel(header)
            if header in ["Дата заключения", "Срок действия"]:
                calendar_widget = QCalendarWidget()
                h_layout = QHBoxLayout()
                h_layout.addWidget(label)
                h_layout.addWidget(calendar_widget)
                layout.addLayout(h_layout)
                self.fields[header] = calendar_widget
            elif header == "Дополнительные условия":
                text_edit = QTextEdit()
                h_layout = QHBoxLayout()
                h_layout.addWidget(label)
                h_layout.addWidget(text_edit)
                layout.addLayout(h_layout)
                self.fields[header] = text_edit
            elif header == "Скан документа":
                self.scan_document_edit = QLineEdit()
                self.scan_document_edit.setEnabled(False)
                scan_document_button_open = QPushButton("Открыть")
                scan_document_button_open.clicked.connect(self.open_document)
                scan_document_button_change = QPushButton("Изменить")
                scan_document_button_change.clicked.connect(self.change_document)
                h_layout = QHBoxLayout()
                h_layout.addWidget(label)
                h_layout.addWidget(self.scan_document_edit)
                h_layout.addWidget(scan_document_button_open)
                h_layout.addWidget(scan_document_button_change)
                layout.addLayout(h_layout)
                self.fields[header] = self.scan_document_edit
            elif header in ["ФИО руководителя", "Номер телефона руководителя(не обязательно)", "Почта руководителя"]:
                match header:
                    case "ФИО руководителя":
                        h_name = QLineEdit(str(self.data[0][1]))
                        h_name.setReadOnly(False)
                        h_layout = QHBoxLayout()
                        h_layout.addWidget(label)
                        h_layout.addWidget(h_name)
                        layout.addLayout(h_layout)
                        self.fields[header] = h_name
                    case "Номер телефона руководителя(не обязательно)": 
                        h_phone = QLineEdit(str(self.data[0][2]))
                        h_phone.setReadOnly(False)
                        h_layout = QHBoxLayout()
                        h_layout.addWidget(label)
                        h_layout.addWidget(h_phone)
                        layout.addLayout(h_layout)
                        self.fields[header] = h_phone
                    case "Почта руководителя": 
                        h_email = QLineEdit(str(self.data[0][3]))
                        h_email.setReadOnly(False)
                        h_layout = QHBoxLayout()
                        h_layout.addWidget(label)
                        h_layout.addWidget(h_email)
                        layout.addLayout(h_layout)
                        self.fields[header] = h_email
            elif header in ["ФИО агента", "Номер телефона агента(не обязательно)", "Почта агента", "Позиция агента", "Компания(не обязательно)"]:
                match header:
                    case "ФИО агента":
                        self.ex_name = QLineEdit()
                        self.ex_name.setEnabled(False)
                        h_layout = QHBoxLayout()
                        h_layout.addWidget(label)
                        h_layout.addWidget(self.ex_name)
                        layout.addLayout(h_layout)
                        self.fields[header] = self.ex_name
                    case "Номер телефона агента(не обязательно)":
                        self.ex_phone = QLineEdit()
                        self.ex_phone.setEnabled(False)
                        h_layout = QHBoxLayout()
                        h_layout.addWidget(label)
                        h_layout.addWidget(self.ex_phone)
                        layout.addLayout(h_layout)
                        self.fields[header] = self.ex_phone 
                    case "Почта агента":
                        self.ex_email = QLineEdit()
                        self.ex_email.setEnabled(False)
                        h_layout = QHBoxLayout()
                        h_layout.addWidget(label)
                        h_layout.addWidget(self.ex_email)
                        layout.addLayout(h_layout)
                        self.fields[header] = self.ex_email
                    case "Позиция агента":
                        self.ex_pos = QLineEdit()
                        self.ex_pos.setEnabled(False)
                        h_layout = QHBoxLayout()
                        h_layout.addWidget(label)
                        h_layout.addWidget(self.ex_pos)
                        layout.addLayout(h_layout)
                        self.fields[header] = self.ex_pos
                    case "Компания(не обязательно)":
                        self.ex_com = QLineEdit()
                        self.ex_com.setEnabled(False)
                        h_layout = QHBoxLayout()
                        h_layout.addWidget(label)
                        h_layout.addWidget(self.ex_com)
                        layout.addLayout(h_layout)
                        self.fields[header] = self.ex_com
                        change_executor = QPushButton("Выбрать агента")
                        change_executor.clicked.connect(self.open_executor_list)
                        layout.addWidget(change_executor)
            else:
                line_edit = QLineEdit()
                h_layout = QHBoxLayout()
                h_layout.addWidget(label)
                h_layout.addWidget(line_edit)
                layout.addLayout(h_layout)
                self.fields[header] = line_edit

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.add_data)
        layout.addWidget(save_button)
        self.setLayout(layout)

    def open_executor_list(self):
        self.executors_window = ChangeExecutorDialog(self, self.username, self.password, 'save')
        self.executors_window.exec()

    def update_executor_def(self, id, full_name, phone, email, pos, company_name):
        self.ex_id = id
        self.ex_name.setText(full_name)
        self.ex_phone.setText(phone)
        self.ex_email.setText(email)
        self.ex_pos.setText(pos)
        self.ex_com.setText(company_name)

    def open_document(self):
        document_path = self.scan_document_edit.text()
        file = QFile(document_path)
        if file.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(document_path))
            file.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось открыть файл. Возможно, он не существует или к нему нет доступа.")

    def change_document(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        document_path, _ = file_dialog.getOpenFileName(self, "Выберите файл", "", "Изображения (*.jpg *.jpeg *.png);;PDF Файлы (*.pdf);;Документы (*.doc *.docx)")
        if document_path:
            self.scan_document_edit.setText(document_path)
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось выбрать файл или файл не поддерживается.")


    def validate_fields(self):
        for header, widget in self.fields.items():
            if isinstance(widget, QLineEdit):
                if not widget.text() and header not in ["Номер телефона руководителя(не обязательно)", "Номер телефона агента(не обязательно)", "Компания(не обязательно)", "Скан документа", "Дополнительные условия"]:
                    QMessageBox.warning(self, "Пустое поле", f"Поле '{header}' не должно быть пустым.")
                    return False
                    
                if widget.text() and header in ["Номер телефона руководителя(не обязательно)", "Номер телефона агента(не обязательно)"]:
                    phone_number = widget.text()
                    if not re.match(r'^\+\d{1}\(\d{3}\)\d{3}-\d{2}-\d{2}$', phone_number):
                        QMessageBox.warning(self, "Неверный формат номера телефона", "Номер телефона должен быть в формате +X(XXX)XXX-XX-XX.")
                        return False
        return True

    
    def add_data(self):
        if self.validate_fields():
            connection = connect(self.username, self.password)
            if connection:
                cursor = connection.cursor()
                try:
                        add_contract_and_update_head = """
                            SELECT * FROM add_contract_and_update_head(
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            );
                        """
                        cursor.execute(add_contract_and_update_head, (
                            self.fields["Номер договора"].text(),
                            self.fields["Наименование договора"].text(),
                            self.fields["ФИО руководителя"].text(),
                            self.fields["Номер телефона руководителя(не обязательно)"].text(),
                            self.fields["Почта руководителя"].text(),
                            self.ex_id,
                            self.data[0][0],
                            self.fields["Дата заключения"].selectedDate().toString("yyyy-MM-dd"),
                            self.fields["Срок действия"].selectedDate().toString("yyyy-MM-dd"),
                            self.fields["Скан документа"].text(),
                            self.fields["Дополнительные условия"].toPlainText()
                        ))
                        connection.commit()
                        
                        self.main_window.reloadTable()
                        self.close()
                        QMessageBox.information(self, "Успех", "Данные успешно добавлены.")
                except DatabaseError as db_error:
                    print("Ошибка при обновлении данных в PostgreSQL:", db_error)
                    QMessageBox.warning(self, "Ошибка БД", f"Добавление контракта. {db_error.pgerror.split('CONTEXT:')[0].strip()}")
                except Exception as error:
                    print("Неожиданная ошибка:", error)
                    QMessageBox.warning(self, "Ошибка", f"Произошла ошибка: {error}")
                    connection.rollback()
                finally:
                    cursor.close()
                    connection.close()

class ContractWindow(QDialog):
    def __init__(self, main_window, username, password, role, contract_id, headers):
        super().__init__()
        self.setWindowTitle("Данные договора")
        self.setGeometry(0, 0, 500, 900)
        layout = QVBoxLayout()
        self.username = username
        self.password = password
        self.role = role
        self.contract_id = contract_id
        self.main_window = main_window

        connection = connect(username, password)
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    SELECT status FROM contract WHERE id = %s""", (contract_id,))
                status = cursor.fetchone()[0]
                if status == 'Согласован': cursor.execute("SELECT * FROM contract_info_view_status WHERE id = %s", (contract_id,))
                else: cursor.execute("SELECT * FROM contract_info_view_all WHERE id = %s", (contract_id,))
                result = cursor.fetchone()
            except Exception as error:
                print("Ошибка при подгрузке данных с PostgreSQL:", error)
                QMessageBox.warning(self, "Ошибка БД", "Данные контракта. Ошибка при подгрузке данных с БД.")
                cursor.close()
                connection.close()
            finally:
                cursor.close()
                connection.close()
        
        self.fields = {}  

        h_layout = QHBoxLayout()
        label = QLabel("<b>Статус</b>")
        combo_box = QComboBox()
        combo_box.addItems(["Создан", "Согласован", "Закрыт"])
        combo_box.setCurrentText(status)
        h_layout.addWidget(label)
        h_layout.addWidget(combo_box)
        self.fields["Статус"] = combo_box
        if role == "executor" or combo_box.currentText() == "Закрыт": combo_box.setEnabled(False)
        layout.addLayout(h_layout)

        for header, value in zip(headers, result):
            label = QLabel(header)
            if header in ["Дата заключения", "Срок действия"]:
                calendar_widget = QCalendarWidget()
                calendar_widget.setSelectedDate(value)
                h_layout = QHBoxLayout()
                h_layout.addWidget(label)
                h_layout.addWidget(calendar_widget)
                layout.addLayout(h_layout)
                self.fields[header] = calendar_widget
                if combo_box.currentText() in ["Согласован", "Закрыт"]: calendar_widget.setEnabled(False)
            elif header == "Дополнительные условия":
                text_edit = QTextEdit()
                text_edit.setPlainText(value)
                h_layout = QHBoxLayout()
                h_layout.addWidget(label)
                h_layout.addWidget(text_edit)
                layout.addLayout(h_layout)
                self.fields[header] = text_edit
                if combo_box.currentText() in ["Согласован", "Закрыт"]: text_edit.setEnabled(False)
            elif header == "Скан документа":
                self.scan_document_edit = QLineEdit(str(value))
                self.scan_document_edit.setEnabled(False)
                scan_document_button_open = QPushButton("Открыть")
                scan_document_button_open.clicked.connect(self.open_document)
                scan_document_button_change = QPushButton("Изменить")
                scan_document_button_change.clicked.connect(self.change_document)
                if combo_box.currentText() in ["Согласован", "Закрыт"]: scan_document_button_change.setEnabled(False)
                h_layout = QHBoxLayout()
                h_layout.addWidget(label)
                h_layout.addWidget(self.scan_document_edit)
                h_layout.addWidget(scan_document_button_open)
                h_layout.addWidget(scan_document_button_change)
                layout.addLayout(h_layout)
                self.fields[header] = self.scan_document_edit
            elif role == "head" and header not in ["ФИО агента", "Номер телефона агента(не обязательно)", "Почта агента", "Позиция агента", "Компания(не обязательно)"]:
                line_edit = QLineEdit(str(value))
                line_edit.setReadOnly(False)
                h_layout = QHBoxLayout()
                h_layout.addWidget(label)
                h_layout.addWidget(line_edit)
                layout.addLayout(h_layout)
                self.fields[header] = line_edit
                if combo_box.currentText() in ["Согласован", "Закрыт"]: line_edit.setEnabled(False)
            elif role == "executor" and header not in ["ФИО руководителя", "Номер телефона руководителя(не обязательно)", "Почта руководителя"]:
                line_edit = QLineEdit(str(value))
                line_edit.setReadOnly(False)
                h_layout = QHBoxLayout()
                h_layout.addWidget(label)
                h_layout.addWidget(line_edit)
                layout.addLayout(h_layout)
                self.fields[header] = line_edit
                if combo_box.currentText() in ["Согласован", "Закрыт"]: line_edit.setEnabled(False)
            elif role == "head" and header in ["ФИО агента", "Номер телефона агента(не обязательно)", "Почта агента", "Позиция агента", "Компания(не обязательно)"]:
                match header:
                    case "ФИО агента":
                        self.ex_name = QLineEdit(str(value))
                        self.ex_name.setEnabled(False)
                        h_layout = QHBoxLayout()
                        h_layout.addWidget(label)
                        h_layout.addWidget(self.ex_name)
                        layout.addLayout(h_layout)
                        self.fields[header] = self.ex_name
                    case "Номер телефона агента(не обязательно)":
                        self.ex_phone = QLineEdit(str(value))
                        self.ex_phone.setEnabled(False)
                        h_layout = QHBoxLayout()
                        h_layout.addWidget(label)
                        h_layout.addWidget(self.ex_phone)
                        layout.addLayout(h_layout)
                        self.fields[header] = self.ex_phone 
                    case "Почта агента":
                        self.ex_email = QLineEdit(str(value))
                        self.ex_email.setEnabled(False)
                        h_layout = QHBoxLayout()
                        h_layout.addWidget(label)
                        h_layout.addWidget(self.ex_email)
                        layout.addLayout(h_layout)
                        self.fields[header] = self.ex_email
                    case "Позиция агента":
                        self.ex_pos = QLineEdit(str(value))
                        self.ex_pos.setEnabled(False)
                        h_layout = QHBoxLayout()
                        h_layout.addWidget(label)
                        h_layout.addWidget(self.ex_pos)
                        layout.addLayout(h_layout)
                        self.fields[header] = self.ex_pos
                    case "Компания(не обязательно)":
                        self.ex_com = QLineEdit(str(value))
                        self.ex_com.setEnabled(False)
                        h_layout = QHBoxLayout()
                        h_layout.addWidget(label)
                        h_layout.addWidget(self.ex_com)
                        layout.addLayout(h_layout)
                        self.fields[header] = self.ex_com

                        if combo_box.currentText() == "Создан": 
                            change_executor = QPushButton("Сменить агента")
                            change_executor.clicked.connect(self.open_executor_list)
                            layout.addWidget(change_executor)
            else:
                line_edit = QLineEdit(str(value))
                line_edit.setEnabled(False)
                h_layout = QHBoxLayout()
                h_layout.addWidget(label)
                h_layout.addWidget(line_edit)
                layout.addLayout(h_layout)
                self.fields[header] = line_edit

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_data)
        layout.addWidget(save_button)
        self.setLayout(layout)
    
    def open_executor_list(self):
        self.executors_window = ChangeExecutorDialog(self, self.username, self.password, 'save')
        self.executors_window.exec()

    def update_executor_def(self, id, full_name, phone, email, pos, company_name):
        self.ex_id = id
        self.ex_name.setText(full_name)
        self.ex_phone.setText(phone)
        self.ex_email.setText(email)
        self.ex_pos.setText(pos)
        self.ex_com.setText(company_name)

    def open_document(self):
        document_path = self.scan_document_edit.text()
        file = QFile(document_path)
        if file.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(document_path))
            file.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось открыть файл. Возможно, он не существует или к нему нет доступа.")

    def change_document(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        document_path, _ = file_dialog.getOpenFileName(self, "Выберите файл", "", "Изображения (*.jpg *.jpeg *.png);;PDF Файлы (*.pdf);;Документы (*.doc *.docx)")
        if document_path:
            self.scan_document_edit.setText(document_path)
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось выбрать файл или файл не поддерживается.")


    def validate_fields(self):
        for header, widget in self.fields.items():
            if isinstance(widget, QLineEdit):
                if not widget.text() and header not in ["Номер телефона руководителя(не обязательно)", "Номер телефона агента(не обязательно)" , "Компания(не обязательно)", "Скан документа", "Дополнительные условия"]:
                    QMessageBox.warning(self, "Пустое поле", f"Поле '{header}' не должно быть пустым.")
                    return False
                
                if widget.text() and header in ["Номер телефона руководителя(не обязательно)", "Номер телефона агента(не обязательно)"]:
                    phone_number = widget.text()
                    if not re.match(r'^\+\d{1}\(\d{3}\)\d{3}-\d{2}-\d{2}$', phone_number):
                        QMessageBox.warning(self, "Неверный формат номера телефона", "Номер телефона должен быть в формате +X(XXX)XXX-XX-XX.")
                        return False
        return True

    def save_data(self):
        if self.validate_fields():
            connection = connect(self.username, self.password)
            if connection:
                cursor = connection.cursor()
                self.message = "Ошибка при обновление таблицы Руководителя"
                try:
                    if self.role == "executor":
                        update_contract_executor = """
                            SELECT update_contract_executor(
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            );
                        """
                        cursor.execute(update_contract_executor, (
                            self.contract_id,
                            self.fields["Номер договора"].text(),
                            self.fields["Наименование договора"].text(),
                            self.fields["Дата заключения"].selectedDate().toString("yyyy-MM-dd"),
                            self.fields["Срок действия"].selectedDate().toString("yyyy-MM-dd"),
                            self.fields["Скан документа"].text(),
                            self.fields["ФИО агента"].text(),
                            self.fields["Номер телефона агента(не обязательно)"].text(),
                            self.fields["Почта агента"].text(),
                            self.fields["Позиция агента"].text(),
                            self.fields["Компания(не обязательно)"].text(),
                            self.fields["Дополнительные условия"].toPlainText()
                        ))
                        connection.commit()
                        QMessageBox.information(self, "Успех", "Данные успешно обновлены.")
                        self.main_window.reloadTable()
                    else:
                        self.message = "Проверьте корректность: email, даты заключения и срок действия, а так же номер контракта(возможно, такой уже существует)."
                        update_contract_head = """
                            SELECT update_contract_head(
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            );
                        """
                        cursor.execute(update_contract_head, (
                            self.contract_id,
                            self.fields["Номер договора"].text(),
                            self.fields["Статус"].currentText(),
                            self.fields["Наименование договора"].text(),
                            self.fields["Дата заключения"].selectedDate().toString("yyyy-MM-dd"),
                            self.fields["Срок действия"].selectedDate().toString("yyyy-MM-dd"),
                            self.fields["Скан документа"].text(),
                            self.fields["ФИО агента"].text(),
                            self.fields["ФИО руководителя"].text(),
                            self.fields["Номер телефона руководителя(не обязательно)"].text(),
                            self.fields["Почта руководителя"].text(),
                            self.fields["Дополнительные условия"].toPlainText()
                        ))
                        connection.commit()
                        QMessageBox.information(self, "Успех", "Данные успешно обновлены.")
                        cursor.close()
                        super().accept()  
                        self.close()
                        self.main_window.reloadTable()
                except DatabaseError as db_error:
                    print("Ошибка при обновлении данных в PostgreSQL:", db_error)
                    QMessageBox.warning(self, "Ошибка БД", f"Сохранение изменений. {db_error.pgerror.split('CONTEXT:')[0].strip()}")
                    connection.rollback()
                except Exception as error:
                    print("Неожиданная ошибка:", error)
                    QMessageBox.warning(self, "Ошибка", f"Произошла ошибка: {error}")
                    connection.rollback()
                else:
                    connection.commit()
                    connection.close()


class ChangeExecutorDialog(QDialog):
    def __init__(self, contract_info, username, password, status):
        super().__init__()
        self.username = username
        self.password = password
        self.contract_info = contract_info
        self.status = status
        self.setWindowTitle("Выбор агента")
        self.setGeometry(400, 400, 600, 250)
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        connection = connect(self.username, self.password)
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    refresh materialized view vm_executors;
                    SELECT * FROM vm_executors;
                """)
                records = cursor.fetchall()
            except Exception as error:
                print("Ошибка при подгрузке данных с PostgreSQL:", error)
                QMessageBox.warning(self, "Ошибка БД", "Таблица агентов. Ошибка при подгрузке данных с БД.")
                cursor.close()
                connection.close()
            finally:
                cursor.close()
                connection.close()

        self.table.setRowCount(len(records))
        self.table.setColumnCount(len(records[0])) 
        headers = ["ФИО агента", "Компания", "Выбор агента"]
        self.table.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(records):
            for j, value in enumerate(row[1:]): 
                self.table.setItem(i, j, QTableWidgetItem(str(value)))
            choose_button = QPushButton("Выбрать")
            choose_button.clicked.connect(lambda _, i=i: self.confirm_executor(records[i][0]))
            self.table.setCellWidget(i, len(row) - 1, choose_button)
            self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.resizeColumnsToContents()
    
    def confirm_executor(self, executor_id):
        self.message = 'Ошибка при подгрузке данных с БД.'
        connection = connect(self.username, self.password)
        if connection:
            cursor = connection.cursor()
            try:
                if self.status == 'save':
                    self.message = 'Ошибка при сохранении данных.'
                    cursor.execute("SELECT id, full_name, phone_number, email, executor_position, company_name, executor_username FROM executor WHERE id = %s", (executor_id,))
                    data = cursor.fetchall()
                    self.contract_info.update_executor_def(executor_id, data[0][1], data[0][2], data[0][3], data[0][4], data[0][5])
                elif self.status == 'delete':
                    self.message = 'Вы не можете удалить агента, так как с ним существует договор в системе'
                    print(executor_id)
                    cursor.execute("SELECT executor_username FROM executor WHERE id = %s", (executor_id,))
                    data = cursor.fetchall()

                    cursor.execute("SELECT * FROM drop_user(%s, %s)", (executor_id, data[0][0]))
                    connection.commit()
                    QMessageBox.information(self, "Готово", "Агент удален из системы.")
                else:
                    QMessageBox.information(self, "Ошибка", "Неизвестный статус операции.")
            except Exception as error:
                print("Ошибка при подгрузке данных с PostgreSQL:", error)
                QMessageBox.warning(self, "Ошибка БД. Таблица агентов", self.message)
                cursor.close()
                connection.close()
            finally:
                cursor.close()
                connection.close()
            self.close()
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    app.exec()