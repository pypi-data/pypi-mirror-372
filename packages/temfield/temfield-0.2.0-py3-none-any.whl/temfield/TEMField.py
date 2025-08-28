# This Python file uses the following encoding: utf-8
import os.path
import sys
import csv
import datetime
import time

import numpy as np

from matplotlib.backends.backend_qtagg import (FigureCanvasQTAgg as FigureCanvas,
                                               NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from PySide6.QtCore import Qt, QLocale, QSettings, QTimer, QThreadPool
from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox,
                               QFileDialog, QTableWidgetItem, QVBoxLayout, QWidget)

from .EUT import EUT_status, simple_eut_status

from mpylab.tools.spacing import logspace, linspace
from mpylab.tools.util import tstamp
from mpylab.tools.sin_fit import fit_sin

from .TestSusceptibility import TestSusceptibiliy

# Important:
# You need to run the following command to generate the mainwindow.py file
#     pyside6-uic mainwindow.ui -o mainwindow.py
from .mainwindow import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.threadpool = QThreadPool()
        self.eut_status = "Unknown"
        self.eut_finished = False
        self.settings = settings
        self.ready_for_next_freq = True
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.table_is_unsaved = False
        self.disable_update = True
        self._read_setup()
        self.disable_update = False

        def _adjust(x):
            self.adjust_to_setting = x
        # register adjust radio buttons
        self.ui.radioButton_Ex.clicked.connect(lambda: _adjust('x'))
        self.ui.radioButton_Ey.clicked.connect(lambda: _adjust('y'))
        self.ui.radioButton_Ez.clicked.connect(lambda: _adjust('z'))
        self.ui.radioButton_absE.clicked.connect(lambda: _adjust('mag'))
        self.ui.radioButton_Largest_E.clicked.connect(lambda: _adjust('largest'))
        self.ui.radioButton_Auto.clicked.connect(lambda: _adjust('auto'))

        # register message box for quit action
        self.ui.actionQuit.triggered.connect(MainWindow.close)
        # File Dialog
        self.ui.actionLoad_Graph.triggered.connect(self.load_graph)

        # cw field strength
        self.ui.cw_doubleSpinBox.valueChanged.connect(self.cw_doubleSpinBox_changed)
        # am percentage
        self.ui.am_spinBox.valueChanged.connect(self.am_spinBox_changed)
        # about
        self.ui.actionAbout.triggered.connect(self.about_triggered)
        # node names
        self.ui.node_names_tableWidget.cellChanged.connect(self.node_names_table_cellChanged)
        # update the other fields
        self.update()
        self.ui.start_pause_pushButton.setDisabled(True)
        self.node_names_table_cellChanged()
        self.ui.start_pause_pushButton.clicked.connect(self.start_pause_pushButton_clicked)
        self.ui.EUT_plainTextEdit.textChanged.connect(self.EUT_plainTextEdit_changed)
        self.ui.save_table_pushButton.clicked.connect(self.save_Table)
        self.ui.clear_table_pushButton.clicked.connect(self.clear_Table)
        # waveform
        self.efield_canvas = FigureCanvas(Figure(figsize=(5, 4)))
        self.efield_toolbar = NavigationToolbar(self.efield_canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(self.efield_toolbar)
        layout.addWidget(self.efield_canvas)
        widget = QWidget()
        widget.setLayout(layout)
        self.ui.waveform_scrollArea.setWidget(widget)
        self._efield_ax = self.efield_canvas.figure.subplots()
        t = np.linspace(0, 10, 101)
        self.lineEx, = self._efield_ax.plot(t, np.sin(t + time.time()), marker=',', label='Ex')
        self.lineEy, = self._efield_ax.plot(t, np.sin(t + time.time()*2), marker=',', label='Ey')
        self.lineEz, = self._efield_ax.plot(t, np.sin(t + time.time()*3), marker=',', label='Ez')
        self.lineSin, = self._efield_ax.plot(t, np.sin(t + time.time()), ls='-', label='sin-fit (Ex)')
        self._efield_ax.set_xlabel("Time in ms")
        self._efield_ax.set_ylabel("E-Field in V/m")
        self._efield_ax.set_title("Dummy Plot")
        self._efield_ax.legend(loc='upper right')
        self._efield_ax.grid(True)
        # Set up a Line2D.
        self._timer = self.efield_canvas.new_timer(50)
        self._timer.add_callback(self._update_efield)
        self._timer.start()

        self.meas = TestSusceptibiliy()
        self.ui.start_pause_pushButton.setDisabled(False)
        self.ui.rf_pushButton.clicked.connect(self.toggle_rf)
        self.rf_isON = False
        self.ui.modulation_pushButton.clicked.connect(self.toggle_am)
        self.am_isON = False

    def check_EUT(self):
        self.eut_finished = False
        self.eut_status = "Unknown"
        self.eut_progress = 0
        self.ready_for_next_freq = False
        worker = EUT_status(simple_eut_status, dw=self.dwell_time)
        worker.signals.result.connect(self.EUT_result)
        worker.signals.finished.connect(self.EUT_finished)
        worker.signals.progress.connect(self.EUT_progress)
        self.threadpool.start(worker)

    def EUT_result(self, result):
        self.eut_status = result
        #print("EUT result:", result)

    def EUT_progress(self, progress):
        self.eut_progress = min(100,progress)
        self.ui.EUT_progressBar.setValue(self.eut_progress)

    def EUT_finished(self):
        self.eut_finished = True
        #print("EUT finished")

    def _update_efield(self):
        err, t, ex, ey, ez = self.meas.get_waveform()
        # print(err)
        if err < 0:
            t = np.linspace(0, 10, 101)
            # Shift the sinusoid as a function of time.
            self.lineEx.set_data(t, np.sin(t + time.time()))
            self.lineEy.set_data(t, np.sin(t + time.time() * 2))
            self.lineEz.set_data(t, np.sin(t + time.time() * 3))
            self.lineSin.set_data(t, np.sin(t + time.time()))
        else:
            self.lineEx.set_data(t, ex)
            self.lineEy.set_data(t, ey)
            self.lineEz.set_data(t, ez)
            if self.adjust_to_setting == 'x' or self.meas.main_e_component == 0:
                _e = ex
            elif self.adjust_to_setting == 'y' or self.meas.main_e_component == 1:
                _e = ey
            elif self.adjust_to_setting == 'z' or self.meas.main_e_component == 2:
                _e = ez
            elif self.adjust_to_setting == 'mag':
                _e = np.sqrt(np.square(ex) + np.square(ey) + np.square(ez))
            elif self.adjust_to_setting == 'largest':
                max_vals = (max(ex), max(ey), max(ez))
                _i = max_vals.index(max(max_vals))
                _e = (ex, ey, ez)[_i]

            fitdata = fit_sin(t, _e)
            freqAM = fitdata['freq']
            meanAM = fitdata['offset']
            modAM = abs(fitdata['amp']) / meanAM * 100
            self.lineSin.set_data(t, fitdata['fitfunc'](t))
            self._efield_ax.set_title(f"E-Field: {meanAM:.2f} V/m, AM-Freq: {freqAM:.2f} kHz, AM-Depth: {modAM:.2f} %")
            self._efield_ax.relim()
            self._efield_ax.autoscale_view(True, True, True)
        self.lineEx.figure.canvas.draw()

    def EUT_plainTextEdit_changed(self):
        self.eut_description = self.ui.EUT_plainTextEdit.toPlainText()

    def log(self, text, short = None):
        if short is None:
            short = text
        longtext = f"{self.get_time_as_string(format='')}: {text}"
        self.ui.logtab_log_plainTextEdit.appendPlainText(longtext)
        self.ui.permanent_log_plainTextEdit.appendPlainText(short)

    def do_fill_table(self, freq=None, cw=(None,None,None), status=None):
        self.table_is_unsaved = True
        table = self.ui.table_tableWidget
        rowposition = table.rowCount()
        table.insertRow(rowposition)
        val = QTableWidgetItem(self.get_time_as_string(format=''))
        val.setFlags(val.flags() & ~Qt.ItemFlag.ItemIsEditable)
        table.setItem(rowposition, 0, val)
        val = QTableWidgetItem(str(freq*1e-6))
        val.setFlags(val.flags() & ~Qt.ItemFlag.ItemIsEditable)
        table.setItem(rowposition, 1, val)
        magnitude = 0.0
        for _r,_cw in enumerate(cw):
            val = QTableWidgetItem(str(round(_cw,2)))
            val.setFlags(val.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(rowposition, 2+_r, val)
            magnitude += _cw*_cw
        magnitude = np.sqrt(magnitude)
        val = QTableWidgetItem(str(round(magnitude, 2)))
        val.setFlags(val.flags() & ~Qt.ItemFlag.ItemIsEditable)
        table.setItem(rowposition, 5, val)
        table.setItem(rowposition, 6, QTableWidgetItem(str(status)))
        table.verticalScrollBar().setSliderPosition(table.verticalScrollBar().maximum())

    def clear_Table(self):
        table = self.ui.table_tableWidget
        table.clearContents()
        table.setRowCount(0)
        self.table_is_unsaved = False

    def process_frequencies(self):
        if self.eut_finished:
            self.do_fill_table(freq=self.current_f, cw=(_e.get_expectation_value_as_float() for _e in self.e_field), status=self.eut_status)
            self.eut_finished = False
            # process next freq
            self.ready_for_next_freq = True
            QTimer.singleShot(100, self.process_frequencies)
        elif self.pause_processing or not self.ready_for_next_freq:
            # stay responsive but don't proceed with next freq
            QTimer.singleShot(100, self.process_frequencies)
        elif self.ready_for_next_freq:
            try:
                self.table_is_unsaved = True
                self.current_f = f = self.remaining_freqs.pop(0)
                Nf = len(self.freqs)
                Nr = len(self.remaining_freqs)
                self.ui.test_progressBar.setValue(int((Nf-Nr) / Nf * 100))
                self.log(f"set freq to {f} MHz", short = f'Freq: {round(f*1e-6,2)} MHz')
                self.meas.mg.SetFreq_Devices(f)
                self.meas.mg.EvaluateConditions()
                self.am_off()
                self.rf_on()
                self.log('adjust Level...')
                self.e_field = self.meas.adjust_level()
                self.log(f"E-Field: Ex = {self.e_field[0]}, Ey = {self.e_field[1]}, Ez = {self.e_field[2]},",
                         short = f'Ex = {round(self.e_field[0].get_expectation_value_as_float(),2)} V/m, Ey = {round(self.e_field[1].get_expectation_value_as_float(),2)} V/m, Ez = {round(self.e_field[2].get_expectation_value_as_float(),2)} V/m')
                self.am_on()
                self.check_EUT()
                #self.eut_timer = QTimer()
                #self.eut_timer.setInterval(10)
                #self.eut_timer.timeout.connect(self.check_EUT)
                #self.eut_timer.start()
                # process next freq
                QTimer.singleShot(100, self.process_frequencies)
            except IndexError:
                # all freqs processed
                self.rf_off()
                self.am_off()
                self.meas.mg.CmdDevices(False, 'Standby')
                self.meas.mg.Quit_Devices()
                self.log("all frequencies processed")
                self.ui.rf_pushButton.setChecked(False)
                self.ui.start_pause_pushButton.setText("Start Test")
                self.ready_for_next_freq = True

    def toggle_rf(self):
        if self.rf_isON is False:
            self.rf_on()
        else:
            self.rf_off()

    def rf_on(self):
        status = self.meas.rf_on()
        if status is True:
            self.log("RF On")
            self.rf_isON = True
        self.ui.rf_pushButton.setChecked(self.rf_isON)

    def rf_off(self):
        status = self.meas.rf_off()
        if status is True:
            self.log("RF Off")
            self.rf_isON = False
        self.ui.rf_pushButton.setChecked(self.rf_isON)

    def toggle_am(self):
        if self.am_isON is False:
            self.am_on()
        else:
            self.am_off()

    def am_on(self):
        status = self.meas.am_on()
        if status is True:
            self.log("AM On")
            self.am_isON = True
        self.ui.modulation_pushButton.setChecked(self.am_isON)

    def am_off(self):
        status = self.meas.am_off()
        if status is True:
            self.log("AM Off")
            self.am_isON = False
        self.ui.modulation_pushButton.setChecked(self.am_isON)

    def start_pause_pushButton_clicked(self):
        if self.ui.start_pause_pushButton.text() == "Start Test":
            if self.table_is_unsaved:
                ret = QMessageBox.question(self, "Unsaved Table detected",
                                              "Do you want to save the table?", QMessageBox.StandardButton.No,
                                           QMessageBox.StandardButton.Yes)
                if ret == QMessageBox.StandardButton.Yes:
                    self.save_Table()

            self.clear_Table()
            self.ui.test_progressBar.setValue(0)
            self.log("Start Test")
            self.log(f"EUT description: {self.eut_description}")
            self.pause_processing = False
            self.ui.start_pause_pushButton.setText("Pause Test")
            err = self.meas.Init(dwell_time=self.dwell_time,
                    e_target=self.cw,
                    names=self.names,
                    dotfile=self.dotfile,
                    SearchPath=self.searchpath,
                    adjust_to_setting=self.adjust_to_setting)
            self.meas.init_measurement(self.am)
            self.remaining_freqs = self.freqs.copy()
            self.ui.rf_pushButton.setChecked(True)
            self.process_frequencies()
        elif self.ui.start_pause_pushButton.text() == "Pause Test":
            self.rf_off()
            self.log("Pause Test")
            self.ui.start_pause_pushButton.setText("Cont. Test")
            self.ui.rf_pushButton.setChecked(False)
            self.pause_processing = True
        else:
            self.rf_on()
            self.log("Continue Test")
            self.ui.start_pause_pushButton.setText("Pause Test")
            self.ui.rf_pushButton.setChecked(True)
            self.pause_processing = False


    def node_names_table_cellChanged(self):
        names = {'sg': None, 'a1': None, 'a2': None, 'tem': None, 'fp': None}
        for row,key in enumerate(['sg', 'a1', 'a2', 'tem', 'fp']):
            names[key] = self.ui.node_names_tableWidget.item(row, 1).text()
        self.names = names

    def load_graph(self):
        fullfile, _ = QFileDialog.getOpenFileName(self,
                                                   "Open Graph File",
                                                   ".",
                                                   "dot files (*.dot)")
        dotpath, self.dotfile = os.path.split(fullfile)
        self.searchpath = [dotpath,]
        self.ui.graph_file_lineEdit.setText(self.dotfile)
        self.ui.search_path_lineEdit.setText(str(self.searchpath))
        # print(self.dotfile, self.searchpath)


    def about_triggered(self):
        QMessageBox.about(self, "TEMField",
                          "Susceptibility measurements in (G)TEM-cell.\n\n(c) 2024: Prof. H. G. Krauthäuser")

    def cw_doubleSpinBox_changed(self):
        self.cw = self.ui.cw_doubleSpinBox.value()

    def am_spinBox_changed(self):
        self.am = self.ui.am_spinBox.value()

    def closeEvent(self, event):
        # fire confirmation box
        self.log("close event")
        ret = QMessageBox.question(self, "TEMField",
                                       "Do you want to exit the application?",
                                           QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
        if ret == QMessageBox.StandardButton.Yes:
            if self.table_is_unsaved:
                ret = QMessageBox.question(self, "Table is unsaved",
                                              "Do you want to save the table?", QMessageBox.StandardButton.No,
                                           QMessageBox.StandardButton.Yes)
                if ret == QMessageBox.StandardButton.Yes:
                    self.save_Table()
            self._save_setup()
            self.meas.quit_measurement()
            self.log("Exit Application")
            event.accept()
        else:
            self.log("Continue Application")
            event.ignore()

    def _read_setup(self):
        self.log("read setup")
        self.start_freq = float(self.settings.value("frequencies/start_freq", 30.))
        self.stop_freq = float(self.settings.value("frequencies/stop_freq", 1000.))
        self.step_freq = float(self.settings.value("frequencies/step_freq", 1.))
        self.log_sweep = (True if self.settings.value("frequencies/log_sweep", True) in (True, 'true', 'True') else False)
        self.cw = float(self.settings.value("fieldstrength/cw", 1.))
        self.am = float(self.settings.value("fieldstrength/am", 80.))
        self.dwell_time = float(self.settings.value("settings/dwell_time", 1.))
        self.dotfile = self.settings.value("settings/dotfile", os.path.abspath('./conf/gtem.dot'))
        self.searchpath = self.settings.value("settings/searchpath", ['.', os.path.abspath('./conf')])
        self.names = self.settings.value("settings/names", {'sg': 'sg', 'a1': 'amp1', 'a2': 'amp2',
                                                            'tem': 'gtem', 'fp': 'prb'})
        self.eut_description = self.settings.value("settings/eut-description", '')
        self.table_save_dir = self.settings.value("settings/table-save-dir", '.')
        self.table_save_dir = os.path.abspath(self.table_save_dir)
        self.adjust_to_setting = self.settings.value("settings/adjust_to_setting", 'auto')   # 'x', 'y', 'z', 'mag', 'largest', 'auto'
        # print("Init: ", self.log_sweep)
        # print(type(self.log_sweep), self.log_sweep)
        self.ui.log_sweep_checkBox.setChecked(self.log_sweep)
        self.ui.freq_start_doubleSpinBox.setValue(self.start_freq)
        self.ui.freq_stop_doubleSpinBox.setValue(self.stop_freq)
        self.ui.freq_step_doubleSpinBox.setValue(self.step_freq)
        self.ui.cw_doubleSpinBox.setValue(self.cw)
        self.ui.am_spinBox.setValue(self.am)
        self.ui.dwell_time_doubleSpinBox.setValue(self.dwell_time)
        self.ui.graph_file_lineEdit.setText(self.dotfile)
        self.ui.search_path_lineEdit.setText(str(self.searchpath))
        for row,key in enumerate(['sg', 'a1', 'a2', 'tem', 'fp']):
            self.ui.node_names_tableWidget.setItem(row, 1, QTableWidgetItem(self.names[key]))
        self.ui.EUT_plainTextEdit.setPlainText(self.eut_description)
        if self.adjust_to_setting == 'auto':
                self.ui.radioButton_Auto.setChecked(True)
        elif self.adjust_to_setting == 'x':
                self.ui.radioButton_Ex.setChecked(True)
        elif self.adjust_to_setting == 'y':
                self.ui.radioButton_Ey.setChecked(True)
        elif self.adjust_to_setting == 'z':
                self.ui.radioButton_Ez.setChecked(True)
        elif self.adjust_to_setting == 'mag':
                self.ui.radioButton_absE.setChecked(True)
        elif self.adjust_to_setting == 'largest':
                self.ui.radioButton_Largest_E.setChecked(True)



    def _save_setup(self):
        self.log("save setup")
        self.settings.setValue("frequencies/start_freq", self.start_freq)
        self.settings.setValue("frequencies/stop_freq", self.stop_freq)
        self.settings.setValue("frequencies/step_freq", self.step_freq)
        self.settings.setValue("frequencies/log_sweep", self.log_sweep)
        self.settings.setValue("fieldstrength/cw", self.cw)
        self.settings.setValue("fieldstrength/am", self.am)
        self.settings.setValue("settings/dwell_time", self.dwell_time)
        self.settings.setValue("settings/searchpath", self.searchpath)
        self.settings.setValue("settings/dotfile", self.dotfile)
        self.settings.setValue("settings/names", self.names)
        self.settings.setValue("settings/eut-description", self.eut_description)
        self.settings.setValue("settings/table-save-dir", self.table_save_dir)
        self.settings.setValue("settings/adjust_to_setting", self.adjust_to_setting)
        # print("Exit: ", self.log_sweep)
        self.settings.sync()

    def update(self):
        if self.disable_update:
            return
        # print("update")
        self.log_sweep = True if self.ui.log_sweep_checkBox.checkState() == Qt.CheckState.Checked else False
        # print("update", self.log_sweep)
        if not self.log_sweep:
            self.ui.freq_step_doubleSpinBox.setSuffix(' MHz')
            self.ui.freq_step_doubleSpinBox.setDecimals(4)
            self.ui.freq_step_doubleSpinBox.setRange(0, 99999.9999)
        else:
            self.ui.freq_step_doubleSpinBox.setSuffix('%')
            self.ui.freq_step_doubleSpinBox.setDecimals(2)
            self.ui.freq_step_doubleSpinBox.setRange(0, 99.99)

        self.start_freq = self.ui.freq_start_doubleSpinBox.value()
        self.stop_freq = self.ui.freq_stop_doubleSpinBox.value()
        self.step_freq = self.ui.freq_step_doubleSpinBox.value()
        if not self.log_sweep:
            self.freqs = linspace(self.start_freq, self.stop_freq, self.step_freq, endpoint=True)
        else:
            self.freqs = logspace(self.start_freq, self.stop_freq, 1+self.step_freq*0.01, endpoint=True)
        self.freqs = [f*1e6 for f in self.freqs]  # convert to Hz
        self.ui.nr_freqs_lineEdit.setText(str(len(self.freqs)))
        self.ui.freqs_plainTextEdit.setPlainText('\n'.join(map(str, self.freqs)))

        self.dwell_time = self.ui.dwell_time_doubleSpinBox.value()
        time_s = (self.dwell_time + 0.9) * len(self.freqs)  # 0.9 s offset per freq
        self.ui.est_time_lineEdit.setText(' '+str(datetime.timedelta(seconds=round(time_s,0)))+' (hh:mm:ss)')

    def get_time_as_string(self, format=None):
        if format is None:
            tstr = tstamp()   # default format from Mpy
        elif format == '':
            format = "%Y-%m-%dT%H:%M:%S.%f%z"
            tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
            tstr = datetime.datetime.now(tz=tz).strftime(format)
        return tstr

    def save_Table(self):
        path, _ = QFileDialog.getSaveFileName(self, caption='Save as CSV',
                                              dir=self.table_save_dir, filter='(*.csv)',
                                              options=QFileDialog.Option.DontUseNativeDialog)
        self.table_save_dir = os.path.dirname(path)
        if path:
            columns = range(self.ui.table_tableWidget.columnCount())
            header = [self.ui.table_tableWidget.horizontalHeaderItem(column).text()
                      for column in columns]
            with open(path, 'w') as csvfile:
                t = self.get_time_as_string(format='')
                csvfile.write(f"# File saved: {t}\n#\n")
                csvfile.write('# EUT Description\n')
                plaintext_EUT = self.eut_description
                for eut_line in plaintext_EUT.splitlines():
                    csvfile.write(f"# {eut_line}\n")

                writer = csv.writer(
                    csvfile, dialect='excel', lineterminator='\n')
                writer.writerow(header)
                for row in range(self.ui.table_tableWidget.rowCount()):
                    writer.writerow(
                        self.ui.table_tableWidget.item(row, column).text()
                        for column in columns)
                self.table_is_unsaved = False

def main():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    app.setOrganizationName("TUD-TETEMV")
    app.setOrganizationDomain("tu-dresden.de/et/tet")
    app.setApplicationName("TEMField")
    settings = QSettings()

    QLocale.setDefault(QLocale.Language.English)

    widget = MainWindow(settings)
    widget.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()