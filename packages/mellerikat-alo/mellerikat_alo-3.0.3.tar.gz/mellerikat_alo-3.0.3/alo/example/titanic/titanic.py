import os
import sys
import logging
import random
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score
from sklearn.model_selection import train_test_split

def preprocess(pipeline: dict):
    logger = pipeline['logger']
    logger.debug("preprocess")

def train(pipeline: dict, x_columns=[], y_column=None, n_estimators=100):
    logger = pipeline['logger']
    logger.debug("train")
    file_list = os.listdir(pipeline['dataset']['workspace'])
    csv_files = [file for file in file_list if file.endswith('.csv')]
    
    for csv_file in csv_files:
        file_path = os.path.join(pipeline['dataset']['workspace'], csv_file)
        df = pd.read_csv(file_path)
        logger.debug("\n%s", df)
        X = pd.get_dummies(df[x_columns])
        X_train, X_test, y_train, y_test = train_test_split(X, df[y_column], test_size=0.2, random_state=42)

        model = RandomForestClassifier(n_estimators=n_estimators, max_depth=5, random_state=1)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        precision = precision_score(y_test, y_pred, average='macro')
        logger.debug("y_pred\n%s", y_pred)
        pipeline['model']['n100_depth5'] = model  # save model
    
    return {
        'summary': {
            'result': f'precision: {precision}',
            'note': f'Test Titanic-demo (date: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")})',
            'score': random.uniform(0.1, 1.0),
        }
    }


def inference(pipeline: dict, x_columns=[]):
    logger = pipeline['logger']
    logger.debug("inference")
    model = pipeline['model']['n100_depth5']
    
    file_list = os.listdir(pipeline['dataset']['workspace'])
    csv_files = [file for file in file_list if file.endswith('.csv')]

    for csv_file in csv_files:
        file_path = os.path.join(pipeline['dataset']['workspace'], csv_file)
        df = pd.read_csv(file_path)
        logger.debug("\n%s", df)
        X = pd.get_dummies(df[x_columns])

        # load trained model
        predict_class = model.predict(X)
        predict_proba = model.predict_proba(X)

        result = pd.concat([df, pd.DataFrame(predict_class, columns=['predicted'])], axis=1)
        print(result)

        # result csv 저장
        result.to_csv(f"{pipeline['artifact']['workspace']}/result.csv")
        logger.debug("Save : %s", f"{pipeline['artifact']['workspace']}/result.csv")

        # summary
        num_survived = len(result[result['predicted'] == 1])
        num_total = len(result)
        survival_ratio = num_survived / num_total
        avg_proba = np.average(predict_proba, axis=0)
        avg_proba_survived = avg_proba[1].item()  # float
        avg_proba_dead = avg_proba[0].item()

    return {
        'extraOutput': '',
        'summary': {
            'result': f"#survived:{num_survived} / #total:{num_total}",
            'score': round(survival_ratio, 3),
            'note': "Score means titanic survival ratio",
            'probability': {"dead": avg_proba_dead, "survived": avg_proba_survived}
        }
    }