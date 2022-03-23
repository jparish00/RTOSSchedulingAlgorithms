from PySide6 import QtCore, QtWidgets

# This is subject to change in the case of a seperate method for plotting timelines

class plotWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Task Set Plot")

        self.placeHolder = QtWidgets.QLabel("Plotting Window")
        self.placeHolder.setAlignment(QtCore.Qt.AlignCenter)

        mainlayout = QtWidgets.QVBoxLayout()
        mainlayout.addWidget(self.placeHolder)
        self.setLayout(mainlayout)


    