# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tab_text.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QPushButton, QSizePolicy,
    QSpacerItem, QSplitter, QWidget)

from iode_gui.text_edit.text_editor import IodeTextEditor

class Ui_TextWidget(object):
    def setupUi(self, TextWidget):
        if not TextWidget.objectName():
            TextWidget.setObjectName(u"TextWidget")
        TextWidget.resize(684, 502)
        self.gridLayout = QGridLayout(TextWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalSpacer = QSpacerItem(582, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 0, 1, 1)

        self.pushButton_print = QPushButton(TextWidget)
        self.pushButton_print.setObjectName(u"pushButton_print")

        self.gridLayout.addWidget(self.pushButton_print, 0, 1, 1, 1)

        self.splitter = QSplitter(TextWidget)
        self.splitter.setObjectName(u"splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Horizontal)
        self.editor = IodeTextEditor(self.splitter)
        self.editor.setObjectName(u"editor")
        self.splitter.addWidget(self.editor)
        self.editor_2 = IodeTextEditor(self.splitter)
        self.editor_2.setObjectName(u"editor_2")
        self.splitter.addWidget(self.editor_2)

        self.gridLayout.addWidget(self.splitter, 1, 0, 1, 2)


        self.retranslateUi(TextWidget)
        self.pushButton_print.clicked.connect(TextWidget.print)

        QMetaObject.connectSlotsByName(TextWidget)
    # setupUi

    def retranslateUi(self, TextWidget):
        TextWidget.setWindowTitle(QCoreApplication.translate("TextWidget", u"Form", None))
        self.pushButton_print.setText(QCoreApplication.translate("TextWidget", u"Print", None))
#if QT_CONFIG(shortcut)
        self.pushButton_print.setShortcut(QCoreApplication.translate("TextWidget", u"Ctrl+P", None))
#endif // QT_CONFIG(shortcut)
    # retranslateUi

