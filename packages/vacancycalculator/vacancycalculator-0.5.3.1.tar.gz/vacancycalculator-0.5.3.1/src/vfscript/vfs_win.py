from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget
from vfscript.gui.training_tab import TrainingTab
from vfscript.gui.processing_tab import ProcessingTab
import sys

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VacancyFinder-SiMAF – Training / Procesado")
        self.resize(1280, 800)

        tabs = QTabWidget()
        self.training_tab = TrainingTab(self)
        tabs.addTab(self.training_tab, "Training")

        self.processing_tab = ProcessingTab(self)
        tabs.addTab(self.processing_tab, "Procesado")

        self.setCentralWidget(tabs)

def main():
    app = QApplication(sys.argv)
    win = SettingsWindow()
    win.show()
    app.exec()
