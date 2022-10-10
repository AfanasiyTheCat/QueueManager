import json
import sys
from PyQt6.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt6.QtGui  import QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QStackedLayout, QLabel, QHBoxLayout,
    QGridLayout, QSpinBox, QDoubleSpinBox,
    )

from QueueSimulation import QueueSimulation


class SimulationThread(QThread):

    queue_update = pyqtSignal(object)
    def __init__(self, queue_simulation, parent):
        QThread.__init__(self, parent=parent)
        self.queue_simulation: QueueSimulation = queue_simulation
        self.queue_simulation.queue_pop_event = lambda ind, size, avg_speed: self.queue_update.emit({
            "ind": ind,
            "size": size,
            "avg_speed": avg_speed,
        })

    def run(self):
        self.queue_simulation.simulation_start()

class QueueWidget(QWidget):

    DEFAULT_SPEED_MIN = 1
    DEFAULT_SPEED_MAX = 4
    FONT_SIZE = 20
    FONT_SMALL_SIZE = 14

    def __init__(self, font = ...):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.queue_speed_min_changed = lambda v: None
        self.queue_speed_max_changed = lambda v: None

        font = QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(self.FONT_SIZE)
        font.setBold(True)
        font.setWeight(75)

        self.queue_size = QLabel("0")
        self.queue_size.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.queue_size.setFont(font)
        layout.addWidget(self.queue_size)

        self.queue_speed = QLabel("")
        self.queue_speed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ufont = QFont(font)
        ufont.setPointSize(self.FONT_SMALL_SIZE)
        self.queue_speed.setFont(ufont)
        layout.addWidget(self.queue_speed)

        queue_speed_layout = QHBoxLayout()
        layout.addLayout(queue_speed_layout)

        self.queue_speed_min = QSpinBox()
        self.queue_speed_min.setValue(QueueWidget.DEFAULT_SPEED_MIN)
        self.queue_speed_min.setMinimum(0)
        self.queue_speed_min.valueChanged.connect(lambda: self.queue_speed_min_changed(self.queue_speed_min.value()))
        queue_speed_layout.addWidget(self.queue_speed_min)

        queue_speed_layout.addWidget(QLabel("-"))

        self.queue_speed_max = QSpinBox()
        self.queue_speed_max.setValue(QueueWidget.DEFAULT_SPEED_MAX)
        self.queue_speed_max.setMinimum(0)
        self.queue_speed_max.valueChanged.connect(lambda: self.queue_speed_max_changed(self.queue_speed_max.value()))
        queue_speed_layout.addWidget(self.queue_speed_max)
    
    def set_queue_size(self, size):
        self.queue_size.setText(str(size))
    
    def set_queue_speed(self, speed):
        self.queue_speed.setText("{:10.2f}/c".format(speed))

class StringsManager():
    def __init__(self):
        pass


