import sys
import os
import random
import time
from PyQt5.QtWidgets import QHeaderView, QAbstractScrollArea, QTableView, QTabBar, QHBoxLayout, QApplication, QMainWindow, QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout, QGridLayout, QTreeWidget, QTreeWidgetItem, QMessageBox
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pynput import keyboard
from services.profil_PCR import profile_PCR
import matplotlib.pyplot as plt
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import threading
from services.save_service import save_service
from services.upload_service import upload_service


# Direktori untuk menyimpan data hasil identifikasi
directory = r'c:\Users\user\OneDrive\Dokumen'


class PCRIdentificationProcess(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCR Identification Process")
        self.setGeometry(512, 300, 1024, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.profile_combobox = QComboBox()
        self.profile_combobox.addItems(
            [profile_PCR[key]['nama_profile'] for key in profile_PCR.keys()])

        self.profile_buttons = []
        for key in profile_PCR.keys():
            button = QPushButton(str(key))
            self.profile_buttons.append(button)

        self.profile_grid = QGridLayout()
        self.profile_grid.setHorizontalSpacing(15)
        self.profile_grid.setVerticalSpacing(15)
        self.profile_grid.addWidget(QLabel("PCR Identification Process", alignment=QtCore.Qt.AlignCenter,
                                           font=QtGui.QFont("Sanserif", 20, QtGui.QFont.Bold)))
        self.profile_grid.addWidget(
            QLabel("Pilih Profile PCR yang Akan Digunakan: "))

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.switch_to_process)

        self.history_button = QPushButton("History")
        self.history_button.clicked.connect(self.switch_to_histories)

        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)

        self.grid_layout = QHBoxLayout()
        self.grid_layout.addWidget(self.profile_combobox)
        self.grid_layout.addWidget(self.start_button)
        self.grid_layout.addWidget(self.history_button)
        self.grid_layout.addWidget(self.exit_button)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.profile_grid)
        self.layout.addLayout(self.grid_layout)

        self.central_widget.setLayout(self.layout)
        self.selected_profile = None

    def switch_to_process(self):
        self.selected_profile = self.profile_combobox.currentIndex() + 1
        if self.selected_profile:
            self.process_view = ProcessView(self.selected_profile)
            self.setCentralWidget(self.process_view)
        else:
            QMessageBox.critical(
                self, "Error", "Please select a PCR profile first.")

    def switch_to_histories(self):
        self.histories_view = HistoriesView()
        self.setCentralWidget(self.histories_view)

    def show_selected_profile(self, button):
        self.selected_profile = int(button.text())


