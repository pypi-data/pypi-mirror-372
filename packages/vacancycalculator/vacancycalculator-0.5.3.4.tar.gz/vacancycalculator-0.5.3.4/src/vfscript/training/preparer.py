# vfscript/training/preparer.py
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple
import json
import math
import numpy as np

# ==== Opcionales ====
try:
    from scipy.spatial import KDTree, ConvexHull  # type: ignore
    _HAS_SCIPY = True
except Exception:
    _HAS_SCIPY = False
    KDTree = None
    ConvexHull = None

try:
    from scipy.special import sph_harm  # type: ignore
    _HAS_SPH = True
except Exception:
    _HAS_SPH = False
    sph_harm = None


# ---------------- Config dataclasses ----------------
@dataclass
class CoordinationCfg:
    enabled: bool = True
    rc: float = 3.25  # Å

@dataclass
class EnergyCfg:
    enabled: bool = True
    # mapeo de nombres posibles de columna de energía en tu dump
    column_candidates: List[str] = field(default_factory=lambda: ["pe", "c_1", "epot", "energy", "c_energy"])

@dataclass
class SteinhardtCfg:
    enabled: bool = True
    radius: float = 2.70  # Å
    orders: Dict[str, bool] = field(default_factory=lambda: {"Q4": True, "Q6": True, "Q8": False, "Q10": False, "Q12": False})

@dataclass
class ConvexHullCfg:
    enabled: bool = False
    area: bool = True
    volume: bool = True

@dataclass
class FeaturesCfg:
    coordination: CoordinationCfg = field(default_factory=CoordinationCfg)
    energy_potential: EnergyCfg = field(default_factory=EnergyCfg)
    steinhardt: SteinhardtCfg = field(default_factory=SteinhardtCfg)
    convex_hull: ConvexHullCfg = field(default_factory=ConvexHullCfg)

@dataclass
class PerfectNetCfg:
    lattice: str = "fcc"     # "fcc" | "bcc"
    a0: float = 3.52         # Å
    cells: List[int] = field(default_factory=lambda: [1, 1, 1])
    atom: str = "Fe"

@dataclass
class TrainingSetup:
    iterations: int = 1000
    max_vacancies: int = 0
    features: FeaturesCfg = field(default_factory=FeaturesCfg)
    perfect_network: PerfectNetCfg = field(default_factory=PerfectNetCfg)

    @staticmethod
    def from_dict(d: Dict) -> "TrainingSetup":
        f = d.get("features", {})
        st = f.get("steinhardt", {})
        ch = f.get("convex_hull", {})
        co = f.get("coordination", {})
        ep = f.get("energy_potential", {})

        return TrainingSetup(
            iterations=int(d.get("iterations", 1000)),
            max_vacancies=int(d.get("max_vacancies", 0)),
            features=FeaturesCfg(
                coordination=CoordinationCfg(**{
                    "enabled": bool(co.get("enabled", True)),
                    "rc": float(co.get("rc", 3.25)),
                }),
                energy_potential=EnergyCfg(**{
                    "enabled": bool(ep.get("enabled", True)),
                    # podés inyectar candidatos desde tu GUI si querés
                }),
                steinhardt=SteinhardtCfg(**{
                    "enabled": bool(st.get("enabled", True)),
                    "radius": float(st.get("radius", 2.70)),
                    "orders": dict(st.get("orders", {"Q4": True, "Q6": True})),
                }),
                convex_hull=ConvexHullCfg(**{
                    "enabled": bool(ch.get("enabled", False)),
                    "area": bool(ch.get("area", True)),
                    "volume": bool(ch.get("volume", True)),
                }),
            ),
            perfect_network=PerfectNetCfg(**{
                "lattice": str(d.get("perfect_network", {}).get("lattice", "fcc")),
                "a0": float(d.get("perfect_network", {}).get("a0", 3.52)),
                "cells": list(d.get("perfect_network", {}).get("cells", [1,1,1])),
                "atom": str(d.get("perfect_network", {}).get("atom", "Fe")),
            })
        )


