import sys
import io
import json
import contextlib
import traceback
from pathlib import Path
import shutil
import os

# Forzar backend XCB en Wayland
os.environ["QT_QPA_PLATFORM"] = "xcb"



from vfscript.gui.common import load_params, save_params, render_dump_to
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFormLayout, QCheckBox,
    QDoubleSpinBox, QSpinBox, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QHBoxLayout, QPlainTextEdit, QVBoxLayout,
    QProgressBar, QSizePolicy, QComboBox, QTableWidget, QTableWidgetItem,
    QScrollArea, QLabel, QTabWidget,QGroupBox  
)
from pyvistaqt import QtInteractor
import pyvista as pv
import numpy as np
from ovito.io import import_file
from vfscript import vfs
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from vfscript.training.preparer import *

# ---------- Widgets de viewers internos ----------
class DumpViewerWidget(QWidget):
    """Viewer genérico: igual que load_dump, con selector de archivo."""
    def __init__(self, parent=None):
        super().__init__(parent)
        top = QWidget()
        top_l = QHBoxLayout(top)
        self.path_edit = QLineEdit()
        self.btn_browse = QPushButton("Browse")
        self.btn_load = QPushButton("Load")
        top_l.addWidget(QLabel("File:"))
        top_l.addWidget(self.path_edit, 1)
        top_l.addWidget(self.btn_browse)
        top_l.addWidget(self.btn_load)

        center = QWidget()
        center_l = QVBoxLayout(center)
        self.plotter = QtInteractor(center)
        center_l.addWidget(self.plotter)
        self.fig = plt.figure(figsize=(4, 4))
        self.canvas = FigureCanvas(self.fig)
        center_l.addWidget(self.canvas)

        root_l = QVBoxLayout(self)
        root_l.addWidget(top)
        root_l.addWidget(center, 1)

        self.btn_browse.clicked.connect(self._browse)
        self.btn_load.clicked.connect(self._load_clicked)

    def _browse(self):
        filtros = "All Files (*);;Dump Files (*.dump)"
        start_dir = getattr(self, "_last_dir", str(Path.cwd()))
        abs_path, _ = QFileDialog.getOpenFileName(self, "Select File", start_dir, filtros)
        if abs_path:
            self._last_dir = str(Path(abs_path).parent)
            self.path_edit.setText(abs_path)

    def _load_clicked(self):
        p = self.path_edit.text().strip()
        if not p:
            QMessageBox.warning(self, "Sin archivo", "Seleccione un archivo primero.")
            return
        try:
            render_dump_to(self.plotter, self.fig, p)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def render_dump(self, p: str):
        self.path_edit.setText(p)
        render_dump_to(self.plotter, self.fig, p)


class KeyAreaSeqWidget(QWidget):
    """Viewer para outputs/dump/key_area_{i}.dump con controles de índice."""
    def __init__(self, parent=None, pattern: str = "outputs/dump/key_area_{i}.dump"):
        super().__init__(parent)
        self.pattern = pattern

        top = QWidget()
        top_l = QHBoxLayout(top)
        self.idx = QSpinBox()
        self.idx.setRange(0, 1_000_000)
        self.btn_prev = QPushButton("◀ Prev")
        self.btn_next = QPushButton("Next ▶")
        self.btn_load = QPushButton("Load")
        self.path_lbl = QLineEdit()
        self.path_lbl.setReadOnly(True)

        top_l.addWidget(QLabel("key_area_{i}.dump   i="))
        top_l.addWidget(self.idx)
        top_l.addWidget(self.btn_prev)
        top_l.addWidget(self.btn_next)
        top_l.addWidget(self.btn_load)
        top_l.addWidget(QLabel("Archivo:"))
        top_l.addWidget(self.path_lbl, 1)

        center = QWidget()
        center_l = QVBoxLayout(center)
        self.plotter = QtInteractor(center)
        center_l.addWidget(self.plotter)
        self.fig = plt.figure(figsize=(4, 4))
        self.canvas = FigureCanvas(self.fig)
        center_l.addWidget(self.canvas)

        root_l = QVBoxLayout(self)
        root_l.addWidget(top)
        root_l.addWidget(center, 1)

        self.btn_prev.clicked.connect(lambda: self._step(-1))
        self.btn_next.clicked.connect(lambda: self._step(+1))
        self.btn_load.clicked.connect(self._load_idx)

        self._auto_seed_index()

    def _pattern_path(self, i: int) -> str:
        return self.pattern.format(i=i)

    def _auto_seed_index(self):
        for i in range(0, 10000):
            if Path(self._pattern_path(i)).exists():
                self.idx.setValue(i)
                self._load_idx()
                return
        self.path_lbl.setText("(no encontrado)")

    def _step(self, delta: int):
        new_i = max(0, self.idx.value() + delta)
        self.idx.setValue(new_i)
        self._load_idx()

    def _load_idx(self):
        p = self._pattern_path(self.idx.value())
        self.path_lbl.setText(p)
        if not Path(p).exists():
            QMessageBox.warning(self, "No existe", f"No se encontró:\n{p}")
            return
        try:
            render_dump_to(self.plotter, self.fig, p)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
