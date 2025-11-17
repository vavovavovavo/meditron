import numpy as np
import pandas as pd
import os

def generate_correlated_gaussian_vectors(mu, R, path, n_samples=1):
    """
    Генерирует n_samples векторов из многомерного нормального распределения
    с вектором средних mu и матрицей корреляций R.
    Сохраняет результат в CSV-файл с помощью pandas в директорию ../data/.
    Если файл уже существует, дописывает новые данные в конец файла.
    Иначе создает новый файл.

    Параметры:
    - mu: 1D array (n,) — вектор средних
    - R: 2D array (n, n) — матрица корреляций (симметричная, положительно определённая)
    - path: str — имя файла (например, 'sample.csv'), будет сохранён в ../data/
    - n_samples: int — количество векторов для генерации

    Возвращает:
    - X: 2D array (n_samples, n) — массив сгенерированных векторов
    """
    # Проверка симметричности и положительной определённости (опционально)
    assert R.shape[0] == R.shape[1], "Матрица R должна быть квадратной"
    assert R.shape[0] == len(mu), "Размер R и mu должны совпадать"

    # Разложение Холецкого: R = L @ L.T
    L = np.linalg.cholesky(R)

    # Генерация стандартных нормальных векторов (n_samples, n)
    Z = np.random.normal(0, 1, size=(n_samples, len(mu)))

    # Преобразование: X = mu + Z @ L.T
    X = mu + Z @ L.T

    # Приводим к int и [1;10]
    X = np.clip(X, 1, 10).astype(int)

    df = pd.DataFrame(X)
    output_path = os.path.join('data', path)  # директория выше в папку data

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if os.path.exists(output_path):
        df.to_csv(output_path, mode='a', header=False, index=False)
    else:
        df.to_csv(output_path, mode='w', header=True, index=False)

    return X