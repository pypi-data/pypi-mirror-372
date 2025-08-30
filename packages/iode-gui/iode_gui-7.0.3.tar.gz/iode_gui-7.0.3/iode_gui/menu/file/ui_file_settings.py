# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'file_settings.ui'
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
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox,
    QDialog, QGridLayout, QLabel, QLineEdit,
    QPlainTextEdit, QPushButton, QRadioButton, QSizePolicy,
    QSpacerItem, QTabWidget, QWidget)

class Ui_MenuFileSettings(object):
    def setupUi(self, MenuFileSettings):
        if not MenuFileSettings.objectName():
            MenuFileSettings.setObjectName(u"MenuFileSettings")
        MenuFileSettings.resize(495, 661)
        self.gridLayout_2 = QGridLayout(MenuFileSettings)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tabWidget = QTabWidget(MenuFileSettings)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tab_print = QWidget()
        self.tab_print.setObjectName(u"tab_print")
        self.gridLayout_3 = QGridLayout(self.tab_print)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_print_dest = QLabel(self.tab_print)
        self.label_print_dest.setObjectName(u"label_print_dest")

        self.gridLayout_3.addWidget(self.label_print_dest, 0, 0, 1, 1)

        self.comboBox_print_dest = QComboBox(self.tab_print)
        self.comboBox_print_dest.setObjectName(u"comboBox_print_dest")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_print_dest.sizePolicy().hasHeightForWidth())
        self.comboBox_print_dest.setSizePolicy(sizePolicy)
        self.comboBox_print_dest.setMinimumSize(QSize(160, 0))
        self.comboBox_print_dest.setMaximumSize(QSize(160, 16777215))

        self.gridLayout_3.addWidget(self.comboBox_print_dest, 0, 1, 1, 1)

        self.pushButton_options = QPushButton(self.tab_print)
        self.pushButton_options.setObjectName(u"pushButton_options")
        sizePolicy.setHeightForWidth(self.pushButton_options.sizePolicy().hasHeightForWidth())
        self.pushButton_options.setSizePolicy(sizePolicy)
        self.pushButton_options.setMinimumSize(QSize(80, 0))
        self.pushButton_options.setMaximumSize(QSize(80, 16777215))

        self.gridLayout_3.addWidget(self.pushButton_options, 0, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(125, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer, 0, 3, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 24, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer, 1, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 24, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_2, 1, 1, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 24, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_3, 1, 2, 1, 1)

        self.tabWidget.addTab(self.tab_print, "")
        self.tab_reports = QWidget()
        self.tab_reports.setObjectName(u"tab_reports")
        self.gridLayout = QGridLayout(self.tab_reports)
        self.gridLayout.setObjectName(u"gridLayout")
        self.radioButton_run_from_parent_dir = QRadioButton(self.tab_reports)
        self.buttonGroup_reports = QButtonGroup(MenuFileSettings)
        self.buttonGroup_reports.setObjectName(u"buttonGroup_reports")
        self.buttonGroup_reports.addButton(self.radioButton_run_from_parent_dir)
        self.radioButton_run_from_parent_dir.setObjectName(u"radioButton_run_from_parent_dir")

        self.gridLayout.addWidget(self.radioButton_run_from_parent_dir, 1, 0, 1, 1)

        self.radioButton_run_from_project_dir = QRadioButton(self.tab_reports)
        self.buttonGroup_reports.addButton(self.radioButton_run_from_project_dir)
        self.radioButton_run_from_project_dir.setObjectName(u"radioButton_run_from_project_dir")
        self.radioButton_run_from_project_dir.setChecked(True)

        self.gridLayout.addWidget(self.radioButton_run_from_project_dir, 0, 0, 1, 1)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_4, 2, 0, 1, 1)

        self.tabWidget.addTab(self.tab_reports, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout_4 = QGridLayout(self.tab)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.pushButton_report_macros = QPushButton(self.tab)
        self.pushButton_report_macros.setObjectName(u"pushButton_report_macros")
        self.pushButton_report_macros.setMaximumSize(QSize(25, 16777215))

        self.gridLayout_4.addWidget(self.pushButton_report_macros, 8, 2, 1, 1)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_10, 7, 3, 1, 1)

        self.horizontalSpacer_6 = QSpacerItem(86, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_6, 5, 3, 1, 1)

        self.pushButton_report_functions = QPushButton(self.tab)
        self.pushButton_report_functions.setObjectName(u"pushButton_report_functions")
        self.pushButton_report_functions.setMaximumSize(QSize(25, 16777215))

        self.gridLayout_4.addWidget(self.pushButton_report_functions, 6, 2, 1, 1)

        self.lineEdit_header_text = QLineEdit(self.tab)
        self.lineEdit_header_text.setObjectName(u"lineEdit_header_text")

        self.gridLayout_4.addWidget(self.lineEdit_header_text, 3, 1, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(86, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_5, 4, 3, 1, 1)

        self.label_7 = QLabel(self.tab)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_4.addWidget(self.label_7, 9, 0, 1, 1)

        self.horizontalSpacer_7 = QSpacerItem(86, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_7, 6, 3, 1, 1)

        self.lineEdit_header_background = QLineEdit(self.tab)
        self.lineEdit_header_background.setObjectName(u"lineEdit_header_background")

        self.gridLayout_4.addWidget(self.lineEdit_header_background, 2, 1, 1, 1)

        self.lineEdit_report_macros = QLineEdit(self.tab)
        self.lineEdit_report_macros.setObjectName(u"lineEdit_report_macros")

        self.gridLayout_4.addWidget(self.lineEdit_report_macros, 8, 1, 1, 1)

        self.plainTextEdit_report_example = QPlainTextEdit(self.tab)
        self.plainTextEdit_report_example.setObjectName(u"plainTextEdit_report_example")
        self.plainTextEdit_report_example.setReadOnly(True)

        self.gridLayout_4.addWidget(self.plainTextEdit_report_example, 10, 0, 1, 4)

        self.lineEdit_report_functions = QLineEdit(self.tab)
        self.lineEdit_report_functions.setObjectName(u"lineEdit_report_functions")

        self.gridLayout_4.addWidget(self.lineEdit_report_functions, 6, 1, 1, 1)

        self.label_2 = QLabel(self.tab)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_4.addWidget(self.label_2, 3, 0, 1, 1)

        self.label_4 = QLabel(self.tab)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_4.addWidget(self.label_4, 5, 0, 1, 1)

        self.lineEdit_report_expressions = QLineEdit(self.tab)
        self.lineEdit_report_expressions.setObjectName(u"lineEdit_report_expressions")

        self.gridLayout_4.addWidget(self.lineEdit_report_expressions, 9, 1, 1, 1)

        self.horizontalSpacer_9 = QSpacerItem(86, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_9, 9, 3, 1, 1)

        self.lineEdit_report_commands = QLineEdit(self.tab)
        self.lineEdit_report_commands.setObjectName(u"lineEdit_report_commands")

        self.gridLayout_4.addWidget(self.lineEdit_report_commands, 5, 1, 1, 1)

        self.label_6 = QLabel(self.tab)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_4.addWidget(self.label_6, 8, 0, 1, 1)

        self.label_3 = QLabel(self.tab)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_4.addWidget(self.label_3, 4, 0, 1, 1)

        self.pushButton_header_text = QPushButton(self.tab)
        self.pushButton_header_text.setObjectName(u"pushButton_header_text")
        self.pushButton_header_text.setMaximumSize(QSize(25, 16777215))

        self.gridLayout_4.addWidget(self.pushButton_header_text, 3, 2, 1, 1)

        self.horizontalSpacer_8 = QSpacerItem(86, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_8, 8, 3, 1, 1)

        self.pushButton_report_internal_functions = QPushButton(self.tab)
        self.pushButton_report_internal_functions.setObjectName(u"pushButton_report_internal_functions")
        self.pushButton_report_internal_functions.setMaximumSize(QSize(25, 16777215))

        self.gridLayout_4.addWidget(self.pushButton_report_internal_functions, 4, 2, 1, 1)

        self.label_5 = QLabel(self.tab)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_4.addWidget(self.label_5, 6, 0, 1, 1)

        self.pushButton_detect_color_theme = QPushButton(self.tab)
        self.pushButton_detect_color_theme.setObjectName(u"pushButton_detect_color_theme")

        self.gridLayout_4.addWidget(self.pushButton_detect_color_theme, 0, 2, 1, 2)

        self.lineEdit_report_internal_functions = QLineEdit(self.tab)
        self.lineEdit_report_internal_functions.setObjectName(u"lineEdit_report_internal_functions")

        self.gridLayout_4.addWidget(self.lineEdit_report_internal_functions, 4, 1, 1, 1)

        self.label = QLabel(self.tab)
        self.label.setObjectName(u"label")

        self.gridLayout_4.addWidget(self.label, 2, 0, 1, 1)

        self.pushButton_report_comments = QPushButton(self.tab)
        self.pushButton_report_comments.setObjectName(u"pushButton_report_comments")
        self.pushButton_report_comments.setMaximumSize(QSize(25, 16777215))

        self.gridLayout_4.addWidget(self.pushButton_report_comments, 7, 2, 1, 1)

        self.label_9 = QLabel(self.tab)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_4.addWidget(self.label_9, 7, 0, 1, 1)

        self.horizontalSpacer_3 = QSpacerItem(86, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_3, 2, 3, 1, 1)

        self.pushButton_report_commands = QPushButton(self.tab)
        self.pushButton_report_commands.setObjectName(u"pushButton_report_commands")
        self.pushButton_report_commands.setMaximumSize(QSize(25, 16777215))

        self.gridLayout_4.addWidget(self.pushButton_report_commands, 5, 2, 1, 1)

        self.pushButton_report_expressions = QPushButton(self.tab)
        self.pushButton_report_expressions.setObjectName(u"pushButton_report_expressions")
        self.pushButton_report_expressions.setMaximumSize(QSize(25, 16777215))

        self.gridLayout_4.addWidget(self.pushButton_report_expressions, 9, 2, 1, 1)

        self.label_color_theme = QLabel(self.tab)
        self.label_color_theme.setObjectName(u"label_color_theme")

        self.gridLayout_4.addWidget(self.label_color_theme, 0, 0, 1, 1)

        self.pushButton_header_background = QPushButton(self.tab)
        self.pushButton_header_background.setObjectName(u"pushButton_header_background")
        self.pushButton_header_background.setMaximumSize(QSize(25, 16777215))

        self.gridLayout_4.addWidget(self.pushButton_header_background, 2, 2, 1, 1)

        self.lineEdit_report_comments = QLineEdit(self.tab)
        self.lineEdit_report_comments.setObjectName(u"lineEdit_report_comments")

        self.gridLayout_4.addWidget(self.lineEdit_report_comments, 7, 1, 1, 1)

        self.comboBox_color_theme = QComboBox(self.tab)
        self.comboBox_color_theme.setObjectName(u"comboBox_color_theme")

        self.gridLayout_4.addWidget(self.comboBox_color_theme, 0, 1, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(86, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_4, 3, 3, 1, 1)

        self.checkBox_default_color_theme = QCheckBox(self.tab)
        self.checkBox_default_color_theme.setObjectName(u"checkBox_default_color_theme")

        self.gridLayout_4.addWidget(self.checkBox_default_color_theme, 1, 1, 1, 1)

        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_11, 1, 0, 1, 1)

        self.pushButton_reset = QPushButton(self.tab)
        self.pushButton_reset.setObjectName(u"pushButton_reset")

        self.gridLayout_4.addWidget(self.pushButton_reset, 1, 2, 1, 2)

        self.tabWidget.addTab(self.tab, "")

        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 4)

        self.horizontalSpacer_2 = QSpacerItem(189, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_2, 1, 0, 1, 1)

        self.pushButton_apply = QPushButton(MenuFileSettings)
        self.pushButton_apply.setObjectName(u"pushButton_apply")
        sizePolicy.setHeightForWidth(self.pushButton_apply.sizePolicy().hasHeightForWidth())
        self.pushButton_apply.setSizePolicy(sizePolicy)
        self.pushButton_apply.setMinimumSize(QSize(80, 0))
        self.pushButton_apply.setMaximumSize(QSize(80, 16777215))

        self.gridLayout_2.addWidget(self.pushButton_apply, 1, 1, 1, 1)

        self.pushButton_cancel = QPushButton(MenuFileSettings)
        self.pushButton_cancel.setObjectName(u"pushButton_cancel")
        sizePolicy.setHeightForWidth(self.pushButton_cancel.sizePolicy().hasHeightForWidth())
        self.pushButton_cancel.setSizePolicy(sizePolicy)
        self.pushButton_cancel.setMinimumSize(QSize(80, 0))
        self.pushButton_cancel.setMaximumSize(QSize(80, 16777215))

        self.gridLayout_2.addWidget(self.pushButton_cancel, 1, 2, 1, 1)

        self.pushButton_help = QPushButton(MenuFileSettings)
        self.pushButton_help.setObjectName(u"pushButton_help")
        sizePolicy.setHeightForWidth(self.pushButton_help.sizePolicy().hasHeightForWidth())
        self.pushButton_help.setSizePolicy(sizePolicy)
        self.pushButton_help.setMinimumSize(QSize(80, 0))
        self.pushButton_help.setMaximumSize(QSize(80, 16777215))

        self.gridLayout_2.addWidget(self.pushButton_help, 1, 3, 1, 1)


        self.retranslateUi(MenuFileSettings)
        self.pushButton_apply.clicked.connect(MenuFileSettings.apply)
        self.pushButton_cancel.clicked.connect(MenuFileSettings.reject)
        self.pushButton_help.clicked.connect(MenuFileSettings.help)
        self.pushButton_options.clicked.connect(MenuFileSettings.set_print_options)
        self.comboBox_color_theme.currentTextChanged.connect(MenuFileSettings.load_colors)
        self.pushButton_detect_color_theme.clicked.connect(MenuFileSettings.detect_color_theme)
        self.pushButton_reset.clicked.connect(MenuFileSettings.reset_colors)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MenuFileSettings)
    # setupUi

    def retranslateUi(self, MenuFileSettings):
        MenuFileSettings.setWindowTitle(QCoreApplication.translate("MenuFileSettings", u"SETTINGS", None))
        self.label_print_dest.setText(QCoreApplication.translate("MenuFileSettings", u"Print to", None))
        self.pushButton_options.setText(QCoreApplication.translate("MenuFileSettings", u"Options", None))
