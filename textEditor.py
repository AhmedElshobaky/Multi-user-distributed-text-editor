# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'textEditor.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_secondWindow(object):
    def setupUi(self, secondWindow):
        secondWindow.setObjectName("secondWindow")
        secondWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(secondWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(10, 10, 771, 541))
        self.textEdit.setObjectName("textEdit")
        secondWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(secondWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        secondWindow.setMenuBar(self.menubar)
        self.actionNew_file = QtWidgets.QAction(secondWindow)
        self.actionNew_file.setObjectName("actionNew_file")
        self.actionSave_file = QtWidgets.QAction(secondWindow)
        self.actionSave_file.setObjectName("actionSave_file")
        self.actiondelete_file = QtWidgets.QAction(secondWindow)
        self.actiondelete_file.setObjectName("actiondelete_file")
        self.menuFile.addAction(self.actionNew_file)
        self.menuFile.addAction(self.actionSave_file)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(secondWindow)
        QtCore.QMetaObject.connectSlotsByName(secondWindow)

    def retranslateUi(self, secondWindow):
        _translate = QtCore.QCoreApplication.translate
        secondWindow.setWindowTitle(_translate("secondWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("secondWindow", "File"))
        self.actionNew_file.setText(_translate("secondWindow", "New file"))
        self.actionSave_file.setText(_translate("secondWindow", "Close file"))
        self.actiondelete_file.setText(_translate("secondWindow", "Delete file"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    secondWindow = QtWidgets.QMainWindow()
    ui = Ui_secondWindow()
    ui.setupUi(secondWindow)
    secondWindow.show()
    sys.exit(app.exec_())
