# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'print_file_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QGridLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QWidget)

from iode_gui.util.widgets.file_chooser import IodeFileChooser

class Ui_PrintFileDialog(object):
    def setupUi(self, PrintFileDialog):
        if not PrintFileDialog.objectName():
            PrintFileDialog.setObjectName(u"PrintFileDialog")
        PrintFileDialog.resize(506, 322)
        self.gridLayout = QGridLayout(PrintFileDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_print_format = QLabel(PrintFileDialog)
        self.label_print_format.setObjectName(u"label_print_format")
        self.label_print_format.setMinimumSize(QSize(140, 0))

        self.gridLayout.addWidget(self.label_print_format, 0, 0, 1, 2)

        self.comboBox_print_format = QComboBox(PrintFileDialog)
        self.comboBox_print_format.setObjectName(u"comboBox_print_format")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_print_format.sizePolicy().hasHeightForWidth())
        self.comboBox_print_format.setSizePolicy(sizePolicy)
        self.comboBox_print_format.setMinimumSize(QSize(220, 0))
        self.comboBox_print_format.setMaximumSize(QSize(220, 16777215))

        self.gridLayout.addWidget(self.comboBox_print_format, 0, 2, 1, 4)

        self.horizontalSpacer = QSpacerItem(123, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 6, 1, 2)

        self.label_print_eq_as = QLabel(PrintFileDialog)
        self.label_print_eq_as.setObjectName(u"label_print_eq_as")
        self.label_print_eq_as.setMinimumSize(QSize(140, 16))
        self.label_print_eq_as.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout.addWidget(self.label_print_eq_as, 1, 0, 1, 2)

        self.comboBox_print_eq_as = QComboBox(PrintFileDialog)
        self.comboBox_print_eq_as.setObjectName(u"comboBox_print_eq_as")
        self.comboBox_print_eq_as.setMinimumSize(QSize(200, 0))

        self.gridLayout.addWidget(self.comboBox_print_eq_as, 1, 2, 1, 3)

        self.horizontalSpacer_print_eq_as = QSpacerItem(86, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_print_eq_as, 1, 5, 1, 3)

        self.label_print_eq_lec_as = QLabel(PrintFileDialog)
        self.label_print_eq_lec_as.setObjectName(u"label_print_eq_lec_as")
        self.label_print_eq_lec_as.setMinimumSize(QSize(140, 16))
        self.label_print_eq_lec_as.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout.addWidget(self.label_print_eq_lec_as, 2, 0, 1, 2)

        self.comboBox_print_eq_lec_as = QComboBox(PrintFileDialog)
        self.comboBox_print_eq_lec_as.setObjectName(u"comboBox_print_eq_lec_as")
        self.comboBox_print_eq_lec_as.setMinimumSize(QSize(200, 0))

        self.gridLayout.addWidget(self.comboBox_print_eq_lec_as, 2, 2, 1, 3)

        self.horizontalSpacer_print_eq_lec_as = QSpacerItem(86, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_print_eq_lec_as, 2, 5, 1, 3)

        self.label_print_table_as = QLabel(PrintFileDialog)
        self.label_print_table_as.setObjectName(u"label_print_table_as")
        self.label_print_table_as.setMinimumSize(QSize(140, 16))
        self.label_print_table_as.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout.addWidget(self.label_print_table_as, 3, 0, 1, 2)

        self.comboBox_print_table_as = QComboBox(PrintFileDialog)
        self.comboBox_print_table_as.setObjectName(u"comboBox_print_table_as")
        self.comboBox_print_table_as.setMinimumSize(QSize(200, 0))

        self.gridLayout.addWidget(self.comboBox_print_table_as, 3, 2, 1, 3)

        self.horizontalSpacer_print_table_as = QSpacerItem(86, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_print_table_as, 3, 5, 1, 3)

        self.label_generalized_sample = QLabel(PrintFileDialog)
        self.label_generalized_sample.setObjectName(u"label_generalized_sample")
        self.label_generalized_sample.setMinimumSize(QSize(140, 16))
        self.label_generalized_sample.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout.addWidget(self.label_generalized_sample, 4, 0, 1, 2)

        self.lineEdit_generalized_sample = QLineEdit(PrintFileDialog)
        self.lineEdit_generalized_sample.setObjectName(u"lineEdit_generalized_sample")
        self.lineEdit_generalized_sample.setMinimumSize(QSize(210, 16))

        self.gridLayout.addWidget(self.lineEdit_generalized_sample, 4, 2, 1, 3)

        self.horizontalSpacer_generalized_sample = QSpacerItem(54, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_generalized_sample, 4, 5, 1, 3)

        self.label_nb_decimals = QLabel(PrintFileDialog)
        self.label_nb_decimals.setObjectName(u"label_nb_decimals")
        self.label_nb_decimals.setMinimumSize(QSize(140, 16))
        self.label_nb_decimals.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout.addWidget(self.label_nb_decimals, 5, 0, 1, 2)

        self.spinBox_nb_decimals = QSpinBox(PrintFileDialog)
        self.spinBox_nb_decimals.setObjectName(u"spinBox_nb_decimals")
        self.spinBox_nb_decimals.setMinimumSize(QSize(80, 16))
        self.spinBox_nb_decimals.setMinimum(-1)
        self.spinBox_nb_decimals.setValue(4)

        self.gridLayout.addWidget(self.spinBox_nb_decimals, 5, 2, 1, 1)

        self.horizontalSpacer_nb_decimals = QSpacerItem(269, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_nb_decimals, 5, 3, 1, 5)

        self.label_output_file = QLabel(PrintFileDialog)
        self.label_output_file.setObjectName(u"label_output_file")
        self.label_output_file.setMinimumSize(QSize(140, 0))

        self.gridLayout.addWidget(self.label_output_file, 6, 0, 1, 2)

        self.fileChooser_output_file = IodeFileChooser(PrintFileDialog)
        self.fileChooser_output_file.setObjectName(u"fileChooser_output_file")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.fileChooser_output_file.sizePolicy().hasHeightForWidth())
        self.fileChooser_output_file.setSizePolicy(sizePolicy1)
        self.fileChooser_output_file.setMinimumSize(QSize(0, 20))
        self.fileChooser_output_file.setMaximumSize(QSize(16777215, 20))

        self.gridLayout.addWidget(self.fileChooser_output_file, 6, 2, 1, 6)

        self.horizontalSpacer_2 = QSpacerItem(35, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 7, 0, 1, 1)

        self.pushButton_apply = QPushButton(PrintFileDialog)
        self.pushButton_apply.setObjectName(u"pushButton_apply")
        sizePolicy.setHeightForWidth(self.pushButton_apply.sizePolicy().hasHeightForWidth())
        self.pushButton_apply.setSizePolicy(sizePolicy)
        self.pushButton_apply.setMinimumSize(QSize(80, 0))
        self.pushButton_apply.setMaximumSize(QSize(80, 16777215))

        self.gridLayout.addWidget(self.pushButton_apply, 7, 1, 1, 1)

        self.pushButton_cancel = QPushButton(PrintFileDialog)
        self.pushButton_cancel.setObjectName(u"pushButton_cancel")
        sizePolicy.setHeightForWidth(self.pushButton_cancel.sizePolicy().hasHeightForWidth())
        self.pushButton_cancel.setSizePolicy(sizePolicy)
        self.pushButton_cancel.setMinimumSize(QSize(80, 0))
        self.pushButton_cancel.setMaximumSize(QSize(80, 16777215))

        self.gridLayout.addWidget(self.pushButton_cancel, 7, 2, 1, 1)

        self.pushButton_options = QPushButton(PrintFileDialog)
        self.pushButton_options.setObjectName(u"pushButton_options")
        sizePolicy.setHeightForWidth(self.pushButton_options.sizePolicy().hasHeightForWidth())
        self.pushButton_options.setSizePolicy(sizePolicy)
        self.pushButton_options.setMinimumSize(QSize(80, 0))
        self.pushButton_options.setMaximumSize(QSize(80, 16777215))

        self.gridLayout.addWidget(self.pushButton_options, 7, 3, 1, 1)

        self.pushButton_help = QPushButton(PrintFileDialog)
        self.pushButton_help.setObjectName(u"pushButton_help")
        sizePolicy.setHeightForWidth(self.pushButton_help.sizePolicy().hasHeightForWidth())
        self.pushButton_help.setSizePolicy(sizePolicy)
        self.pushButton_help.setMinimumSize(QSize(80, 0))
        self.pushButton_help.setMaximumSize(QSize(80, 16777215))

        self.gridLayout.addWidget(self.pushButton_help, 7, 4, 1, 3)

        self.horizontalSpacer_3 = QSpacerItem(37, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_3, 7, 7, 1, 1)


        self.retranslateUi(PrintFileDialog)
        self.pushButton_apply.clicked.connect(PrintFileDialog.apply)
        self.pushButton_cancel.clicked.connect(PrintFileDialog.reject)
        self.pushButton_options.clicked.connect(PrintFileDialog.set_print_options)
        self.pushButton_help.clicked.connect(PrintFileDialog.help)

        QMetaObject.connectSlotsByName(PrintFileDialog)
    # setupUi

    def retranslateUi(self, PrintFileDialog):
        PrintFileDialog.setWindowTitle(QCoreApplication.translate("PrintFileDialog", u"Dialog", None))
        self.label_print_format.setText(QCoreApplication.translate("PrintFileDialog", u"Format", None))
        self.label_print_eq_as.setText(QCoreApplication.translate("PrintFileDialog", u"Print Equations As", None))
        self.label_print_eq_lec_as.setText(QCoreApplication.translate("PrintFileDialog", u"Print Equations LEC As", None))
        self.label_print_table_as.setText(QCoreApplication.translate("PrintFileDialog", u"Print Tables As", None))
        self.label_generalized_sample.setText(QCoreApplication.translate("PrintFileDialog", u"Generalized Sample", None))
        self.label_nb_decimals.setText(QCoreApplication.translate("PrintFileDialog", u"Nb Decimals", None))
        self.label_output_file.setText(QCoreApplication.translate("PrintFileDialog", u"File", None))
        self.pushButton_apply.setText(QCoreApplication.translate("PrintFileDialog", u"Apply", None))
#if QT_CONFIG(shortcut)
        self.pushButton_apply.setShortcut(QCoreApplication.translate("PrintFileDialog", u"F10", None))
#endif // QT_CONFIG(shortcut)
        self.pushButton_cancel.setText(QCoreApplication.translate("PrintFileDialog", u"Cancel", None))
#if QT_CONFIG(shortcut)
        self.pushButton_cancel.setShortcut(QCoreApplication.translate("PrintFileDialog", u"Esc", None))
#endif // QT_CONFIG(shortcut)
        self.pushButton_options.setText(QCoreApplication.translate("PrintFileDialog", u"Options", None))
#if QT_CONFIG(shortcut)
        self.pushButton_options.setShortcut(QCoreApplication.translate("PrintFileDialog", u"F8", None))
#endif // QT_CONFIG(shortcut)
        self.pushButton_help.setText(QCoreApplication.translate("PrintFileDialog", u"Help", None))
#if QT_CONFIG(shortcut)
        self.pushButton_help.setShortcut(QCoreApplication.translate("PrintFileDialog", u"F1", None))
#endif // QT_CONFIG(shortcut)
    # retranslateUi

