
import sys
import pathlib
import traceback

import numpy as np
import scipy as sp

import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from PyQt6 import QtGui

import DNMR.fileops as fileops
from DNMR.miniwidgets import *

from DNMR.tab_phase_adj import *
from DNMR.tab_fourier_transform import *
from DNMR.tab_t1_fitting import *
from DNMR.tab_field_scan import *
from DNMR.tab_peak_amplitude import *
from DNMR.tab_inv_laplace import *

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        path_to_icon = str(pathlib.Path(__file__).parent.absolute())+'/icon_transparent.png'
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(pathlib.Path(path_to_icon).read_bytes())
        appIcon = QtGui.QIcon(pixmap)
        
        self.setWindowIcon(appIcon)

        self.tabwidget_tabs = QTabWidget()
        data_widgets = {}
        self.fileselector = FileSelectionWidget()
        data_widgets['fileselector'] = self.fileselector
        if(len(sys.argv) > 1): # passed arguments are files to load
            self.fileselector.load_files(sys.argv[1:])
        
        self.pushbutton_process = QPushButton('Reload')
        self.pushbutton_process.clicked.connect(self.update_all)
        
        self.filedialog_export = QFileDialog()
        self.button_export = QPushButton('Export Data (CSV)')
        self.button_export.clicked.connect(self.export_selected)
        
        self.tab_phaseadj = TabPhaseAdjustment(data_widgets, self)
        self.tab_ft = TabFourierTransform(data_widgets, self)
        self.tab_t1 = TabT1Fit(data_widgets, self)
        self.tab_fieldscan = TabFieldScan(data_widgets, self)
        self.tab_peakamp = TabPeakAmplitude(data_widgets, self)
        self.tab_inv_laplace = TabInvLaplace(data_widgets, self)

        self.tabwidget_tabs.addTab(self.tab_phaseadj, 'Time Domain')
        self.tabwidget_tabs.addTab(self.tab_ft, 'Freq. Domain')
        self.tabwidget_tabs.addTab(self.tab_t1, 'T1 Fit')
        self.tabwidget_tabs.addTab(self.tab_fieldscan, 'Field Scan')
        self.tabwidget_tabs.addTab(self.tab_peakamp, 'Peak Amplitudes')
        self.tabwidget_tabs.addTab(self.tab_inv_laplace, 'Inverse Laplace')
        self.tabwidget_tabs.currentChanged.connect(lambda: self.tabwidget_tabs.currentWidget().update())

        layout = QVBoxLayout()
        layout.addWidget(self.tabwidget_tabs)
        layout.addWidget(self.fileselector)
        layouth = QHBoxLayout()
        layouth.addWidget(self.pushbutton_process)
        layouth.addWidget(self.button_export)
        layout.addLayout(layouth)
        self.setLayout(layout)

    def export_selected(self):
        fn = self.filedialog_export.getSaveFileName()[0]
        saved_dict = self.tabwidget_tabs.currentWidget().get_exported_data()
        print(saved_dict)
        df = pd.DataFrame(dict([ (k, pd.Series(v)) for k,v in saved_dict.items() ]))
        df.to_csv(path_or_buf=fn)
        print('Exporting dataframe:')
        print(df)

    def update_all(self):
        ct = self.tabwidget_tabs.count()
        for i in range(ct):
            self.tabwidget_tabs.widget(i).update()

def start_app():
    print('Starting QT. Please wait...')
    app = QApplication(sys.argv)
    main = MainWindow()
    main.setWindowTitle('DNMR')
    main.resize(640, 960)
    main.show()

    try:
        app.exec()
    except:
        traceback.print_exc
        
if __name__=='__main__':
    start_app()