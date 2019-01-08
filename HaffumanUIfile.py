# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'haffuman.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(831, 469)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.label_compress = QtWidgets.QLabel(Form)
        self.label_compress.setObjectName("label_compress")
        self.gridLayout.addWidget(self.label_compress, 0, 0, 1, 1)
        self.lineEdit_open_path = QtWidgets.QLineEdit(Form)
        self.lineEdit_open_path.setObjectName("lineEdit_open_path")
        self.gridLayout.addWidget(self.lineEdit_open_path, 0, 1, 1, 1)
        self.pushButton_open_path = QtWidgets.QPushButton(Form)
        self.pushButton_open_path.setObjectName("pushButton_open_path")
        self.gridLayout.addWidget(self.pushButton_open_path, 0, 2, 1, 2)
        self.pushButton_compress = QtWidgets.QPushButton(Form)
        self.pushButton_compress.setObjectName("pushButton_compress")
        self.gridLayout.addWidget(self.pushButton_compress, 0, 4, 1, 1)
        self.label_decompress = QtWidgets.QLabel(Form)
        self.label_decompress.setObjectName("label_decompress")
        self.gridLayout.addWidget(self.label_decompress, 1, 0, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 1, 1, 1, 2)
        self.pushButton_decompress_path_ = QtWidgets.QPushButton(Form)
        self.pushButton_decompress_path_.setObjectName("pushButton_decompress_path_")
        self.gridLayout.addWidget(self.pushButton_decompress_path_, 1, 3, 1, 1)
        self.pushButton_decompress = QtWidgets.QPushButton(Form)
        self.pushButton_decompress.setObjectName("pushButton_decompress")
        self.gridLayout.addWidget(self.pushButton_decompress, 1, 4, 1, 1)
        self.textBrowser_message = QtWidgets.QTextBrowser(Form)
        self.textBrowser_message.setEnabled(False)
        self.textBrowser_message.setObjectName("textBrowser_message")
        self.gridLayout.addWidget(self.textBrowser_message, 2, 0, 1, 5)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "单文件压缩与解压"))
        self.label_compress.setText(_translate("Form", "请选择要压缩的文件"))
        self.pushButton_open_path.setText(_translate("Form", "打开"))
        self.pushButton_compress.setText(_translate("Form", "压缩"))
        self.label_decompress.setText(_translate("Form", "请选择要解压的文件"))
        self.pushButton_decompress_path_.setText(_translate("Form", "打开"))
        self.pushButton_decompress.setText(_translate("Form", "解压"))