# ---------------- Utilidades de dump muy mínimas ----------------
class MinimalDumpIO:
    """
    Lector/escritor de .dump (formato ITEM:) con soporte básico:
    - coords (x,y,z)
    - box ortogonal [0,Lx]x[0,Ly]x[0,Lz]
    - columnas extra opcionales (dict de arrays)
    """
    @staticmethod
    def write_simple_dump(path: Path, coords: np.ndarray, box: Tuple[float,float,float],
                          extra_cols: Optional[Dict[str, np.ndarray]] = None) -> None:
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        n = coords.shape[0]
        Lx, Ly, Lz = box
        cols = ["id", "type", "x", "y", "z"]
        extra_cols = extra_cols or {}
        cols += list(extra_cols.keys())

        with path.open("w", encoding="utf-8") as f:
            f.write("ITEM: TIMESTEP\n0\n")
            f.write("ITEM: NUMBER OF ATOMS\n%d\n" % n)
            f.write("ITEM: BOX BOUNDS pp pp pp\n")
            f.write(f"0 {Lx}\n0 {Ly}\n0 {Lz}\n")
            f.write("ITEM: ATOMS " + " ".join(cols) + "\n")
            for i in range(n):
                row = [str(i+1), "1",
                       f"{coords[i,0]:.8f}", f"{coords[i,1]:.8f}", f"{coords[i,2]:.8f}"]
                for k in extra_cols:
                    row.append(str(extra_cols[k][i]))
                f.write(" ".join(row) + "\n")

    @staticmethod
    def read_coords_and_table(path: Path) -> Tuple[np.ndarray, Dict[str, np.ndarray], Tuple[float,float,float]]:
        """
        Devuelve (coords, tabla, (Lx,Ly,Lz)).
        tabla: dict nombre_columna -> ndarray alineado con coords.
        """
        path = Path(path)
        coords = []
        table_cols = []
        table_vals: List[List[float]] = []
        Lx = Ly = Lz = None  # type: ignore
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            line = f.readline()
            while line:
                if line.startswith("ITEM: BOX BOUNDS"):
                    Lx = float(f.readline().split()[1]);  # segunda col es el max
                    Ly = float(f.readline().split()[1])
                    Lz = float(f.readline().split()[1])
                if line.startswith("ITEM: ATOMS"):
                    parts = line.strip().split()
                    table_cols = parts[2:]  # después de "ITEM: ATOMS"
                    # esperamos filas
                    for row in f:
                        if row.startswith("ITEM:"):
                            break
                        vals = row.strip().split()
                        # mapeo por nombres
                        id_idx = table_cols.index("id") if "id" in table_cols else None
                        x_idx = table_cols.index("x")
                        y_idx = table_cols.index("y")
                        z_idx = table_cols.index("z")
                        coords.append([float(vals[x_idx]), float(vals[y_idx]), float(vals[z_idx])])
                        row_vals = []
                        for j, name in enumerate(table_cols):
                            try:
                                row_vals.append(float(vals[j]))
                            except Exception:
                                row_vals.append(np.nan)
                        table_vals.append(row_vals)
                    break
                line = f.readline()
        coords = np.array(coords, dtype=float)
        table = {}
        if table_cols and table_vals:
            arr = np.array(table_vals, dtype=float)
            for j, name in enumerate(table_cols):
                table[name] = arr[:, j]
        box = (Lx or 0.0, Ly or 0.0, Lz or 0.0)
        return coords, table, box


