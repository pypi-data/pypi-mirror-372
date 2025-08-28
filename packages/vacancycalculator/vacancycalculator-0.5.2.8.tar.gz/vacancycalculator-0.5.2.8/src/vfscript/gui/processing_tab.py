import sys
import io
import json
import contextlib
import traceback
from pathlib import Path
import shutil
import os


from vfscript.gui.common import load_params, save_params, render_dump_to
# Forzar backend XCB en Wayland
os.environ["QT_QPA_PLATFORM"] = "xcb"


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

    
class ProcessingTab(QWidget):
    """
    Pestaña 'Procesado' para configurar el pipeline de inferencia
    sobre una muestra con número de vacancias desconocido.
    Guarda en params['CONFIG'][0]['processing_setup'].
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.params = load_params()
        self.cfg = self.params.setdefault('CONFIG', [{}])[0]
        pr = self.cfg.get('processing_setup', {})

        root = QVBoxLayout(self)

        # ===== Selección de muestra =====
        box_sample = QGroupBox("Muestra a procesar (.dump)")
        form_s = QFormLayout(box_sample)

        self.edit_sample = QLineEdit(pr.get('sample_dump', ''))
        btn_browse = QPushButton("Buscar")
        btn_browse.clicked.connect(self._browse_dump)
        hb = QHBoxLayout(); hb.addWidget(self.edit_sample, 1); hb.addWidget(btn_browse)

        self.spin_topk = QSpinBox()
        self.spin_topk.setRange(1, 10)
        self.spin_topk.setValue(int(pr.get('top_k', 3)))

        form_s.addRow("Archivo .dump:", hb)  # QFormLayout acepta layouts directamente

        form_s.addRow("Top-K predicciones:", self.spin_topk)
        root.addWidget(box_sample)

        # ===== Features (igual que en Training, para garantizar consistencia) =====
        box_feat = QGroupBox("Features a calcular en la muestra")
        feat_layout = QVBoxLayout(box_feat)

        # Coordinación
        row_coord = QHBoxLayout()
        self.chk_coord = QCheckBox("Coordinación")
        self.spin_rc = QDoubleSpinBox()
        self.spin_rc.setRange(0.0, 20.0)
        self.spin_rc.setDecimals(2)
        self.spin_rc.setSingleStep(0.01)
        self.spin_rc.setValue(float(pr.get('features', {}).get('coordination', {}).get('rc', 3.25)))
        row_coord.addWidget(self.chk_coord)
        row_coord.addStretch()
        row_coord.addWidget(QLabel("rc (Å):"))
        row_coord.addWidget(self.spin_rc)
        feat_layout.addLayout(row_coord)

        # Energía potencial
        self.chk_energy = QCheckBox("Energía potencial por átomo")
        feat_layout.addWidget(self.chk_energy)

        # Steinhardt
        row_s = QHBoxLayout()
        self.chk_steinhardt = QCheckBox("Steinhardt Q_l")
        self.spin_qr = QDoubleSpinBox(); self.spin_qr.setRange(0.0,20.0); self.spin_qr.setDecimals(2); self.spin_qr.setSingleStep(0.01)
        self.spin_qr.setValue(float(pr.get('features', {}).get('steinhardt', {}).get('radius', 2.70)))
        row_s.addWidget(self.chk_steinhardt); row_s.addStretch(); row_s.addWidget(QLabel("r (Å):")); row_s.addWidget(self.spin_qr)
        feat_layout.addLayout(row_s)

        row_orders = QHBoxLayout()
        self.chk_Q4 = QCheckBox("Q4"); self.chk_Q6 = QCheckBox("Q6"); self.chk_Q8 = QCheckBox("Q8"); self.chk_Q10 = QCheckBox("Q10"); self.chk_Q12 = QCheckBox("Q12")
        for w in (self.chk_Q4, self.chk_Q6, self.chk_Q8, self.chk_Q10, self.chk_Q12):
            row_orders.addWidget(w)
        feat_layout.addLayout(row_orders)

        # Casco convexo
        self.chk_hull = QCheckBox("Casco convexo")
        row_hull = QHBoxLayout()
        self.chk_area = QCheckBox("Área"); self.chk_vol = QCheckBox("Volumen")
        row_hull.addWidget(self.chk_area); row_hull.addWidget(self.chk_vol)
        feat_layout.addWidget(self.chk_hull); feat_layout.addLayout(row_hull)

        root.addWidget(box_feat)

        # ===== Preview de la muestra =====
        box_prev = QGroupBox("Preview de la muestra")
        prev_layout = QVBoxLayout(box_prev)
        self.lbl_atoms = QLabel("Átomos totales: -")
        prev_layout.addWidget(self.lbl_atoms)
        self.preview_plotter = QtInteractor(box_prev); prev_layout.addWidget(self.preview_plotter)
        self.preview_fig = plt.figure(figsize=(4,4)); self.preview_canvas = FigureCanvas(self.preview_fig); prev_layout.addWidget(self.preview_canvas)
        btn_preview = QPushButton("Cargar preview")
        btn_preview.clicked.connect(self.update_preview_from_dump)
        prev_layout.addWidget(btn_preview)
        root.addWidget(box_prev)

        # ===== Botones =====
        row_btns = QHBoxLayout()
        btn_save = QPushButton("Guardar configuración")
        btn_load = QPushButton("Cargar configuración actual")
        btn_process = QPushButton("Procesar muestra")
        btn_save.clicked.connect(self.save_processing_setup)
        btn_load.clicked.connect(self.load_from_params)
        btn_process.clicked.connect(self._process_stub)  # stub
        row_btns.addWidget(btn_save); row_btns.addWidget(btn_load); row_btns.addWidget(btn_process)
        root.addLayout(row_btns)

        # Log local
        self.log_box = QPlainTextEdit(); self.log_box.setReadOnly(True); self.log_box.setMinimumHeight(120)
        root.addWidget(self.log_box)
        root.addStretch()

        # Estados iniciales de checks
        self.chk_coord.setChecked(pr.get('features', {}).get('coordination', {}).get('enabled', True))
        self.chk_energy.setChecked(pr.get('features', {}).get('energy_potential', {}).get('enabled', True))
        st = pr.get('features', {}).get('steinhardt', {})
        self.chk_steinhardt.setChecked(st.get('enabled', True))
        orders = st.get('orders', {})
        self.chk_Q4.setChecked(orders.get('Q4', True))
        self.chk_Q6.setChecked(orders.get('Q6', True))
        self.chk_Q8.setChecked(orders.get('Q8', False))
        self.chk_Q10.setChecked(orders.get('Q10', False))
        self.chk_Q12.setChecked(orders.get('Q12', False))
        hull = pr.get('features', {}).get('convex_hull', {})
        self.chk_hull.setChecked(hull.get('enabled', False))
        self.chk_area.setChecked(hull.get('area', True))
        self.chk_vol.setChecked(hull.get('volume', True))

        # Habilitar subopciones
        self.chk_coord.toggled.connect(self.spin_rc.setEnabled)
        self.spin_rc.setEnabled(self.chk_coord.isChecked())

        def _en_steinhardt(on):
            for w in (self.spin_qr, self.chk_Q4, self.chk_Q6, self.chk_Q8, self.chk_Q10, self.chk_Q12):
                w.setEnabled(on)
        self.chk_steinhardt.toggled.connect(_en_steinhardt); _en_steinhardt(self.chk_steinhardt.isChecked())

        def _en_hull(on):
            for w in (self.chk_area, self.chk_vol):
                w.setEnabled(on)
        self.chk_hull.toggled.connect(_en_hull); _en_hull(self.chk_hull.isChecked())

    # ---------- Acciones ----------
    def _wrap(self, w):
        box = QWidget(); l = QHBoxLayout(box); l.setContentsMargins(0,0,0,0); l.addWidget(w); return box

    def _browse_dump(self):
        filtros = "All Files (*);;Dump Files (*.dump)"
        start_dir = getattr(self, "_last_dir", str(Path.cwd()))
        abs_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar muestra", start_dir, filtros)
        if abs_path:
            self._last_dir = str(Path(abs_path).parent)
            self.edit_sample.setText(abs_path)

    def save_processing_setup(self):
        params = load_params()
        cfg = params.setdefault('CONFIG', [{}])[0]
        setup = {
            'sample_dump': self.edit_sample.text().strip(),
            'top_k': int(self.spin_topk.value()),
            'features': {
                'coordination': {'enabled': self.chk_coord.isChecked(), 'rc': float(self.spin_rc.value())},
                'energy_potential': {'enabled': self.chk_energy.isChecked()},
                'steinhardt': {
                    'enabled': self.chk_steinhardt.isChecked(),
                    'radius': float(self.spin_qr.value()),
                    'orders': {
                        'Q4': self.chk_Q4.isChecked(), 'Q6': self.chk_Q6.isChecked(),
                        'Q8': self.chk_Q8.isChecked(), 'Q10': self.chk_Q10.isChecked(),
                        'Q12': self.chk_Q12.isChecked()
                    }
                },
                'convex_hull': {'enabled': self.chk_hull.isChecked(),
                                'area': self.chk_area.isChecked(),
                                'volume': self.chk_vol.isChecked()},
            }
        }
        cfg['processing_setup'] = setup
        path = save_params(params)
        QMessageBox.information(self, "Procesado guardado", f"Se guardó processing_setup en:\n{path}")

    def load_from_params(self):
        self.__init__(self.parent)

    def update_preview_from_dump(self):
        p = self.edit_sample.text().strip()
        if not p:
            QMessageBox.warning(self, "Sin archivo", "Elegí primero un .dump de muestra.")
            return
        try:
            # Render 3D/2D + conteo de átomos
            pipeline = import_file(p)
            data = pipeline.compute()
            n_atoms = int(data.particles.count)
            self.lbl_atoms.setText(f"Átomos totales: {n_atoms}")
            # Render con tu función común
            render_dump_to(self.preview_plotter, self.preview_fig, p)
            self.preview_canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Error en preview", str(e))

    def _process_stub(self):
        # Aquí conectarás tu pipeline real de inferencia.
        # Por ahora, solo deja registro y un aviso.
        self.log_box.appendPlainText("Procesado: stub ejecutado. Conectar modelo + extracción de features + predicción.")
        QMessageBox.information(self, "Procesar muestra", "Stub de procesado ejecutado. Falta conectar lógica real.")


