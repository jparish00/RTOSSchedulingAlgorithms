/********************************************************************************
** Form generated from reading UI file 'mainwindow.ui'
**
** Created by: Qt User Interface Compiler version 6.2.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_MAINWINDOW_H
#define UI_MAINWINDOW_H

#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QComboBox>
#include <QtWidgets/QFrame>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenu>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QSpinBox>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QTableWidget>
#include <QtWidgets/QTextBrowser>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_MainWindow
{
public:
    QWidget *centralwidget;
    QPushButton *randomizeButton;
    QSpinBox *taskNumber;
    QTableWidget *taskTable;
    QPushButton *infoButton;
    QComboBox *algorithms;
    QTextBrowser *logOutput;
    QFrame *taskFrame;
    QMenuBar *menubar;
    QMenu *menuFile;
    QMenu *menuEdit;
    QMenu *menuHelp;
    QStatusBar *statusbar;

    void setupUi(QMainWindow *MainWindow)
    {
        if (MainWindow->objectName().isEmpty())
            MainWindow->setObjectName(QString::fromUtf8("MainWindow"));
        MainWindow->resize(800, 600);
        centralwidget = new QWidget(MainWindow);
        centralwidget->setObjectName(QString::fromUtf8("centralwidget"));
        randomizeButton = new QPushButton(centralwidget);
        randomizeButton->setObjectName(QString::fromUtf8("randomizeButton"));
        randomizeButton->setGeometry(QRect(40, 30, 83, 29));
        taskNumber = new QSpinBox(centralwidget);
        taskNumber->setObjectName(QString::fromUtf8("taskNumber"));
        taskNumber->setGeometry(QRect(140, 30, 48, 29));
        taskTable = new QTableWidget(centralwidget);
        taskTable->setObjectName(QString::fromUtf8("taskTable"));
        taskTable->setGeometry(QRect(40, 70, 256, 192));
        infoButton = new QPushButton(centralwidget);
        infoButton->setObjectName(QString::fromUtf8("infoButton"));
        infoButton->setGeometry(QRect(480, 30, 83, 29));
        algorithms = new QComboBox(centralwidget);
        algorithms->addItem(QString());
        algorithms->addItem(QString());
        algorithms->setObjectName(QString::fromUtf8("algorithms"));
        algorithms->setGeometry(QRect(40, 280, 82, 28));
        logOutput = new QTextBrowser(centralwidget);
        logOutput->setObjectName(QString::fromUtf8("logOutput"));
        logOutput->setGeometry(QRect(310, 70, 256, 192));
        taskFrame = new QFrame(centralwidget);
        taskFrame->setObjectName(QString::fromUtf8("taskFrame"));
        taskFrame->setGeometry(QRect(130, 280, 431, 151));
        taskFrame->setFrameShape(QFrame::StyledPanel);
        taskFrame->setFrameShadow(QFrame::Raised);
        MainWindow->setCentralWidget(centralwidget);
        menubar = new QMenuBar(MainWindow);
        menubar->setObjectName(QString::fromUtf8("menubar"));
        menubar->setGeometry(QRect(0, 0, 800, 21));
        menuFile = new QMenu(menubar);
        menuFile->setObjectName(QString::fromUtf8("menuFile"));
        menuEdit = new QMenu(menubar);
        menuEdit->setObjectName(QString::fromUtf8("menuEdit"));
        menuHelp = new QMenu(menubar);
        menuHelp->setObjectName(QString::fromUtf8("menuHelp"));
        MainWindow->setMenuBar(menubar);
        statusbar = new QStatusBar(MainWindow);
        statusbar->setObjectName(QString::fromUtf8("statusbar"));
        MainWindow->setStatusBar(statusbar);

        menubar->addAction(menuFile->menuAction());
        menubar->addAction(menuEdit->menuAction());
        menubar->addAction(menuHelp->menuAction());

        retranslateUi(MainWindow);

        QMetaObject::connectSlotsByName(MainWindow);
    } // setupUi

    void retranslateUi(QMainWindow *MainWindow)
    {
        MainWindow->setWindowTitle(QCoreApplication::translate("MainWindow", "RTOS Scheduling Algorithms", nullptr));
        randomizeButton->setText(QCoreApplication::translate("MainWindow", "Randomize", nullptr));
        infoButton->setText(QCoreApplication::translate("MainWindow", "Info", nullptr));
        algorithms->setItemText(0, QCoreApplication::translate("MainWindow", "EDF", nullptr));
        algorithms->setItemText(1, QCoreApplication::translate("MainWindow", "RM", nullptr));

        menuFile->setTitle(QCoreApplication::translate("MainWindow", "File", nullptr));
        menuEdit->setTitle(QCoreApplication::translate("MainWindow", "Edit", nullptr));
        menuHelp->setTitle(QCoreApplication::translate("MainWindow", "Help", nullptr));
    } // retranslateUi

};

namespace Ui {
    class MainWindow: public Ui_MainWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_MAINWINDOW_H