# ---------------- Clase principal ----------------
class TrainingPreparer:
    def __init__(self,
                 setup: TrainingSetup,
                 out_dir: Path,
                 logger: Optional[Callable[[str], None]] = None):
        self.setup = setup
        self.out_dir = Path(out_dir)
        self.logger = logger or (lambda m: None)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        (self.out_dir / "cache").mkdir(exist_ok=True)

    # ---------- API de construcción ----------
    @staticmethod
    def from_setup_dict(d: Dict, out_dir: Path, logger: Optional[Callable[[str], None]] = None) -> "TrainingPreparer":
        return TrainingPreparer(TrainingSetup.from_dict(d), out_dir, logger)

    def validate(self) -> None:
        s = self.setup
        assert s.iterations > 0, "iterations debe ser > 0"
        assert all(isinstance(c, int) and c >= 1 for c in s.perfect_network.cells), "cells deben ser enteros >=1"
        assert s.perfect_network.lattice.lower() in ("fcc", "bcc"), "lattice debe ser fcc o bcc"

    def prepare_workspace(self) -> None:
        meta = self.out_dir / "meta_training_setup.json"
        with meta.open("w", encoding="utf-8") as f:
            json.dump(self._to_serializable(), f, indent=2)
        self.log(f"Workspace listo. Metadatos en: {meta}")

    # ---------- Red perfecta ----------
    def generate_perfect_dump(self, out_path: Optional[Path] = None) -> Path:
        p = self.setup.perfect_network
        a0 = float(p.a0)
        rx, ry, rz = map(int, p.cells)
        pts = self._make_lattice_points(p.lattice, a0, rx, ry, rz)
        Lx, Ly, Lz = rx * a0, ry * a0, rz * a0
        out_path = Path(out_path or (self.out_dir / "relax_structure.dump"))
        MinimalDumpIO.write_simple_dump(out_path, pts, (Lx, Ly, Lz))
        self.log(f"Dump perfecto generado: {out_path}  (átomos: {pts.shape[0]})")
        return out_path

    # ---------- Dataset / features ----------
    def extract_features_from_dump(self, dump_path: Path) -> Dict[str, float]:
        coords, table, box = MinimalDumpIO.read_coords_and_table(Path(dump_path))
        feats: Dict[str, float] = {}

        # Coordinación (promedio global, como ejemplo)
        if self.setup.features.coordination.enabled:
            rc = self.setup.features.coordination.rc
            neigh_counts = self._coordination_counts(coords, rc)
            feats["coord_mean_rc=%.2f" % rc] = float(np.nanmean(neigh_counts)) if len(neigh_counts) else np.nan

        # Energía potencial (promedio global)
        if self.setup.features.energy_potential.enabled:
            val = self._pick_energy_column(table, self.setup.features.energy_potential.column_candidates)
            feats["energy_potential_mean"] = float(np.nanmean(val)) if val is not None else np.nan

        # Steinhardt Ql (promedio global por l)
        if self.setup.features.steinhardt.enabled:
            if not (_HAS_SCIPY and _HAS_SPH):
                self.log("Steinhardt omitido (requiere SciPy con scipy.special.sph_harm).")
            else:
                r = self.setup.features.steinhardt.radius
                orders = [int(k[1:]) for k, on in self.setup.features.steinhardt.orders.items() if on]
                q_by_atom = self._steinhardt_all_atoms(coords, r, orders)
                for l in orders:
                    feats[f"Q{l}_mean_r={r:.2f}"] = float(np.nanmean(q_by_atom[l])) if l in q_by_atom else np.nan

        # Casco convexo global
        if self.setup.features.convex_hull.enabled:
            if not _HAS_SCIPY or ConvexHull is None:
                self.log("Convex Hull omitido (requiere scipy.spatial.ConvexHull).")
            else:
                try:
                    hull = ConvexHull(coords)
                    if self.setup.features.convex_hull.area:
                        feats["hull_area"] = float(hull.area)
                    if self.setup.features.convex_hull.volume:
                        feats["hull_volume"] = float(hull.volume)
                except Exception as e:
                    self.log(f"ConvexHull falló: {e}")

        return feats

    def build_dataset_csv(self, dumps: Iterable[Path], out_csv: Optional[Path] = None) -> Path:
        rows: List[Dict[str, float]] = []
        for dp in dumps:
            try:
                feats = self.extract_features_from_dump(dp)
                feats["source"] = str(dp)
                rows.append(feats)
                self.log(f"✔ features: {dp}")
            except Exception as e:
                self.log(f"✖ error en {dp}: {e}")

        # columnas ordenadas
        keys = sorted({k for r in rows for k in r.keys()})
        # ‘source’ al final
        if "source" in keys:
            keys.remove("source")
            keys.append("source")

        import csv
        out_csv = Path(out_csv or (self.out_dir / "training_dataset.csv"))
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, np.nan) for k in keys})

        self.log(f"CSV de dataset: {out_csv}")
        return out_csv

    # ---------- Helpers internos ----------
    def _to_serializable(self) -> Dict:
        s = self.setup
        return {
            "iterations": s.iterations,
            "max_vacancies": s.max_vacancies,
            "features": {
                "coordination": {"enabled": s.features.coordination.enabled, "rc": s.features.coordination.rc},
                "energy_potential": {"enabled": s.features.energy_potential.enabled,
                                     "column_candidates": s.features.energy_potential.column_candidates},
                "steinhardt": {"enabled": s.features.steinhardt.enabled,
                               "radius": s.features.steinhardt.radius,
                               "orders": s.features.steinhardt.orders},
                "convex_hull": {"enabled": s.features.convex_hull.enabled,
                                "area": s.features.convex_hull.area,
                                "volume": s.features.convex_hull.volume},
            },
            "perfect_network": {
                "lattice": s.perfect_network.lattice,
                "a0": s.perfect_network.a0,
                "cells": s.perfect_network.cells,
                "atom": s.perfect_network.atom,
            }
        }

    def _make_lattice_points(self, lattice: str, a0: float, rx: int, ry: int, rz: int) -> np.ndarray:
        lattice = (lattice or "fcc").lower()
        if lattice not in ("fcc", "bcc"):
            lattice = "fcc"
        if lattice == "fcc":
            basis = np.array([[0,0,0],[0,0.5,0.5],[0.5,0,0.5],[0.5,0.5,0]], float)
        else:
            basis = np.array([[0,0,0],[0.5,0.5,0.5]], float)
        ii, jj, kk = np.mgrid[0:rx, 0:ry, 0:rz]
        cells = np.stack([ii.ravel(), jj.ravel(), kk.ravel()], axis=1).astype(float)
        pos = (cells[:,None,:] + basis[None,:,:]).reshape(-1,3) * a0
        return pos

    def _coordination_counts(self, coords: np.ndarray, rc: float) -> np.ndarray:
        n = coords.shape[0]
        if n == 0:
            return np.array([], dtype=float)

        if _HAS_SCIPY and KDTree is not None:
            tree = KDTree(coords)
            # count neighbors within rc (excluding self)
            counts = np.array([max(0, len(tree.query_ball_point(coords[i], rc)) - 1) for i in range(n)], dtype=float)
            return counts

        # Fallback O(N^2)
        counts = np.zeros(n, dtype=float)
        for i in range(n):
            diffs = coords - coords[i]
            d2 = np.einsum("ij,ij->i", diffs, diffs)
            c = float(np.count_nonzero((d2 > 0.0) & (d2 <= rc*rc)))
            counts[i] = c
        return counts

    def _pick_energy_column(self, table: Dict[str, np.ndarray], candidates: List[str]) -> Optional[np.ndarray]:
        if not table:
            return None
        lowmap = {k.lower(): k for k in table.keys()}
        for name in candidates:
            if name.lower() in lowmap:
                return table[lowmap[name.lower()]]
        # heurística: primera col que contenga 'e' y sea numérica
        for k in table:
            if "e" in k.lower():
                v = table[k]
                if isinstance(v, np.ndarray) and np.issubdtype(v.dtype, np.number):
                    return v
        return None

    def _steinhardt_all_atoms(self, coords: np.ndarray, r: float, orders: List[int]) -> Dict[int, np.ndarray]:
        """
        Implementación estándar:
        q_l(i) = sqrt((4π/(2l+1)) * sum_m |q_lm(i)|^2 ), con
        q_lm(i) = (1/N_b(i)) sum_{j in nb(i)} Y_lm(theta_ij, phi_ij).
        """
        if not (_HAS_SCIPY and KDTree is not None and sph_harm is not None):
            raise RuntimeError("Steinhardt requiere SciPy (KDTree + sph_harm).")

        n = coords.shape[0]
        tree = KDTree(coords)
        # vecinos por átomo
        nbs = [tree.query_ball_point(coords[i], r) for i in range(n)]
        # eliminamos self
        for i in range(n):
            if i in nbs[i]:
                nbs[i].remove(i)

        # preparar salida
        q: Dict[int, np.ndarray] = {l: np.zeros(n, dtype=float) for l in orders}

        # cálculo por átomo
        for i in range(n):
            nbrs = nbs[i]
            Nb = len(nbrs)
            if Nb == 0:
                for l in orders:
                    q[l][i] = np.nan
                continue
            r_ij = coords[nbrs] - coords[i]
            # esféricas
            r_norm = np.linalg.norm(r_ij, axis=1)
            # evitar divisiones por cero
            mask = r_norm > 0
            if not np.any(mask):
                for l in orders:
                    q[l][i] = np.nan
                continue
            x, y, z = r_ij[mask, 0], r_ij[mask, 1], r_ij[mask, 2]
            theta = np.arccos(np.clip(z / np.linalg.norm(r_ij[mask], axis=1), -1.0, 1.0))  # [0,pi]
            phi = np.mod(np.arctan2(y, x), 2*np.pi)  # [0,2pi)

            for l in orders:
                qlm_sum = 0+0j
                # promediamos sobre m y vecinos:
                qlm_sq_sum = 0.0
                for m in range(-l, l+1):
                    Y = sph_harm(m, l, phi, theta)  # complejo
                    qlm = np.mean(Y)  # promedio sobre vecinos
                    qlm_sq_sum += (np.abs(qlm)**2).real
                q[i] = q.get(l, q[l])
                q[l][i] = math.sqrt((4*math.pi/(2*l+1)) * qlm_sq_sum)
        return q

    def log(self, msg: str) -> None:
        self.logger(str(msg))
