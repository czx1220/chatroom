# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(630, 567)
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(QtGui.QPixmap("gui/background.png")))
        Form.setPalette(palette)
        Form.setStyleSheet("*{\n"
"font-size:24px;\n"
"font-family:Century Gothic;\n"
"}\n"
"QFrame{\n"
"background:rgba(0,0,0,0.8);\n"
"border-radius:15px;\n"
"}\n"
"#Widget{\n"
"background:url(D:/pictures/sunrise.jpg);\n"
"}\n"
"\n"
"QToolButton{\n"
"background:red;\n"
"border-radius:60px;\n"
"}\n"
"\n"
"#Form\n"
"{\n"
"    background: url(:gui/background.jpg);\n"
"}\n"
"QLabel{\n"
"color:white;\n"
"background:transparent;\n"
"}\n"
"QPushButton{\n"
"background:red;\n"
"border-radius:15px;\n"
"}\n"
"QPushButton:hover{\n"
"background:#333;\n"
"border-radius:15px;\n"
"background:#49ebff;\n"
"}\n"
"QLineEdit{\n"
"background:transparent;\n"
"border:none;\n"
"color:#717072;\n"
"border-bottom:1px solid #717072;\n"
"}")
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(80, 110, 471, 431))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(130, 30, 211, 51))
        self.label.setStyleSheet("QLabel{\n"
"color:white;\n"
"background:transparent;\n"
"}\n"
"\n"
"*{\n"
"font-size:24px;\n"
"font-family:Century Gothic;\n"
"}")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.button = QtWidgets.QPushButton(self.frame)
        self.button.setGeometry(QtCore.QRect(50, 360, 371, 51))
        self.button.setStyleSheet("")
        self.button.setObjectName("button")
        self.username_input = QtWidgets.QLineEdit(self.frame)
        self.username_input.setGeometry(QtCore.QRect(50, 190, 341, 31))
        self.username_input.setText("")
        self.username_input.setObjectName("username_input")
        self.password_input = QtWidgets.QLineEdit(self.frame)
        self.password_input.setGeometry(QtCore.QRect(50, 280, 341, 31))
        self.password_input.setText("")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setObjectName("password_input")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(50, 160, 141, 31))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(50, 250, 141, 31))
        self.label_3.setObjectName("label_3")
        self.back_main = QtWidgets.QPushButton(self.frame)
        self.back_main.setGeometry(QtCore.QRect(390, 0, 81, 41))
        self.back_main.setStyleSheet("QPushButton{\n"
"background:transparent;\n"
"border:none;\n"
"color:#717072;\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"background:#333;\n"
"border-radius:15px;\n"
"background:#49ebff;\n"
"}")
        self.back_main.setIconSize(QtCore.QSize(64, 64))
        self.back_main.setObjectName("back_main")
        self.toolButton = QtWidgets.QToolButton(Form)
        self.toolButton.setGeometry(QtCore.QRect(260, 10, 121, 121))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("gui/icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton.setIcon(icon)
        self.toolButton.setIconSize(QtCore.QSize(64, 64))
        self.toolButton.setObjectName("toolButton")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "LOGIN HERE"))
        self.button.setText(_translate("Form", "LOGIN"))
        self.username_input.setPlaceholderText(_translate("Form", "Username"))
        self.password_input.setPlaceholderText(_translate("Form", "Password"))
        self.label_2.setText(_translate("Form", "Username"))
        self.label_3.setText(_translate("Form", "Password"))
        self.back_main.setText(_translate("Form", "back"))
