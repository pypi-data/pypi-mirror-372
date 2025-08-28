import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from .pipeline import create_pipeline


def train_model(csv_path: str, model_path: str = "model.pkl"):
    """
    Entrena el modelo con un CSV y guarda el pipeline.

    Parámetros:
        csv_path: ruta al CSV con datos.
        model_path: ruta donde guardar el modelo entrenado.
    """
    # Cargar datos
    df = pd.read_csv(csv_path)

    # Filtrado de datos (biológicas sin valores 0)
    cols_biologicas = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    df_filtered = df[~(df[cols_biologicas] == 0).any(axis=1)]

    # Separación en X e y
    X = df_filtered.drop('Outcome', axis=1)
    y = df_filtered['Outcome']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=101)

    # Crear pipeline y entrenar
    pipe = create_pipeline()
    pipe.fit(X_train, y_train)

    # Evaluar
    y_pred = pipe.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")

    # Guardar modelo
    joblib.dump(pipe, model_path)
    print(f"Modelo guardado en {model_path}")