class ProcessView(QWidget):
    def __init__(self, input_numpad):
        super().__init__()
        self.input_numpad = int(input_numpad)
        self.process_running = False
        self.chart_thread = None
        self.table_thread = None
        self.process_thread = None
        self.timer = QTimer(self)
        self.data_suhu = []
        self.data_intensity_sampel_1 = []
        self.data_intensity_sampel_2 = []
        self.data_intensity_control_pos = []
        self.data_intensity_control_neg = []
        self.all_data = {}
        # Lock untuk sinkronisasi akses data_suhu dan data_intensity
        self.data_lock = threading.Lock()
        self.initUI()

    def initUI(self):
        self.fig, self.ax = plt.subplots(figsize=(7, 4))
        data_pcr = profile_PCR.get(self.input_numpad)
        self.ax.set_xlim(0, data_pcr["jumlah_cycle"]+1)
        self.ax.set_ylim(0, 100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.draw()

        self.table = QTreeWidget()
        self.table.setHeaderLabels(["Component", "Value"])
        self.table.setColumnWidth(0, 170)
        self.table.setColumnWidth(1, 50)

        # Buat objek QTreeWidgetItem
        self.cycle_item = QTreeWidgetItem(["Cycle", "0"])
        self.suhu_item = QTreeWidgetItem(["Suhu", "0"])
        self.intensity_control_pos = QTreeWidgetItem(
            ["Intensity Control Pos", "0"])
        self.intensity_control_neg = QTreeWidgetItem(
            ["Intensity Control Neg", "0"])
        self.intensity_sampel_1_item = QTreeWidgetItem(
            ["Intensity Sample 1", "0"])
        self.intensity_sampel_2_item = QTreeWidgetItem(
            ["Intensity Sample 2", "0"])

        # Tambahkan objek QTreeWidgetItem ke objek QTreeWidget
        self.table.addTopLevelItem(self.cycle_item)
        self.table.addTopLevelItem(self.suhu_item)
        self.table.addTopLevelItem(self.intensity_control_pos)
        self.table.addTopLevelItem(self.intensity_control_neg)
        self.table.addTopLevelItem(self.intensity_sampel_1_item)
        self.table.addTopLevelItem(self.intensity_sampel_2_item)

        self.simulate_button = QPushButton("Simulate Process")
        self.simulate_button.clicked.connect(self.simulate_process)
        self.stop_button = QPushButton("Stop Process")
        self.stop_button.clicked.connect(self.stop_process)
        self.back_button = QPushButton("Back to Standby")
        self.back_button.clicked.connect(self.switch_to_standby)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.table)
        self.layout_widget = QWidget()
        self.layout_widget.setLayout(self.layout)

        self.layout_buttons = QHBoxLayout()
        self.layout_buttons.addWidget(self.simulate_button)
        self.layout_buttons.addWidget(self.stop_button)
        self.layout_buttons.addWidget(self.back_button)

        self.layout_main = QVBoxLayout()
        self.layout_main.addWidget(QLabel("Identification WSSV on Shrimp"))
        self.layout_main.addWidget(self.layout_widget)
        self.layout_main.addLayout(self.layout_buttons)

        self.setLayout(self.layout_main)

    def start_simulation(self):
        profile = profile_PCR.get(self.input_numpad)
        if profile:
            cycle_times = profile["jumlah_cycle"]
            if self.current_cycle < cycle_times:
                self.process_thread = threading.Thread(
                    target=self.run_simulation)
                self.process_thread.start()
                self.chart_thread = threading.Thread(target=self.update_chart)
                self.chart_thread.start()
                self.table_thread = threading.Thread(target=self.update_table)
                self.table_thread.start()
                self.stop_thread = threading.Thread(target=self.stop_process)
                self.stop_thread.start()

                # 100000 adalah faktor konversi dari detik ke milidetik
                cycle_time = (sum(profile['waktu']) * 1000000)
                self.timer.setInterval(cycle_time)
                self.timer.start(cycle_time)
            else:
                self.all_data = {
                    "Sample 1": self.data_intensity_sampel_1,
                    "Sample 2": self.data_intensity_sampel_2,
                    "Control Positive": self.data_intensity_control_pos,
                    "Control Negative": self.data_intensity_control_neg
                }
                self.stop_process()
                self.stop_thread.join()
                save_service("txt", self.all_data, directory)
        else:
            QMessageBox.critical(self, "Error", "No profile selected.")

    def simulate_process(self):
        if not self.process_running:
            self.process_running = True
            self.current_cycle = 0
            self.start_simulation()
        else:
            QMessageBox.critical(
                self, "Error", "Process is already running.")

    def run_simulation(self):
        profile = profile_PCR.get(self.input_numpad)
        if profile:
            with self.data_lock:
                self.data_suhu.append(random.randint(30, 90))
                self.data_intensity_sampel_1.append(
                    random.randint(5, 80))
                self.data_intensity_sampel_2.append(
                    random.randint(5, 80))
                self.data_intensity_control_pos.append(
                    random.randint(50, 100))
                self.data_intensity_control_neg.append(
                    random.randint(10, 40))
                self.current_cycle += 1
            self.update_table()
            self.update_chart()
            self.start_simulation()
        else:
            QMessageBox.critical(self, "Error", "No profile selected.")

    def stop_process(self):
        if self.process_running:
            self.process_running = False
            self.chart_thread.join()
            self.table_thread.join()
            self.process_thread.join()
            self.timer.stop()

    def update_chart(self):
        profile = profile_PCR.get(self.input_numpad)
        if profile:
            with self.data_lock:
                self.ax.clear()
                self.ax.plot(
                    [i+1 for i in range(len(self.data_intensity_control_pos))], self.data_intensity_control_pos)
                self.ax.plot(
                    [i+1 for i in range(len(self.data_intensity_control_neg))], self.data_intensity_control_neg)
                self.ax.plot(
                    [i+1 for i in range(len(self.data_intensity_sampel_1))], self.data_intensity_sampel_1)
                self.ax.plot(
                    [i+1 for i in range(len(self.data_intensity_sampel_2))], self.data_intensity_sampel_2)
                self.ax.legend(
                    ["Control Positive", "Control Negative", "Sampel 1", "Sampel 2"], loc='upper right')
                self.ax.set_title("PCR Graphic Result")
                self.ax.set_xlabel("Number of Cycle")
                self.ax.set_xlim(0, profile["jumlah_cycle"]+1)
                self.ax.set_ylim(0, 100)
                self.ax.set_ylabel("Lux Levels")
                self.canvas.draw()
        else:
            QMessageBox.critical(self, "Error", "No profile selected.")

    def update_table(self):
        profile = profile_PCR.get(self.input_numpad)
        if profile:
            with self.data_lock:
                self.cycle_item.setText(1, str(len(self.data_suhu)))
                self.suhu_item.setText(1, str(self.data_suhu[-1]))
                self.intensity_control_pos.setText(
                    1, str(self.data_intensity_control_pos[-1]))
                self.intensity_control_neg.setText(
                    1, str(self.data_intensity_control_neg[-1]))
                self.intensity_sampel_1_item.setText(
                    1, str(self.data_intensity_sampel_1[-1]))
                self.intensity_sampel_2_item.setText(
                    1, str(self.data_intensity_sampel_2[-1]))
        else:
            QMessageBox.critical(self, "Error", "No profile selected.")

    def switch_to_standby(self):
        self.standby_view = PCRIdentificationProcess()
        window.setCentralWidget(self.standby_view)


