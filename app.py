import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem
from db import connect

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        layout = QVBoxLayout()

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
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
            
                QMessageBox.warning(self, "Login Error", "Invalid username or password.")
            except Exception as error:
                print("Error while executing SQL query:", error)
                QMessageBox.warning(self, "Database Error", "Error while executing SQL query.")
            finally:
                cursor.close()
                connection.close()
        else:
            QMessageBox.warning(self, "Database Error", "Failed to connect to the database.")

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
        self.setWindowTitle("Contract Details")
        layout = QVBoxLayout()
        self.setGeometry(100, 100, 800, 700)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        connection = connect(username, password)
        if connection:
            cursor = connection.cursor()
            try:
                if role == "head":
                    cursor.execute("SELECT cn.contract_num, cn.status, cn.agreement_object, h.full_name as head_name, ex.full_name as executor_name, ex.company_name, cn.conclusion_date, cn.agreement_term FROM contract cn JOIN head h ON cn.head_id = h.id JOIN executor ex ON cn.executor_id = ex.id")
                elif role == "executor":
                    cursor.execute("SELECT cn.contract_num, cn.status, cn.agreement_object, h.full_name as head_name, ex.full_name as executor_name, ex.company_name, cn.conclusion_date, cn.agreement_term FROM contract cn JOIN head h ON cn.head_id = h.id JOIN executor ex ON cn.executor_id = ex.id WHERE ex.executor_username = %s", (username,))
                records = cursor.fetchall()
                self.populateTable(records)
            except Exception as error:
                print("Error while fetching data from PostgreSQL:", error)
                QMessageBox.warning(self, "Database Error", "Failed to fetch data from the database.")
            finally:
                cursor.close()
                connection.close()

        self.setLayout(layout)

    def populateTable(self, records):
        self.table.setRowCount(len(records))
        self.table.setColumnCount(len(records[0]))
        headers = ["Номер договора", "Статус", "Наименование договора", "ФИО руководителя", "ФИО агента", "Компания", "Дата заключения", "Срок действия"]
        self.table.setHorizontalHeaderLabels(headers)

        for i, row in enumerate(records):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
