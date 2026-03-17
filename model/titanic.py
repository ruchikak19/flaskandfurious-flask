import pandas as pd
import numpy as np
import seaborn as sns

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import OneHotEncoder


class TitanicModel:
    _instance = None  # singleton

    def __init__(self):
        self.model = None
        self.dt = None
        self.encoder = OneHotEncoder(handle_unknown='ignore')

        self.features = ['pclass', 'sex', 'age', 'sibsp', 'parch', 'fare', 'alone']
        self.target = 'survived'

        # Load dataset
        self.data = sns.load_dataset('titanic')

    def _clean(self):
        td = self.data

        # Drop unused columns
        td.drop(['alive', 'who', 'adult_male', 'class', 'embark_town', 'deck'], axis=1, inplace=True)

        # Convert categorical → numeric
        td['sex'] = td['sex'].apply(lambda x: 1 if x == 'male' else 0)
        td['alone'] = td['alone'].apply(lambda x: 1 if x else 0)

        # Handle embarked (one-hot)
        td.dropna(subset=['embarked'], inplace=True)
        onehot = self.encoder.fit_transform(td[['embarked']]).toarray()

        cols = ['embarked_' + val for val in self.encoder.categories_[0]]
        onehot_df = pd.DataFrame(onehot, columns=cols)

        td = pd.concat([td.reset_index(drop=True), onehot_df], axis=1)
        td.drop(['embarked'], axis=1, inplace=True)

        self.features.extend(cols)

        td.dropna(inplace=True)

        self.data = td

    def _train(self):
        X = self.data[self.features]
        y = self.data[self.target]

        # Logistic regression (main model)
        self.model = LogisticRegression(max_iter=1000)
        self.model.fit(X, y)

        # Decision tree (for feature importance)
        self.dt = DecisionTreeClassifier()
        self.dt.fit(X, y)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._clean()
            cls._instance._train()
        return cls._instance

    def predict(self, passenger):
        df = pd.DataFrame(passenger, index=[0])

        # Convert fields
        df['sex'] = df['sex'].apply(lambda x: 1 if x == 'male' else 0)
        df['alone'] = df['alone'].apply(lambda x: 1 if x else 0)

        # One-hot encode embarked
        onehot = self.encoder.transform(df[['embarked']]).toarray()
        cols = ['embarked_' + val for val in self.encoder.categories_[0]]
        onehot_df = pd.DataFrame(onehot, columns=cols)

        df = pd.concat([df.reset_index(drop=True), onehot_df], axis=1)

        # Drop unused
        df.drop(['embarked', 'name'], axis=1, inplace=True)

        # Predict probabilities
        die, survive = np.squeeze(self.model.predict_proba(df))

        return {
            "die": float(die),
            "survive": float(survive)
        }

    def feature_weights(self):
        importances = self.dt.feature_importances_
        return dict(zip(self.features, importances))


def initTitanic():
    TitanicModel.get_instance()