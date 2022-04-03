from sqlite3 import Time
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
        self.timelineWidth = 10
        self.frequencies = []

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

        # Spin box for # of Invocations
        self.invSpinBox = QtWidgets.QSpinBox()
        self.invSpinBox.setMinimum(1)
        self.invSpinBox.setMaximum(3)
        self.invSpinBox.setValue(1)

        # Label widget set as buddy to spinbox
        self.invLabel = QtWidgets.QLabel("Invocations:")
        initWidget(self.invLabel, "invLabel")
        self.invLabel.setBuddy(self.invSpinBox)

        # Combo Box containing usable algorithms
        self.algorithmComboBox = QtWidgets.QComboBox()
        initWidget(self.algorithmComboBox, "algorithmComboBox")
        
        # Add algorithms here
        self.algorithmComboBox.addItems(["RM", "EDF", "ccEDF"])

        # Checkbox to check if the frequency is forced or not
        self.frequencyCheckBox = QtWidgets.QCheckBox("Frequency forced?")
        initWidget(self.frequencyCheckBox, "frequencyCheckBox")
        self.frequencyCheckBox.toggled.connect(self.freqForceChecked)

        # Horizontal layout inside of group box
        tasksLayout = QtWidgets.QHBoxLayout()
        tasksLayout.addWidget(self.taskLabel)
        tasksLayout.addWidget(self.taskSpinBox)
        tasksLayout.addStretch(1)
        tasksLayout.addWidget(self.invLabel)
        tasksLayout.addWidget(self.invSpinBox)

        freqLayout = QtWidgets.QHBoxLayout()
        freqLayout.addWidget(self.frequencyCheckBox)
        freqLayout.addStretch(1)
        freqLayout.addWidget(self.algorithmComboBox)

        # Frequency forced input line
        self.freqLineEdit = QtWidgets.QLineEdit()
        initWidget(self.freqLineEdit, "freqLineEdit")
        self.freqLineEdit.setPlaceholderText("0.5, 0.75...")
        self.freqLineEdit.setText("0.5, 0.75, 1")
        self.freqLineEdit.editingFinished.connect(self.FreqLineEdited)



        # Final layout with all widhets contained inside the options box
        optionsLayout = QtWidgets.QVBoxLayout(result)
        optionsLayout.addLayout(tasksLayout)
        optionsLayout.addLayout(freqLayout)
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
    def freqLineEdited(self):
        
        self.frequencies.clear()

        text = self.freqLineEdit.text()

        textList = text.split(", ")

        for i in range(len(textList)):
            self.frequencies.append(int(textList[i]))


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

        # Temporary dict for tasks
        tasks = dict()
        for i in range(self.taskTable.rowCount()):
            tasks[(int(self.taskTable.item(i, 1).text()), int(self.taskTable.item(i, 2).text()))] = self.taskTable.item(i, 0).text()

        text = ""
        # Test values
        schedulability = True
        s = 0.85

        # Schedulability Test on currently selected algorithm
        if self.algorithmComboBox.currentText() == "EDF":
            schedulability, s = algorithms.schEDF(tasks)
            text = "<p><strong>Schedulability Test: </strong>Exact (Sufficient + Necessary)</p><p>Using the formula &Sigma;(Ci/Di) &le; 1</p><p>&Sigma;(Ci/Di) = " + str(s) + "</p><p>The result of the test is " + str(schedulability) + ", so...</p>"
            if schedulability:
                text += "<p>The task set <strong>is</strong> schedulable</p>"
            else:
                text += "<p>The task set <strong>is not</strong> schedulable</p>"
        
        if self.algorithmComboBox.currentText() == "RM":
            #schedulability, s = algorithms.schRM(tasks)
            text = "<p><strong>Schedulability Test: </strong>Sufficient</p><p>Using the formula &Sigma;(Ci/Di) &le; " + str(len(self.tasks) * (2**(1/len(self.tasks)) - 1)) + "</p><p>&Sigma;(Ci/Di) = " + str(s) + "</p><p>The result of the test is " + str(schedulability) + ", so...</p>"
            if schedulability:
                text += "<p>The task set <strong>is</strong> schedulable</p>"
            else:
                text += "<p>The task set <strong>may be</strong> schedulable</p>"

        # Other algorithms added here, if time permits

        # Display algorithm information
        self.textBox.insertHtml(text)

        # Generate plot
        self.Timelines = [("T1", 0, 2), ("T1", 4, 5), ("T1", 8, 10), ("T2", 2, 4), ("T2", 5, 7), ("T3", 7, 8)]
        self.Timelinesf = [("T1", 0, 3, 0.87), ("T2", 3, 4.5, 0.9), ("T3", 4.5, 7, 0.6)]
        self.missedDeadlines = [("T1", 2), ("T2", 5)]

        currentAlgo = self.algorithmComboBox.currentText()

        if (currentAlgo == "EDF") or (currentAlgo == "RM"):
            self.plot(self.Timelines, self.missedDeadlines)
        else:
            self.plotCC(self.Timelinesf, self.missedDeadlines)


    def plot(self, Timelines, missedDeadlines):
    
        fig, gnt = plt.subplots()

        colors = ["red", "blue", "green"]

        # Sort values into seperate lists
        # Better task sort based on name
        taskSort = []
        j = 0
        k = 0
        name = ""

        # Get lists to pass to plot
        for i in range(len(self.tasks)):
            taskSort.append([])

        # Sort tuples into list by name
        for i in range(len(Timelines)):
            name = Timelines[k][0] 
            if Timelines[i][0] == name:
                taskSort[j].append((Timelines[i][1], Timelines[i][2] - Timelines[i][1]))
            else:
                j += 1
                k = i
                taskSort[j].append((Timelines[i][1], Timelines[i][2] - Timelines[i][1]))

        # Sent info to chart
        j = 10
        for i in range(len(taskSort)):
            gnt.broken_barh(taskSort[i], (j, 9), color=colors[(i + 3) % 3])
            j += 10

        gnt.set_ylim(0, len(self.tasks) * 10 + 25)
        gnt.set_xlim(0, self.timelineWidth)

        gnt.set_xlabel("Time")
        gnt.set_ylabel("Tasks")

        yTickList = []
        yTickLabels = []
        j = 15
        for i in range(len(self.tasks)):
            yTickList.append(j + 10*i)
            yTickLabels.append(self.tasks[i].name)

        gnt.set_yticks(yTickList)
        gnt.set_yticklabels(yTickLabels)
        gnt.grid(False)

        plt.show()

        # Print missed deadlines
        self.textBox.insertHtml("<p></p><p><Strong><br><br>Missed deadlines:<br></Strong></p>")
        for i in range(len(missedDeadlines)):
            self.textBox.insertHtml("<p>Task " + missedDeadlines[i][0] +  " missed deadline at t = " + str(missedDeadlines[i][1]) + "<br></p>")

    def plotCC(self, Timelines, missedDeadlines):
        
        fig, gnt = plt.subplots()

        colors = ["red", "blue", "green"]

        # Display tasks and frequencies
        for i in range(len(Timelines)):
            gnt.broken_barh([(Timelines[i][1], Timelines[i][2] - Timelines[i][1])], (10, 10 * Timelines[i][3]), color=colors[(i + 3) % 3])
            gnt.annotate(Timelines[i][0] + ": " + str(Timelines[i][3]) + "Fmax", xy=(Timelines[i][1] + (Timelines[i][2] - Timelines[i][1])/2, 10 + 10 * Timelines[i][3]), xytext=(Timelines[i][1] + ((Timelines[i][2] - Timelines[i][1])/2) + 1, 10 + 10 * Timelines[i][3] + 5), arrowprops=dict(facecolor='black', shrink=0.01, width=0.5), fontsize=9)

        gnt.set_ylim(25)
        gnt.set_xlim(0, self.timelineWidth)

        gnt.set_xlabel("Time")
        gnt.set_ylabel("Frequency")

        gnt.set_yticks([10, 15, 17.5, 20])
        gnt.set_yticklabels(["0", "0.5Fmax", "0.75Fmax", "Fmax"])
        gnt.grid(False)

        gnt.invert_yaxis()

        plt.show()

        # Print missed deadlines
        self.textBox.insertHtml("<p></p><p><Strong><br><br>Missed deadlines:<br></Strong></p>")
        for i in range(len(missedDeadlines)):
            self.textBox.insertHtml("<p>Task " + missedDeadlines[i][0] +  " missed deadline at t = " + str(missedDeadlines[i][1]) + "<br></p>") 

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


        






        
        




