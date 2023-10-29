import sys
import random
import time
from PyQt5.QtWidgets import QHBoxLayout, QApplication, QMainWindow, QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout, QGridLayout, QTreeWidget, QTreeWidgetItem, QMessageBox
from PyQt5.QtCore import QTimer
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


class PCRIdentificationProcess(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCR Identification Process")
        self.setGeometry(100, 100, 800, 480)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.profile_combobox = QComboBox()
        self.profile_combobox.addItems(
            [str(key) for key in profile_PCR.keys()])

        self.profile_buttons = []
        for key in profile_PCR.keys():
            button = QPushButton(str(key))
            self.profile_buttons.append(button)

        self.profile_grid = QGridLayout()
        self.profile_grid.setHorizontalSpacing(10)
        self.profile_grid.setVerticalSpacing(10)
        self.profile_grid.addWidget(QLabel("PCR Identification Process", alignment=QtCore.Qt.AlignCenter,
                                           font=QtGui.QFont("Sanserif", 20, QtGui.QFont.Bold)))
        self.profile_grid.addWidget(
            QLabel("Pilih Profile PCR yang Akan Digunakan: "), 1, 0)

        # row = 1
        # col = 0
        # for button in self.profile_buttons:
        #     self.profile_grid.addWidget(button, row, col)
        #     col += 1
        #     if col == 3:
        #         col = 0
        #         row += 1

        # if len(self.profile_buttons) % 3 != 0:
        #     spacer = QWidget()
        #     self.profile_grid.addWidget(spacer, row, col, 1, 2)
        # self.profile_grid.clicked.connect(self.show_selected_profile)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.switch_to_process)

        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.profile_grid)
        self.layout.addWidget(self.profile_combobox)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.exit_button)

        self.central_widget.setLayout(self.layout)
        self.selected_profile = None

    def switch_to_process(self):
        self.selected_profile = self.profile_combobox.currentText()
        if self.selected_profile:
            self.process_view = ProcessView(self.selected_profile)
            self.setCentralWidget(self.process_view)
        else:
            QMessageBox.critical(
                self, "Error", "Please select a PCR profile first.")

    def show_selected_profile(self, button):
        self.selected_profile = int(button.text())


class ProcessView(QWidget):
    def __init__(self, input_numpad):
        super().__init__()
        self.input_numpad = int(input_numpad)
        self.process_running = False
        self.chart_thread = None
        self.process_thread = None
        self.chart_timer = QTimer(self)
        self.initUI()

    def initUI(self):
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        data_pcr = profile_PCR.get(self.input_numpad)
        self.ax.set_xlim(0, len(data_pcr))
        self.ax.set_ylim(0, 100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.draw()

        self.table = QTreeWidget()
        self.table.setHeaderLabels(["Component", "Value"])
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 80)

        # Buat objek QTreeWidgetItem
        self.cycle_item = QTreeWidgetItem(["Cycle", "0"])
        self.suhu_item = QTreeWidgetItem(["Suhu", "0"])
        self.light_item = QTreeWidgetItem(["Intensity", "0"])

        # Tambahkan objek QTreeWidgetItem ke objek QTreeWidget
        self.table.addTopLevelItem(self.cycle_item)
        self.table.addTopLevelItem(self.suhu_item)
        self.table.addTopLevelItem(self.light_item)

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

    def simulate_process(self):
        profile = profile_PCR.get(self.input_numpad)
        num_cycle = 0
        if not self.process_running:
            self.process_running = True
            # self.chart_timer.timeout.connect(self.update_chart)
            self.chart_thread = threading.Thread(target=self.update_chart)
            self.chart_thread.start()
            self.process_thread = threading.Thread(target=self.run_simulation)
            self.process_thread.start()
        else:
            QMessageBox.critical(
                self, "Error", "Process is already running.")

    def run_simulation(self):
        profile = profile_PCR.get(self.input_numpad)
        if profile:
            while self.process_running:
                self.chart_timer.start(1000)  # Update chart every 1 seconds
        else:
            QMessageBox.critical(self, "Error", "No profile selected.")

    def stop_process(self):
        if self.process_running:
            self.process_running = False
            self.chart_timer.stop()
            self.chart_thread.join()
            self.process_thread.join()

    def update_chart(self):
        profile = profile_PCR.get(self.input_numpad)
        data_suhu = []
        data_intensity = []
        if profile:
            while self.process_running and len(data_suhu) < profile["jumlah_cycle"]:
                data_suhu.append(random.randint(30, 90))
                data_intensity.append(random.randint(0, 80))
                self.ax.clear()
                self.ax.plot(
                    [(i+1) for i in range(len(data_intensity))], data_intensity)
                self.ax.plot(
                    [(i+1) for i in range(len(data_suhu))], data_suhu)
                # tambahkan legend
                self.ax.legend(["Sampel 1", "Sampel 2"])
                # tambahkan judul grafik
                self.ax.set_title("PCR Graphic Result")
                self.ax.set_xlabel("Jumlah Cycle")
                self.ax.set_xlim(0, profile["jumlah_cycle"]+1)
                self.ax.set_ylim(0, 100)
                self.ax.set_ylabel("Pembacaan Lux")
                # Ubah nilai suhu di tabel menjadi nilai data terakhir
                self.suhu_item.setText(1, str(data_suhu[-1]))  # Dummy
                self.cycle_item.setText(1, str(len(data_suhu)))  # Udah Bener
                self.light_item.setText(1, str(data_intensity[-1]))  # Dummy
                self.canvas.draw()
            # jika selesai, jalankan fungsi stop_process
            self.stop_process()
        else:
            QMessageBox.critical(self, "Error", "No profile selected.")

    def switch_to_standby(self):
        self.stop_process()
        self.standby_view = PCRIdentificationProcess()
        window.setCentralWidget(self.standby_view)


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
