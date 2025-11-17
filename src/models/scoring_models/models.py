from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.decomposition import  PCA

class Model(ABC):
    """Базовый класс модели"""
    
    @abstractmethod
    def fit(self, x, y=None):
        """Обучение модели"""
        pass

    @abstractmethod
    def predict(self, x):
        """Предсказание модели"""
        pass

class NaiveModel(Model):
    """Наивная модель на основе суммы признаков и порогов"""
    
    def __init__(self, bounds=[10, 32, 33, 60, 61, 100]):
        self.bounds = bounds

    def fit(self, x, y=None):
        """Для наивной модели fit не требуется"""
        return self

    def predict(self, x):
        """
        Применяет модель к массиву данных.
        x: numpy array или pandas DataFrame с формой (n_samples, n_features).
            Каждая строка суммируется для получения оценки.
        bounds: list из 6 значений [min_0, max_0, min_1, max_1, min_2, max_2],
            определяет диапазоны для классов 0, 1, 2 соответственно.

        Возвращает:
            numpy array с предсказаниями (0, 1 или 2) для каждой строки x.
        """
        scores = x.sum(axis=1)

        conditions = [
            (self.bounds[0] <= scores) & (scores <= self.bounds[1]),  # Класс 0
            (self.bounds[2] <= scores) & (scores <= self.bounds[3]),  # Класс 1
            (self.bounds[4] <= scores) & (scores <= self.bounds[5])   # Класс 2
        ]
        choices = [0, 1, 2]

        # Применяем условия
        result = np.select(conditions, choices, default=-1)  # -1 для значений вне диапазонов

        # Проверяем, были ли значения вне диапазонов
        if (result == -1).any():
            raise ValueError('Score на тесте больше(меньше), чем max=100(min=10)')

        return result

class KMeansModel(Model):
    """Модель кластеризации KMeans с предварительным t-SNE"""
    def __init__(self, n_clusters=3, random_state=42, n_tsne = 2):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.pca = PCA(n_components=n_tsne, random_state=random_state)
        
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
        # self.scaler = StandardScaler()
        

    def fit(self, x, y=None):
        x = self.pca.fit_transform(x)
        self.kmeans.fit(x)
        return self

    def predict(self, x):
        x = self.pca.transform(x)  # замечание: t-SNE не умеет трансформировать новые точки напрямую
        
        cluster_labels = self.kmeans.predict(x)
        return cluster_labels
