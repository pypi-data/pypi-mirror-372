import sys
import io
import json
import contextlib
import traceback
from pathlib import Path
import shutil
import os

from vfscript.training.training_graph import AtomicGraphGenerator
from vfscript.gui.common import load_params, save_params, render_dump_to
from vfscript.training.preparer import TrainingPreparer

# Forzar backend XCB en Wayland
os.environ["QT_QPA_PLATFORM"] = "xcb"

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFormLayout, QCheckBox,
    QDoubleSpinBox, QSpinBox, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QHBoxLayout, QPlainTextEdit, QVBoxLayout,
    QProgressBar, QSizePolicy, QComboBox, QTableWidget, QTableWidgetItem,
    QScrollArea, QLabel, QTabWidget, QGroupBox
)
from pyvistaqt import QtInteractor
import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class TrainingTab(QWidget):
    """
    Pestaña 'Training' para configurar generación de red perfecta y features.
    Guarda en params['CONFIG'][0]['training_setup'].
    """
    # ---------------------- utilidades internas ----------------------
    def _msg(self, title, text, kind="info"):
        try:
            fn = {
                "info": QMessageBox.information,
                "warn": QMessageBox.warning,
                "err": QMessageBox.critical,
            }.get(kind, QMessageBox.information)
            fn(self, title, text)
        except Exception:
            print(f"[{kind}] {title}: {text}")

    def _gw(self, name, default=None):
        """Get Widget: intenta value(), text(), currentText(), isChecked()."""
        w = getattr(self, name, None)
        if w is None:
            return default
        for attr in ("value", "text", "currentText", "isChecked"):
            fn = getattr(w, attr, None)
            if callable(fn):
                try:
                    v = fn()
                    return v.strip() if isinstance(v, str) else v
                except Exception:
                    pass
        return default

    def _sw(self, name, value):
        """Set Widget: intenta setValue(), setText(), setCurrentText(), setChecked()."""
        w = getattr(self, name, None)
        if w is None:
            return
        for attr in ("setValue", "setText", "setCurrentText", "setChecked"):
            fn = getattr(w, attr, None)
            if callable(fn):
                try:
                    fn(value)
                    return
                except Exception:
                    pass

    # --------------------------- constructor ---------------------------
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # Cargar params actuales
        self.params = load_params()
        self.cfg = self.params.setdefault('CONFIG', [{}])[0]
        tr = self.cfg.get('training_setup', {})

        root = QVBoxLayout(self)

        # ===== Sección: Red perfecta de entrenamiento =====
        box_net = QGroupBox("Red perfecta de entrenamiento (.dump)")
        form_net = QFormLayout(box_net)

        self.combo_lattice = QComboBox()
        self.combo_lattice.addItems(["fcc", "bcc"])
        self.combo_lattice.setCurrentText(tr.get('perfect_network', {}).get('lattice', "fcc"))

        self.spin_a0 = QDoubleSpinBox()
        self._cfg_spin(self.spin_a0, 0.0, 50.0, float(tr.get('perfect_network', {}).get('a0', 3.52)), step=0.01, decimals=3)

        cells_def = tr.get('perfect_network', {}).get('cells', [1, 1, 1])
        self.spin_rx = QSpinBox(); self._cfg_spin(self.spin_rx, 1, 500, int(cells_def[0]))
        self.spin_ry = QSpinBox(); self._cfg_spin(self.spin_ry, 1, 500, int(cells_def[1]))
        self.spin_rz = QSpinBox(); self._cfg_spin(self.spin_rz, 1, 500, int(cells_def[2]))

        self.edit_atom = QLineEdit(tr.get('perfect_network', {}).get('atom', "Fe"))

        btn_gen = QPushButton("Generar red perfecta")
        btn_gen.clicked.connect(self._generate_stub)   # genera outputs/json/training_inputs.json

        form_net.addRow("Lattice:", self.combo_lattice)
        form_net.addRow("a₀ (Å):", self.spin_a0)
        form_net.addRow("Réplicas X:", self.spin_rx)
        form_net.addRow("Réplicas Y:", self.spin_ry)
        form_net.addRow("Réplicas Z:", self.spin_rz)
        form_net.addRow("Elemento:", self.edit_atom)
        form_net.addRow(btn_gen)
        root.addWidget(box_net)

        # ===== Sección: Configuración de entrenamiento =====
        box_train = QGroupBox("Configuraciones de entrenamiento")
        form_train = QFormLayout(box_train)

        self.spin_iters = QSpinBox()
        self._cfg_spin(self.spin_iters, 1, 1_000_000, int(tr.get('iterations', 1000)))

        self.spin_max_vacs = QSpinBox()
        self._cfg_spin(self.spin_max_vacs, 0, 1_000_000, int(tr.get('max_vacancies', 0)))

        form_train.addRow("Iteraciones:", self.spin_iters)
        form_train.addRow("Vacancias máximas a retirar:", self.spin_max_vacs)
        root.addWidget(box_train)

        # ===== Sección: Features =====
        box_feat = QGroupBox("Features a extraer")
        feat_layout = QVBoxLayout(box_feat)

        # Coordinación (rc)
        row_coord = QHBoxLayout()
        self.chk_coord = QCheckBox("Coordinación")
        self.spin_rc = QDoubleSpinBox()
        self._cfg_spin(self.spin_rc, 0.0, 20.0, float(tr.get('features', {}).get('coordination', {}).get('rc', 3.25)), step=0.01, decimals=2)
        row_coord.addWidget(self.chk_coord)
        row_coord.addStretch()
        row_coord.addWidget(QLabel("rc (Å):"))
        row_coord.addWidget(self.spin_rc)
        feat_layout.addLayout(row_coord)

        # Energía potencial
        self.chk_energy = QCheckBox("Energía potencial por átomo")
        feat_layout.addWidget(self.chk_energy)

        # Steinhardt Q_l
        row_s = QHBoxLayout()
        self.chk_steinhardt = QCheckBox("Steinhardt Q_l")
        self.spin_qr = QDoubleSpinBox()
        self._cfg_spin(self.spin_qr, 0.0, 20.0, float(tr.get('features', {}).get('steinhardt', {}).get('radius', 2.70)), step=0.01, decimals=2)
        row_s.addWidget(self.chk_steinhardt)
        row_s.addStretch()
        row_s.addWidget(QLabel("r (Å):"))
        row_s.addWidget(self.spin_qr)
        feat_layout.addLayout(row_s)

        row_orders = QHBoxLayout()
        self.chk_Q4 = QCheckBox("Q4"); self.chk_Q6 = QCheckBox("Q6"); self.chk_Q8 = QCheckBox("Q8")
        self.chk_Q10 = QCheckBox("Q10"); self.chk_Q12 = QCheckBox("Q12")
        for w in (self.chk_Q4, self.chk_Q6, self.chk_Q8, self.chk_Q10, self.chk_Q12):
            row_orders.addWidget(w)
        feat_layout.addLayout(row_orders)

        # Casco convexo
        self.chk_hull = QCheckBox("Casco convexo")
        row_hull = QHBoxLayout()
        self.chk_area = QCheckBox("Área"); self.chk_vol = QCheckBox("Volumen")
        row_hull.addWidget(self.chk_area); row_hull.addWidget(self.chk_vol)
        feat_layout.addWidget(self.chk_hull)
        feat_layout.addLayout(row_hull)

        root.addWidget(box_feat)

        # ===== Preview de red =====
        box_prev = QGroupBox("Preview de red")
        prev_layout = QVBoxLayout(box_prev)
        self.lbl_atoms = QLabel("Átomos totales: -")
        prev_layout.addWidget(self.lbl_atoms)
        self.preview_plotter = QtInteractor(box_prev)
        prev_layout.addWidget(self.preview_plotter)
        self.preview_fig = plt.figure(figsize=(4, 4))
        self.preview_canvas = FigureCanvas(self.preview_fig)
        prev_layout.addWidget(self.preview_canvas)
        root.addWidget(box_prev)

        # Señales para refrescar preview y contador
        self.combo_lattice.currentTextChanged.connect(self.update_preview)
        self.spin_a0.valueChanged.connect(self.update_preview)
        self.spin_rx.valueChanged.connect(self.update_preview)
        self.spin_ry.valueChanged.connect(self.update_preview)
        self.spin_rz.valueChanged.connect(self.update_preview)

        # Render inicial del preview
        self.update_preview()

        # ===== Botones guardar/cargar =====
        row_btns = QHBoxLayout()
        btn_save = QPushButton("Guardar configuración")
        btn_load = QPushButton("Cargar configuración actual")
        btn_prepare = QPushButton("Preparar dataset")
        btn_save.clicked.connect(self.save_training_setup)
        btn_load.clicked.connect(self.load_from_params)        # <- ahora existe
        btn_prepare.clicked.connect(self.on_prepare_training_clicked)
        row_btns.addWidget(btn_save)
        row_btns.addWidget(btn_load)
        row_btns.addWidget(btn_prepare)
        root.addLayout(row_btns)

        # ===== Estados iniciales de checks =====
        self.chk_coord.setChecked(tr.get('features', {}).get('coordination', {}).get('enabled', True))
        self.chk_energy.setChecked(tr.get('features', {}).get('energy_potential', {}).get('enabled', True))
        st = tr.get('features', {}).get('steinhardt', {})
        self.chk_steinhardt.setChecked(st.get('enabled', True))
        orders = st.get('orders', {})
        self.chk_Q4.setChecked(orders.get('Q4', True))
        self.chk_Q6.setChecked(orders.get('Q6', True))
        self.chk_Q8.setChecked(orders.get('Q8', False))
        self.chk_Q10.setChecked(orders.get('Q10', False))
        self.chk_Q12.setChecked(orders.get('Q12', False))
        hull = tr.get('features', {}).get('convex_hull', {})
        self.chk_hull.setChecked(hull.get('enabled', False))
        self.chk_area.setChecked(hull.get('area', True))
        self.chk_vol.setChecked(hull.get('volume', True))

        # Log local de la pestaña
        self.log_box = QPlainTextEdit(); self.log_box.setReadOnly(True); self.log_box.setMinimumHeight(120)
        root.addWidget(self.log_box)

        # Habilitar/deshabilitar sub-opciones
        self.chk_coord.toggled.connect(self.spin_rc.setEnabled)
        self.spin_rc.setEnabled(self.chk_coord.isChecked())

        def _en_steinhardt(on):
            for w in (self.spin_qr, self.chk_Q4, self.chk_Q6, self.chk_Q8, self.chk_Q10, self.chk_Q12):
                w.setEnabled(on)
        self.chk_steinhardt.toggled.connect(_en_steinhardt)
        _en_steinhardt(self.chk_steinhardt.isChecked())

        def _en_hull(on):
            for w in (self.chk_area, self.chk_vol):
                w.setEnabled(on)
        self.chk_hull.toggled.connect(_en_hull)
        _en_hull(self.chk_hull.isChecked())

    # ===== Helpers =====
    def _cfg_spin(self, spin, mn, mx, val, step=1, decimals=None):
        spin.setRange(mn, mx)
        if isinstance(spin, QDoubleSpinBox):
            if decimals is not None:
                spin.setDecimals(decimals)
            spin.setSingleStep(step)
        else:
            spin.setSingleStep(int(step))
        spin.setValue(val)

    # ===================== persistencia/IO =====================
    def save_training_setup(self):
        """Guarda en params['CONFIG'][0]['training_setup'] y además exporta un JSON de compatibilidad."""
        setup = {
            'iterations': int(self.spin_iters.value()),
            'max_vacancies': int(self.spin_max_vacs.value()),
            'features': {
                'coordination': {
                    'enabled': self.chk_coord.isChecked(),
                    'rc': float(self.spin_rc.value()),
                },
                'energy_potential': {
                    'enabled': self.chk_energy.isChecked(),
                },
                'steinhardt': {
                    'enabled': self.chk_steinhardt.isChecked(),
                    'radius': float(self.spin_qr.value()),
                    'orders': {
                        'Q4': self.chk_Q4.isChecked(),
                        'Q6': self.chk_Q6.isChecked(),
                        'Q8': self.chk_Q8.isChecked(),
                        'Q10': self.chk_Q10.isChecked(),
                        'Q12': self.chk_Q12.isChecked(),
                    },
                },
                'convex_hull': {
                    'enabled': self.chk_hull.isChecked(),
                    'area': self.chk_area.isChecked(),
                    'volume': self.chk_vol.isChecked(),
                },
            },
            'perfect_network': {
                'lattice': self.combo_lattice.currentText(),
                'a0': float(self.spin_a0.value()),
                'cells': [int(self.spin_rx.value()), int(self.spin_ry.value()), int(self.spin_rz.value())],
                'atom': self.edit_atom.text().strip() or "Fe",
            },
        }

        # Actualiza params y persiste con save_params
        self.cfg['training_setup'] = setup
        try:
            save_params(self.params)
        except Exception as e:
            self._msg("Advertencia", f"No se pudo guardar con save_params():\n{e}", "warn")

        # Export JSON de compatibilidad para pipelines que esperan outputs/json/training_inputs.json
        # Incluimos training_setup dentro de CONFIG[0]; otras claves (relax/cutoff/...) pueden venir de otras pestañas o del stub.
        out_dir = Path("outputs/json"); out_dir.mkdir(parents=True, exist_ok=True)
        export_path = out_dir / "training_inputs.json"
        compat = {"CONFIG": [{"training_setup": setup}]}
        try:
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(compat, f, indent=4)
        except Exception as e:
            self._msg("Advertencia", f"No se pudo escribir {export_path}:\n{e}", "warn")

        self._msg("Training guardado", f"Configuración exportada a:\n{export_path}")

    def load_from_params(self):
        """Carga params['CONFIG'][0]['training_setup'] a la UI (si existe)."""
        try:
            self.params = load_params()
            self.cfg = self.params.setdefault('CONFIG', [{}])[0]
            tr = self.cfg.get('training_setup', {})

            # perfect_network
            pn = tr.get('perfect_network', {})
            self._sw('combo_lattice', pn.get('lattice', 'fcc'))
            try:
                self.spin_a0.setValue(float(pn.get('a0', self.spin_a0.value())))
            except Exception:
                pass
            cells = pn.get('cells', [self.spin_rx.value(), self.spin_ry.value(), self.spin_rz.value()])
            if isinstance(cells, (list, tuple)) and len(cells) == 3:
                self._sw('spin_rx', int(cells[0])); self._sw('spin_ry', int(cells[1])); self._sw('spin_rz', int(cells[2]))
            self._sw('edit_atom', pn.get('atom', 'Fe'))

            # features
            ft = tr.get('features', {})
            crd = ft.get('coordination', {})
            self._sw('chk_coord', bool(crd.get('enabled', True)))
            try:
                self.spin_rc.setValue(float(crd.get('rc', self.spin_rc.value())))
            except Exception:
                pass
            self._sw('chk_energy', bool(ft.get('energy_potential', {}).get('enabled', True)))

            st = ft.get('steinhardt', {})
            self._sw('chk_steinhardt', bool(st.get('enabled', True)))
            try:
                self.spin_qr.setValue(float(st.get('radius', self.spin_qr.value())))
            except Exception:
                pass
            od = st.get('orders', {})
            self._sw('chk_Q4',  bool(od.get('Q4', True)))
            self._sw('chk_Q6',  bool(od.get('Q6', True)))
            self._sw('chk_Q8',  bool(od.get('Q8', False)))
            self._sw('chk_Q10', bool(od.get('Q10', False)))
            self._sw('chk_Q12', bool(od.get('Q12', False)))

            hull = ft.get('convex_hull', {})
            self._sw('chk_hull', bool(hull.get('enabled', False)))
            self._sw('chk_area', bool(hull.get('area', True)))
            self._sw('chk_vol',  bool(hull.get('volume', True)))

            self.update_preview()
            self._msg("OK", "Parámetros cargados en la interfaz.")
        except Exception as e:
            self._msg("Error", f"No se pudo cargar la configuración:\n{e}", "err")

    # ===================== acciones principales =====================
    def _generate_stub(self):
        """
        Genera outputs/json/training_inputs.json para pipelines que esperan CONFIG.
        Toma valores si existen en esta pestaña; donde no, usa defaults.
        """
        try:
            def _num(x, dflt):
                try:
                    return float(x)
                except Exception:
                    return dflt

            cfg = {
                "CONFIG": [{
                    # Claves usadas por AtomicGraphGenerator
                    "relax": self._gw("edit_relax_path", ""),
                    "cutoff": _num(self._gw("spin_cutoff", 3.25), 3.25),
                    "radius": _num(self._gw("spin_radius", 2.70), 2.70),
                    "smoothing_level_training": int(self._gw("spin_smoothing", 2) or 2),
                    "max_graph_variations": int(self._gw("spin_variations", 1) or 1),
                    "max_graph_size": int(self._gw("spin_max_nodes", 16) or 16),
                    # Además guardamos el bloque training_setup de esta pestaña (si existe)
                    "training_setup": self.cfg.get('training_setup', {}),
                }]
            }
            out = Path.cwd() / "outputs/json/training_inputs.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            with open(out, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2, ensure_ascii=False)
            self._msg("Listo", f"Se generó:\n{out}")
        except Exception as e:
            self._msg("Error", f"No se pudo generar el stub:\n{e}", "err")

    def on_prepare_training_clicked(self):
        params = load_params()
        setup_dict = params['CONFIG'][0].get('training_setup', {})
        out_dir = Path('outputs/training')

        def log_to_gui(msg: str):
            try:
                self.log_box.appendPlainText(str(msg))
            except Exception:
                print(str(msg))

        prep = TrainingPreparer.from_setup_dict(setup_dict, out_dir, logger=log_to_gui)
        try:
            prep.validate()
            prep.prepare_workspace()
            ref_dump = prep.generate_perfect_dump()      # opcional
            _ = prep.build_dataset_csv([ref_dump])       # dataset base

            log_to_gui("🔄 Ejecutando AtomicGraphGenerator...")
            gen = AtomicGraphGenerator()
            gen.run()
            log_to_gui("✔️ Entrenamiento finalizado. Dataset en outputs/csv/finger_data.csv")

            self._msg(
                "Entrenamiento completado",
                "Dataset generado y entrenamiento terminado.\n"
                "Ver archivos en outputs/csv/finger_data.csv"
            )
        except Exception as e:
            self._msg("Error en preparación/entrenamiento", str(e), "err")

    # ===================== preview geométrico =====================
    def _make_lattice_points(self, lattice: str, a0: float, rx: int, ry: int, rz: int) -> np.ndarray:
        lattice = (lattice or "fcc").strip().lower()
        if lattice not in ("fcc", "bcc"):
            lattice = "fcc"
        if lattice == "fcc":
            basis = np.array([
                [0.0, 0.0, 0.0],
                [0.0, 0.5, 0.5],
                [0.5, 0.0, 0.5],
                [0.5, 0.5, 0.0],
            ], dtype=float)
        else:  # bcc
            basis = np.array([
                [0.0, 0.0, 0.0],
                [0.5, 0.5, 0.5],
            ], dtype=float)
        ii, jj, kk = np.mgrid[0:rx, 0:ry, 0:rz]
        cells = np.stack([ii.ravel(), jj.ravel(), kk.ravel()], axis=1).astype(float)
        pos = cells[:, None, :] + basis[None, :, :]
        pos = pos.reshape(-1, 3) * a0
        return pos

    def _draw_box_edges(self, ax2d, Lx, Ly, Lz):
        corners = np.array([
            [0, 0, 0],
            [Lx, 0, 0],
            [0, Ly, 0],
            [0, 0, Lz],
            [Lx, Ly, 0],
            [Lx, 0, Lz],
            [0, Ly, Lz],
            [Lx, Ly, Lz]
        ], dtype=float)
        edges = [(0,1),(0,2),(0,3),(1,4),(1,5),(2,4),(2,6),(3,5),(3,6),(4,7),(5,7),(6,7)]

        # 3D (PyVista)
        self.preview_plotter.clear()
        for i, j in edges:
            self.preview_plotter.add_mesh(pv.Line(corners[i], corners[j]), color="blue", line_width=2)

        # 2D (Matplotlib)
        ax2d.cla()
        for i, j in edges:
            x0, y0 = corners[i][0], corners[i][1]
            x1, y1 = corners[j][0], corners[j][1]
            ax2d.plot([x0, x1], [y0, y1], '-', linewidth=1)
        ax2d.set_xlabel("X"); ax2d.set_ylabel("Y")
        ax2d.set_aspect("equal", "box"); ax2d.grid(True, linewidth=0.3)

    def update_preview(self):
        """
        Recalcula posiciones según parámetros actuales y refresca:
        - Conteo de átomos totales
        - Vista 3D (PyVista) y 2D (Matplotlib)
        """
        try:
            lattice = self.combo_lattice.currentText().strip().lower()
            a0 = float(self.spin_a0.value())
            rx = int(self.spin_rx.value())
            ry = int(self.spin_ry.value())
            rz = int(self.spin_rz.value())

            # Generar posiciones
            pts = self._make_lattice_points(lattice, a0, rx, ry, rz)
            n_atoms = int(pts.shape[0])
            self.lbl_atoms.setText(f"Átomos totales: {n_atoms}")

            # Tamaños de caja
            Lx, Ly, Lz = rx * a0, ry * a0, rz * a0

            # 3D
            self.preview_plotter.clear()
            # Caja + reset de 2D
            ax = self.preview_fig.gca() if self.preview_fig.axes else self.preview_fig.add_subplot(111)
            self._draw_box_edges(ax, Lx, Ly, Lz)
            # Puntos 3D
            self.preview_plotter.add_mesh(
                pv.PolyData(pts), color="black", render_points_as_spheres=True, point_size=6
            )
            self.preview_plotter.reset_camera(); self.preview_plotter.set_scale(1, 1, 1)

            # 2D XY
            ax2d = self.preview_fig.axes[0]
            ax2d.scatter(pts[:, 0], pts[:, 1], s=6, color="k")
            self.preview_canvas.draw()
        except Exception as e:
            self.lbl_atoms.setText(f"Error en preview: {e}")
