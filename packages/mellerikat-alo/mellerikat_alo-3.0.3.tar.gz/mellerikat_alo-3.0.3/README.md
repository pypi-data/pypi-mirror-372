# Welcome to ALO (AI Learning Organizer)

⚡ [Mellerikat](https://mellerikat.com) 에서 AI Solution 이 실행 가능하게 하는 ML framework 입니다. ⚡

[![Generic badge](https://img.shields.io/badge/release-v2.0.0-green.svg?style=for-the-badge)](http://링크)
[![Generic badge](https://img.shields.io/badge/last_update-2024.08.18-002E5F?style=for-the-badge)]()
[![Generic badge](https://img.shields.io/badge/python-3.10.12-purple.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Generic badge](https://img.shields.io/badge/dependencies-up_to_date-green.svg?style=for-the-badge&logo=python&logoColor=white)](requirement링크)
[![Generic badge](https://img.shields.io/badge/collab-blue.svg?style=for-the-badge)](http://collab.lge.com/main/display/AICONTENTS)
[![Generic badge](https://img.shields.io/badge/request_clm-green.svg?style=for-the-badge)](http://collab.lge.com/main/pages/viewpage.action?pageId=2157128981)


# ALO Manual
- [설치 및 실행](#설치가이드)
  - [ALO 설치](#alo-설치)
  - [AI Contents 실행](#ai-contents-실행)
- [AI Contents 제작](#ai-contents-제작)
  1. [pipeline 코딩](#pipeline-코딩)
  2. [experimental_plan yaml 작성](#experimental_plan-yaml-작성)
- [개발 가이드](#개발-가이드)
  - [pipeline 코딩 가이드](#pipeline-코딩-가이드)
  - [experimental_plan yaml 작성 가이드](#experimental_plan-yaml-작성-가이드)
  - [jupyter 예제](#jupyter-예제)
- [문제 해결 방법](#문제-해결-방법)

---

## 설치 및 실행
conda 또는 python(system 또는 가상 환경) 설치된 환경 기준 설치가이드 입니다.

### ALO 설치
- 소스 코드를 직접 사용하는 경우
  ```console
  git clone http://mod.lge.com/hub/dxadvtech/aicontents-framework/alo-v2.git
  cd alo-v2
  ```
- ALO 패키지를 install 후 사용하는 방식
  ```console
  git clone http://mod.lge.com/hub/dxadvtech/aicontents-framework/alo-v2.git
  cd alo-v2
  python setup.py install
  ```
  alo가 정상 설치된 경우  `alo` command를 이용하여 AI Contents를 실행할 수 있습니다.


### AI Contents 실행
contents는 2개의 파일이 필요합니다.
- pipline.py : contents 를 실행하기 위한 코드    
  `ALO`의 실행 구조에 맞는 형식의 함수 형식으로 작성되어야 하며,  
  pipeline.py 단독으로 실행 가능한 상태의 파일이어야 합니다.
- experimental_plan.yaml : `ALO` 실행 환경에서의 pipeline.py 동작을 위한 환경 설정 파일 

> [**AI Contents 들의 git 입니다.**]    
> :loud_sound: Contents 별로 다른 virtualenv 를 사용하세요. ~~  (Package 충돌 주의 !! :sob: :sob:)    
> :scroll: Titanic : http://mod.lge.com/hub/smartdata/tvlog/utils/alo_solution_test.git    


```console
alo --git.url http://mod.lge.com/hub/smartdata/tvlog/utils/alo_solution_test.git
# 특정 브랜치로 변경이 필요한 경우 --git.branch branch_name 옵션 추가 
```
[:point_up: Go First ~ ](#alo-manual)

---
## AI Contents 제작
AI Contents 가 과제 진행하는데 기능 추가를 해야 할 경우 AI Contents 제작자에게 의뢰 ([기능개발 의뢰하기](http://collab.lge.com/main/pages/viewpage.action?pageId=2157128981))를 하거나,  
파이프라인에 Asset 을 추가하여 과제를 진행 할 수 있습니다.

`로컬` 환경에서 1차적으로  
`<<python>>pipeline` 코드 개발 및 테스트를 진행 완료 후  
`mellerikat`과 통합테스트를 진행할 수 있습니다.

![SequenceDaigram](zenuml_sequence_diagram.png)
<!---
    title ALO Run
    @Actor Local
    <<python>> pipeline
    group mellericat{
      @Server ALO
      @Database Redis
      @server EdgeApp
      @Client Mellerikat
    }
    @Starter(Local)
    if("학습"){
        summary = pipeline.preprocess(context, pipeline, kwargs)
        summary = pipeline.train(context, pipeline, kwargs)
    }
    if("추론"){
        summary = pipeline.preprocess(context, pipeline, kwargs)
        summary = pipeline.inference(context, pipeline, kwargs)
    }
    if (Mellerikat){
        Mellerikat->ALO.run{
            EdgeApp->Redis: connect
            ALO->Redis: connect
            loop("반복"){
                ALO->Redis: publish(status:waiting)
                EdgeApp->Redis: subscribe(waiting)
                // 추론실행 요청
                Mellerikat-> EdgeApp: inference()
                EdgeApp->Redis: push(json)
                Redis.pop(BLOCKING){
                    return json
                }
                ALO.update(json){
                    return kwargs
                }
                summary = pipeline.preprocess(context, pipeline, kwargs)
                summary = pipeline.inference(context, pipeline, kwargs)
                ALO->Redis: publish(status:save)
                EdgeApp->Redis: subscribe(save)
            }            
        }
    }
-->

### pipeline 코딩
`ALO`의 실행 구조에 맞는 형식의 함수로 작성되어야 하며,  
pipeline.py 단독으로 실행 가능한 상태의 파일이어야 합니다.
#### pipeline.py 예) Titanic
```python
# -*- coding: utf-8 -*-
import os
import sys
import logging
import random
import pandas as pd
import numpy as np
import pathlib
from datetime import datetime, timezone
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score
from sklearn.model_selection import train_test_split


def preprocess(context: dict, pipeline: dict):
  logger = context['logger']
  logger.info("preprocess.")
  logger.info(".")


def train(context: dict, pipeline: dict, x_columns=[], y_column=None, n_estimators=100):
  logger = context['logger']
  logger.debug("train")
  df = pd.read_csv(pipeline['dataset']['train.csv'])
  logger.debug("\n%s", df)
  X = pd.get_dummies(df[x_columns])
  X_train, X_test, y_train, y_test = train_test_split(X, df[y_column], test_size=0.2, random_state=42)

  model = RandomForestClassifier(n_estimators=n_estimators, max_depth=5, random_state=1)
  model.fit(X_train, y_train)

  y_pred = model.predict(X_test)
  precision = precision_score(y_test, y_pred, average='macro')
  logger.debug("y_pred\n%s", y_pred)

  # 객체를 파일로 저장
  # 객체 직렬화(pickle)가 지원되지 않는 경우 사용자가 직접 저장 및 불러오기를 구현해야함.
  # 저장 및 불러오기 구현시 context['model']['workspace'] 경로 이하에 저장.
  context['model']['n100_depth5'] = model  # Save object to both memory and files.
  return {
    'summary': {
      'result': f'precision: {precision}',
      'note': f'Test Titanic-demo (date: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")})',
      'score': random.uniform(0.1, 1.0),
    }
  }


def inference(context: dict, pipeline: dict, x_columns=[]):
  logger = context['logger']
  logger.debug("inference")
  model = context['model']['n100_depth5']  # 저장된 모델을 불러오기
  df = pd.read_csv(pipeline['dataset']["test.csv"])
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
    'summary': {
      'result': f"#survived:{num_survived} / #total:{num_total}",
      'score': round(survival_ratio, 3),
      'note': "Score means titanic survival ratio",
      'probability': {"dead": avg_proba_dead, "survived": avg_proba_survived}
    }
  }

def run():
  # 로컬 pipeline 구성 테스트
  logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
  dataset_dir = os.environ.get('SOLUTION_DATA_PATH', 'data')
  train_artifact, inference_artifact = '/tmp/titanic/train', '/tmp/titanic/inference'
  pathlib.Path(train_artifact).mkdir(parents=True, exist_ok=True)
  pathlib.Path(inference_artifact).mkdir(parents=True, exist_ok=True)

  train_pipeline = {
    'dataset': {    # 학습 또는 필요한 파일들을 포함한 폴더 및 파일 경로 정보
      'workspace': f'{dataset_dir}/train/dataset',           # dataset 파일이 저장된 절대 폴더 경로
      'train.csv': f'{dataset_dir}/train/dataset/train.csv'  # train.csv 파일의 절대 경로
    },
    'artifact': {
      'workspace': train_artifact  # 결과물 저장 경로
    },
    'preprocess': {'argument': {}, 'result': {}},
    'train': {
      'argument': {
        'x_columns': ['Pclass', 'Sex', 'SibSp', 'Parch'],
        'y_column': 'Survived'
      },
      'result': {}
    },
  }
  inference_pipeline = {
    'dataset': {    # 학습 또는 필요한 파일들을 포함한 폴더 및 파일 경로 정보
      'workspace': f'{dataset_dir}/inference/dataset',         # dataset 파일이 저장된 절대 폴더 경로
      'test.csv': f'{dataset_dir}/inference/dataset/test.csv'  # train.csv 파일의 절대 경로
    },
    'artifact': {
      'workspace': inference_artifact  # 결과물 저장 경로
    },
    'preprocess': {'argument': {}, 'result': {}},
    'inference': {
      'argument': {
        'x_columns': ['Pclass', 'Sex', 'SibSp', 'Parch']
      },
      'result': {}
    },
  }
  context = {
    'logger': logging.getLogger(),
    'train': train_pipeline,
    'inference': inference_pipeline,
    'model': {},
  }

  # train pipeline 실행 및 결과 저장
  context['train']['preprocess']['result'] = preprocess(context, train_pipeline, **context['train']['preprocess']['argument'])
  context['train']['train']['result'] = train(context, train_pipeline, **context['train']['train']['argument'])

  # inference pipeline 실행 및 결과 저장
  context['inference']['preprocess']['result'] = preprocess(context, train_pipeline, **context['inference']['preprocess']['argument'])
  context['inference']['inference']['result'] = inference(context, inference_pipeline, **context['inference']['inference']['argument'])


if __name__ == '__main__':
  run()
```
실행 결과
```angular2html
python pipeline.py

INFO:root:preprocess.
INFO:root:.
DEBUG:root:train
DEBUG:root:
PassengerId  Survived  Pclass                                               Name     Sex   Age  SibSp  Parch            Ticket     Fare Cabin Embarked
0              1         0       3                            Braund, Mr. Owen Harris    male  22.0      1      0         A/5 21171   7.2500   NaN        S
1              2         1       1  Cumings, Mrs. John Bradley (Florence Briggs Th...  female  38.0      1      0          PC 17599  71.2833   C85        C
...
...
...
[418 rows x 12 columns]
DEBUG:root:Save : /tmp/titanic/inference/result.csv
```

### experimental_plan yaml 작성
`ALO`를 통해 실행할 수 있도록 experimental_plan.yaml 아래 예제와 같이 작성한다.
#### experimental_plna.yaml
```yaml
name: titanic
version: 1.0.0
solution:
  pip:
    requirements:             # Optional) 개별 library를 설치하고자 하는 경우
      - numpy==1.26.4
      - pandas==1.5.3
      - scikit-learn
  function:                       # Required) 사용자 함수 정의
    preprocess:                   # 대상 함수 이름
      def: pipeline.preprocess    # 호출 대상 모듈명.함수명
    train:
      def: pipeline.train
      argument:
        x_columns: [ 'Pclass', 'Sex', 'SibSp', 'Parch' ]
        y_column: Survived
    inference:
      def: pipeline.inference
      argument:
        x_columns: [ 'Pclass', 'Sex', 'SibSp', 'Parch' ]
  train:
    dataset_uri: data/train/dataset/
    artifact_uri: artifacts/train/
    pipeline: [preprocess, train]        # 실행 대상 function 목록
  inference:
    dataset_uri: data/inference/dataset/
    model_uri: data/inference/models/n100_depth5.pkl
    artifact_uri: artifacts/inference/
    pipeline: [preprocess, inference]    # 실행 대상 function 목록
```
실행 결과
```angular2html
# experimental_plan.yaml 파일을 생성한 폴더 경로에서 실행시
alo

================================================================================
__         __ _          ___    __    ____                  __   __
/ /   ___  / /( )_____   /   |  / /   / __ \                / /  / /
/ /   / _ \/ __/// ___/  / /| | / /   / / / /    ______     / /  / /
/ /___/  __/ /_  (__  )  / ___ |/ /___/ /_/ /    /_____/    /_/  /_/
/_____/\___/\__/ /____/  /_/  |_/_____/\____/               (_)  (_)
================================================================================
[2024-08-18 07:02:11,971|alo|INFO|alo.py(558)|show_version()]
=========================================== Info ===========================================
- Time (UTC)        : 2024-08-18 07:02:11
- Alo               : 3.0.0
- Solution Name     : titanic
- Solution Version  : 1.0.0
- Solution Config   : /alo/titanic/experimental_plan.yaml
- Home Directory    : /alo/titanic
============================================================================================
...
...
...
[2024-08-18 07:02:13,034|alo|INFO|alo.py(722)|artifact()] [ARTIFACT] Success save to : [LocalFile(path='artifacts/inference/', compress=FileCompress(enable=True, type='tar.gz'))]
[2024-08-18 07:02:13,035|alo|DEBUG|alo.py(699)|backup_to_v1()] [ARTIFACTS] Copy /alo/titanic/.workspace/titanic/history/2024-08-18T07:02:12.689107/inference to /alo/titanic/inference_artifacts
[2024-08-18 07:02:13,039|alo|INFO|alo.py(470)|__exit__()] [CONTEXT] Total elapsed second : 0.35
[2024-08-18 07:02:13,039|alo|DEBUG|alo.py(475)|retain_history()] [HISTORY] remove old directory : []
```
[:point_up: Go First ~ ](#alo-manual)

---
## 개발 가이드
`ALO` 를 통해 사용자 contents를 실행하기 위해서는  
`experimental_plan.yml`과 `python` 소스 코드 파일이 필요하며,  
아래 이미지와 같은 참조 관계 설정이 필요합니다.
![연관관계](yml_py_relation.png)

### pipeline 코딩 가이드
pipeline.py 파일명은   
임의의 어떠한 파일명 또는 여러 파일명으로 분리하여 코딩하여도 무방합니다.

아래 조건을 반드시 준수하여야 합니다.
- pipeline은 1개 이상의 함수로 구성되어져야 합니다.
  ```python
  def train(context: dict, pipeline: dict, x_columns=[], y_column=None, n_estimators=100):
      pass
  ...
  def inference(context: dict, pipeline: dict, x_columns=[]):
      pass
  ```
- pipeline 각 함수는  
  > **Warning**  
  > 시스템 공통 인자 context, pipeline 2개를 반드시 정의해야 하며,  
  > 사용자 정의 인자(keyword argument)를 1개 이상 정의할 수 있습니다.  
  ```python
  def train(context: dict, pipeline: dict, x_columns=[], y_column=None, n_estimators=100, **kwargs):
      pass
  ```
  - context: 실행 전반에 관련한 정보를 담고 있는 dict
    ```python
    context = {
        'id': 'c2d93251-2307-413f-90ba-d1ea72d5eef4',     # 요청 UID
        'name': 'titanic',                                # 이름
        'host': 'eks-kuber-titanic-01',                   # 호스트명
        'version': '3.0.0',                               # ALO 버전
        'startAt': datetime.datetime(2024, 6, 28, 8, 48, 11, 159265),   # 시작 시각
        'finishAt': datetime.datetime(2024, 6, 24, 11, 27, 55, 324312), # 완료 시각
        'workspace': '/alo/titanic',                      # 작업 경로
        'logger': logger,                                 # 로거 객체
        'model': {
            'workspace': '/alo/titanic/model_artifacts',     # 모델 저장 경로
            'n100_depth5': (object),                          # n100_depth5 모델 객체
        },
        'stage': 'train' 또는 'inference',                 # 현재 실행 단계명
        'train': {...},                                   # 학습 pipeline 관련 정보
        'inference': {...},                               # 추론 pipeline 관련 정보
    }
    ```
  - pipeline: train/inference 함수 실행과 관련된 정보를 담고 있는 dict
    ```python
    pipeline = {
        'startAt': datetime.datetime(2024, 6, 28, 8, 48, 11, 159265),   # 시작 시각
        'finishAt': datetime.datetime(2024, 6, 24, 11, 27, 55, 324312), # 완료 시각
        'workspace': '/alo/titanic/train',                # 작업 경로
        'artifact': '/alo/titanic/artifact',              # 실행 결과 파일 저장 경로
        'dataset': {
            'workspace': '/alo/titanic/train/dataset',    # dataset 파일들이 저장된 경로
            'train.csv': '/alo/titanic/train/dataset/train.csv',  # 파일명으로 저장된 경로 정보를 가져올 수 있음
        },
        'preprocess': {        # pipeline 함수 실행 정보
            'argument': {...},  # 함수 인자
            'result': {...},    # 함수 결과
        },
        'train': {             # pipeline 함수 실행 정보
            'argument': {...},  # 함수 인자
            'result': {...},    # 함수 결과
        },
    }
    ```
  - 사용자 정의 인자(named parameters): 함수 호출 실행시 필요함 인자

- 기본적으로 pipeline 함수의 return 결과는 없어도 무방하며,    
  score 데이터 저장을 원하는 경우 summary 형식(result, score, note, probability)을 return 할 수 있습니다.  
  ```python
  def train(context: dict, pipeline: dict, x_columns=[], y_column=None, n_estimators=100):
      ...
      ...
      ...
      """
      result      (str): Inference result summarized info. (length limit: 25)
      score       (float): model performance score to be used for model retraining (0 ~ 1.0)
      note        (str): optional & additional info. for inference result (length limit: 100) (optional)
      probability (dict): probability per class prediction if the solution is classification problem.  (optional) e.g. {'OK': 0.6, 'NG':0.4}
      """
      return {
        'summary': {
            'result': f'precision: {precision}',
            'note': f'Test Titanic-demo',
            'score': random.uniform(0.1, 1.0),  # 0~1 사이의 실수여야 함.
        }
    }
  ```


### experimental_plan yaml 작성 가이드
experimental_plan.yaml 파일은 ALO를 통해 실행할 수 있도록  
pipeline 함수 정의, dataset 파일 위치, 결과 저장 위치 등 환경 설정을 위한 파일입니다.

```yaml
name: titanic  # contents 명
version: 1.0.0 # contents 버전
solution:
  pip:            # 옵션) contents 수행에 필요한 3rd party library
    requirements:        # 개별 library 설치 시 이름 및 버전 명시
      - numpy==1.26.4
      - pandas==1.5.3
      - scikit-learn
  function:       # 필수) pipeline 대상 함수 정의
    preprocess:                   # 함수명
      def: pipeline.preprocess    # 호출 대상 모듈명.함수명
    train:
      def: pipeline.train
      argument:                   # 함수 호출시 넘겨줄 사용자 정의 인자
        x_columns: [ 'Pclass', 'Sex', 'SibSp', 'Parch' ]
        y_column: Survived
    inference:
      def: pipeline.inference
      argument:
        x_columns: [ 'Pclass', 'Sex', 'SibSp', 'Parch' ]
  train:          # 옵션) 학습 정의
    pipeline: [preprocess, train]              # 필수) 실행 대상 function 목록
    dataset_uri: data/train/dataset/           # 옵션) 학습시 필요한 데이터셋 파일 경로 또는 폴더 
    artifact_uri: artifacts/train/             # 옵션) 학습 관련 사용자 임의의 파일을 저장할 경로
  inference:      # 옵션) 추론 정의
    pipeline: [preprocess, inference]          # 필수) 실행 대상 function 목록
    dataset_uri: data/inference/dataset/
    model_uri: data/inference/models/n100_depth5.pkl # 옵션) 모델 파일 경로
    artifact_uri: artifacts/inference/
    # xxx_uri 속성은 로컬 절대/상대 경로 형식 또는 s3://bucket/path 형식 지원
```

[:point_up: Go First ~ ](#alo-manual)

### jupyter 예제

```python
from alo import Alo

alo = Alo() # 초기화
alo.train() # 학습만 실행
alo.train({ # 학습 각 pipeline 함수 인자 전달
    'train': {
        'n_estimators': 100,
        'x_columns': ['Pclass', 'Sex', 'SibSp', 'Parch'],
        'y_column': 'Survived',
    },
    'preprocess': {
        'test': 123
    },
})
alo.inference() # 추론만 실행

alo.run() # train(), inference() 모두 수행

results = alo.history()                         # stdout으로 출력하지 않으며, 이력 list[dict] 객체 리턴
alo.history(show_table=True)                    # 표준출력으로 테이블 출력
alo.history(show_table={'col_sort': 'asc'})     # 컬럼명 오름차순으로 정렬 후 출력
alo.history(show_table={'col_sort': 'desc'})    # 컬럼명 내림차순으로 정렬 후 출력
alo.history(show_table={'col_max_width': 100})  # 테이블 출력시 컬럼의 사이즈를 100자로 늘림

alo.reload() # yaml 파일 및 환경 변수 재로딩
```
[:point_up: Go First ~ ](#alo-manual)

---
## 문제 해결 방법
### 에러 코드별 가이드
#### 분류
- INI : ALO 초기화 작업 관련 오류
- PIP : pipeline 설정/동작 관련 오류
- VAL : 설정 항목의 누락, 미허용 값과 관련된 오류

#### 에러코드 원인 및 조치 가이드
|     코드      | 설명                                     | 원인 및 조치                                                          |
|:-----------:|:---------------------------------------|:-----------------------------------------------------------------|
| ALO-INI-000 | 초기화 작업 중 에러가 발생                        | 원인이 다양함으로 에러 메시지 확인 및 조치                                         |
| ALO-INI-002 | 사용자 library 설치 오류                      | requirements.txt 확인 및 python 버전 확인                               |
| ALO-INI-003 | 초기화 작업시 필요한 파일 없음                      | The file or directory does not exist: {...} 메시지 확인               |
| ALO-INI-004 | redis 연결 실패                            | 에러 메시지 및 redis 설정 정보 확인                                          |
| ALO-INI-005 | 설정 항목중 허용되지 않는 key 또는 value            | 에러 메시지의 해당 key 또는 value 확인                                       |
| ALO-PIP-000 | 동작에 필요한 특정 key 또는 value의 누락            | 오류 메시지의 해당 key 및 value 확인                                        |
| ALO-PIP-001 | git으로부터 contents(.py)를 checkout 할 수 없음 | git.url 확인 및 에러 메시지 확인                                           |
| ALO-PIP-002 | 사용자 contents(.py) 파일을 import 할 수 없음    | 모듈의 폴더 구조 및 파일명 확인                                               |
| ALO-PIP-007 | 동작에 필요한 파일이 없음                         | context['model'][모델명], pipeline['dataset'][파일명] 및 경로 확인          |
| ALO-PIP-009 | Edge App으로부터 수신된 데이터 변환 실패             | 로그 및 에러 메시지 확인                                                   |
| ALO-PIP-010 | 모델 파일을 pickle 저장 실패                    | 모델을 serialization(pickling) 불가함<br/> 사용자가 직접 모델 정보를 파일로 저장하도록 구현 |
| ALO-PIP-011 | summary(score) 파일 생성 실패                | 허용된 값 유형 및 에러 메시지 확인                                             |
| ALO-PIP-012 | 파일 압축 해제 불가                            | 압축 대상 파일 및 디스크 확인                                                |
| ALO-PIP-013 | function.schema 정의에 따른 값 검증 오류         | schema 의 각 인자별 허용 인자 확인                                          |
| ALO-VAL-000 | 설정 항목중 허용되지 않는 key 또는 value            | 에러 메시지의 해당 key 또는 value 확인                                       |
|    (없음)     | 확인되지 않은 오류 유형<br>사용중인 library에서 발생     | 에러 메시지 확인 및 ALO 담당자를 통한 문의                                       |



---
## License
ALO is Free software, and may be redistributed under the terms of specified in the [LICENSE]() file.

