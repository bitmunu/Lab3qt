import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, \
                 QPushButton, QDialog, QVBoxLayout, QLineEdit, QLabel
from PyQt5.QtGui import *
from PyQt5.QtWidgets import*
from PyQt5.QtCore import *


class FilmApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("movies")
        self.setGeometry(550, 250, 1000, 749)
        #self.setAutoFillBackground(True)
        #self.setStyleSheet("background-image: url(yes.jpg); background-attachment: fixed")
        #self.setStyleSheet("'background-color: White;' background-attachment: fixed")

        label = QLabel(self)
        pixmap = QPixmap('yes.jpg')
        label.setPixmap(pixmap)
        self.setCentralWidget(label)
        label.setScaledContents(2)
        label.move(400, 400)

        self.table_widget = QTableWidget(self)
        self.table_widget.setGeometry(0, 0, 400, 320)
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["название", "год выпуска", "длительность", "жанр"])
        self.table_widget.setStyleSheet('background-color: Black;')
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.load_data()

        add_button = QPushButton("добавить", self)
        add_button.setGeometry(250, 340, 80, 20)
        add_button.setStyleSheet('background-color: White;')
        add_button.clicked.connect(self.add_film)

        delete_button = QPushButton("удалить", self)
        delete_button.setGeometry(250, 380, 80, 20)
        delete_button.setStyleSheet('background-color: White;')
        delete_button.clicked.connect(self.delete_film)

        self.table_widget.itemDoubleClicked.connect(self.on_item_double_clicked)

    def load_data(self):
        connection = sqlite3.connect("films_db.sqlite")
        cursor = connection.cursor()
        cursor.execute("SELECT f.title, f.year, f.duration, g.title AS genre "
                       "FROM films f JOIN genres g ON f.genre = g.id")
        films = cursor.fetchall()
        connection.close()

        self.table_widget.setRowCount(len(films))

        for row, film in enumerate(films):
            for col, value in enumerate(film):
                self.table_widget.setItem(row, col, QTableWidgetItem(str(value)))
        #self.table_widget.setAutoFillBackground(True)
        p = self.table_widget.palette()
        p.setColor(self.table_widget.backgroundRole(), Qt.white)
        self.table_widget.setStyleSheet('background-color: White;')


    def save_entry(self, dia, name, year, duration, genre, rowid=None):
        connection = sqlite3.connect("films_db.sqlite")
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM genres WHERE title = ?", (genre,))
        genre_id = cursor.fetchone()

        if not genre_id:
            cursor.execute("INSERT INTO genres (title) VALUES (?)", (genre,))
            connection.commit()
            cursor.execute("SELECT id FROM genres WHERE title = ?", (genre,))
            genre_id = cursor.fetchone()

        genre_id = genre_id[0]

        if rowid is None:
            cursor.execute("INSERT INTO films (title, year, duration, genre) VALUES (?, ?, ?, ?)",
                           (name, year, duration, genre_id))
        else:
            cursor.execute("UPDATE films SET title = ?, year = ?, duration = ?, genre = ? WHERE rowid = ?",
                           (name, year, duration, genre_id, rowid))
        connection.commit()
        connection.close()
        self.load_data()
        dia.close()

    def add_film(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("question?mark")
        layout = QVBoxLayout()

        name_label = QLabel("название:")
        name_input = QLineEdit()
        layout.addWidget(name_label)
        layout.addWidget(name_input)

        year_label = QLabel("год выпуска:")
        year_input = QLineEdit()
        layout.addWidget(year_label)
        layout.addWidget(year_input)

        duration_label = QLabel("длительность:")
        duration_input = QLineEdit()
        layout.addWidget(duration_label)
        layout.addWidget(duration_input)

        genre_label = QLabel("жанр:")
        genre_input = QLineEdit()
        layout.addWidget(genre_label)
        layout.addWidget(genre_input)

        save_button = QPushButton("сохранить", dialog)
        save_button.clicked.connect(lambda: self.save_entry(dialog, name_input.text(), year_input.text(),
                                                            duration_input.text(), genre_input.text() ))
        layout.addWidget(save_button)
        dialog.setLayout(layout)
        dialog.exec_()

    def delete_film(self):
        selected_row = self.table_widget.currentRow()
        if selected_row >= 0:
            connection = sqlite3.connect("films_db.sqlite")
            cursor = connection.cursor()
            cursor.execute("SELECT rowid FROM films LIMIT 1 OFFSET ?", (selected_row,))
            rowid = cursor.fetchone()[0]
            cursor.execute("DELETE FROM films WHERE rowid = ?", (rowid,))
            connection.commit()
            connection.close()
            self.load_data()

    def save_and_edit(self, name, year, duration, genre, ri=None):
        self.save_film(name, year, duration, genre, ri)

    def on_item_double_clicked(self, item):
        row = item.row()
        film_data = [self.table_widget.item(row, col).text() for col in range(4)]
        connection = sqlite3.connect("films_db.sqlite")
        cursor = connection.cursor()
        cursor.execute("SELECT rowid FROM films LIMIT 1 OFFSET ?", (row,))
        rowid = cursor.fetchone()[0]
        connection.close()

        dialog = QDialog(self)
        dialog.setWindowTitle("edit")
        layout = QVBoxLayout()

        name_label = QLabel("название:")
        name_input = QLineEdit(film_data[0])
        layout.addWidget(name_label)
        layout.addWidget(name_input)

        year_label = QLabel("год выпуска:")
        year_input = QLineEdit(film_data[1])
        layout.addWidget(year_label)
        layout.addWidget(year_input)

        duration_label = QLabel("длительность:")
        duration_input = QLineEdit(film_data[2])
        layout.addWidget(duration_label)
        layout.addWidget(duration_input)

        genre_label = QLabel("жанр:")
        genre_input = QLineEdit(film_data[3])
        layout.addWidget(genre_label)
        layout.addWidget(genre_input)

        save_button = QPushButton("сохранить", dialog)
        save_button.clicked.connect(
            lambda: self.save_entry(dialog, name_input.text(), year_input.text(), duration_input.text(), genre_input.text(), rowid))
        #save_button.clicked.connect(self.save_and_edit(name_input.text(), year_input.text(), duration_input.text(), genre_input.text(), rowid))
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec_()



app = QApplication(sys.argv)
window = FilmApp()
window.show()
sys.exit(app.exec_())