class HistoriesView(QAbstractScrollArea):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.table = QTableView()
        self.model = self.initModel()
        self.table.setModel(self.model)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

    def initModel(self):
        model = QtGui.QStandardItemModel(self)
        model.setHorizontalHeaderLabels(["No.", "Date", "Result", "Action"])

        # Membaca file csv dan png di folder Hasil pada direktori utama
        # dan menambahkan data ke dalam tabel
        path = r'c:\Users\user\OneDrive\Dokumen'
        files = os.listdir(path)

        for i, file in enumerate(files):
            if file.endswith(".txt"):
                row = []
                row.append(QtGui.QStandardItem(str(i+1)))
                # row.append(QtGui.QStandardItem(file[:-4]))
                row.append(QtGui.QStandardItem(
                    os.path.getctime(os.path.join(path, file))))
                row.append(QtGui.QStandardItem("5 Positive"))
                row.append(QtGui.QStandardItem("View"))
                model.appendRow(row)

        return model


def on_press(key):
    global input_numpad
    if hasattr(key, 'vk') and 96 <= key.vk <= 105:  # 96-105 adalah kode tombol numpad 0-9
        input_numpad += str(key.vk - 96)
    elif key == keyboard.Key.enter:
        window.central_widget.switch_to_standby()


def on_release(key):
    if key == keyboard.Key.esc:
        return False


if __name__ == "__main__":
    input_numpad = ''

    app = QApplication(sys.argv)
    window = PCRIdentificationProcess()
    idle_view = window.central_widget

    # with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    #     listener.join()

    window.show()
    sys.exit(app.exec_())
