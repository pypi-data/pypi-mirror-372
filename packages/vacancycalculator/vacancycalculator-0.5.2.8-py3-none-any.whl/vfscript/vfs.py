# main.py

from .core import *  
from .config_loader import cargar_json_usuario
from pathlib import Path
import os
import pandas as pd
import warnings
import argparse
warnings.filterwarnings('ignore', message='.*OVITO.*PyPI')

def VacancyAnalysis():
    
    base = "outputs"
    for sub in ("csv", "dump", "json"):
        os.makedirs(os.path.join(base, sub), exist_ok=True)

    


    
    CONFIG = cargar_json_usuario()
    
    if "CONFIG" not in CONFIG or not isinstance(CONFIG["CONFIG"], list) or len(CONFIG["CONFIG"]) == 0:
        raise ValueError("input_params.json debe contener una lista 'CONFIG' con al menos un objeto.")

    configuracion = CONFIG["CONFIG"][0]
    raw_defects = configuracion.get('defect', [])  
    defect_files = raw_defects if isinstance(raw_defects, list) else [raw_defects]  
    for FILE in defect_files:
        cs_out_dir = Path("inputs")
        cs_generator = CrystalStructureGenerator(configuracion, cs_out_dir)
        dump_path = cs_generator.generate()
        #print(f"Estructura relajada generada en: {dump_path}")
        if configuracion['training']:
        # 1) Recuperar el dict que guarda tu pestaña (CONFIG[0]['training_setup'])
     
            params = json.load(open("input_params.json", "r", encoding="utf-8"))
            setup_dict = params["CONFIG"][0]["training_setup"]

            # 2) Construir el preparador
            prep = TrainingPreparer.from_setup_dict(setup_dict, out_dir=Path("outputs/training"),
                                                    logger=lambda m: print("[training]", m))

            # 3) Validar + preparar entorno
            prep.validate()
            prep.prepare_workspace()

            # 4) (Opcional) generar una red perfecta .dump para pruebas
            dump_ref = prep.generate_perfect_dump()  # outputs/training/relax_structure.dump

            # 5) Extraer features de uno o varios dumps y generar CSV
            csv_path = prep.build_dataset_csv([dump_ref])   # o bien una lista de dumps reales tuyos
            print("Dataset listo en:", csv_path)
            gen = AtomicGraphGenerator()
            gen.run()
            p = argparse.ArgumentParser(description="Exporta features (normas + ConvexHull) a CSV.")
            p.add_argument("--output-csv", default="outputs/csv/finger_data.csv",
                        help="Ruta del CSV de salida.")
            p.add_argument("--dump", action="append",
                        help="Ruta a uno o más .dump (repetible). Si se omite, se toma de input_params.json.")
            args = p.parse_args()

            exporter = FeatureExporter(
                dump_paths=args.dump if args.dump else None,
                output_csv=args.output_csv
            )
            try:
                exporter.export()
            except ImportError as e:
                # Si falta SciPy, el compute_convex_hull lo avisa acá
                print(f"[ERROR] {e}\nSugerencia: pip install scipy")


        analyzer = DeformationAnalyzer(FILE, configuracion['generate_relax'][0], configuracion['generate_relax'][5], threshold=0.02)
        delta = analyzer.compute_metric()
        method = analyzer.select_method()
        #print(f"Métrica δ = {delta:.4f}, método seleccionado: {method}")
        






        # 2) Condicional
        if method == 'geometric' and configuracion['geometric_method']:
            # Aplico el método geométrico
            vac_analyzer = WSMet(
                defect_dump_path=FILE,
                lattice_type=configuracion['generate_relax'][0],
                element=configuracion['generate_relax'][5],
                tolerance=0.5
            )
            vacancies = vac_analyzer.run()
            # vacancies es la lista de posiciones
        elif method == 'ml' or configuracion['geometric_method']==False :
            vac_analyzer = WSMet(
                defect_dump_path=FILE,
                lattice_type=configuracion['generate_relax'][0],
                element=configuracion['generate_relax'][5],
                tolerance=0.5
            )
            vac_analyzer.generate_perfect_atoms()
            
            processor = ClusterProcessor(FILE)
            processor.run()
            separator = KeyFilesSeparator(configuracion, os.path.join("outputs/json", "clusters.json"))
            separator.run()

            # 3. Procesar dumps críticos
            clave_criticos = ClusterDumpProcessor.cargar_lista_archivos_criticos("outputs/json/key_archivos.json")
            for archivo in clave_criticos:
                try:
                    dump_proc = ClusterDumpProcessor(archivo, decimals=5)
                    dump_proc.load_data()
                    dump_proc.process_clusters()
                    dump_proc.export_updated_file(f"{archivo}_actualizado.txt")
                except Exception as e:
                    print(f"Error procesando {archivo}: {e}")

            # 4. Subdivisión iterativa
            lista_criticos = ClusterDumpProcessor.cargar_lista_archivos_criticos("outputs/json/key_archivos.json")
            for archivo in lista_criticos:
                machine_proc = ClusterProcessorMachine(archivo)  # o ClusterProcessorMachine(archivo, "input_params.json")
                machine_proc.process_clusters()
                machine_proc.export_updated_file()


            # 5. Separar archivos finales vs críticos
            separator = KeyFilesSeparator(configuracion, os.path.join("outputs/json", "clusters.json"))
            separator.run()

            # 6. Generar nuevos dumps por cluster
            export_list = ExportClusterList("outputs/json/key_archivos.json")
            export_list.process_files()

            # 7. Calcular superficies de dump
            surf_proc = SurfaceProcessor(configuracion)
            surf_proc.process_all_files()
            surf_proc.export_results()


            exporter = ClusterFeatureExporter("outputs/json/key_archivos.json")
            exporter.export()


            # ------------------------------------------------------------------------
            # 8. Entrenar y clasificar defectos con el nuevo modelo ensemble
            if configuracion['geometric_method']:
                analyzer = WSMet("inputs/void_15.dump", "bcc", "Fe", tolerance=0.5)
                vac_positions = analyzer.run()
            # Instancia y entrena el modelo
            clf = ImprovedVacancyClassifier(json_path='outputs/json/training_graph.json')
            clf.train()  
            # → ya imprime mejores parámetros y reporte de clasificación

            # Clasifica tu CSV de defectos (añade columna 'grupo_predicho')
            df_clasif = clf.classify_csv(
                csv_path='outputs/csv/defect_data.csv',
                output_path='outputs/csv/finger_data_clasificado.csv'
            )
            #print(df_clasif[['archivo','grupo_predicho']])
            # ------------------------------------------------------------------------
            # 9. Predicción de vacancias según grupo_predicho
            # Como ImprovedVacancyClassifier usa la misma API de train/classify,
            # podemos reusar el método classify_csv para predecir vacancias
            # (o bien, si lo prefieres, crear un método predict_from_csv
            #  similar al anterior)
            df_pred = clf.classify_csv(
                csv_path='outputs/csv/finger_data_clasificado.csv',
                output_path='outputs/csv/finger_data_predicha.csv'
            )
            #print("✅ Vacancias predichas guardadas en outputs/csv/finger_data_predicha.csv")

            # ------------------------------------------------------------------------
           
            assigner = FingerprintVacancyAssigner(
                base_csv_path="outputs/csv/finger_data.csv",
                query_csv_path="outputs/csv/finger_key_files.csv",
                weight_N=1
            )
            df_result = assigner.assign()
            df_result.to_csv("outputs/csv/finger_key_files_clasificado.csv", index=False)
            #print("✅ Resultado guardado con peso_N =", assigner.weight_N)
            #Calcular categoria de defect_file.csv
            #model = BehaviorTreeModel(weight_cluster_size=2.0, max_depth=5)
            #model.train('outputs/json/training_graph.json')

            #df_resultado = model.classify_csv(
            #   csv_path='outputs/csv/defect_data.csv',
            #  output_path='outputs/csv/finger_data_clasificado.csv'
            #)

            #print(df_resultado[['archivo', 'grupo_predicho']])


            #ETAPA DE PREDICCIONES

            trainer = VacancyModelTrainer(json_path="outputs/json/training_graph.json")
            trainer.load_data()
            trainer.train_group_classifier()
            trainer.train_all_regressors()
        
            # Predicción por CSV
            out_df = trainer.predict_from_csv("outputs/csv/finger_data_clasificado.csv")

            out_df.to_csv("outputs/csv/results.csv", index=False)
            #print("✅ Guardado results.csv")
        # Ejemplo de uso
            assigner = FingerprintVacancyAssigner(
                base_csv_path="outputs/csv/finger_data.csv",
                query_csv_path="outputs/csv/finger_key_files.csv",
                weight_N=100 # peso mayor para 'N'
            )
            df_result = assigner.assign()
            df_result.to_csv("outputs/csv/finger_key_files_clasificado.csv", index=False)
            #print("✅ Resultado guardado con peso_N =", assigner.weight_N)

        else:
            raise RuntimeError(f"Método desconocido: {method}")
        

        #ESTIMACION POR CLASIGICACION DE COEFICIENTE DE VACANCIA AREA
        calc = GroupCoefficientCalculator("outputs/json/training_graph.json")
        calc.load()
        # Usa mínimos teóricos (1,4,7,10) y redondeo hacia arriba (ceil)
        out = calc.estimate_from_defect_csv(
            defect_csv_path="outputs/csv/finger_data_clasificado.csv",
            group_col=None,                 # detecta entre ['grupo_predicho','grupo','Group','label','group']
            surface_area_col="surface_area",
            out_path="outputs/csv/defect_data_estimated.csv",
            use_observed_min_instead=False, # pon True si querés dividir por el min OBSERVADO del grupo
            round_mode="ceil"
        )
        #print(out.head())

            

if __name__ == "__main__":
    VacancyAnalysis()
    print("Script ejecutado correctamente.")



