# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QDoubleSpinBox,
    QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QMainWindow,
    QMenu, QMenuBar, QPlainTextEdit, QProgressBar,
    QPushButton, QRadioButton, QScrollArea, QSizePolicy,
    QSpacerItem, QSpinBox, QStatusBar, QTabWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1073, 816)
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName(u"actionQuit")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit))
        self.actionQuit.setIcon(icon)
        self.actionQuit.setMenuRole(QAction.MenuRole.QuitRole)
        self.actionLoad_Graph = QAction(MainWindow)
        self.actionLoad_Graph.setObjectName(u"actionLoad_Graph")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.centralwidget_gridLayout = QGridLayout()
        self.centralwidget_gridLayout.setObjectName(u"centralwidget_gridLayout")
        self.main_buttons_horizontalLayout = QHBoxLayout()
        self.main_buttons_horizontalLayout.setObjectName(u"main_buttons_horizontalLayout")
        self.start_pause_pushButton = QPushButton(self.centralwidget)
        self.start_pause_pushButton.setObjectName(u"start_pause_pushButton")

        self.main_buttons_horizontalLayout.addWidget(self.start_pause_pushButton)

        self.rf_pushButton = QPushButton(self.centralwidget)
        self.rf_pushButton.setObjectName(u"rf_pushButton")
        self.rf_pushButton.setCheckable(True)

        self.main_buttons_horizontalLayout.addWidget(self.rf_pushButton)

        self.modulation_pushButton = QPushButton(self.centralwidget)
        self.modulation_pushButton.setObjectName(u"modulation_pushButton")
        self.modulation_pushButton.setCheckable(True)

        self.main_buttons_horizontalLayout.addWidget(self.modulation_pushButton)

        self.est_time_label = QLabel(self.centralwidget)
        self.est_time_label.setObjectName(u"est_time_label")

        self.main_buttons_horizontalLayout.addWidget(self.est_time_label)

        self.est_time_lineEdit = QLineEdit(self.centralwidget)
        self.est_time_lineEdit.setObjectName(u"est_time_lineEdit")
        self.est_time_lineEdit.setReadOnly(True)

        self.main_buttons_horizontalLayout.addWidget(self.est_time_lineEdit)

        self.test_progressBar = QProgressBar(self.centralwidget)
        self.test_progressBar.setObjectName(u"test_progressBar")
        self.test_progressBar.setValue(0)

        self.main_buttons_horizontalLayout.addWidget(self.test_progressBar)

        self.EUT_progressBar = QProgressBar(self.centralwidget)
        self.EUT_progressBar.setObjectName(u"EUT_progressBar")
        self.EUT_progressBar.setValue(0)

        self.main_buttons_horizontalLayout.addWidget(self.EUT_progressBar)

        self.main_buttons_horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.main_buttons_horizontalLayout.addItem(self.main_buttons_horizontalSpacer)

        self.quit_pushButton = QPushButton(self.centralwidget)
        self.quit_pushButton.setObjectName(u"quit_pushButton")

        self.main_buttons_horizontalLayout.addWidget(self.quit_pushButton)


        self.centralwidget_gridLayout.addLayout(self.main_buttons_horizontalLayout, 2, 0, 1, 1)

        self.permanent_log_plainTextEdit = QPlainTextEdit(self.centralwidget)
        self.permanent_log_plainTextEdit.setObjectName(u"permanent_log_plainTextEdit")
        self.permanent_log_plainTextEdit.setAcceptDrops(False)
        self.permanent_log_plainTextEdit.setReadOnly(True)

        self.centralwidget_gridLayout.addWidget(self.permanent_log_plainTextEdit, 1, 0, 1, 1)

        self.centralwidget_tabWidget = QTabWidget(self.centralwidget)
        self.centralwidget_tabWidget.setObjectName(u"centralwidget_tabWidget")
        self.settings_tab = QWidget()
        self.settings_tab.setObjectName(u"settings_tab")
        self.verticalLayout = QVBoxLayout(self.settings_tab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.settings_tab_horizontalLayout = QHBoxLayout()
        self.settings_tab_horizontalLayout.setObjectName(u"settings_tab_horizontalLayout")
        self.field_strengh_groupBox = QGroupBox(self.settings_tab)
        self.field_strengh_groupBox.setObjectName(u"field_strengh_groupBox")
        self.gridLayout_3 = QGridLayout(self.field_strengh_groupBox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.field_strength_formLayout = QFormLayout()
        self.field_strength_formLayout.setObjectName(u"field_strength_formLayout")
        self.cw_label = QLabel(self.field_strengh_groupBox)
        self.cw_label.setObjectName(u"cw_label")

        self.field_strength_formLayout.setWidget(0, QFormLayout.LabelRole, self.cw_label)

        self.cw_doubleSpinBox = QDoubleSpinBox(self.field_strengh_groupBox)
        self.cw_doubleSpinBox.setObjectName(u"cw_doubleSpinBox")
        self.cw_doubleSpinBox.setValue(1.000000000000000)

        self.field_strength_formLayout.setWidget(0, QFormLayout.FieldRole, self.cw_doubleSpinBox)

        self.am_label = QLabel(self.field_strengh_groupBox)
        self.am_label.setObjectName(u"am_label")

        self.field_strength_formLayout.setWidget(1, QFormLayout.LabelRole, self.am_label)

        self.am_spinBox = QSpinBox(self.field_strengh_groupBox)
        self.am_spinBox.setObjectName(u"am_spinBox")
        self.am_spinBox.setWrapping(True)
        self.am_spinBox.setMaximum(100)
        self.am_spinBox.setValue(80)

        self.field_strength_formLayout.setWidget(1, QFormLayout.FieldRole, self.am_spinBox)

        self.dwell_time_label = QLabel(self.field_strengh_groupBox)
        self.dwell_time_label.setObjectName(u"dwell_time_label")

        self.field_strength_formLayout.setWidget(2, QFormLayout.LabelRole, self.dwell_time_label)

        self.dwell_time_doubleSpinBox = QDoubleSpinBox(self.field_strengh_groupBox)
        self.dwell_time_doubleSpinBox.setObjectName(u"dwell_time_doubleSpinBox")
        self.dwell_time_doubleSpinBox.setDecimals(3)
        self.dwell_time_doubleSpinBox.setMaximum(999.999000000000024)
        self.dwell_time_doubleSpinBox.setValue(1.000000000000000)

        self.field_strength_formLayout.setWidget(2, QFormLayout.FieldRole, self.dwell_time_doubleSpinBox)

        self.label_adjust = QLabel(self.field_strengh_groupBox)
        self.label_adjust.setObjectName(u"label_adjust")

        self.field_strength_formLayout.setWidget(3, QFormLayout.LabelRole, self.label_adjust)

        self.groupBox_E_component = QGroupBox(self.field_strengh_groupBox)
        self.groupBox_E_component.setObjectName(u"groupBox_E_component")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_E_component)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.radioButton_Ex = QRadioButton(self.groupBox_E_component)
        self.radioButton_Ex.setObjectName(u"radioButton_Ex")

        self.verticalLayout_3.addWidget(self.radioButton_Ex)

        self.radioButton_Ey = QRadioButton(self.groupBox_E_component)
        self.radioButton_Ey.setObjectName(u"radioButton_Ey")
        self.radioButton_Ey.setChecked(False)

        self.verticalLayout_3.addWidget(self.radioButton_Ey)

        self.radioButton_Ez = QRadioButton(self.groupBox_E_component)
        self.radioButton_Ez.setObjectName(u"radioButton_Ez")

        self.verticalLayout_3.addWidget(self.radioButton_Ez)

        self.radioButton_absE = QRadioButton(self.groupBox_E_component)
        self.radioButton_absE.setObjectName(u"radioButton_absE")

        self.verticalLayout_3.addWidget(self.radioButton_absE)

        self.radioButton_Largest_E = QRadioButton(self.groupBox_E_component)
        self.radioButton_Largest_E.setObjectName(u"radioButton_Largest_E")

        self.verticalLayout_3.addWidget(self.radioButton_Largest_E)

        self.radioButton_Auto = QRadioButton(self.groupBox_E_component)
        self.radioButton_Auto.setObjectName(u"radioButton_Auto")
        self.radioButton_Auto.setChecked(True)

        self.verticalLayout_3.addWidget(self.radioButton_Auto)


        self.field_strength_formLayout.setWidget(3, QFormLayout.FieldRole, self.groupBox_E_component)


        self.gridLayout_3.addLayout(self.field_strength_formLayout, 0, 0, 1, 1)


        self.settings_tab_horizontalLayout.addWidget(self.field_strengh_groupBox)

        self.frequency_groupBox = QGroupBox(self.settings_tab)
        self.frequency_groupBox.setObjectName(u"frequency_groupBox")
        self.gridLayout_6 = QGridLayout(self.frequency_groupBox)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.frequency_ormLayout = QFormLayout()
        self.frequency_ormLayout.setObjectName(u"frequency_ormLayout")
        self.freq_start_label = QLabel(self.frequency_groupBox)
        self.freq_start_label.setObjectName(u"freq_start_label")

        self.frequency_ormLayout.setWidget(0, QFormLayout.LabelRole, self.freq_start_label)

        self.freq_start_doubleSpinBox = QDoubleSpinBox(self.frequency_groupBox)
        self.freq_start_doubleSpinBox.setObjectName(u"freq_start_doubleSpinBox")
        self.freq_start_doubleSpinBox.setDecimals(4)
        self.freq_start_doubleSpinBox.setMaximum(99999.999899999995250)
        self.freq_start_doubleSpinBox.setSingleStep(1.000000000000000)
        self.freq_start_doubleSpinBox.setValue(30.000000000000000)

        self.frequency_ormLayout.setWidget(0, QFormLayout.FieldRole, self.freq_start_doubleSpinBox)

        self.freq_stop_label = QLabel(self.frequency_groupBox)
        self.freq_stop_label.setObjectName(u"freq_stop_label")

        self.frequency_ormLayout.setWidget(1, QFormLayout.LabelRole, self.freq_stop_label)

        self.freq_stop_doubleSpinBox = QDoubleSpinBox(self.frequency_groupBox)
        self.freq_stop_doubleSpinBox.setObjectName(u"freq_stop_doubleSpinBox")
        self.freq_stop_doubleSpinBox.setDecimals(4)
        self.freq_stop_doubleSpinBox.setMaximum(99999.990000000005239)
        self.freq_stop_doubleSpinBox.setValue(1000.000000000000000)

        self.frequency_ormLayout.setWidget(1, QFormLayout.FieldRole, self.freq_stop_doubleSpinBox)

        self.freq_step_label = QLabel(self.frequency_groupBox)
        self.freq_step_label.setObjectName(u"freq_step_label")

        self.frequency_ormLayout.setWidget(2, QFormLayout.LabelRole, self.freq_step_label)

        self.freq_step_doubleSpinBox = QDoubleSpinBox(self.frequency_groupBox)
        self.freq_step_doubleSpinBox.setObjectName(u"freq_step_doubleSpinBox")
        self.freq_step_doubleSpinBox.setValue(1.000000000000000)

        self.frequency_ormLayout.setWidget(2, QFormLayout.FieldRole, self.freq_step_doubleSpinBox)

        self.log_sweep_checkBox = QCheckBox(self.frequency_groupBox)
        self.log_sweep_checkBox.setObjectName(u"log_sweep_checkBox")
        self.log_sweep_checkBox.setChecked(True)

        self.frequency_ormLayout.setWidget(3, QFormLayout.FieldRole, self.log_sweep_checkBox)

        self.nr_freqs_label = QLabel(self.frequency_groupBox)
        self.nr_freqs_label.setObjectName(u"nr_freqs_label")

        self.frequency_ormLayout.setWidget(4, QFormLayout.LabelRole, self.nr_freqs_label)

        self.nr_freqs_lineEdit = QLineEdit(self.frequency_groupBox)
        self.nr_freqs_lineEdit.setObjectName(u"nr_freqs_lineEdit")
        self.nr_freqs_lineEdit.setReadOnly(True)

        self.frequency_ormLayout.setWidget(4, QFormLayout.FieldRole, self.nr_freqs_lineEdit)

        self.freqs_plainTextEdit = QPlainTextEdit(self.frequency_groupBox)
        self.freqs_plainTextEdit.setObjectName(u"freqs_plainTextEdit")
        self.freqs_plainTextEdit.setAcceptDrops(False)
        self.freqs_plainTextEdit.setReadOnly(True)

        self.frequency_ormLayout.setWidget(5, QFormLayout.FieldRole, self.freqs_plainTextEdit)


        self.gridLayout_6.addLayout(self.frequency_ormLayout, 0, 0, 1, 1)


        self.settings_tab_horizontalLayout.addWidget(self.frequency_groupBox)

        self.settings_groupBox = QGroupBox(self.settings_tab)
        self.settings_groupBox.setObjectName(u"settings_groupBox")
        self.gridLayout_5 = QGridLayout(self.settings_groupBox)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.settings_formLayout = QFormLayout()
        self.settings_formLayout.setObjectName(u"settings_formLayout")
        self.graph_file_label = QLabel(self.settings_groupBox)
        self.graph_file_label.setObjectName(u"graph_file_label")

        self.settings_formLayout.setWidget(1, QFormLayout.LabelRole, self.graph_file_label)

        self.graph_file_lineEdit = QLineEdit(self.settings_groupBox)
        self.graph_file_lineEdit.setObjectName(u"graph_file_lineEdit")
        self.graph_file_lineEdit.setReadOnly(True)

        self.settings_formLayout.setWidget(1, QFormLayout.FieldRole, self.graph_file_lineEdit)

        self.search_path_label = QLabel(self.settings_groupBox)
        self.search_path_label.setObjectName(u"search_path_label")

        self.settings_formLayout.setWidget(2, QFormLayout.LabelRole, self.search_path_label)

        self.search_path_lineEdit = QLineEdit(self.settings_groupBox)
        self.search_path_lineEdit.setObjectName(u"search_path_lineEdit")
        self.search_path_lineEdit.setReadOnly(True)

        self.settings_formLayout.setWidget(2, QFormLayout.FieldRole, self.search_path_lineEdit)

        self.node_names_label = QLabel(self.settings_groupBox)
        self.node_names_label.setObjectName(u"node_names_label")

        self.settings_formLayout.setWidget(3, QFormLayout.LabelRole, self.node_names_label)

        self.node_names_tableWidget = QTableWidget(self.settings_groupBox)
        if (self.node_names_tableWidget.columnCount() < 2):
            self.node_names_tableWidget.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.node_names_tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.node_names_tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        if (self.node_names_tableWidget.rowCount() < 5):
            self.node_names_tableWidget.setRowCount(5)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setFlags(Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsEnabled);
        self.node_names_tableWidget.setItem(0, 0, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.node_names_tableWidget.setItem(0, 1, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setFlags(Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsEnabled);
        self.node_names_tableWidget.setItem(1, 0, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.node_names_tableWidget.setItem(1, 1, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        __qtablewidgetitem6.setFlags(Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsEnabled);
        self.node_names_tableWidget.setItem(2, 0, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.node_names_tableWidget.setItem(2, 1, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        __qtablewidgetitem8.setFlags(Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsEnabled);
        self.node_names_tableWidget.setItem(3, 0, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.node_names_tableWidget.setItem(3, 1, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        __qtablewidgetitem10.setFlags(Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsEnabled);
        self.node_names_tableWidget.setItem(4, 0, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.node_names_tableWidget.setItem(4, 1, __qtablewidgetitem11)
        self.node_names_tableWidget.setObjectName(u"node_names_tableWidget")
        self.node_names_tableWidget.setAlternatingRowColors(True)
        self.node_names_tableWidget.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerItem)
        self.node_names_tableWidget.setRowCount(5)
        self.node_names_tableWidget.setColumnCount(2)
        self.node_names_tableWidget.verticalHeader().setVisible(False)

        self.settings_formLayout.setWidget(3, QFormLayout.FieldRole, self.node_names_tableWidget)


        self.gridLayout_5.addLayout(self.settings_formLayout, 0, 0, 1, 1)


        self.settings_tab_horizontalLayout.addWidget(self.settings_groupBox)


        self.verticalLayout.addLayout(self.settings_tab_horizontalLayout)

        self.EUT_groupBox = QGroupBox(self.settings_tab)
        self.EUT_groupBox.setObjectName(u"EUT_groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.EUT_groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.EUT_plainTextEdit = QPlainTextEdit(self.EUT_groupBox)
        self.EUT_plainTextEdit.setObjectName(u"EUT_plainTextEdit")

        self.verticalLayout_2.addWidget(self.EUT_plainTextEdit)


        self.verticalLayout.addWidget(self.EUT_groupBox)

        self.centralwidget_tabWidget.addTab(self.settings_tab, "")
        self.waveform_tab = QWidget()
        self.waveform_tab.setObjectName(u"waveform_tab")
        self.gridLayout_7 = QGridLayout(self.waveform_tab)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.waveform_scrollArea = QScrollArea(self.waveform_tab)
        self.waveform_scrollArea.setObjectName(u"waveform_scrollArea")
        self.waveform_scrollArea.setWidgetResizable(True)
        self.waveform_scrollAreaWidgetContents = QWidget()
        self.waveform_scrollAreaWidgetContents.setObjectName(u"waveform_scrollAreaWidgetContents")
        self.waveform_scrollAreaWidgetContents.setGeometry(QRect(0, 0, 98, 28))
        self.waveform_scrollArea.setWidget(self.waveform_scrollAreaWidgetContents)

        self.gridLayout_7.addWidget(self.waveform_scrollArea, 0, 0, 1, 1)

        self.centralwidget_tabWidget.addTab(self.waveform_tab, "")
        self.table_tab = QWidget()
        self.table_tab.setObjectName(u"table_tab")
        self.gridLayout = QGridLayout(self.table_tab)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.widget = QWidget(self.table_tab)
        self.widget.setObjectName(u"widget")
        self.gridLayout_4 = QGridLayout(self.widget)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.save_table_pushButton = QPushButton(self.widget)
        self.save_table_pushButton.setObjectName(u"save_table_pushButton")

        self.gridLayout_4.addWidget(self.save_table_pushButton, 0, 0, 1, 1, Qt.AlignmentFlag.AlignTop)

        self.clear_table_pushButton = QPushButton(self.widget)
        self.clear_table_pushButton.setObjectName(u"clear_table_pushButton")

        self.gridLayout_4.addWidget(self.clear_table_pushButton, 1, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer, 2, 0, 1, 1)


        self.gridLayout_8.addWidget(self.widget, 0, 1, 1, 1)

        self.table_tableWidget = QTableWidget(self.table_tab)
        if (self.table_tableWidget.columnCount() < 7):
            self.table_tableWidget.setColumnCount(7)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.table_tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.table_tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.table_tableWidget.setHorizontalHeaderItem(2, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.table_tableWidget.setHorizontalHeaderItem(3, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.table_tableWidget.setHorizontalHeaderItem(4, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.table_tableWidget.setHorizontalHeaderItem(5, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        self.table_tableWidget.setHorizontalHeaderItem(6, __qtablewidgetitem18)
        self.table_tableWidget.setObjectName(u"table_tableWidget")

        self.gridLayout_8.addWidget(self.table_tableWidget, 0, 0, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_8, 0, 0, 1, 1)

        self.centralwidget_tabWidget.addTab(self.table_tab, "")
        self.log_tab = QWidget()
        self.log_tab.setObjectName(u"log_tab")
        self.gridLayout_9 = QGridLayout(self.log_tab)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.logtab_log_plainTextEdit = QPlainTextEdit(self.log_tab)
        self.logtab_log_plainTextEdit.setObjectName(u"logtab_log_plainTextEdit")
        self.logtab_log_plainTextEdit.setReadOnly(True)

        self.gridLayout_9.addWidget(self.logtab_log_plainTextEdit, 0, 0, 1, 1)

        self.centralwidget_tabWidget.addTab(self.log_tab, "")

        self.centralwidget_gridLayout.addWidget(self.centralwidget_tabWidget, 0, 0, 1, 1)


        self.gridLayout_2.addLayout(self.centralwidget_gridLayout, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1073, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
#if QT_CONFIG(shortcut)
        self.cw_label.setBuddy(self.cw_doubleSpinBox)
        self.am_label.setBuddy(self.am_spinBox)
        self.dwell_time_label.setBuddy(self.dwell_time_doubleSpinBox)
        self.freq_start_label.setBuddy(self.freq_start_doubleSpinBox)
        self.freq_stop_label.setBuddy(self.freq_stop_doubleSpinBox)
        self.freq_step_label.setBuddy(self.freq_step_doubleSpinBox)
        self.graph_file_label.setBuddy(self.graph_file_lineEdit)
        self.search_path_label.setBuddy(self.search_path_lineEdit)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.cw_doubleSpinBox, self.am_spinBox)
        QWidget.setTabOrder(self.am_spinBox, self.dwell_time_doubleSpinBox)
        QWidget.setTabOrder(self.dwell_time_doubleSpinBox, self.freq_start_doubleSpinBox)
        QWidget.setTabOrder(self.freq_start_doubleSpinBox, self.freq_stop_doubleSpinBox)
        QWidget.setTabOrder(self.freq_stop_doubleSpinBox, self.freq_step_doubleSpinBox)
        QWidget.setTabOrder(self.freq_step_doubleSpinBox, self.log_sweep_checkBox)
        QWidget.setTabOrder(self.log_sweep_checkBox, self.EUT_plainTextEdit)
        QWidget.setTabOrder(self.EUT_plainTextEdit, self.start_pause_pushButton)
        QWidget.setTabOrder(self.start_pause_pushButton, self.rf_pushButton)
        QWidget.setTabOrder(self.rf_pushButton, self.modulation_pushButton)
        QWidget.setTabOrder(self.modulation_pushButton, self.quit_pushButton)
        QWidget.setTabOrder(self.quit_pushButton, self.graph_file_lineEdit)
        QWidget.setTabOrder(self.graph_file_lineEdit, self.search_path_lineEdit)
        QWidget.setTabOrder(self.search_path_lineEdit, self.waveform_scrollArea)
        QWidget.setTabOrder(self.waveform_scrollArea, self.table_tableWidget)
        QWidget.setTabOrder(self.table_tableWidget, self.logtab_log_plainTextEdit)
        QWidget.setTabOrder(self.logtab_log_plainTextEdit, self.nr_freqs_lineEdit)
        QWidget.setTabOrder(self.nr_freqs_lineEdit, self.permanent_log_plainTextEdit)
        QWidget.setTabOrder(self.permanent_log_plainTextEdit, self.node_names_tableWidget)
        QWidget.setTabOrder(self.node_names_tableWidget, self.save_table_pushButton)
        QWidget.setTabOrder(self.save_table_pushButton, self.freqs_plainTextEdit)
        QWidget.setTabOrder(self.freqs_plainTextEdit, self.clear_table_pushButton)
        QWidget.setTabOrder(self.clear_table_pushButton, self.centralwidget_tabWidget)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionAbout)
        self.menuFile.addAction(self.actionLoad_Graph)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)

        self.retranslateUi(MainWindow)
        self.quit_pushButton.clicked.connect(self.actionQuit.trigger)
        self.actionQuit.triggered.connect(MainWindow.close)
        self.log_sweep_checkBox.stateChanged.connect(MainWindow.update)
        self.freq_start_doubleSpinBox.valueChanged.connect(MainWindow.update)
        self.freq_stop_doubleSpinBox.valueChanged.connect(MainWindow.update)
        self.freq_step_doubleSpinBox.valueChanged.connect(MainWindow.update)
        self.dwell_time_doubleSpinBox.valueChanged.connect(MainWindow.update)

        self.centralwidget_tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About ...", None))
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
#if QT_CONFIG(shortcut)
        self.actionQuit.setShortcut(QCoreApplication.translate("MainWindow", u"Meta+Q", None))
#endif // QT_CONFIG(shortcut)
        self.actionLoad_Graph.setText(QCoreApplication.translate("MainWindow", u"Load Graph ...", None))
        self.start_pause_pushButton.setText(QCoreApplication.translate("MainWindow", u"Start Test", None))
        self.rf_pushButton.setText(QCoreApplication.translate("MainWindow", u"RF", None))
        self.modulation_pushButton.setText(QCoreApplication.translate("MainWindow", u"MOD", None))
        self.est_time_label.setText(QCoreApplication.translate("MainWindow", u"Estimated Test Time", None))
        self.quit_pushButton.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
        self.field_strengh_groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Field Strength", None))
        self.cw_label.setText(QCoreApplication.translate("MainWindow", u"CW Field", None))
        self.cw_doubleSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" V/m", None))
        self.am_label.setText(QCoreApplication.translate("MainWindow", u"AM", None))
        self.am_spinBox.setSuffix(QCoreApplication.translate("MainWindow", u"%", None))
        self.dwell_time_label.setText(QCoreApplication.translate("MainWindow", u"Dwell Time", None))
        self.dwell_time_doubleSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" s", None))
        self.label_adjust.setText(QCoreApplication.translate("MainWindow", u"Adjust to", None))
        self.groupBox_E_component.setTitle("")
        self.radioButton_Ex.setText(QCoreApplication.translate("MainWindow", u"Ex", None))
        self.radioButton_Ey.setText(QCoreApplication.translate("MainWindow", u"Ey", None))
        self.radioButton_Ez.setText(QCoreApplication.translate("MainWindow", u"Ez", None))
        self.radioButton_absE.setText(QCoreApplication.translate("MainWindow", u"|E|", None))
        self.radioButton_Largest_E.setText(QCoreApplication.translate("MainWindow", u"Largest", None))
        self.radioButton_Auto.setText(QCoreApplication.translate("MainWindow", u"Auto", None))
        self.frequency_groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Frequency", None))
        self.freq_start_label.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.freq_start_doubleSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" MHz", None))
        self.freq_stop_label.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.freq_stop_doubleSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" MHz", None))
        self.freq_step_label.setText(QCoreApplication.translate("MainWindow", u"Step", None))
        self.freq_step_doubleSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u"%", None))
        self.log_sweep_checkBox.setText(QCoreApplication.translate("MainWindow", u"Log Sweep", None))
        self.nr_freqs_label.setText(QCoreApplication.translate("MainWindow", u"# Freqs.", None))
        self.settings_groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Measument Graph", None))
        self.graph_file_label.setText(QCoreApplication.translate("MainWindow", u"Graph File", None))
        self.graph_file_lineEdit.setText(QCoreApplication.translate("MainWindow", u"gtem.dot", None))
        self.search_path_label.setText(QCoreApplication.translate("MainWindow", u"Search Path", None))
        self.search_path_lineEdit.setText(QCoreApplication.translate("MainWindow", u"[\u2018.\u2018, \u2018conf\u2018]", None))
        self.node_names_label.setText(QCoreApplication.translate("MainWindow", u"Node Names", None))
        ___qtablewidgetitem = self.node_names_tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Function", None));
        ___qtablewidgetitem1 = self.node_names_tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Node in Graph", None));

        __sortingEnabled = self.node_names_tableWidget.isSortingEnabled()
        self.node_names_tableWidget.setSortingEnabled(False)
        ___qtablewidgetitem2 = self.node_names_tableWidget.item(0, 0)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Generator", None));
        ___qtablewidgetitem3 = self.node_names_tableWidget.item(0, 1)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"sg", None));
        ___qtablewidgetitem4 = self.node_names_tableWidget.item(1, 0)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"Amp. Input", None));
        ___qtablewidgetitem5 = self.node_names_tableWidget.item(1, 1)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"amp1", None));
        ___qtablewidgetitem6 = self.node_names_tableWidget.item(2, 0)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"Amp. Output", None));
        ___qtablewidgetitem7 = self.node_names_tableWidget.item(2, 1)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"amp2", None));
        ___qtablewidgetitem8 = self.node_names_tableWidget.item(3, 0)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"Cell", None));
        ___qtablewidgetitem9 = self.node_names_tableWidget.item(3, 1)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"gtem", None));
        ___qtablewidgetitem10 = self.node_names_tableWidget.item(4, 0)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"Field Probe", None));
        ___qtablewidgetitem11 = self.node_names_tableWidget.item(4, 1)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainWindow", u"prb", None));
        self.node_names_tableWidget.setSortingEnabled(__sortingEnabled)

        self.EUT_groupBox.setTitle(QCoreApplication.translate("MainWindow", u"EUT", None))
        self.EUT_plainTextEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Describe the EUT here", None))
        self.centralwidget_tabWidget.setTabText(self.centralwidget_tabWidget.indexOf(self.settings_tab), QCoreApplication.translate("MainWindow", u"Settings", None))
        self.centralwidget_tabWidget.setTabText(self.centralwidget_tabWidget.indexOf(self.waveform_tab), QCoreApplication.translate("MainWindow", u"Waveform", None))
        self.save_table_pushButton.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.clear_table_pushButton.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        ___qtablewidgetitem12 = self.table_tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("MainWindow", u"Time", None));
        ___qtablewidgetitem13 = self.table_tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("MainWindow", u"Frequency [MHz]", None));
        ___qtablewidgetitem14 = self.table_tableWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("MainWindow", u"CW Ex [V/m]", None));
        ___qtablewidgetitem15 = self.table_tableWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("MainWindow", u"CW Ey [V/m]", None));
        ___qtablewidgetitem16 = self.table_tableWidget.horizontalHeaderItem(4)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("MainWindow", u"CW Ez [V/m]", None));
        ___qtablewidgetitem17 = self.table_tableWidget.horizontalHeaderItem(5)
        ___qtablewidgetitem17.setText(QCoreApplication.translate("MainWindow", u"CW |E| [V/m]", None));
        ___qtablewidgetitem18 = self.table_tableWidget.horizontalHeaderItem(6)
        ___qtablewidgetitem18.setText(QCoreApplication.translate("MainWindow", u"Status", None));
        self.centralwidget_tabWidget.setTabText(self.centralwidget_tabWidget.indexOf(self.table_tab), QCoreApplication.translate("MainWindow", u"Table", None))
        self.centralwidget_tabWidget.setTabText(self.centralwidget_tabWidget.indexOf(self.log_tab), QCoreApplication.translate("MainWindow", u"Log", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
    # retranslateUi

