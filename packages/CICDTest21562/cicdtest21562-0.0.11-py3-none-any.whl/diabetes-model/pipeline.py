from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline


def create_pipeline():
    """
    Pipeline para el modelo de diabetes.

    Args:
        None

    Returns:
        pipe: Pipeline con escalado y regresión logistica.
    """
    pipe = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1000)
    )
    print("Pipeline creado.")
    return pipe