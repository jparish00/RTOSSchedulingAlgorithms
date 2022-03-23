import sys
import os
import random
import numpy as np
import pandas as pd
from PySide6 import QtCore, QtWidgets, QtGui

import algorithms
import taskformats as tf

def initWidget(w, name):
    w.setObjectName(name)

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        mainWindow = QtWidgets.QMainWindow()

        self.setWindowTitle("RTOS Scheduling Algorithm Playground")

        self.filePath = ""

        # Task data, in two forms as too support algorithm with different inputs
        self.defaulttask = { (50,12) : 'T1', (40,10) : 'T2', (30,10) : 'T3' }
        self.tasks = [tf.Task(1,50,12), tf.Task(2, 40, 10), tf.Task(3, 30, 10)]

        self.menubar = self.createMenuBar()
        mainWindow.setMenuWidget(self.menubar)

        # Generate individual layouts/widgets
        optionsGroupBox = self.createOptionsBox()
        self.taskTable = self.createTable()
        self.textBox = self.createTextBox()
        generateGroup = self.createGenerateButton()

        # Order Widgets however we wish
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addWidget(optionsGroupBox, 0, 0)
        mainLayout.addWidget(self.taskTable, 1, 0)
        mainLayout.addWidget(self.textBox, 0, 1)
        mainLayout.addWidget(generateGroup, 1, 1)

        # Final widget layout
        mainLayoutV = QtWidgets.QVBoxLayout(self)
        mainLayoutV.addWidget(self.menubar)
        mainLayoutV.addLayout(mainLayout)

    """--------------UI FUNCTIONS--------------"""
    
    def createMenuBar(self):
        menubar = QtWidgets.QMenuBar(self)
        fileMenu = QtWidgets.QMenu("&File", self)
        menubar.addMenu(fileMenu)

        openAction = QtGui.QAction("Open", self)
        saveAsAction = QtGui.QAction("Save As", self)
        saveAction = QtGui.QAction("Save", self)

        fileMenu.addActions([openAction, saveAsAction, saveAction])
        openAction.triggered.connect(self.openFileExplorer)
        saveAsAction.triggered.connect(self.saveAsFileExplorer)
        saveAction.triggered.connect(self.saveFileSlot)

        return menubar

    def createOptionsBox(self):
        result = QtWidgets.QGroupBox("Options")
        initWidget(result, "options_groupbox")
        
        self.randoButton = QtWidgets.QPushButton("Randomize")
        self.randoButton.setDefault(True)
        self.randoButton.toggle()
        self.randoButton.clicked.connect(self.randomClicked)

        self.taskSpinBox = QtWidgets.QSpinBox()
        initWidget(self.taskSpinBox, "taskSpinBox")
        # Play with this, 15 almost seems to high
        self.taskSpinBox.setMinimum(1)
        self.taskSpinBox.setMaximum(15)
        self.taskSpinBox.setValue(3)
        self.taskSpinBox.valueChanged.connect(self.taskNumberChanged)

        self.taskLabel = QtWidgets.QLabel("Tasks:")
        initWidget(self.taskLabel, "taskLabel")
        self.taskLabel.setBuddy(self.taskSpinBox)

        self.algorithmComboBox = QtWidgets.QComboBox()
        initWidget(self.algorithmComboBox, "algorithmComboBox")
        # Add algorithms here
        self.algorithmComboBox.addItems(["RM", "EDF"])

        tasksLayout = QtWidgets.QHBoxLayout()
        tasksLayout.addWidget(self.taskLabel)
        tasksLayout.addWidget(self.taskSpinBox)
        tasksLayout.addStretch(1)
        tasksLayout.addWidget(self.algorithmComboBox)

        self.freqLineEdit = QtWidgets.QLineEdit()
        initWidget(self.freqLineEdit, "freqLineEdit")
        self.freqLineEdit.setPlaceholderText("0.5, 0.75...")
        self.freqLineEdit.setText("0.5, 0.75, 1")

        self.frequencyCheckBox = QtWidgets.QCheckBox("Frequency forced?")
        initWidget(self.frequencyCheckBox, "frequencyCheckBox")
        self.frequencyCheckBox.toggled.connect(self.freqForceChecked)

        optionsLayout = QtWidgets.QVBoxLayout(result)
        optionsLayout.addLayout(tasksLayout)
        optionsLayout.addWidget(self.frequencyCheckBox)
        optionsLayout.addWidget(self.freqLineEdit)
        optionsLayout.addWidget(self.randoButton)

        return result

    def createTable(self):
        result = QtWidgets.QTableWidget()
        initWidget(result, "taskTable")

        # For default tasks
        result.setRowCount(3)
        result.setColumnCount(3)
        result.setHorizontalHeaderLabels(["Task", "Period", "Execution"])

        #default tasks, MAKE SURE TO RETURN STRING TO INT WHEN READING FROM TABLE
        i = 0
        for key, value in self.defaulttask.items():
            result.setItem(i, 0, QtWidgets.QTableWidgetItem(value))
            result.setItem(i, 1, QtWidgets.QTableWidgetItem(str(key[0])))
            result.setItem(i, 2, QtWidgets.QTableWidgetItem(str(key[1])))
            i += 1

        result.itemChanged.connect(self.tableEdited)

        return result

    def createTextBox(self):
        result = QtWidgets.QTextBrowser()
        initWidget(result, "textBox")

        return result

    def createGenerateButton(self):
        result = QtWidgets.QGroupBox()

        generateButton = QtWidgets.QPushButton("Generate!")
        initWidget(generateButton, "generateButton")
        generateButton.clicked.connect(self.generatePlot)

        infoButton = QtWidgets.QPushButton("Info")
        initWidget(infoButton, "infoButton")
        infoButton.clicked.connect(self.algorithmInfo)

        layout = QtWidgets.QHBoxLayout(result)
        layout.addWidget(infoButton)
        layout.addWidget(generateButton)

        return result

    """--------------SLOTS--------------"""

    @QtCore.Slot()
    def openFileExplorer(self):
        self.filePath = self.openFile()

        self.textBox.clear()

        # Load file data from external file
        if (self.filePath[-5:] == ".xlsx"):
            data = pd.read_excel(self.filePath)
        elif(self.filePath[-4:] == ".csv"):
            data = pd.read_csv(self.filePath)
        elif(self.filePath[-4:] == ".txt"):
            data = pd.read_csv(self.filePath, sep = "\t")
        else:
            self.textBox.insertHtml("<p><strong>File type not supported!</strong></p><p>Supported file types: .xlsx .csv .txt<p>")
            self.filePath = ""
            return

        self.tasks.clear()
        self.defaulttask.clear()
        self.taskTable.setRowCount(len(data))
        self.taskSpinBox.setValue(len(data))
        # Sort into class list and dict
        for i in range(len(data)):
            self.tasks.append(tf.Task(i + 1, data.iloc[i,1], data.iloc[i,2]))
            self.defaulttask[(data.iloc[i, 1], data.iloc[i, 2])] = 'T' + str(i + 1)
            self.taskTable.setItem(i, 0, QtWidgets.QTableWidgetItem("T" + str(i + 1)))
            self.taskTable.setItem(i, 1, QtWidgets.QTableWidgetItem(str(data.iloc[i, 1])))
            self.taskTable.setItem(i, 2, QtWidgets.QTableWidgetItem(str(data.iloc[i, 2])))

        self.textBox.insertHtml("<p>File loaded successfully!</p>")

        # Update Window Title
        self.updateWindowTitle()

    @QtCore.Slot()
    def saveAsFileExplorer(self):

        self.textBox.clear()

        # Save data as a dataframe
        data = pd.DataFrame()
        # For now, load from task class
        for i in range(len(self.tasks)):
            data.loc[i, 0] = self.tasks[i].name
            data.loc[i, 1] = self.tasks[i].period
            data.loc[i, 2] = self.tasks[i].exec_t
        
        data.columns = ["Task", "Period", "Execution"]

        self.filePath = self.saveFile()

        if (self.filePath[-5:] == ".xlsx"):
            data.to_excel(self.filePath, index = False)
        elif (self.filePath[-4:] == ".csv"):
            data.to_csv(self.filePath, index = False)
        elif (self.filePath[-4:] == ".txt"):
            data.to_csv(self.filePath, "\t", index = False)
        else:
            self.textBox.insertHtml("<p><strong>File type is not supported, file save failed!</strong></p><p>Supported file types: .xlsx .csv .txt<p>")
            self.filePath = ""
            return
        
        self.textBox.insertHtml("</p>File saved successfully!</p>")

        self.updateWindowTitle()

    @QtCore.Slot()
    def saveFileSlot(self):

        self.textBox.clear()

        if (self.filePath != ""):
            # TODO: Abstract this from both functions
            data = pd.DataFrame()

            print(self.filePath)

            for i in range(len(self.tasks)):
                data.loc[i, 0] = self.tasks[i].name
                data.loc[i, 1] = self.tasks[i].period
                data.loc[i, 2] = self.tasks[i].exec_t
        
            data.columns = ["Task", "Period", "Execution"]

            if (self.filePath[-5:] == ".xlsx"):
                data.to_excel(self.filePath, index = False)
            elif (self.filePath[-4:] == ".csv"):
                data.to_csv(self.filePath, index = False)
            elif (self.filePath[-4:] == ".txt"):
                data.to_csv(self.filePath, "\t", index = False)
        else:
            self.saveAsFileExplorer()
            return
        
        self.textBox.insertHtml("</p>File save successfully!</p>")

    @QtCore.Slot()
    def randomClicked(self):
        # Refill table
        for i in range(self.taskTable.rowCount()):
            self.taskTable.setItem(i, 1, QtWidgets.QTableWidgetItem(str(np.random.randint(25, 50))))
            self.taskTable.setItem(i, 2, QtWidgets.QTableWidgetItem(str(np.random.randint(0, 25))))
            while(int(self.taskTable.item(i, 2).text()) > int(self.taskTable.item(i, 1).text()) or int(self.taskTable.item(i, 2).text()) == 0):
                self.taskTable.setItem(i, 2, QtWidgets.QTableWidgetItem(str(np.random.randint(0, 25))))
        
    @QtCore.Slot()
    def tableEdited(self, item):
        #Find the item that was changed
        self.defaulttask.clear()
        for i in range(self.taskTable.rowCount()):
            self.defaulttask[(int(self.taskTable.item(i, 1).text()), int(self.taskTable.item(i, 2).text()))] = "T" + str(i + 1)
        
        row = item.row()
        column = item.column()
        if column == 1:
            self.tasks[row].period = int(self.taskTable.item(row, column).text())
        elif column == 2:
            self.tasks[row].exec_t = int(self.taskTable.item(row, column).text())

    @QtCore.Slot()
    def freqForceChecked(self):
        print("[INFO]: frequency checkbox state changed!")
        if self.frequencyCheckBox.isChecked():
            self.freqLineEdit.setReadOnly(False)
            # TODO: add some grey when readonly is true
        else:
            self.freqLineEdit.setReadOnly(True)

    @QtCore.Slot()
    def taskNumberChanged(self):
        print("[INFO]: New task number!")
        # Change according to difference
        if self.taskSpinBox.value() > self.taskTable.rowCount():
            r = self.taskSpinBox.value() - self.taskTable.rowCount()
            for i in range(r):
                self.taskTable.setRowCount(self.taskTable.rowCount() + 1)
                rowNum = self.taskTable.rowCount()
                self.taskTable.setItem(rowNum - 1, 0, QtWidgets.QTableWidgetItem("T" + str(rowNum)))
                self.taskTable.setItem(rowNum - 1, 1, QtWidgets.QTableWidgetItem(str(10)))
                self.taskTable.setItem(rowNum - 1, 2, QtWidgets.QTableWidgetItem(str(5)))
                # Add task data to lists
                self.tasks.append(tf.Task(rowNum, 10, 5))
                self.defaulttask[(10, 5)] = "T" + str(rowNum)
        else:
            r = self.taskTable.rowCount() - self.taskSpinBox.value()
            self.taskTable.setRowCount(self.taskTable.rowCount() - r)
            for i in range (r):
                self.tasks.pop()
                # I truly despise working with dicts, lists are supreme
                for key, value in dict(self.defaulttask).items():
                    if value == "T" + str(self.taskTable.rowCount() + r - i):
                        del self.defaulttask[key]

    @QtCore.Slot()
    def algorithmInfo(self):
        self.textBox.clear()
        if self.algorithmComboBox.currentText() == "RM":
            self.textBox.insertHtml("<p><strong>Rate-Monotonic Algorithm:</strong></p><p>The rate utilizes a static priority policy to determine which tasks are executed at a given time. This policy gives each task a priority based on the length of the period. So, longer periods are given less priority than shorter ones. This scheduling algorithm is preemptive, meaning that at any point a higher priority task than the current one executing becomes available, the higher priority task will start to execute.</p>")

        if self.algorithmComboBox.currentText() == "EDF":
            self.textBox.insertHtml("<p><strong>Earliest Deadline First Algorithm:</strong></p><p>As the name suggests, the Earliest Deadline First (EDF) algorithm will always give priority to the task with the closest deadline. Like Rate Monotonic, EDF is a preemptive algorithm, such that if a higher priority task becomes available while a lower priority task is running, the higher priority task will start to execute.</p>")

    @QtCore.Slot()
    def generatePlot(self):
        # Setup Algorithm and Generate Plot
        #print("Success!")

        self.textBox.clear()

        tasks = dict()
        for i in range(self.taskTable.rowCount()):
            tasks[(int(self.taskTable.item(i, 1).text()), int(self.taskTable.item(i, 2).text()))] = self.taskTable.item(i, 0).text()

        print(tasks)

        # Scheduability Tests
        if self.algorithmComboBox.currentText() == "EDF":
            schedulability, s = algorithms.schEDF(tasks)
            text = "<p><strong>Schedulability Test: </strong>Exact (Sufficient + Necessary)</p><p>Using the formula &Sigma;(Ci/Di) &le; 1</p><p>&Sigma;(Ci/Di) = " + str(s) + "</p><p>The result of the test is " + str(schedulability) + ", so...</p>"
            if schedulability:
                text += "<p>The task set <strong>is</strong> schedulable</p>"
            else:
                text += "<p>The task set <strong>is not</strong> schedulable</p>"

        self.textBox.insertHtml(text)
        
        if self.algorithmComboBox.currentText() == "RM":
            print("Nothing here yet...")

        # Generate plot

    """--------------MISC--------------"""

    def updateTasks(self):
        print("Yay!")


    def openFile(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Open a file", '', 'All Files (*.*)')
        return filePath[0]

    def saveFile(self):
        filePath = QtWidgets.QFileDialog.getSaveFileName(self, "Save file as", '', 'All Files (*.*)')
        return filePath[0]
        
    def updateWindowTitle(self):
        if (self.filePath != ""):
            head, tail = os.path.split(self.filePath)
            self.setWindowTitle(" RTOS Scheduling Algorithm Playground - " + tail)


        






        
        




