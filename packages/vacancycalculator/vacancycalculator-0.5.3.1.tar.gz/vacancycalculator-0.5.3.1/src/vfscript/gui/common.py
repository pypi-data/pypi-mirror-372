import sys
import io
import json
import contextlib
import traceback
from pathlib import Path
import shutil
import os


from vfscript.training.preparer import TrainingPreparer


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


# Forzar backend XCB en Wayland
os.environ["QT_QPA_PLATFORM"] = "xcb"



from pyvistaqt import QtInteractor
import pyvista as pv
import numpy as np
from ovito.io import import_file

# ---------- Gestión de input_params.json ----------
GUI_ROOT = Path(__file__).resolve().parent

def runtime_params_path():
    cwd_params = Path.cwd() / "input_params.json"
    if cwd_params.exists():
        return cwd_params
    src_params = GUI_ROOT / "input_params.json"
    if src_params.exists():
        shutil.copy(src_params, cwd_params)
        return cwd_params
    return src_params

PARAMS_FILE = runtime_params_path()

def load_params():
    if PARAMS_FILE.exists():
        return json.loads(PARAMS_FILE.read_text())
    return {}

def save_params(params, target_path: Path = None):
    if target_path is None:
        target_path = Path.cwd() / "input_params.json"
    target_path.write_text(json.dumps(params, indent=4))
    return target_path


# ---------- Función común de render (3D+2D) ----------
def render_dump_to(plotter: QtInteractor, fig: plt.Figure, dump_path: str):
    """Dibuja celda + puntos igual que load_dump, coloreando por 'Cluster' si existe."""
    pipeline = import_file(dump_path)
    data = pipeline.compute()

    # === Celda desde OVITO: columnas a1,a2,a3 y última columna origen ===
    M = np.asarray(data.cell.matrix, dtype=float)   # (3x4)
    a1, a2, a3, origin = M[:, 0], M[:, 1], M[:, 2], M[:, 3]

    corners = [
        origin,
        origin + a1,
        origin + a2,
        origin + a3,
        origin + a1 + a2,
        origin + a1 + a3,
        origin + a2 + a3,
        origin + a1 + a2 + a3
    ]
    edges = [(0,1),(0,2),(0,3),(1,4),(1,5),(2,4),(2,6),(3,5),(3,6),(4,7),(5,7),(6,7)]

    # === Partículas ===
    pos_prop = data.particles.positions
    positions = pos_prop.array if hasattr(pos_prop, "array") else np.asarray(pos_prop, dtype=float)

    # --- Detectar columna de clúster (varios alias posibles) ---
    cluster_vals = None
    for name in ("Cluster", "cluster", "c_Cluster", "c_cluster", "ClusterID", "cluster_id"):
        if name in data.particles:
            prop = data.particles[name]
            arr = prop.array if hasattr(prop, "array") else prop
            cluster_vals = np.asarray(arr).astype(int).reshape(-1)
            break

    # --- Remapeo a 0..K-1 para paleta discreta ---
    cluster_idx = None
    unique_clusters = None
    if cluster_vals is not None and cluster_vals.shape[0] == positions.shape[0]:
        unique_clusters = np.unique(cluster_vals)
        map_idx = {val: i for i, val in enumerate(unique_clusters)}
        # vectorizado seguro
        cluster_idx = np.vectorize(map_idx.get, otypes=[int])(cluster_vals)

    # === Vista 3D ===
    plotter.clear()
    for i, j in edges:
        plotter.add_mesh(pv.Line(corners[i], corners[j]), color="blue", line_width=2)

    if cluster_idx is not None:
        pts = pv.PolyData(positions)
        pts["cluster"] = cluster_idx
        plotter.add_mesh(
            pts,
            scalars="cluster",
            render_points_as_spheres=True,
            point_size=8,
            cmap="tab20",
            show_scalar_bar=False,   # oculto barra para muchos clústeres
        )
    else:
        plotter.add_mesh(
            pv.PolyData(positions),
            color="black",
            render_points_as_spheres=True,
            point_size=8
        )

    plotter.reset_camera()
    plotter.set_scale(1, 1, 1)

    # === Vista 2D ===
    fig.clf()
    ax = fig.add_subplot(111)
    for i, j in edges:
        x0, y0 = corners[i][0], corners[i][1]
        x1, y1 = corners[j][0], corners[j][1]
        ax.plot([x0, x1], [y0, y1], '-', linewidth=1)

    if cluster_idx is not None:
        # Paleta consistente con PyVista
        ax.scatter(
            positions[:, 0], positions[:, 1], s=10,
            c=cluster_idx, cmap="tab20",
            vmin=0, vmax=len(unique_clusters)-1
        )
    else:
        ax.scatter(positions[:, 0], positions[:, 1], s=10, color="k")

    ax.set_xlabel('X'); ax.set_ylabel('Y')
    ax.set_aspect('equal', 'box')
    ax.grid(True, linewidth=0.3)
    fig.canvas.draw()

