import sys
import application

if __name__ == "__main__":
    app = application.QtWidgets.QApplication([])

    widget = application.MyWidget()
    widget.resize(800, 480)
    widget.show()

    sys.exit(app.exec())