class MainWindow(QMainWindow):

    DEFAULT_QUEUE_COUNT = 3
    QUEUES_IN_ROW = 5

    def __init__(self):
        super().__init__()

        self.strings = self._load_strings("strings.json", "ru")

        self.queue_simulation = QueueSimulation(MainWindow.DEFAULT_QUEUE_COUNT)
        self.queue_widgets = []

        self._init_gui()
        self.add_queue(MainWindow.DEFAULT_QUEUE_COUNT)

    def update_queue(self, ind, size, avg_speed):
        self.queue_widgets[ind].set_queue_size(size)
        self.queue_widgets[ind].set_queue_speed(avg_speed)

    def add_queue(self, count=1):
        for i in range(count):
            ind = len(self.queue_widgets)
            queue_widget = QueueWidget()
            self.queues_layout.addWidget(queue_widget, ind/self.QUEUES_IN_ROW, ind%self.QUEUES_IN_ROW)
            self.queue_widgets.append(queue_widget)
            queue_widget.set_queue_size(0)
            queue_widget.set_queue_speed(0)
            queue_widget.queue_speed_min_changed = lambda v: self.queue_simulation.set_queue_period_min(ind, v)
            queue_widget.queue_speed_max_changed = lambda v: self.queue_simulation.set_queue_period_max(ind, v)
    
    def remove_queue(self, count=1):
        n = len(self.queue_widgets)-1
        for i in range(count):
            self.queue_widgets.pop().deleteLater()
    
    def set_queues_count(self, new_count):
        an = len(self.queue_widgets)
        if new_count != an:
            if an < new_count:
                self.add_queue(new_count - an)
                self.queue_simulation.set_queues_count(new_count)
            if an > new_count:
                self.queue_simulation.set_queues_count(new_count)
                self.remove_queue(an - new_count)

    def _init_gui(self):
        self.setWindowTitle("Queue Simulation")
        self.setMinimumSize(QSize(400, 300))

        self.root_layout = QVBoxLayout()
        root_widget = QWidget()
        root_widget.setLayout(self.root_layout)
        self.setCentralWidget(root_widget)        

        # Область с очередьми
        self.queues_layout = QGridLayout()
        self.queues_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.root_layout.addLayout(self.queues_layout)

        # Область с элементами управления
        self.controls_layout = QGridLayout()
        self.controls_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.root_layout.addLayout(self.controls_layout)

        queue_count = QSpinBox()
        queue_count.setValue(self.DEFAULT_QUEUE_COUNT)
        queue_count.valueChanged.connect(lambda: self.set_queues_count(queue_count.value()))
        queue_count.setMinimum(1)
        self._add_control_input(self.strings["queue_count"], self.strings["queue_count_tooltip"], 
            queue_count, (0, 0))

        queue_append_period = QSpinBox()
        queue_append_period.setValue(self.queue_simulation.DEFAULT_APPEND_PERIOD)
        queue_append_period.valueChanged.connect(lambda: self.queue_simulation.set_queue_append_period(queue_append_period.value()))
        queue_append_period.setMinimum(1)
        self._add_control_input(self.strings["queue_append_period"], self.strings["queue_append_period_tooltip"],
            queue_append_period, (1, 0))
        
        simulation_control_layout = QVBoxLayout()
        self.controls_layout.addLayout(simulation_control_layout, 0, 1)
        self.simulation_start_btn = QPushButton(self.strings["simulation_start"])
        self.simulation_start_btn.clicked.connect(self.start_simulation)
        simulation_control_layout.addWidget(self.simulation_start_btn)
        self.simulation_stop_btn = QPushButton(self.strings["simulation_stop"])
        self.simulation_stop_btn.clicked.connect(self.stop_simulation)
        simulation_control_layout.addWidget(self.simulation_stop_btn)

        queue_append_size = QSpinBox()
        queue_append_size.setValue(self.queue_simulation.DEFAULT_APPEND_SIZE)
        queue_append_size.valueChanged.connect(lambda: self.queue_simulation.set_queue_append_size(queue_append_size.value()))
        queue_append_size.setMinimum(0)
        self._add_control_input(self.strings["queue_append_size"], self.strings["queue_append_size_tooltip"],
            queue_append_size, (1, 1))
    
    def _add_control_input(self, label, tooltip, widget, pos):
        layout = QVBoxLayout()
        lbl = QLabel(label)
        lbl.setToolTip(tooltip)
        layout.addWidget(lbl)
        layout.addWidget(widget)
        self.controls_layout.addLayout(layout, pos[0], pos[1])        

    def start_simulation(self):
        if not self.queue_simulation.is_simulation:
            simulation_thread = SimulationThread(self.queue_simulation, self)
            simulation_thread.queue_update.connect(lambda obj: self.update_queue(obj["ind"], obj["size"], obj["avg_speed"]))
            simulation_thread.start()
            self.simulation_start_btn.setText(self.strings["simulation_pause"])
        else:
            self.queue_simulation.simulation_stop()
            self.simulation_start_btn.setText(self.strings["simulation_start"])
    
    def stop_simulation(self):
        self.queue_simulation.simulation_stop()
        self.simulation_start_btn.setText(self.strings["simulation_start"])
    
    def _load_strings(self, filename, lang):
        strings_json = json.loads(open(filename, encoding="utf-8").read())
        return strings_json[lang]

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()