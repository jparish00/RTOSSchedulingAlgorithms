import sys
import os
import random
import numpy as np
import pandas as pd
from PySide6 import QtCore, QtWidgets, QtGui
import matplotlib.pyplot as plt

import algorithms
import taskformats as tf

def initWidget(w, name):
    w.setObjectName(name)

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        mainWindow = QtWidgets.QMainWindow()
        self.setWindowTitle("RTOS Scheduling Algorithm Playground")

        # Class variables
        self.filePath = ""

        # Task data, in two forms as too support algorithm with different inputs[Dict support removed for obvious reasons]
        # self.defaulttask = { (50,12) : 'T1', (40,10) : 'T2', (30,10) : 'T3' }
        self.tasks = [tf.Task(1,50,12), tf.Task(2, 40, 10), tf.Task(3, 30, 10)]

        # Menu bar setup
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

        # Setup for Open, Save functionality
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

        # Group box to contain all options
        result = QtWidgets.QGroupBox("Options")
        initWidget(result, "options_groupbox")
        
        # Randomize tasks button setup
        self.randoButton = QtWidgets.QPushButton("Randomize")
        self.randoButton.setDefault(True)
        self.randoButton.toggle()
        self.randoButton.clicked.connect(self.randomClicked)

        # Setup Task box for number of tasks in table
        self.taskSpinBox = QtWidgets.QSpinBox()
        initWidget(self.taskSpinBox, "taskSpinBox")
        # Set to max 15, can be changed however
        self.taskSpinBox.setMinimum(1)
        self.taskSpinBox.setMaximum(15)
        self.taskSpinBox.setValue(3)
        self.taskSpinBox.valueChanged.connect(self.taskNumberChanged)

        # Label widget set as buddy to spinbox
        self.taskLabel = QtWidgets.QLabel("Tasks:")
        initWidget(self.taskLabel, "taskLabel")
        self.taskLabel.setBuddy(self.taskSpinBox)

        # Combo Box containing usable algorithms
        self.algorithmComboBox = QtWidgets.QComboBox()
        initWidget(self.algorithmComboBox, "algorithmComboBox")
        
        # Add algorithms here
        self.algorithmComboBox.addItems(["RM", "EDF"])

        # Horizontal layout inside of group box
        tasksLayout = QtWidgets.QHBoxLayout()
        tasksLayout.addWidget(self.taskLabel)
        tasksLayout.addWidget(self.taskSpinBox)
        tasksLayout.addStretch(1)
        tasksLayout.addWidget(self.algorithmComboBox)

        # Frequency forced input line
        self.freqLineEdit = QtWidgets.QLineEdit()
        initWidget(self.freqLineEdit, "freqLineEdit")
        self.freqLineEdit.setPlaceholderText("0.5, 0.75...")
        self.freqLineEdit.setText("0.5, 0.75, 1")

        # Checkbox to check if the frequency is forced or not
        self.frequencyCheckBox = QtWidgets.QCheckBox("Frequency forced?")
        initWidget(self.frequencyCheckBox, "frequencyCheckBox")
        self.frequencyCheckBox.toggled.connect(self.freqForceChecked)

        # Final layout with all widhets contained inside the options box
        optionsLayout = QtWidgets.QVBoxLayout(result)
        optionsLayout.addLayout(tasksLayout)
        optionsLayout.addWidget(self.frequencyCheckBox)
        optionsLayout.addWidget(self.freqLineEdit)
        optionsLayout.addWidget(self.randoButton)

        return result

    def createTable(self):

        # Setup for task table, containing all current data
        result = QtWidgets.QTableWidget()
        initWidget(result, "taskTable")

        # For default tasks
        result.setRowCount(3)
        result.setColumnCount(3)
        result.setHorizontalHeaderLabels(["Task", "Period", "Execution"])

        # Load default data
        for i in range(len(self.tasks)):
            result.setItem(i, 0, QtWidgets.QTableWidgetItem(self.tasks[i].name))
            result.setItem(i, 1, QtWidgets.QTableWidgetItem(str(self.tasks[i].period)))
            result.setItem(i, 2, QtWidgets.QTableWidgetItem(str(self.tasks[i].exec_t)))

        # Connect to data updater
        result.itemChanged.connect(self.tableEdited)

        return result

    def createTextBox(self):

        # Text box for basic html output
        result = QtWidgets.QTextBrowser()
        initWidget(result, "textBox")

        return result

    def createGenerateButton(self):

        # Generate button setup to deploy second window with timeline graph, and to display task set information
        result = QtWidgets.QGroupBox()

        generateButton = QtWidgets.QPushButton("Generate!")
        initWidget(generateButton, "generateButton")
        generateButton.clicked.connect(self.generatePlot)

        # Information to display info on currently selected algorithm
        infoButton = QtWidgets.QPushButton("Info")
        initWidget(infoButton, "infoButton")
        infoButton.clicked.connect(self.algorithmInfo)

        # Horizontal layout
        layout = QtWidgets.QHBoxLayout(result)
        layout.addWidget(infoButton)
        layout.addWidget(generateButton)

        return result

    """--------------SLOTS--------------"""

    # A quick note: If the classes self.filePath is an empty string, it is assumed that that there is no open file(either due to a failed save/load, or because of startup)

    @QtCore.Slot()
    def openFileExplorer(self):

        # Open the file explorer, then save the filepath to self
        self.filePath = self.openFile()

        # Clear to display file support fail or success
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
        self.taskTable.setRowCount(len(data))
        self.taskSpinBox.setValue(len(data))

        # Sort into class list and dict[Support for dict removed]
        for i in range(len(data)):
            self.tasks.append(tf.Task(i + 1, data.iloc[i,1], data.iloc[i,2]))
            self.taskTable.setItem(i, 0, QtWidgets.QTableWidgetItem("T" + str(i + 1)))
            self.taskTable.setItem(i, 1, QtWidgets.QTableWidgetItem(str(data.iloc[i, 1])))
            self.taskTable.setItem(i, 2, QtWidgets.QTableWidgetItem(str(data.iloc[i, 2])))

        self.textBox.insertHtml("<p>File loaded successfully!</p>")

        # Update Window Title to display the file that was loaded
        self.updateWindowTitle()

    @QtCore.Slot()
    def saveAsFileExplorer(self):

        # Clear to display save fail or success
        self.textBox.clear()

        # Save data as a dataframe
        data = pd.DataFrame()

        # For now, load from task class
        for i in range(len(self.tasks)):
            data.loc[i, 0] = self.tasks[i].name
            data.loc[i, 1] = self.tasks[i].period
            data.loc[i, 2] = self.tasks[i].exec_t
        
        data.columns = ["Task", "Period", "Execution"]

        # Open file explorer to save file
        # TODO: Figure out how to add file type options to file explorer
        self.filePath = self.saveFile()

        # Check to see if filetype is supported
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

        # Update window title to show that the saved file is the current file open
        self.updateWindowTitle()

    @QtCore.Slot()
    def saveFileSlot(self):

        # Clear to display save fail or success
        self.textBox.clear()

        if (self.filePath != ""):
            # TODO: Abstract this from both functions, as it is the same as the above function
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
        
        # Refill table with a set of random values(this will trigger tableEdited() by signal)
        # Period is set from a range of 25-50, and exec_t is set to a range of 1-25
        for i in range(self.taskTable.rowCount()):
            self.taskTable.setItem(i, 1, QtWidgets.QTableWidgetItem(str(np.random.randint(25, 50))))
            self.taskTable.setItem(i, 2, QtWidgets.QTableWidgetItem(str(np.random.randint(0, 25))))
            while(int(self.taskTable.item(i, 2).text()) > int(self.taskTable.item(i, 1).text()) or int(self.taskTable.item(i, 2).text()) == 0):
                self.taskTable.setItem(i, 2, QtWidgets.QTableWidgetItem(str(np.random.randint(0, 25))))
        
    # TODO: Add exec_t > period check
    @QtCore.Slot()
    def tableEdited(self, item):

        #Find the item that was changed, this will run for every item like a queue
        row = item.row()
        column = item.column()

        # When the taskNumber changes, tableEdited() will run BEFORE taskNumberChanged()
        # add task until matching rowcount
        if self.taskTable.rowCount() - 1 > len(self.tasks) - 1:
            self.tasks.append((tf.Task(len(self.tasks) + 1, 10, 5)))
            #print("Task added")

        if column == 1:
            self.tasks[row].period = int(self.taskTable.item(row, column).text())

        elif column == 2:
            self.tasks[row].exec_t = int(self.taskTable.item(row, column).text())


    @QtCore.Slot()
    def freqForceChecked(self):

        # Don't let the user edit the line if the frequency forced checkbox isn't checked
        if self.frequencyCheckBox.isChecked():
            self.freqLineEdit.setReadOnly(False)
            # TODO: add some grey when readonly is true
        else:
            self.freqLineEdit.setReadOnly(True)

    @QtCore.Slot()
    def taskNumberChanged(self):

        # Change according to difference (Currently deafults to period = 10, exec_t = 5)
        # TODO: Add randomization?
        if self.taskSpinBox.value() > self.taskTable.rowCount():
            r = self.taskSpinBox.value() - self.taskTable.rowCount()
            for i in range(r):
                self.taskTable.setRowCount(self.taskTable.rowCount() + 1)
                rowNum = self.taskTable.rowCount()
                self.taskTable.setItem(rowNum - 1, 0, QtWidgets.QTableWidgetItem("T" + str(rowNum)))
                self.taskTable.setItem(rowNum - 1, 1, QtWidgets.QTableWidgetItem(str(10)))
                self.taskTable.setItem(rowNum - 1, 2, QtWidgets.QTableWidgetItem(str(5)))
        else:
            r = self.taskTable.rowCount() - self.taskSpinBox.value()
            self.taskTable.setRowCount(self.taskTable.rowCount() - r)
            for i in range (r):
                # self.tasks tasks are added in tableEdited(), and removed here (because of porder of functions)
                self.tasks.pop()


    @QtCore.Slot()
    def algorithmInfo(self):

        # Print the info on the currently selected algorithm
        self.textBox.clear()
        if self.algorithmComboBox.currentText() == "RM":
            self.textBox.insertHtml("<p><strong>Rate-Monotonic Algorithm:</strong></p><p>The rate utilizes a static priority policy to determine which tasks are executed at a given time. This policy gives each task a priority based on the length of the period. So, longer periods are given less priority than shorter ones. This scheduling algorithm is preemptive, meaning that at any point a higher priority task than the current one executing becomes available, the higher priority task will start to execute.</p>")

        if self.algorithmComboBox.currentText() == "EDF":
            self.textBox.insertHtml("<p><strong>Earliest Deadline First Algorithm:</strong></p><p>As the name suggests, the Earliest Deadline First (EDF) algorithm will always give priority to the task with the closest deadline. Like Rate Monotonic, EDF is a preemptive algorithm, such that if a higher priority task becomes available while a lower priority task is running, the higher priority task will start to execute.</p>")

    @QtCore.Slot()
    def generatePlot(self):

        # Setup Algorithm and Generate Plot

        self.textBox.clear()

        #for i in range(len(self.tasks)):
        #    print(str(self.tasks[i].name) + ", " + str(self.tasks[i].period) + ", " + str(self.tasks[i].exec_t))

        # Temporary dict for tasks
        tasks = dict()
        for i in range(self.taskTable.rowCount()):
            tasks[(int(self.taskTable.item(i, 1).text()), int(self.taskTable.item(i, 2).text()))] = self.taskTable.item(i, 0).text()

        text = ""

        # Schedulability Test on currently selected algorithm
        if self.algorithmComboBox.currentText() == "EDF":
            schedulability, s = algorithms.schEDF(tasks)
            text = "<p><strong>Schedulability Test: </strong>Exact (Sufficient + Necessary)</p><p>Using the formula &Sigma;(Ci/Di) &le; 1</p><p>&Sigma;(Ci/Di) = " + str(s) + "</p><p>The result of the test is " + str(schedulability) + ", so...</p>"
            if schedulability:
                text += "<p>The task set <strong>is</strong> schedulable</p>"
            else:
                text += "<p>The task set <strong>is not</strong> schedulable</p>"
        
        if self.algorithmComboBox.currentText() == "RM":
            print("Nothing here yet...")

        # Other algorithms added here, if time permits

        # Display algorithm information
        self.textBox.insertHtml(text)

        # Generate plot
        self.Timelines = [("T1", 0, 2), ("T1", 4, 5), ("T1", 8, 10), ("T2", 2, 4), ("T2", 5, 8)]
        self.plot(self.Timelines)

        # Placeholder data

    def plot(self, Timelines):
    
        fig, gnt = plt.subplots()












        gnt.set_ylim(0, 45)
        gnt.set_xlim(0, 10)


        gnt.set_xlabel("Time")
        gnt.set_ylabel("Tasks")

        gnt.set_yticks([15, 25])

        gnt.set_yticklabels(["T1", "T2"])
        gnt.grid(False)

        gnt.broken_barh([(0, 2), (4, 1), (8, 2)], (20, 9), color='red')
        gnt.broken_barh([(2, 2), (5, 3)], (10, 9))

        plt.show()

    """--------------MISC--------------"""

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


        






        
        




