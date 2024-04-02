from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(633, 566)
        # Create a palette and set the background image
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

"\n"
"QToolButton{\n"
"background:red;\n"
"border-radius:60px;\n"
"}\n"
"\n"
"#Form\n"
"{\n"
"background : url(gui/background.png);\n"
"}\n"
"\n"
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
        self.label.setGeometry(QtCore.QRect(70, 30, 311, 51))
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
        self.login_button = QtWidgets.QPushButton(self.frame)
        self.login_button.setGeometry(QtCore.QRect(50, 150, 371, 51))
        self.login_button.setStyleSheet("")
        self.login_button.setObjectName("login_button")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(40, 100, 131, 31))
        self.label_2.setStyleSheet("QLabel{\n"
"background:transparent;\n"
"border:none;\n"
"color:#717072;\n"
"}")
        self.label_2.setObjectName("label_2")
        self.register_button = QtWidgets.QPushButton(self.frame)
        self.register_button.setGeometry(QtCore.QRect(50, 310, 371, 51))
        self.register_button.setStyleSheet("")
        self.register_button.setObjectName("register_button")
        self.face_login = QtWidgets.QPushButton(self.frame)
        self.face_login.setGeometry(QtCore.QRect(50, 230, 371, 51))
        self.face_login.setStyleSheet("")
        self.face_login.setObjectName("face_login")
        self.help = QtWidgets.QPushButton(self.frame)
        self.help.setGeometry(QtCore.QRect(380, 370, 81, 51))
        self.help.setStyleSheet("QPushButton{\n"
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
        self.help.setObjectName("help")
        self.toolButton = QtWidgets.QToolButton(Form)
        self.toolButton.setGeometry(QtCore.QRect(260, 10, 121, 121))
        self.toolButton.setText("")
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
        self.label.setText(_translate("Form", "WELCOME CHATROOM"))
        self.login_button.setText(_translate("Form", "LOGIN"))
        self.label_2.setText(_translate("Form", "do what"))
        self.register_button.setText(_translate("Form", "REGISTER"))
        self.face_login.setText(_translate("Form", "FACE LOGIN"))
        self.help.setText(_translate("Form", "help"))
