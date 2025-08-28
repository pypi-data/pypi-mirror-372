# modifiers/surface_processor/surface_processor.py

import os
import json
import numpy as np
from scipy.spatial import ConvexHull


from ..config import CONFIG

class SurfaceProcessor:
    def __init__(
        self,
        config=CONFIG[0],
        json_path="outputs/json/key_archivos.json",
        threshold_file="outputs/json/training_graph.json"
    ):
        self.config = config
        self.json_path = json_path

        # Cargo clusters finales
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.clusters_final = data.get("clusters_final", [])

        # Cargo umbrales desde un JSON que es una lista de registros
        with open(threshold_file, "r", encoding="utf-8") as f:
            threshold_data = json.load(f)
        # Usamos el primer registro de la lista:
        first = threshold_data[0]
        self.min_area_threshold          = first["surface_area"]   / 2
        self.min_filled_volume_threshold = first["filled_volume"]  / 2
    def _read_dump_coordinates(self, dump_file: str) -> np.ndarray:
        """
        Extrae las coordenadas (x,y,z) del dump LAMMPS. 
        Busca la línea "ITEM: ATOMS ..." y lee cada fila como [id, type, x, y, z, ...].
        Devuelve un array Nx3 con (x,y,z) de cada partícula.
        """
        coords = []
        with open(dump_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        start = None
        for i, line in enumerate(lines):
            if line.strip().startswith("ITEM: ATOMS"):
                start = i + 1
                break
        if start is None:
            return np.empty((0, 3))

        for line in lines[start:]:
            parts = line.split()
            if len(parts) < 5:
                continue
            try:
                x = float(parts[2])
                y = float(parts[3])
                z = float(parts[4])
                coords.append((x, y, z))
            except ValueError:
                continue

        return np.array(coords)

    def process_surface_for_file(self, archivo: str) -> tuple:
        """
        Dado un dump (archivo), calcula:
          - cluster_size = número de partículas
          - avg_distance = distancia promedio al centro de masa
          - area, filled_volume a partir del convex hull de las coordenadas

        Si el área o el volumen no superan el umbral, devuelve todos None excepto cluster_size y avg_distance.
        """
        
        positions = self._read_dump_coordinates(archivo)
        cluster_size = positions.shape[0]

        if cluster_size == 0:
            return None, None, None, None, 0, None

        
        center = np.mean(positions, axis=0)
        avg_distance = np.mean(np.linalg.norm(positions - center, axis=1))

        
        try:
            hull = ConvexHull(positions)
            area = hull.area
            filled_volume = hull.volume
        except Exception:
            area = 0
            filled_volume = 0

        
        if area < self.min_area_threshold or filled_volume < self.min_filled_volume_threshold:
            return None, None, None, None, cluster_size, avg_distance

        
        best_pipeline = None
        best_radius = None

        return best_pipeline, best_radius, area, filled_volume, cluster_size, avg_distance

    def process_all_files(self) -> np.ndarray:
        """
        Itera sobre cada ruta en self.clusters_final, calcula los valores y
        construye una matriz con [archivo, mejor_radius, area, filled_volume, cluster_size, avg_distance].
        """
        results = []
        for archivo in self.clusters_final:
            bp, br, ba, fv, num_atm, avg_dist = self.process_surface_for_file(archivo)
            
            if ba is not None:
                results.append([archivo, br, ba, fv, num_atm, avg_dist])
        self.results_matrix = np.array(results, dtype=object)
        return self.results_matrix

    def export_results(self, output_csv: str = "outputs/csv/defect_data.csv"):
        """
        Guarda self.results_matrix en un CSV (creando la carpeta si no existe).
        """
        if self.results_matrix is None:
            self.process_all_files()

        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        np.savetxt(
            output_csv,
            self.results_matrix,
            delimiter=",",
            fmt="%s",  
            header="archivo,mejor_radio,surface_area,filled_volume,cluster_size,mean_distance",
            comments=""
        )
