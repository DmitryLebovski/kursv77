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
            except Exception as error:
                print("Ошибка при выполнении SQL запроса:", error)
                QMessageBox.warning(self, "Ошибка БД", "Ошибка при выполнении SQL запроса.")
                cursor.close()
                connection.close()
            finally:
                cursor.close()
                connection.close()
        else:
            QMessageBox.warning(self, "Ошибка входа", "Неверное имя полльзователя или пароль.")

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
        self.setFixedWidth(1550)
        self.table = QTableWidget()
        self.table.setFixedHeight(250)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        connection = connect(self.username, self.password)
        if connection:
            cursor = connection.cursor()
            try:
                panel_view = QHBoxLayout()
                panel_view.setAlignment(Qt.AlignmentFlag.AlignLeft)
                update_buttom = QPushButton("Обновить таблицу")
                update_buttom.setFixedWidth(180)
                update_buttom.clicked.connect(self.reloadTable)
                panel_view.addWidget(update_buttom)

                if self.role == "head":
                    cursor.execute("SELECT id, full_name FROM head WHERE head_username =  %s", (self.username,))
                    self.data = cursor.fetchall()
                    self.full_name_v = self.data[0][1]
                    self.id_head = self.data[0][0]
                    self.welcome_label = QLabel(f"Здравствуйте, {self.full_name_v}!")
                    self.status = QLabel(f"Статус пользователя: Руководитель, Вы имеете полный доступ к договорам.")
                    self.layoutQV.addWidget(self.welcome_label)
                    self.layoutQV.addWidget(self.status)
                    self.setFixedHeight(470)
                    add_buttom = QPushButton("Добавить договор")
                    add_buttom.setFixedWidth(180)
                    add_buttom.clicked.connect(self.add_contract)
                    panel_view.addWidget(add_buttom)

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
                    cursor.execute("SELECT ex.full_name FROM executor ex WHERE ex.executor_username = %s", (self.username,))
                    full_name_v = cursor.fetchone()[0]
                    self.welcome_label = QLabel(f"Здравствуйте, {full_name_v}!")
                    self.status = QLabel(f"Статус пользователя: Агент, Вы можете редактировать разрешенную информацию только в течении статуса 'Создано'.")
                    self.status_add = QLabel(f"Как только статус договора будет изменен Руководителем - дальнейшее редактирование недоступно.")
                    self.layoutQV.addWidget(self.welcome_label)
                    self.layoutQV.addWidget(self.status)
                    self.layoutQV.addWidget(self.status_add)
                    self.setFixedHeight(460)
                self.layoutQV.addLayout(panel_view)
            except Exception as error:
                print("Ошибка при подгрузке данных с PostgreSQL:", error)
                QMessageBox.warning(self, "Ошибка БД", "Ошибка при подгрузке данных с БД.")
                cursor.close()
                connection.close()
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
                    cursor.execute("SELECT cn.id, cn.contract_num, cn.status, cn.agreement_object, h.full_name as head_name, "+
                                "ex.full_name as executor_name, ex.company_name, cn.conclusion_date, cn.agreement_term "+
                                "FROM contract cn JOIN head h ON cn.head_id = h.id JOIN executor ex ON cn.executor_id = ex.id "+
                                "WHERE ex.executor_username = %s", (self.username,))
                records = cursor.fetchall()

                if not records:
                    QMessageBox.information(self, "Пусто", "Записи отсутствуют.")
                    self.table.setRowCount(0)
                    return

            except Exception as error:
                print("Ошибка при подгрузке данных с PostgreSQL:", error)
                QMessageBox.warning(self, "Ошибка БД", "Ошибка при подгрузке данных с БД.")
                cursor.close()
                connection.close()
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


    def confirm_delete(self, contract_id):
        confirm_dialog = QMessageBox.question(self, "Подтверждение удаления",
                                                "Вы уверены, что хотите удалить договор?",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm_dialog == QMessageBox.StandardButton.Yes:
            self.delete_contract(contract_id)
        else:
            pass 

    def delete_contract(self, contract_id):
        connection = connect(self.username, self.password)
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("DELETE FROM extra_condition WHERE contract_id = %s", (contract_id,))
                cursor.execute("DELETE FROM contract WHERE id = %s", (contract_id,))
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
                   "Номер телефона руководителя",
                   "Почта руководителя",
                   "ФИО агента",
                   "Номер телефона агента",
                   "Почта агента",
                   "Позиция агента",
                   "Компания",
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
                   "Номер телефона руководителя",
                   "Почта руководителя",
                   "ФИО агента",
                   "Номер телефона агента",
                   "Почта агента",
                   "Позиция агента",
                   "Компания",
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
        self.executors_window = AddExecuterWindow(self.username, self.password, self.id_head)
        self.executors_window.exec()

class AddExecuterWindow(QDialog):
    def __init__(self, username, password, head_id):
        super().__init__()
        self.setWindowTitle("Добавление агента")
        self.setGeometry(0, 0, 500, 400)
        layout = QVBoxLayout()
        self.username = username
        self.password = password
        self.head_id = head_id

        headers = ["ФИО агента",
                   "Номер телефона агента(не обязательно)",
                   "Почта агента",
                   "Позиция агента",
                   "Компания(не обязательно)",
                   "Имя пользователя",
                   "Пароль"]

        self.fields = {}  

        for header in headers:
            label = QLabel(header)
            line_edit = QLineEdit()
            if header == 'Пароль': line_edit.setEchoMode(QLineEdit.EchoMode.Password)
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
            connection = connect('postgres', 'placeholder_password')
            if connection:
                cursor = connection.cursor()
                try:
                        cursor.execute("SELECT full_name, id FROM head WHERE head_username =  %s", (self.username,))
                        self.full_name_v = cursor.fetchone()[0]
                        
                        add_executor = """
                            INSERT INTO executor 
                                (full_name, phone_number, email, company_name, executor_position, executor_username, head_id) 
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s);
                        """    
                        cursor.execute(add_executor, (
                            self.fields["ФИО агента"].text(),
                            self.fields["Номер телефона агента(не обязательно)"].text(),
                            self.fields["Почта агента"].text(),
                            self.fields["Компания(не обязательно)"].text(),
                            self.fields["Позиция агента"].text(),
                            self.fields["Имя пользователя"].text(),
                            self.head_id
                        ))

                        create_executor = f"""
                        CREATE USER {self.fields["Имя пользователя"].text()} PASSWORD '{self.fields["Пароль"].text()}';
                        """
                        cursor.execute(create_executor)
                        grant_role = f"""
                        GRANT executor TO {self.fields["Имя пользователя"].text()};
                        """
                        cursor.execute(grant_role)
                        connection.commit()
                        QMessageBox.information(self, "Успех", f"Руководитель '{self.full_name_v}' успешно добавил своего агента.")
                except Exception as error:
                    print("Ошибка при обновлении данных в PostgreSQL:", error)
                    QMessageBox.warning(self, "Ошибка БД", "Добавление контракта. Ошибка при обновлении данных в БД.")
                    connection.rollback()
                    cursor.close()
                    connection.close()
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
            elif header in ["ФИО руководителя", "Номер телефона руководителя", "Почта руководителя"]:
                match header:
                    case "ФИО руководителя":
                        h_name = QLineEdit(str(self.data[0][1]))
                        h_name.setReadOnly(False)
                        h_layout = QHBoxLayout()
                        h_layout.addWidget(label)
                        h_layout.addWidget(h_name)
                        layout.addLayout(h_layout)
                        self.fields[header] = h_name
                    case "Номер телефона руководителя": 
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
            elif header in ["ФИО агента", "Номер телефона агента", "Почта агента", "Позиция агента", "Компания"]:
                match header:
                    case "ФИО агента":
                        self.ex_name = QLineEdit()
                        self.ex_name.setEnabled(False)
                        h_layout = QHBoxLayout()
                        h_layout.addWidget(label)
                        h_layout.addWidget(self.ex_name)
                        layout.addLayout(h_layout)
                        self.fields[header] = self.ex_name
                    case "Номер телефона агента":
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
                    case "Компания":
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
                if not widget.text() and header not in ["Номер телефона руководителя", "Номер телефона агента", "Компания", "Скан документа", "Дополнительные условия"]:
                    QMessageBox.warning(self, "Пустое поле", f"Поле '{header}' не должно быть пустым.")
                    return False
                    
                if widget.text() and header in ["Номер телефона руководителя", "Номер телефона агента"]:
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
                        add_contract = """
                            INSERT INTO contract 
                                (contract_num, conclusion_date, agreement_term, agreement_object, status, executor_id, head_id) 
                            VALUES
                                (%s, %s, %s, %s, 'Создан', %s, %s);
                        """    
                        cursor.execute(add_contract, (
                            self.fields["Номер договора"].text(),
                            self.fields["Дата заключения"].selectedDate().toString("yyyy-MM-dd"),
                            self.fields["Срок действия"].selectedDate().toString("yyyy-MM-dd"),
                            self.fields["Наименование договора"].text(),
                            self.ex_id,
                            self.data[0][0]
                        ))

                        add_extra_condition = """
                            INSERT INTO extra_condition 
                                (agreement_extras, contract_id) 
                            VALUES 
                                (%s, (SELECT id FROM contract WHERE contract_num = %s));
                        """
                        cursor.execute(add_extra_condition, (
                            self.fields["Дополнительные условия"].toPlainText(),
                            self.fields["Номер договора"].text()
                        ))

                        update_head = """
                        UPDATE head AS h
                        SET 
                            full_name = %s,
                            phone_number = %s,
                            email = %s
                        WHERE 
                            h.id = (SELECT head_id FROM contract WHERE contract_num = %s);
                        """
                        cursor.execute(update_head, (
                            self.fields["ФИО руководителя"].text(),
                            self.fields["Номер телефона руководителя"].text(),
                            self.fields["Почта руководителя"].text(),
                            self.fields["Номер договора"].text()
                        ))
                        connection.commit()
                        self.main_window.reloadTable()
                        QMessageBox.information(self, "Успех", "Данные успешно добавлены.")
                except Exception as error:
                    print("Ошибка при обновлении данных в PostgreSQL:", error)
                    QMessageBox.warning(self, "Ошибка БД", "Добавление контракта. Ошибка при обновлении данных в БД.")
                    connection.rollback()
                    cursor.close()
                    connection.close()
                else:
                    connection.commit()
                finally:
                    cursor.close()
                    connection.close()
                    super().accept()
            self.close()

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
                    SELECT 
                        cn.contract_num AS "Номер договора", 
                        cn.agreement_object AS "Наименование договора", 
                        h.full_name AS "ФИО руководителя", 
                        h.phone_number AS "Номер телефона руководителя", 
                        h.email AS "Почта руководителя", 
                        ex.full_name AS "ФИО агента",
                        ex.phone_number AS "Номер телефона агента", 
                        ex.email AS "Почта агента",
                        ex.executor_position AS "Позиция агента",
                        ex.company_name AS "Компания", 
                        cn.conclusion_date AS "Дата заключения", 
                        cn.agreement_term AS "Срок действия",
                        cn.document_scan AS "Скан документа",
                        exc.agreement_extras AS "Дополнительные условия"
                    FROM 
                        contract cn
                    JOIN 
                        head h ON cn.head_id = h.id
                    JOIN 
                        executor ex ON cn.executor_id = ex.id
                    LEFT JOIN 
                        extra_condition exc ON cn.id = exc.contract_id
                    WHERE cn.id = %s""", (contract_id,))
                result = cursor.fetchone()

                cursor.execute("""
                    SELECT status FROM contract WHERE id = %s""", (contract_id,))
                status = cursor.fetchone()[0]
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
            elif role == "head" and header not in ["ФИО агента", "Номер телефона агента", "Почта агента", "Позиция агента", "Компания"]:
                line_edit = QLineEdit(str(value))
                line_edit.setReadOnly(False)
                h_layout = QHBoxLayout()
                h_layout.addWidget(label)
                h_layout.addWidget(line_edit)
                layout.addLayout(h_layout)
                self.fields[header] = line_edit
                if combo_box.currentText() in ["Согласован", "Закрыт"]: line_edit.setEnabled(False)
            elif role == "executor" and header not in ["Номер договора", "Наименование договора", "ФИО руководителя", "Номер телефона руководителя", "Почта руководителя"]:
                line_edit = QLineEdit(str(value))
                line_edit.setReadOnly(False)
                h_layout = QHBoxLayout()
                h_layout.addWidget(label)
                h_layout.addWidget(line_edit)
                layout.addLayout(h_layout)
                self.fields[header] = line_edit
                if combo_box.currentText() in ["Согласован", "Закрыт"]: line_edit.setEnabled(False)
            elif role == "head" and header in ["ФИО агента", "Номер телефона агента", "Почта агента", "Позиция агента", "Компания"]:
                match header:
                    case "ФИО агента":
                        self.ex_name = QLineEdit(str(value))
                        self.ex_name.setEnabled(False)
                        h_layout = QHBoxLayout()
                        h_layout.addWidget(label)
                        h_layout.addWidget(self.ex_name)
                        layout.addLayout(h_layout)
                        self.fields[header] = self.ex_name
                    case "Номер телефона агента":
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
                    case "Компания":
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
                if not widget.text() and header not in ["Номер телефона руководителя", "Номер телефона агента" , "Компания", "Скан документа", "Дополнительные условия"]:
                    QMessageBox.warning(self, "Пустое поле", f"Поле '{header}' не должно быть пустым.")
                    return False
                
                if widget.text() and header in ["Номер телефона руководителя", "Номер телефона агента"]:
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
                try:
                    if self.role == "executor":
                        update_contract = """
                            UPDATE contract
                            SET 
                                conclusion_date = %s, 
                                agreement_term = %s,
                                document_scan = %s
                            WHERE id = %s;
                        """
                        cursor.execute(update_contract, (
                            self.fields["Дата заключения"].selectedDate().toString("yyyy-MM-dd"),
                            self.fields["Срок действия"].selectedDate().toString("yyyy-MM-dd"),
                            self.fields["Скан документа"].text(),
                            self.contract_id
                        ))

                        update_executor = """
                            UPDATE executor AS ex
                            SET 
                                full_name = %s,
                                phone_number = %s,
                                email = %s,
                                executor_position = %s,
                                company_name = %s
                            WHERE 
                                ex.id = (SELECT executor_id FROM contract WHERE id = %s);
                        """
                        cursor.execute(update_executor, (
                            self.fields["ФИО агента"].text(),
                            self.fields["Номер телефона агента"].text(),
                            self.fields["Почта агента"].text(),
                            self.fields["Позиция агента"].text(),
                            self.fields["Компания"].text(),
                            self.contract_id
                        ))

                        update_extra_condition = """
                            UPDATE extra_condition AS exc
                            SET 
                                agreement_extras = %s
                            FROM contract cn
                            WHERE 
                                cn.id = exc.contract_id
                                AND cn.id = %s;
                        """
                        cursor.execute(update_extra_condition, (
                            self.fields["Дополнительные условия"].toPlainText(),
                            self.contract_id
                        ))
                        connection.commit()
                        QMessageBox.information(self, "Успех", "Данные успешно обновлены.")
                        self.main_window.reloadTable()
                    else:
                        update_contract = """
                            UPDATE contract
                            SET 
                                contract_num = %s, 
                                status = %s, 
                                agreement_object = %s, 
                                conclusion_date = %s, 
                                agreement_term = %s, 
                                document_scan = %s,
                                executor_id = (SELECT id FROM executor WHERE full_name = %s)
                            WHERE id = %s;
                        """
                        cursor.execute(update_contract, (
                            self.fields["Номер договора"].text(),
                            self.fields["Статус"].currentText(),
                            self.fields["Наименование договора"].text(),
                            self.fields["Дата заключения"].selectedDate().toString("yyyy-MM-dd"),
                            self.fields["Срок действия"].selectedDate().toString("yyyy-MM-dd"),
                            self.fields["Скан документа"].text(),
                            self.fields["ФИО агента"].text(),
                            self.contract_id
                        ))

                        update_head = """
                        UPDATE head AS h
                        SET 
                            full_name = %s,
                            phone_number = %s,
                            email = %s
                        WHERE 
                            h.id = (SELECT head_id FROM contract WHERE id = %s);
                        """
                        cursor.execute(update_head, (
                            self.fields["ФИО руководителя"].text(),
                            self.fields["Номер телефона руководителя"].text(),
                            self.fields["Почта руководителя"].text(),
                            self.contract_id
                        ))
                        
                        update_extra_condition = """
                            UPDATE extra_condition AS exc
                            SET 
                                agreement_extras = %s
                            FROM contract cn
                            WHERE 
                                cn.id = exc.contract_id
                                AND cn.id = %s;
                        """
                        cursor.execute(update_extra_condition, (
                            self.fields["Дополнительные условия"].toPlainText(),
                            self.contract_id
                        ))
                        connection.commit()
                        self.main_window.reloadTable()
                        QMessageBox.information(self, "Успех", "Данные успешно обновлены.")
                except Exception as error:
                    print("Ошибка при обновлении данных в PostgreSQL:", error)
                    QMessageBox.warning(self, "Ошибка БД", "Сохранение изменений. Ошибка при обновлении данных в БД. Номер контракта уже существует")
                    connection.rollback()
                    cursor.close()
                    connection.close()
                else:
                    connection.commit()
                finally:
                    cursor.close()
                    connection.close()
                    super().accept()
            self.close()

class ChangeExecutorDialog(QDialog):
    def __init__(self, contract_info, username, password, status):
        super().__init__()
        self.username = username
        self.password = password
        self.contract_info = contract_info
        self.status = status
        self.setWindowTitle("Выбор агента")
        self.setGeometry(400, 400, 550, 250)
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
        self.table.resizeColumnsToContents()
    
    def confirm_executor(self, executor_id):
        self.message = 'Ошибка при подгрузке данных с БД.'
        connection = connect(self.username, self.password)
        if connection:
            cursor = connection.cursor()
            try:
                if self.status == 'save':
                    self.message = 'Ошибка при сохранении данных.'
                    cursor.execute("SELECT id, full_name, phone_number, email, executor_position, company_name FROM executor WHERE id = %s", (executor_id,))
                    data = cursor.fetchall()
                    self.contract_info.update_executor_def(executor_id, data[0][1], data[0][2], data[0][3], data[0][4], data[0][5])
                elif self.status == 'delete':
                    self.message = 'Вы не можете удалить агента, так как с ним существует договор в системе'
                    print(executor_id)
                    cursor.execute("DELETE FROM executor WHERE id = %s", (executor_id,))
                    #TODO: продумать удаление из user
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