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
                            QCalendarWidget)
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
        self.setFixedWidth(1450)
        self.setFixedHeight(420)
        self.table = QTableWidget()
        self.table.setFixedHeight(300)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        connection = connect(self.username, self.password)
        if connection:
            cursor = connection.cursor()
            try:
                if self.role == "head":
                    cursor.execute("SELECT h.full_name FROM head h WHERE h.head_username =  %s", (self.username,))
                    full_name_v = cursor.fetchone()[0]
                    self.welcome_label = QLabel(f"Здравствуйте, {full_name_v}!")
                    self.status = QLabel(f"Статус пользователя: Руководитель, Вы имеете полный доступ к договорам.")
                    self.layoutQV.addWidget(self.welcome_label)
                    self.layoutQV.addWidget(self.status)
                elif self.role == "executor":
                    cursor.execute("SELECT ex.full_name FROM executor ex WHERE ex.executor_username = %s", (self.username,))
                    full_name_v = cursor.fetchone()[0]
                    self.welcome_label = QLabel(f"Здравствуйте, {full_name_v}!")
                    self.status = QLabel(f"Статус пользователя: Агент, Вы можете редактировать разрешенную информацию только в течении статуса 'Создано'.")
                    self.status_add = QLabel(f"Как только статус договора будет изменен Руководителем - дальнейшее редактирование недоступно.")
                    self.layoutQV.addWidget(self.welcome_label)
                    self.layoutQV.addWidget(self.status)
                    self.layoutQV.addWidget(self.status_add)
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
                    cursor.execute("SELECT cn.id, cn.contract_num, cn.status, cn.agreement_object, h.full_name as head_name, " +
                                "ex.full_name as executor_name, ex.company_name, cn.conclusion_date, cn.agreement_term "+
                                "FROM contract cn JOIN head h ON cn.head_id = h.id JOIN executor ex ON cn.executor_id = ex.id")
                elif self.role == "executor":
                    cursor.execute("SELECT cn.id, cn.contract_num, cn.status, cn.agreement_object, h.full_name as head_name, "+
                                "ex.full_name as executor_name, ex.company_name, cn.conclusion_date, cn.agreement_term "+
                                "FROM contract cn JOIN head h ON cn.head_id = h.id JOIN executor ex ON cn.executor_id = ex.id "+
                                "WHERE ex.executor_username = %s", (self.username,))
                records = cursor.fetchall()
            except Exception as error:
                print("Ошибка при подгрузке данных с PostgreSQL:", error)
                QMessageBox.warning(self, "Ошибка БД", "Ошибка при подгрузке данных с БД.")
                cursor.close()
                connection.close()
            finally:
                cursor.close()
                connection.close()

        self.table.setRowCount(len(records))
        self.table.setColumnCount(len(records[0])) 
        headers = ["Номер договора", "Статус", "Наименование договора", "ФИО руководителя",
                   "ФИО агента", "Компания", "Дата заключения", "Срок действия", "Полная информация"]
        self.table.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(records):
            for j, value in enumerate(row[1:]): 
                self.table.setItem(i, j, QTableWidgetItem(str(value)))
            open_button = QPushButton("Открыть")
            open_button.clicked.connect(lambda _, i=i: self.openContract(records[i][0])) 
            self.table.setCellWidget(i, len(row) - 1, open_button)  
        self.table.resizeColumnsToContents()

    def openContract(self, contract_id): 
        headers = ["Номер договора",
                   "Статус",
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
                        cn.status AS "Статус", 
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
            except Exception as error:
                print("Ошибка при подгрузке данных с PostgreSQL:", error)
                QMessageBox.warning(self, "Ошибка БД", "Данные контракта. Ошибка при подгрузке данных с БД.")
                cursor.close()
                connection.close()
            finally:
                cursor.close()
                connection.close()
        
        self.fields = {}  

        for header, value in zip(headers, result):
            label = QLabel(header)
            if header == "Статус":
                combo_box = QComboBox()
                combo_box.addItems(["Создан", "Согласован/В работе", "Закрыт"])
                combo_box.setCurrentText(value)
                layout.addWidget(label)
                layout.addWidget(combo_box)
                self.fields[header] = combo_box
                if role == "executor": combo_box.setEnabled(False)
            elif header in ["Дата заключения", "Срок действия"]:
                calendar_widget = QCalendarWidget()
                calendar_widget.setSelectedDate(value)
                h_layout = QHBoxLayout()
                h_layout.addWidget(label)
                h_layout.addWidget(calendar_widget)
                layout.addLayout(h_layout)
                self.fields[header] = calendar_widget
            elif header == "Дополнительные условия":
                text_edit = QTextEdit()
                text_edit.setPlainText(value)
                h_layout = QHBoxLayout()
                h_layout.addWidget(label)
                h_layout.addWidget(text_edit)
                layout.addLayout(h_layout)
                self.fields[header] = text_edit
            elif role == "head" and header not in ["ФИО агента", "Номер телефона агента", "Почта агента", "Позиция агента", "Компания"]:
                line_edit = QLineEdit(str(value))
                line_edit.setReadOnly(False)
                h_layout = QHBoxLayout()
                h_layout.addWidget(label)
                h_layout.addWidget(line_edit)
                layout.addLayout(h_layout)
                self.fields[header] = line_edit
            elif role == "executor" and header not in ["Номер договора", "Наименование договора", "ФИО руководителя", "Номер телефона руководителя", "Почта руководителя"]:
                line_edit = QLineEdit(str(value))
                line_edit.setReadOnly(False)
                h_layout = QHBoxLayout()
                h_layout.addWidget(label)
                h_layout.addWidget(line_edit)
                layout.addLayout(h_layout)
                self.fields[header] = line_edit
            else:
                line_edit = QLineEdit(str(value))
                line_edit.setReadOnly(True)
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

    def validate_fields(self):
        for header, widget in self.fields.items():
            if isinstance(widget, QLineEdit):
                if not widget.text():
                    QMessageBox.warning(self, "Пустое поле", f"Поле '{header}' не должно быть пустым.")
                    return False
                elif header in ["Номер телефона руководителя", "Номер телефона агента"]:
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
                            self.fields["Дата заключения"].selectedDate().toString("dd-MM-yyyy"),
                            self.fields["Срок действия"].selectedDate().toString("dd-MM-yyyy"),
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
                                document_scan = %s 
                            WHERE id = %s;
                        """
                        cursor.execute(update_contract, (
                            self.fields["Номер договора"].text(),
                            self.fields["Статус"].currentText(),
                            self.fields["Наименование договора"].text(),
                            self.fields["Дата заключения"].selectedDate().toString("yyyy-MM-dd"),
                            self.fields["Срок действия"].selectedDate().toString("yyyy-MM-dd"),
                            self.fields["Скан документа"].text(),
                            self.contract_id
                        ))

                        update_executor = """
                        UPDATE head AS h
                        SET 
                            full_name = %s,
                            phone_number = %s,
                            email = %s
                        WHERE 
                            h.id = (SELECT head_id FROM contract WHERE id = %s);
                        """
                        cursor.execute(update_executor, (
                            self.fields["ФИО руководителя"].text(),
                            self.fields["Номер телефона руководителя"].text(),
                            self.fields["Почта руководителя"].text(),
                            self.contract_id
                        ))

                        connection.commit()
                        self.main_window.reloadTable()
                        QMessageBox.information(self, "Успех", "Данные успешно обновлены.")
                except Exception as error:
                    print("Ошибка при обновлении данных в PostgreSQL:", error)
                    QMessageBox.warning(self, "Ошибка БД", "Сохранение изменений. Ошибка при обновлении данных в БД.")
                    connection.rollback()
                else:
                    connection.commit()
                finally:
                    cursor.close()
                    connection.close()
                    super().accept()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    app.exec()

 