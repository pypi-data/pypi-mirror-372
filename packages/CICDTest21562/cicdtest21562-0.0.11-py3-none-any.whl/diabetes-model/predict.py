import pandas as pd
import joblib


def predict(model_path: str, csv_path: str):
    """
    Carga un modelo entrenado y predice con un CSV.

    Args:
        model_path: ruta al modelo entrenado.
        csv_path: ruta al CSV con datos (mismas columnas que entrenamiento).

    Returns:
        preds: predicciones del modelo.
    """
    pipe = joblib.load(model_path)

    df = pd.read_csv(csv_path)

    preds = pipe.predict(df)
    return preds