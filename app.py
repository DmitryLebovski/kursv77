import sys
from PyQt6.QtWidgets import (QApplication, 
                            QWidget, 
                            QVBoxLayout, 
                            QLabel, 
                            QLineEdit, 
                            QPushButton, 
                            QMessageBox, 
                            QTableWidget,
                            QTableWidgetItem, 
                            QDialog, 
                            QDialogButtonBox)
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
        layout = QVBoxLayout()
        self.setFixedWidth(1440)
        
        self.table = QTableWidget()
        self.table.setFixedHeight(300) 
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        connection = connect(username, password)
        if connection:
            cursor = connection.cursor()
            try:
                if role == "head":
                    cursor.execute("SELECT h.full_name FROM head h WHERE h.head_username =  %s", (self.username,))
                    full_name_v = cursor.fetchone()[0]
                    self.welcome_label = QLabel(f"Здравствуйте, {full_name_v}!")
                    self.status = QLabel(f"Статус пользователя: Руководитель, Вы можете редактировать, добавлять, согласовывать, закрывать договоры")
                    layout.addWidget(self.welcome_label)
                    layout.addWidget(self.status)
                    cursor.execute("SELECT cn.contract_num, cn.status, cn.agreement_object, h.full_name as head_name, " + 
                                   "ex.full_name as executor_name, ex.company_name, cn.conclusion_date, cn.agreement_term "+
                                   "FROM contract cn JOIN head h ON cn.head_id = h.id JOIN executor ex ON cn.executor_id = ex.id")
                elif role == "executor":
                    cursor.execute("SELECT ex.full_name FROM executor ex WHERE ex.executor_username = %s", (self.username,))
                    full_name_v = cursor.fetchone()[0]
                    self.welcome_label = QLabel(f"Здравствуйте, {full_name_v}!")
                    self.status = QLabel(f"Статус пользователя: Агент, Вы можете редактировать только Дату заключения, Срок действия, Скан документа и Доп. информацию только в течении статуса 'Создано'")
                    self.status_add = QLabel(f"Как только статус договора будет изменен Руководителем - дальнейшее редактирование запрещено")
                    layout.addWidget(self.welcome_label)
                    layout.addWidget(self.status)
                    layout.addWidget(self.status_add)
                    cursor.execute("SELECT cn.contract_num, cn.status, cn.agreement_object, h.full_name as head_name, "+
                                   "ex.full_name as executor_name, ex.company_name, cn.conclusion_date, cn.agreement_term "+
                                   "FROM contract cn JOIN head h ON cn.head_id = h.id JOIN executor ex ON cn.executor_id = ex.id "+
                                   "WHERE ex.executor_username = %s", (username,))
                records = cursor.fetchall()
                self.populateTable(records)
            except Exception as error:
                print("Ошибка при подгрузке данных с PostgreSQL:", error)
                QMessageBox.warning(self, "Ошибка БД", "Ошибка при подгрузке данных с БД.")
                cursor.close()
                connection.close()
            finally:
                cursor.close()
                connection.close()

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.logout_button = QPushButton("Выйти")
        self.logout_button.clicked.connect(self.logout)
        layout.addWidget(self.logout_button)

    def logout(self):
        login_window = LoginWindow()
        login_window.show()
        self.close()

    def populateTable(self, records):
        self.table.setRowCount(len(records))
        self.table.setColumnCount(len(records[0]) + 1) 
        headers = ["Номер договора", "Статус", "Наименование договора", "ФИО руководителя", 
                   "ФИО агента", "Компания", "Дата заключения", "Срок действия", "Полная информация"]
        self.table.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(records):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))
            open_button = QPushButton("Открыть")
            open_button.clicked.connect(lambda _, i=i: self.openContract(i))
            self.table.setCellWidget(i, len(row), open_button)
        self.table.resizeColumnsToContents()

    def openContract(self, row_index):
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
        contract_data = self.table.item(row_index, 0).text()
        contract_window = ContractWindow(self.username, self.password, self.role, contract_data, headers)
        contract_window.exec()

class ContractWindow(QDialog):
    def __init__(self, username, password, role, contract_data, headers):
        super().__init__()
        self.setWindowTitle("Данные договора")
        self.setGeometry(0, 0, 300, 900)
        layout = QVBoxLayout()
        self.username = username
        self.password = password

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
                    WHERE cn.contract_num = %s""", (contract_data,))
                result = cursor.fetchall()
            except Exception as error:
                print("Ошибка при подгрузке данных с PostgreSQL:", error)
                QMessageBox.warning(self, "Ошибка БД", "Данные контракта. Ошибка при подгрузке данных с БД.")
                cursor.close()
                connection.close()
            finally:
                cursor.close()
                connection.close()

        for row in result:
            for i, (value, header) in enumerate(zip(row, headers)):
                label = QLabel(header)
                line_edit = QLineEdit()
                line_edit.setText(str(value))
                if role == "head" or headers[i] in ["Дата заключения", "Срок действия", "Скан документа", "Дополнительные условия"]:
                    line_edit.setReadOnly(False)
                else:
                    line_edit.setReadOnly(True)
                layout.addWidget(label)
                layout.addWidget(line_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    app.exec()
