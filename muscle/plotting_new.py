# pip install pyqtgraph

import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg
from PyQt5.QtCore import QTimer

class RealTimePlot(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1000)  # Update every 1000 milliseconds (1 second)

        self.cb1 = []
        self.cb2 = []

    def initUI(self):
        self.centralWidget = pg.GraphicsLayoutWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.plot_widget = self.centralWidget.addPlot(title="Real-time plot")
        self.plot_widget.showGrid(True, True)
        self.plot_widget.setYRange(-180, 180 )

        # Add legends
        self.plot_widget.addLegend()

        self.plot_curve1 = self.plot_widget.plot(pen='r', name='Cam bien 1')
        self.plot_curve2 = self.plot_widget.plot(pen='b', name='Cam bien 2')

    def update_plot(self):
        # Generate random data for demonstration
        new_cb1 = random.uniform(-180, 180)
        new_cb2 = random.uniform(-180, 180)

        # Accumulate data
        self.cb1.append(new_cb1)
        self.cb2.append(new_cb2)

        # Update the entire plot data
        self.plot_curve1.setData(self.cb1, name='Cam bien 1')
        self.plot_curve2.setData(self.cb2, name='Cam bien 2')

def plot_real_time():
    app = QApplication(sys.argv)
    mainWindow = RealTimePlot()
    mainWindow.setGeometry(100, 100, 800, 600)  # Set window size
    mainWindow.show()
    sys.exit(app.exec_())

plot_real_time()
