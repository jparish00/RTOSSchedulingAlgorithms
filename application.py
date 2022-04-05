"""
UI application incorporating scheduling algorithms

Jarod Parish
4/4/22
UBC-O ENGR 467 2021W2 - RTOS Embedded Systems
"""

from sqlite3 import Time
import os
import numpy as np
import pandas as pd
from PySide6 import QtCore, QtWidgets, QtGui
import matplotlib.pyplot as plt

import algorithms
import schedulers.RM as rm
import schedulers.helpers.Helpers as help
import schedulers.helpers.Classes as tf
import EDF.EDF as edf
import schedulers.EDF_CC as cc

def initWidget(w, name):
    w.setObjectName(name)

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        
        """
        This function initializes all the default variables and tasks, 
        and sets the final layout of widgets.
        """

        super().__init__()

        mainWindow = QtWidgets.QMainWindow()
        self.setWindowTitle("RTOS Scheduling Algorithm Playground")

        # Class variables (defaults)
        self.filePath = ""
        self.timelineWidth = 24
        self.frequencies = [0.5, 0.75, 1]
        self.invValue = 1

        # Task data, in two forms as too support algorithm with different inputs[Dict support removed for obvious reasons]
        self.tasks = [tf.Task(1,4,1, [1]), tf.Task(2, 5, 2, [2]), tf.Task(3, 7, 2, [1])]

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

        """
        createMenuBar() adds the menu bar to the widget, such that
        the file menu can be used. It also adds each signal to its
        specified slot.
        """

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

        """
        createOptionsBox() creates all the necessary widgets,
        like push buttons, sets their values and functionality,
        and connects their respective signals to corresponding
        slots.
        """

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
        self.invSpinBox.setMinimum(0)
        self.invSpinBox.setMaximum(2)
        self.invSpinBox.setValue(1)
        self.invSpinBox.valueChanged.connect(self.invChanged)

        # Label widget set as buddy to spinbox
        self.invLabel = QtWidgets.QLabel("Invocations:")
        initWidget(self.invLabel, "invLabel")
        self.invLabel.setBuddy(self.invSpinBox)

        # Spin box for # of Invocations
        self.widthSpinBox = QtWidgets.QSpinBox()
        self.widthSpinBox.setMinimum(1)
        self.widthSpinBox.setMaximum(150)
        self.widthSpinBox.setValue(24)
        self.widthSpinBox.valueChanged.connect(self.updateWidth)

        # Label widget set as buddy to spinbox
        self.widthLabel = QtWidgets.QLabel("Timeline Width:")
        initWidget(self.widthLabel, "widthLabel")
        self.widthLabel.setBuddy(self.widthSpinBox)

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
        tasksLayout.addWidget(self.widthLabel)
        tasksLayout.addWidget(self.widthSpinBox)
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
        self.freqLineEdit.editingFinished.connect(self.freqLineEdited)

        # Final layout with all widgets contained inside the options box
        optionsLayout = QtWidgets.QVBoxLayout(result)
        optionsLayout.addLayout(tasksLayout)
        optionsLayout.addLayout(freqLayout)
        optionsLayout.addWidget(self.freqLineEdit)
        optionsLayout.addWidget(self.randoButton)

        return result

    def createTable(self):

        """
        createTable() create a table widgets, adds the default
        rows and columns, loads the default data, sets the 
        headers, and connects the taskEdited signal to the
        corresponding slot.
        """

        # Setup for task table, containing all current data
        result = QtWidgets.QTableWidget()
        initWidget(result, "taskTable")

        # For default tasks
        result.setRowCount(3)
        result.setColumnCount(4)
        result.setHorizontalHeaderLabels(["Task", "Period", "Execution", "AC1"])

        # Load default data
        for i in range(len(self.tasks)):
            result.setItem(i, 0, QtWidgets.QTableWidgetItem(self.tasks[i].name))
            result.setItem(i, 1, QtWidgets.QTableWidgetItem(str(self.tasks[i].period)))
            result.setItem(i, 2, QtWidgets.QTableWidgetItem(str(self.tasks[i].exec_t)))
            result.setItem(i, 3, QtWidgets.QTableWidgetItem(str(self.tasks[i].invocations[0])))

        # Connect to data updater
        result.itemChanged.connect(self.tableEdited)

        return result

    def createTextBox(self):

        """
        createTextBox() creates a text box widget.
        """

        # Text box for basic html output
        result = QtWidgets.QTextBrowser()
        initWidget(result, "textBox")

        return result

    def createGenerateButton(self):

        """
        createGenerateButton() adds the group box and
        button widgets to the layout, and adds the signal to 
        its corresponding slot.
        """

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

        """
        This function opens a file dialog, and if applicable
        loads the file into the table and stores the data.
        """

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
            self.tasks.append(tf.Task(i + 1, data.iloc[i,1], data.iloc[i,2], []))
            self.taskTable.setItem(i, 0, QtWidgets.QTableWidgetItem("T" + str(i + 1)))
            self.taskTable.setItem(i, 1, QtWidgets.QTableWidgetItem(str(data.iloc[i, 1])))
            self.taskTable.setItem(i, 2, QtWidgets.QTableWidgetItem(str(data.iloc[i, 2])))

        self.textBox.insertHtml("<p>File loaded successfully!</p>")

        # Update Window Title to display the file that was loaded
        self.updateWindowTitle()

    @QtCore.Slot()
    def saveAsFileExplorer(self):

        """
        This function saves the task table data to one of 
        three formats, .txt(tab), .csv, .xlsx.
        """

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

        """
        This function does the same as the function above,
        saveAsFileExplorer(), however it assumes that the file we are 
        saving to is currently open, so there is no need for a file dialog.
        """

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
        
        """
        This function randomizes the values in the table,
        as well as the stored values when the 'Randomize'
        button is clicked.
        """

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

        """
        This function updates the corresponding stored value when
        a value(s) in the table change.
        """

        #Find the item that was changed, this will run for every item like a queue
        row = item.row()
        column = item.column()

        # When the taskNumber changes, tableEdited() will run BEFORE taskNumberChanged()
        # add task until matching rowcount
        if self.taskTable.rowCount() - 1 > len(self.tasks) - 1:
            if self.invValue == 0:
                self.tasks.append((tf.Task(len(self.tasks) + 1, 10, 5, [])))
            elif self.invValue == 1:
                self.tasks.append((tf.Task(len(self.tasks) + 1, 10, 5, [2])))
            elif self.invValue == 2:
                self.tasks.append((tf.Task(len(self.tasks) + 1, 10, 5, [2, 2])))

        if column == 1:
            self.tasks[row].period = int(self.taskTable.item(row, column).text())

        elif column == 2:
            self.tasks[row].exec_t = float(self.taskTable.item(row, column).text())
            self.tasks[row].remaining_t = float(self.taskTable.item(row, column).text())
        elif column == 3:
            self.tasks[row].invocations[0] = float(self.taskTable.item(row, column).text())
        elif column == 4:
            self.tasks[row].invocations[1] = float(self.taskTable.item(row, column).text())

        # Make sure exec time is less than period
        if self.tasks[row].exec_t >= self.tasks[row].period:
            self.tasks[row].exec_t = self.tasks[row].period - 1
            self.taskTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(self.tasks[row].exec_t)))
            self.textBox.clear()
            self.textBox.insertHtml("<p>Execution time <Strong>cannot</Strong> be greater than or equal to the period!</p>")
        
        for i in range(len(self.tasks[row].invocations)):
            if self.tasks[row].invocations[i] > self.tasks[row].exec_t:
                self.tasks[row].invocations[i] = self.tasks[row].exec_t
                self.taskTable.setItem(row, 3 + i, QtWidgets.QTableWidgetItem(str(self.tasks[row].invocations[i])))
                self.textBox.clear()
                self.textBox.insertHtml("<p>Invocation time <Strong>cannot</Strong> be greater than or equal to the execution time!</p>")



    @QtCore.Slot()
    def updateWidth(self):

        """
        This function updates the timeline width.
        """

        self.timelineWidth = self.widthSpinBox.value()


    @QtCore.Slot()
    def freqLineEdited(self):
        
        """
        This function runs whenever the text for the frequencies
        input is changed, and stores the values found as a list.
        """

        self.frequencies.clear()

        text = self.freqLineEdit.text()

        textList = text.split(", ")

        for i in range(len(textList)):
            self.frequencies.append(float(textList[i]))


    @QtCore.Slot()
    def freqForceChecked(self):

        """
        This function blocks the input of the user for the
        frequencies whenver the frequency forced checkbox is checked.
        """

        # Don't let the user edit the line if the frequency forced checkbox isn't checked
        if self.frequencyCheckBox.isChecked():
            self.freqLineEdit.setReadOnly(False)
            # TODO: add some grey when readonly is true
        else:
            self.freqLineEdit.setReadOnly(True)

    @QtCore.Slot()
    def taskNumberChanged(self):

        """
        This function appends or removes tasks from the
        task table and stored tasks whenever the number
        of tasks is changed.
        """

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
                if self.invValue >= 1:
                    self.taskTable.setItem(rowNum - 1, 3, QtWidgets.QTableWidgetItem(str(2)))
                if self.invValue == 2:
                    self.taskTable.setItem(rowNum - 1, 4, QtWidgets.QTableWidgetItem(str(2)))
        else:
            r = self.taskTable.rowCount() - self.taskSpinBox.value()
            self.taskTable.setRowCount(self.taskTable.rowCount() - r)
            for i in range (r):
                # self.tasks tasks are added in tableEdited(), and removed here (because of porder of functions)
                self.tasks.pop()

    @QtCore.Slot()
    def invChanged(self):

        """
        This function is the same as above, however is appends
        or pops the invocations from the task table and the 
        stored tasks.
        """

        if self.invSpinBox.value() < self.invValue:
            for i in self.tasks:
                i.invocations.pop()
                if (self.invValue - self.invSpinBox.value()) == 2:
                    i.invocations.pop()
            self.taskTable.setColumnCount(self.taskTable.columnCount() - (self.invValue - self.invSpinBox.value()))

        # Change this if you ever add the ability for more invocations
        elif self.invValue < self.invSpinBox.value():
            self.taskTable.setColumnCount(self.taskTable.columnCount() + (self.invSpinBox.value() - self.invValue))
            for i in self.tasks:
                for j in range(self.invSpinBox.value() - self.invValue):
                    i.invocations.append(2)
                if (self.invSpinBox.value() - self.invValue) == 2:
                    self.taskTable.setItem(self.tasks.index(i), 3, QtWidgets.QTableWidgetItem(str(2)))
                    self.taskTable.setItem(self.tasks.index(i), 4, QtWidgets.QTableWidgetItem(str(2)))
                elif self.invSpinBox.value() == 1:
                    self.taskTable.setItem(self.tasks.index(i), 3, QtWidgets.QTableWidgetItem(str(2)))
                else:
                    self.taskTable.setItem(self.tasks.index(i), 4, QtWidgets.QTableWidgetItem(str(2)))



            self.taskTable.setHorizontalHeaderLabels(["Task", "Period", "Execution", "AC1",  "AC2"])

        for i in self.tasks:
            print(i.invocations)

        self.invValue = self.invSpinBox.value()


    @QtCore.Slot()
    def algorithmInfo(self):

        """
        This function prints the information on the currently
        selected algorithm to the text box, whenever the 
        'Info' button is pressed.
        """

        # Print the info on the currently selected algorithm
        self.textBox.clear()
        if self.algorithmComboBox.currentText() == "RM":
            self.textBox.insertHtml("<p><strong>Rate-Monotonic Algorithm:</strong></p><p>The rate utilizes a static priority policy to determine which tasks are executed at a given time. This policy gives each task a priority based on the length of the period. So, longer periods are given less priority than shorter ones. This scheduling algorithm is preemptive, meaning that at any point a higher priority task than the current one executing becomes available, the higher priority task will start to execute.</p>")

        elif self.algorithmComboBox.currentText() == "EDF":
            self.textBox.insertHtml("<p><strong>Earliest Deadline First Algorithm:</strong></p><p>As the name suggests, the Earliest Deadline First (EDF) algorithm will always give priority to the task with the closest deadline. Like Rate Monotonic, EDF is a preemptive algorithm, such that if a higher priority task becomes available while a lower priority task is running, the higher priority task will start to execute.</p>")

        else:
            self.textBox.insertHtml("<p><strong>Cyclic Conserving EDF:</strong></p><p>The cyclic conserving EDF, like regular EDF, gives priority to the next available deadline. The difference is that the cyclic conserving EDF expects a worst case time, and calculates the frequency of the task based on that. Once the task is finished, if the task took less time then expected, the next available task will reduce its frequency to fill the gaps. The goal of the Cyclic Conserving EDF algorithm is to save energy by reducing the frequency of tasks whenever possible.<br /></p>")

    @QtCore.Slot()
    def generatePlot(self):

        """
        This function sets up the data, runs scheduability tests,
        and passes the data to be plotted, depending on the currently
        selected algorithm.
        """

        # Setup Algorithm and Generate Plot

        # Clear textbox
        self.textBox.clear()

        # Temporary dict for tasks, since the EDF scheduability test uses a dicts
        tasks = dict()
        for i in range(self.taskTable.rowCount()):
            tasks[(int(self.taskTable.item(i, 1).text()), int(self.taskTable.item(i, 2).text()))] = self.taskTable.item(i, 0).text()

        text = ""
        taskcopy = self.tasks            


        # Schedulability Test on currently selected algorithm
        if self.algorithmComboBox.currentText() == "EDF" or self.algorithmComboBox.currentText() == "ccEDF":
            schedulability, s = algorithms.schEDF(tasks)
            text = "<p><strong>Schedulability Test: </strong>Exact (Sufficient + Necessary)</p><p>Using the formula &Sigma;(Ci/Di) &le; 1</p><p>&Sigma;(Ci/Di) = " + str(s) + "</p><p>The result of the test is " + str(schedulability) + ", so...</p>"
            if schedulability:
                text += "<p>The task set <strong>is</strong> schedulable</p>"
            else:
                text += "<p>The task set <strong>is not</strong> schedulable</p>"
        
        if self.algorithmComboBox.currentText() == "RM":
            schedulability, s, bounds = rm.schedulability_test(help.format_input(taskcopy))
            text = "<p><strong>Schedulability Test: </strong>Sufficient</p><p>Using the formula &Sigma;(Ci/Di) &le; " + str(bounds) + "</p><p>&Sigma;(Ci/Di) = " + str(s) + "</p><p>The result of the test is " + str(schedulability) + ", so...</p>"
            if schedulability:
                text += "<p>The task set <strong>is</strong> schedulable</p>"
            else:
                text += "<p>The task set <strong>may be</strong> schedulable</p>"

        # Other algorithms added here, if time permits

        # Display algorithm information
        self.textBox.insertHtml(text)

        currentAlgo = self.algorithmComboBox.currentText()

        # Algorithm processing

        if currentAlgo == "RM":
            tm, tl = rm.run_RM(taskcopy, self.timelineWidth)

            self.Timelines = help.output_RM_EDF(tm,tl)
            self.Timelines[0] = sorted(self.Timelines[0])

            tl.reset()
            for task in tm.tasks_list:
                task.reset()

        elif currentAlgo == "EDF":
            self.Timelines, self.missedDeadlines = edf.EDF(self.tasks, self.timelineWidth)
            self.Timelines = sorted(self.Timelines)

        else:
            if self.frequencyCheckBox.isChecked():
                for i in self.frequencies:
                    print(i)
                tm, tl = cc.run_EDF_CC(taskcopy, self.timelineWidth, self.frequencies)
            else:
                tm, tl = cc.run_EDF_CC(taskcopy, self.timelineWidth, [])
            self.Timelinesf = help.output_EDF_CC(tm, tl)
            self.Timelinesf[0] = sorted(self.Timelinesf[0])

            tl.reset()
            for task in tm.tasks_list:
                task.reset()

        # Plotting functions
        if currentAlgo == "RM":
            self.plot(self.Timelines[0], self.Timelines[1])
        elif currentAlgo == "EDF":
            self.plot(self.Timelines, self.missedDeadlines)
        else:
            self.plotCC(self.Timelinesf[0], self.Timelinesf[1])


    def plot(self, Timelines, missedDeadlines):
    
        """
        This function plots the timelines that seperates the tasks,
        and adds charting information.
        """

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

        # Send info to chart
        j = 10
        k = 0
        for i in range(len(taskSort)):
            gnt.broken_barh(taskSort[i], (j, 9), color=colors[(i + 3) % 3])

            k = self.tasks[i].period
            releaseArrowCount = self.timelineWidth / self.tasks[i].period
            print(releaseArrowCount)
            for l in range(int(releaseArrowCount)):
                gnt.arrow(k, j + 10, 0, -10, head_width = 0.2 *(self.timelineWidth/24), head_length = 2.5)
                gnt.arrow(k, j, 0, 10, head_width = 0.2 *(self.timelineWidth/24), head_length = 2.5)  
                k += self.tasks[i].period
            gnt.arrow(0, j + 10, 0, -10, head_width = 0.2 *(self.timelineWidth/24), head_length = 2.5)

            j += 10
            k = 0

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

        gnt.invert_yaxis()

        gnt.set_yticks(yTickList)
        gnt.set_yticklabels(yTickLabels)
        gnt.grid(False)

        plt.show()

        # Print missed deadlines
        self.textBox.insertHtml("<p></p><p><Strong><br><br>Missed deadlines:<br></Strong></p>")
        if self.algorithmComboBox.currentText() == "RM":
            for i in range(len(missedDeadlines)):
                if len(missedDeadlines[i][1]) != 0: 
                    self.textBox.insertHtml("<p>Task " + missedDeadlines[i][0] +  " missed deadline at t = " + str(missedDeadlines[i][1][0]) + "<br></p>")
        else:
            for i in range(len(missedDeadlines)):
                self.textBox.insertHtml("<p>Task " + missedDeadlines[i][0] +  " missed deadline at t = " + str(missedDeadlines[i][1]) + "<br></p>")

    def plotCC(self, Timelines, missedDeadlines):
        
        """
        This function plots functions that use a single timeline
        to plot all functions.
        """

        fig, gnt = plt.subplots()

        colors = ["red", "blue", "green"]

        # Display tasks and frequencies
        for i in range(len(Timelines)):
            gnt.broken_barh([(Timelines[i][1], Timelines[i][2] - Timelines[i][1])], (10, 10 * Timelines[i][3]), color=colors[(i + 3) % 3])
            gnt.annotate(Timelines[i][0] + ": " + str(Timelines[i][3]), xy=(Timelines[i][1] + (Timelines[i][2] - Timelines[i][1])/2, 10 + 10 * Timelines[i][3]), xytext=(Timelines[i][1] + ((Timelines[i][2] - Timelines[i][1])/2) + 1, 10 + 10 * Timelines[i][3] + 3), arrowprops=dict(facecolor='black', shrink=0.01, width=0.5), fontsize=9)

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
            if len(missedDeadlines[i][1]) != 0: 
                self.textBox.insertHtml("<p>Task " + missedDeadlines[i][0] +  " missed deadline at t = " + str(missedDeadlines[i][1][0]) + "<br></p>")

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