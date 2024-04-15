import os, sys, serial, time
import folium
import numpy as np
from pyqtgraph import PlotWidget
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QTextEdit, QHBoxLayout, QLineEdit
from PyQt5.QtCore import QTimer, QDateTime, Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QPixmap
import serial_read
import random

class TelemetriaWindow(QMainWindow):
    def __init__(self):
        super(TelemetriaWindow, self).__init__()

        self.datatimeLabel = QLabel()
        self.logsfield = QTextEdit()
        self.inputfield = QLineEdit()
        self.map = QWebEngineView()
        self.indicators = QLabel()
        self.battary_temperature_graph = PlotWidget()
        self.battary_voltage_graph = PlotWidget()
        self.battary_amperage_graph = PlotWidget()
        self.pressure_graph = PlotWidget()
        self.accZ_graph = PlotWidget()
        self.temperature_graph = PlotWidget()

        self.indicators.setPixmap(QPixmap("4.png"))
        self.indicators.setScaledContents(True)

        main_layout = QHBoxLayout()

        self.graphLayout = QVBoxLayout()
        self.graphLayout.addWidget(self.pressure_graph)
        self.graphLayout.addWidget(self.temperature_graph)
        self.graphLayout.addWidget(self.battary_temperature_graph)
        self.graphLayout.addWidget(self.battary_voltage_graph)
        self.graphLayout.addWidget(self.battary_amperage_graph)
        self.graphLayout.addWidget(self.accZ_graph)
        main_layout.addLayout(self.graphLayout)

        data_layout = QVBoxLayout()
        data_layout.addWidget(self.datatimeLabel)
        data_layout.addWidget(self.logsfield)
        data_layout.addWidget(self.inputfield)
        bottom_data_layout = QHBoxLayout()
        bottom_data_layout.addWidget(self.map)
        bottom_data_layout.addWidget(self.indicators)
        data_layout.addLayout(bottom_data_layout)
        main_layout.addLayout(data_layout)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
        self.setWindowTitle("Телеметрия")
        self.setGeometry(100, 200, 1000, 600)

        self.pressure_graph.setTitle("Внешнее Давление")
        self.temperature_graph.setTitle("Внешняя температура")
        self.battary_temperature_graph.setTitle("Температура АКБ")
        self.battary_voltage_graph.setTitle("Напряжение АКБ")
        self.battary_amperage_graph.setTitle("Ток АКБ")
        self.accZ_graph.setTitle("Уcкорение по Z")
        self.inputfield.returnPressed.connect(self.update_text)

        self.load_html_content(m.get_root().render(), QUrl.fromLocalFile(os.path.abspath('')))

        self.plot_update_timer = QTimer()
        self.plot_update_timer.setInterval(2000)
        self.plot_update_timer.timeout.connect(self.update_plot)
        self.plot_update_timer.start()

        self.map_update_timer = QTimer()
        self.map_update_timer.setInterval(20000)
        self.map_update_timer.timeout.connect(self.update_map)
        self.map_update_timer.start()

        self.data_pressure = np.zeros(100)
        self.data_temperature = np.zeros(100)
        self.data_battary_temperature = np.zeros(100)
        self.data_battary_voltage = np.zeros(100)
        self.data_battary_amperage = np.zeros(100)
        self.data_accZ = np.zeros(100)
        self.x = np.linspace(0, 10, 100)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b; /* Цвет фона */
            }

            QLabel#datetimeLabel {
                font-size: 22px;
                color: #f0f0f0; /* Цвет текста */
                font-weight: bold;
            }

            QTextEdit {
                background-color: #1e1e1e; /* Цвет фона текстового поля */
                border: 5px solid #000;
                color: #f0f0f0; /* Цвет текста */
                font-size: 14px;
            }

            QLineEdit {
                background-color: #1e1e1e; /* Цвет фона поля ввода */
                color: #f0f0f0; /* Цвет текста */
                font-size: 14px;
                border: 5px solid #555;
                border-radius: 5px;
            }

            PlotWidget {
                background-color: #1e1e1e; /* Цвет фона графиков */
                border: 5px solid #555;
                border-radius: 100px;

            }

            /* Заголовки графиков */
            PlotWidget > QLabel {
                color: #f0f0f0; /* Цвет текста */
            }

            /* Цвет линий графиков */
            PlotWidget > QFrame {
                background-color: #2b2b2b; /* Цвет фона */
            }
        """)

    def update_plot(self):
        global prev_data, port

        try:
            data = serial_read.read_from_com_port(port, 115200)
            if len(data) < 10:
                data = prev_data
            # data = [1, 12483, 20047, round(random.random()*10000, 0), round(random.random()*10, 1), round(random.random(), 0),
            #         0, 0, round(random.random()*10, 1), round(random.random()*10, 1), 0, 0, 0, 56.33, 44.0, 0]
        except:
            data = [1, 12483, 20047, round(random.random()*10000, 0), round(random.random()*10, 1), round(random.random(), 0),
                0, 0, round(random.random()*10, 1), round(random.random()*10, 1), 0, 0, 0, 56.33, 44.0, 0]

        RTCtime = QDateTime.currentDateTime().toString("dd.MM.yyyy hh:mm:ss")
        lora = data[0]
        mission_time = data[1]
        baro_h = data[2]
        pressure = data[3]
        temperature = data[4]
        accZ = data[5]
        accX = data[6]
        accY = data[7]
        battary_temperature = data[8]
        battary_voltage = data[9]
        battary_current = data[10]
        clapanS = data[11]
        nagrev = data[12]
        shirota = data[13]
        dolgota = data[14]
        rssi = data[-1]
        state = ''

        if clapanS:
            state = "стравливание"
        if nagrev:
            nagrev_state = "батарея нагревается"
        else:
            nagrev_state = ''

        log_string = f"Модуль №{lora}\t{RTCtime}\tвремя миссии: {mission_time}c\t{temperature}°C\tускорение х, y, z: {accX, accY, accZ}м/с\tАКБ: {battary_temperature}°C\t{battary_voltage}B\t{battary_current}А\nкоординаты: {shirota}°\t{dolgota}°\t{pressure}Па\t{baro_h}м (по давлению)\t{state}\t{nagrev_state}\trssi {rssi}\n\n\n\n"

        self.data_pressure = np.append(self.data_pressure[1:], pressure)
        self.data_battary_temperature = np.append(self.data_battary_temperature[1:], battary_temperature)
        self.data_battary_voltage = np.append(self.data_battary_voltage[1:], battary_voltage)
        self.data_battary_amperage = np.append(self.data_battary_amperage[1:], battary_current)
        self.data_accZ = np.append(self.data_accZ[1:], accZ)
        prev_data = data
        self.x += 0.1

        self.pressure_graph.plot(self.x, self.data_pressure, clear=True, pen={'color': 'b', 'width': 4})
        self.temperature_graph.plot(self.x, self.data_temperature, clear=True, pen={'color': 'w', 'width': 4})
        self.battary_temperature_graph.plot(self.x, self.data_battary_temperature, clear=True, pen={'color': 'b', 'width': 4})
        self.battary_voltage_graph.plot(self.x, self.data_battary_voltage, clear=True, pen={'color': 'g', 'width': 4})
        self.battary_amperage_graph.plot(self.x, self.data_battary_amperage, clear=True, pen={'color': 'm', 'width': 4})
        self.accZ_graph.plot(self.x, self.data_accZ, clear=True, pen={'color': 'c', 'width': 4})

        self.datatimeLabel.setText(f"{RTCtime}\t{shirota}° {dolgota}° {baro_h} м")
        self.datatimeLabel.setStyleSheet("font-size: 22px; color: white; font-weight: bold;")

        self.logsfield.append(log_string)
        if lora:
            file = open("logs.txt", 'a', encoding='utf-8')
        else:
            file = open("logs2.txt", 'a', encoding='utf-8')
        file.write(log_string)
        file.close()

    def update_text(self):
        global port
        ser = serial.Serial(port, 115200)
        file = open("logs.txt", 'a', encoding='utf-8')
        text = self.inputfield.text().strip()

        match text:
            case "openS":
                text = "Система сдува запущена\n"
                ser.write(b"1103s")
            case "clear":
                text = ''
                self.logsfield.clear()
            case _:
                pass

        self.logsfield.append(text)
        file.write(text)
        file.close()
        self.inputfield.clear()

    def load_html_content(self, content, base_url):
        self.map.setHtml(content, baseUrl=base_url)

    def update_map(self):
        global m, marker, prev_data
        marker.location = [prev_data[5], prev_data[6]]
        m.location = [marker.location[0], marker.location[1]]
        html_content = m.get_root().render()
        self.load_html_content(html_content, QUrl.fromLocalFile(os.path.abspath('')))


if __name__ == "__main__":
    prev_data = [1, 12483, 20047, round(random.random()*10000, 0), round(random.random()*10, 1), round(random.random(), 0),
                0, 0, round(random.random()*10, 1), round(random.random()*10, 1), 0, 0, 0, 56.33, 44.0, 0]
    port = 'COM' + input('введите номер порта: ')

    m = folium.Map(location=[55.9297334, 44.0026], zoom_start=10)
    marker = folium.Marker(location=[55.9297334, 44.0026], popup='Мое местоположение')
    marker.add_to(m)
    m.save('index.html')

    app = QApplication(sys.argv)
    mainWindow = TelemetriaWindow()
    mainWindow.show()
    sys.exit(app.exec_())