#if QT_CONFIG(shortcut)
        self.pushButton_options.setShortcut(QCoreApplication.translate("MenuFileSettings", u"F8", None))
#endif // QT_CONFIG(shortcut)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_print), QCoreApplication.translate("MenuFileSettings", u"Print", None))
        self.radioButton_run_from_parent_dir.setText(QCoreApplication.translate("MenuFileSettings", u"Run Reports From The Parent Directory", None))
        self.radioButton_run_from_project_dir.setText(QCoreApplication.translate("MenuFileSettings", u"Run Reports From The Project Directory", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_reports), QCoreApplication.translate("MenuFileSettings", u"Reports", None))
        self.pushButton_report_macros.setText("")
        self.pushButton_report_functions.setText("")
        self.label_7.setText(QCoreApplication.translate("MenuFileSettings", u"report expressions ({expression})", None))
        self.plainTextEdit_report_example.setPlainText("")
        self.label_2.setText(QCoreApplication.translate("MenuFileSettings", u"IODE objects headers text", None))
        self.label_4.setText(QCoreApplication.translate("MenuFileSettings", u"report commands ($ or #)", None))
        self.label_6.setText(QCoreApplication.translate("MenuFileSettings", u"report macros (%macro%)", None))
        self.label_3.setText(QCoreApplication.translate("MenuFileSettings", u"internal report functions ($ or #)", None))
        self.pushButton_header_text.setText("")
        self.pushButton_report_internal_functions.setText("")
        self.label_5.setText(QCoreApplication.translate("MenuFileSettings", u"report functions (@)", None))
