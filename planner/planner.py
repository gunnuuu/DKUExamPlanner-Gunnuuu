import sys
from datetime import datetime
import os
import json
import sys
sys.path.append('C:\\Users\\pkunw\\OneDrive\\바탕 화면\\Alarm') 
import alarm
from PyQt5.QtWidgets import (QApplication, QWidget, QCalendarWidget, QLabel,
                             QHBoxLayout, QPushButton, QVBoxLayout, QLineEdit,
                             QListWidget, QMessageBox, QInputDialog, QLCDNumber)
from PyQt5.QtCore import QDate, Qt, QTimer, QTime
from PyQt5 import QtGui
from PyQt5.QtGui import QTextCharFormat, QColor, QPixmap
from style import *
from os import path
import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

class Calendar(QWidget):
    # keep the current time as class variable for reference
    currentDay = str(datetime.now().day).rjust(2, '0')
    currentMonth = str(datetime.now().month).rjust(2, '0')
    currentYear = str(datetime.now().year).rjust(2, '0')
    
    def __init__(self, width, height):
        super().__init__()
        folder = path.dirname(__file__)
        self.icon_folder = path.join(folder, "icon")

        self.setWindowTitle("DKU ExamPlanner")
        self.setWindowIcon(QtGui.QIcon(path.join(self.icon_folder, 'window.png')))

        self.setGeometry(width // 4, height // 4, width // 2, height // 2)
        self.initUI()

    def initUI(self):
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)

        # don't allow going back to past months in calendar
        self.calendar.setMinimumDate(QDate(int(self.currentYear), int(self.currentMonth), 1))

        # format for dates in calendar that have events
        self.fmt = QTextCharFormat()
        self.fmt.setBackground(QColor(255, 165, 0, 100))

        # format for the current day
        cur_fmt = QTextCharFormat()
        cur_fmt.setBackground(QColor(0, 255, 90, 70))

        # format to change back to if all events are deleted
        self.delfmt = QTextCharFormat()
        self.delfmt.setBackground(Qt.transparent)

        # check if json file exists, if it does load the data from it
        file_exists = path.isfile(path.join(path.dirname(__file__), "data.json"))
        if file_exists:
            with open("data.json", "r") as json_file:
                self.data = json.load(json_file)
        else:
            self.data = {}

        # delete data from days prior to the current day
        cur = QDate.currentDate()
        for date in list(self.data.keys()):
            check_date = QDate.fromString(date, "ddMMyyyy")
            if cur.daysTo(check_date) <= 0 and cur != check_date:
                self.data.pop(date)
            else:
                self.calendar.setDateTextFormat(check_date, self.fmt)

        # mark current day in calendar
        current = self.currentDay + self.currentMonth + self.currentYear
        self.calendar.setDateTextFormat(QDate.fromString(current, "ddMMyyyy"), cur_fmt)

        # organize buttons and layouts for display
        addButton = QPushButton("시험일정 추가")
        addButton.clicked.connect(self.addNote)
        fileButton = QPushButton("공부파일 추가")
        fileButton.clicked.connect(self.addFile)
        openButton = QPushButton("파일 열기")
        openButton.clicked.connect(self.openFile)
        editButton = QPushButton("정보 수정")
        editButton.clicked.connect(self.editNote)
        delButton = QPushButton("정보 삭제")
        delButton.clicked.connect(self.delNote)
        askButton = QPushButton("검색 하기")
        askButton.clicked.connect(self.ask)
        arlButton = QPushButton("알람 설정")
        arlButton.clicked.connect(self.arl)

        self.calendar.selectionChanged.connect(self.showDateInfo)
        self.calendar.selectionChanged.connect(self.labelDate)
        self.calendar.selectionChanged.connect(self.highlightFirstItem)

        self.note_group = QListWidget()
        self.note_group.setSortingEnabled(True)
        self.note_group.setStyleSheet("QListView::item {height: 40px;}")

        self.label = QLabel()
        label_font = QtGui.QFont("Gabriola", 18)
        self.label.setFont(label_font)
        self.labelDate()
        self.showDateInfo()

        labelp = QLabel()
        pixmap = QPixmap(path.join(self.icon_folder, 'DKU.png'))
        labelp.setPixmap(pixmap)

        # set up a timer that automatically updates every second
        self.lcd = QLCDNumber()
        self.lcd.setSegmentStyle(QLCDNumber.Filled)
        self.lcd.setMinimumWidth(80)
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)
        self.showTime()

        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(self.label)
        hbox1.addStretch(1)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(addButton)
        hbox2.addWidget(fileButton)
        hbox2.addWidget(openButton)
        hbox2.addWidget(editButton)
        hbox2.addWidget(delButton)
        hbox2.addWidget(askButton)
        hbox2.addWidget(arlButton)

        hbox3 = QHBoxLayout()
        hbox3.addStretch(1)
        hbox3.addWidget(labelp)
        hbox3.addWidget(self.lcd)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addWidget(self.note_group)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)

        hbox = QHBoxLayout()
        hbox.addWidget(self.calendar, 55)
        hbox.addLayout(vbox, 45)

        self.setLayout(hbox)

    def showDateInfo(self):
        # add events to selected date
        date = self.getDate()
        self.note_group.clear()
        if date in self.data:
            self.note_group.addItems(self.data[date])

    def addNote(self):
        # adding notes for selected date
        # if a note starts with any number other than 0, 1, 2
        # add a 0 before it so that we can easily sort events
        # by start time
        date = self.getDate()
        row = self.note_group.currentRow()
        title = "시험일정"
        string, ok = QInputDialog.getText(self, " ", title)

        if ok and string:
            if string[0].isdigit() and string[0] not in ["0", "1", "2"]:
                string = string.replace(string[0], "0" + string[0])
            self.note_group.insertItem(row, string)
            self.calendar.setDateTextFormat(QDate.fromString(date, "ddMMyyyy"), self.fmt)
            if date in self.data:
                self.data[date].append(string)
            else:
                self.data[date] = [string]

    def addFile(self):
        date = self.getDate()
        row = self.note_group.currentRow()
        title = "공부파일"
        string, ok = QInputDialog.getText(self, " ", title)

        if ok and string:
            if string[0].isdigit() and string[0] not in ["0", "1", "2"]:
                string = string.replace(string[0], "0" + string[0])
            self.note_group.insertItem(row, string)
            self.calendar.setDateTextFormat(QDate.fromString(date, "ddMMyyyy"), self.fmt)
            if date in self.data:
                self.data[date].append(string)
            else:
                self.data[date] = [string]

    def delNote(self):
        # delete the currently selected item
        date = self.getDate()
        row = self.note_group.currentRow()
        item = self.note_group.item(row)

        if not item:
            return
        reply = QMessageBox.question(self, " ", "삭제",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            item = self.note_group.takeItem(row)
            self.data[date].remove(item.text())
            if not self.data[date]:
                del(self.data[date])
                self.calendar.setDateTextFormat(QDate.fromString(date, "ddMMyyyy"), self.delfmt)
            del(item)

    def openFile(self):
        row = self.note_group.currentRow()
        item = self.note_group.item(row)

        if not item:
            return
        reply = QMessageBox.question(self, " ", "파일을 열까요?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            item = self.note_group.takeItem(row)
            link = item.text()
            webbrowser.open(link)
           

    def editNote(self):
        # edit the currently selected item
        date = self.getDate()
        row = self.note_group.currentRow()
        item = self.note_group.item(row)

        if item:
            copy = item.text()
            title = "수정"
            string, ok = QInputDialog.getText(self, " ", title,
                                              QLineEdit.Normal, item.text())

            if ok and string:
                self.data[date].remove(copy)
                self.data[date].append(string)
                if string[0].isdigit() and string[0] not in ["0", "1", "2"]:
                    string = string.replace(string[0], "0" + string[0])
                item.setText(string)

    def ask(self):
        title = "질문이 무었인가요?"
        string, ok = QInputDialog.getText(self, " ", title)

        if ok and string:
            search = string

        webdriver_path = "C:\\Users\\pkunw\\OneDrive\\바탕 화면\\chromedriver.exe"
        service = Service(webdriver_path)
        # WebDriver를 통해 Chrome 브라우저 실행
        driver = webdriver.Chrome(service=service)
        driver.get('https://www.google.com')

        wait = WebDriverWait(driver, 10)
        search_box = wait.until(EC.presence_of_element_located((By.NAME, 'q')))

        search_box.send_keys(string)
        search_box.submit()

        wait.until(EC.title_contains(string))
        sys.exit(app.exec_())
       
    def arl(self):
        alarm.alarm()
       
    def getDate(self):
        # parse the selected date into usable string form
        select = self.calendar.selectedDate()
        date = str(select.day()).rjust(2, '0') + str(select.month()).rjust(2, '0') + str(select.year())
        return date

    def labelDate(self):
        # label to show the long name form of the selected date
        # format US style like "Thursday, February 20, 2020"
        select = self.calendar.selectedDate()
        weekday, month = select.dayOfWeek(), select.month()
        day, year = str(select.day()), str(select.year())
        week_day, word_month = QDate.longDayName(weekday), QDate.longMonthName(month)
        self.label.setText(week_day + ", " + word_month + " " + day + ", " + year)

    def highlightFirstItem(self):
        # highlight the first item immediately after switching selection
        if self.note_group.count() > 0:
            self.note_group.setCurrentRow(0)

    def showTime(self):
        # keep the current time updated
        time = QTime.currentTime()
        text = time.toString("hh:mm")
        if time.second() % 2 == 0:
            text.replace(text[2], '')
        self.lcd.display(text)

    def closeEvent(self, e):
        # save all data into json file when user closes app
        with open("data.json", "w") as json_file:
            json.dump(self.data, json_file)
        e.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    screen = app.primaryScreen()
    size = screen.size()
    window = Calendar(size.width(), size.height())
    window.show()
    sys.exit(app.exec_())
