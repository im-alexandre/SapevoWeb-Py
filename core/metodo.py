"""
File: electre.py
Author: Alexandre Castro
Email: im.alexandre07@gmail.com
Github: https://www.github.com/im-alexandre
Description: SAPEVO method implementation
"""

import itertools
import json
from typing import Dict, List, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class DecisionMatrix:
    """
    Class responsible for generate the Sapevo decision matrix.
    It can be applied in criteria and alternatives evaluation
    """
    def __init__(self, alternatives):
        self.alternatives = alternatives
        self._data_frame = self._matrix_data_frame()
        self.matrix = self._matrix_generator()

    def _normalized_vector(self) -> np.ndarray:
        """
        Normalize Sum Vector using as follows:
        [a - min(alternatives) / max(alternatives)/min(alternatives) for a in alternatives]
        """
        scaler = MinMaxScaler()
        normalized_vector = scaler.fit_transform(self._data_frame['Sum Vector'].values.reshape(-1,1))
        self._data_frame['Normalized Vector'] = normalized_vector

    def _soma_alternativas(self):
        """
        Create Sum vector with row sums
        """
        self._data_frame['Sum Vector'] = self._data_frame.apply(np.sum, axis=1)


    def _normalized_vector_not_null(self):
        """
        Replaces zeros with min(non-zeros)/100
        """
        minimum = min(self._data_frame['Normalized Vector'][self._data_frame['Normalized Vector'] > 0])
        vector_not_null = self._data_frame['Normalized Vector'].replace(0, minimum/100)
        self._data_frame['Not null normalized vector'] = vector_not_null

    def _matrix_data_frame(self) -> pd.DataFrame:
        """Generate decision matrix as a pandas.DataFrame"""
        data = {eval(key):val for (key, val) in self.alternatives.items()}
        columns = list()
        for (x, y) in data.keys():
            columns.extend([x,y])
        columns = set(columns)
        data_frame = pd.DataFrame(None, index=columns, columns=columns)
        for x in columns:
            data_frame.at[x, x] = 0
        for (x, y), val in data.items():
            data_frame.at[x, y] = val
            data_frame.at[y, x] = -val
        return data_frame

    def _matrix_generator(self):
        """Generate dataframe with sum, normalized and not null normalized vectors"""
        self._soma_alternativas()
        self._normalized_vector()
        self._normalized_vector_not_null()
        return self._data_frame


if __name__ == '__main__':
    dados = {"('a', 'b')": 1, "('a', 'c')": -1, "('b', 'c')": 2}
    dados = json.dumps(dados)
    decisao = DecisionMatrix(dados)

    print("\n", "DADOS DE TESTE".center(70, "*"), "\n")
    print(dados)

    df = decisao.matrix
    print("\n", "MATRIZ DE DECISÃO DOS CRITÉRIOS".center(70, '*'), '\n')

    print(df)