#if QT_CONFIG(tooltip)
        self.pushButton_detect_color_theme.setToolTip(QCoreApplication.translate("MenuFileSettings", u"Try to dectect if light mode or dark mode from the OS settings", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_detect_color_theme.setText(QCoreApplication.translate("MenuFileSettings", u"Detect Automatically", None))
        self.label.setText(QCoreApplication.translate("MenuFileSettings", u"IODE objects headers background", None))
        self.pushButton_report_comments.setText("")
        self.label_9.setText(QCoreApplication.translate("MenuFileSettings", u"report comments", None))
        self.pushButton_report_commands.setText("")
        self.pushButton_report_expressions.setText("")
        self.label_color_theme.setText(QCoreApplication.translate("MenuFileSettings", u"Color Theme", None))
        self.pushButton_header_background.setText("")
        self.checkBox_default_color_theme.setText(QCoreApplication.translate("MenuFileSettings", u"Default for all projects", None))
        self.pushButton_reset.setText(QCoreApplication.translate("MenuFileSettings", u"Reset", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MenuFileSettings", u"Color Theme", None))
        self.pushButton_apply.setText(QCoreApplication.translate("MenuFileSettings", u"Apply", None))
#if QT_CONFIG(shortcut)
        self.pushButton_apply.setShortcut(QCoreApplication.translate("MenuFileSettings", u"F10", None))
#endif // QT_CONFIG(shortcut)
        self.pushButton_cancel.setText(QCoreApplication.translate("MenuFileSettings", u"Cancel", None))
#if QT_CONFIG(shortcut)
        self.pushButton_cancel.setShortcut(QCoreApplication.translate("MenuFileSettings", u"Esc", None))
#endif // QT_CONFIG(shortcut)
        self.pushButton_help.setText(QCoreApplication.translate("MenuFileSettings", u"Help", None))
#if QT_CONFIG(shortcut)
        self.pushButton_help.setShortcut(QCoreApplication.translate("MenuFileSettings", u"F1", None))
#endif // QT_CONFIG(shortcut)
    # retranslateUi

