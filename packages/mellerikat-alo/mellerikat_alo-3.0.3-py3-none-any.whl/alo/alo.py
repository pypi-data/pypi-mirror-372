# ----------------------------------------------------------------------
# Copyright (C) 2024, mellerikat. LGE
# ----------------------------------------------------------------------

"""
ALO
"""

import os
import json
import redis
import uuid
import shutil
import pickle
import tarfile
import re
import yaml
# import pkg_resources  # todo deprecated. should be fixed.
import zipfile
import psutil
import glob
import hashlib
import inspect
import socket
from abc import ABCMeta, abstractmethod
from enum import Enum
from copy import deepcopy
from datetime import datetime
from collections import OrderedDict
from pathlib import Path
from functools import wraps
from threading import Thread
from pytz import timezone
import subprocess

from alo.model import settings
from alo.exceptions import AloError, AloErrors
from alo.logger import LOG_PROCESS_FILE_NAME, create_pipline_handler, log_start_finish
from alo.model import load_model, SolutionMetadata, update_storage_credential, EXP_FILE_NAME, copytree
from alo.utils import ResourceProfile, print_copyright, print_table
from alo.__version__ import __version__, COPYRIGHT

import argparse # argparse 추가 (handle_api_request에서 사용하기 위해)
from alo.api.api_server import run_server # run_server import 추가

logger = settings.logger
TRAIN = 'train'
INFERENCE = 'inference'
MODES = [TRAIN, INFERENCE]
LOG_PIPELINE_FILE_NAME = "pipeline.log"
ARTIFACT = 'artifact'
HISTORY_FOLDER_FORMAT = "%Y%m%dT%H%M%S.%f"
HISTORY_PATTERN = re.compile(r'([0-9]{4}[0-9]{2}[0-9]{2}T[0-9]{2}[0-9]{2}[0-9]{2}.[0-9]{6})($|-error$)')
RUN_PIPELINE_NAME = '__pipeline_names__'
RESULT_INFO_FILE = 'result_info.json'


def extract_file(file_paths: list, destination: str):
    """ 지정된 경로에 압축 파일을 해제합니다.

    Args:
        file_paths: 파일 경로 목록
        destination: 압축 해제된 파일을 저장할 경로

    Raises:
        AloErrors: ALO-PIP-012

    """
    for file_path in file_paths:
        try:
            if file_path.lower().endswith(('.tar.gz', '.tgz')):
                with tarfile.open(file_path) as file:
                    file.extractall(os.sep.join(file_path.split(os.sep)[:-1]))
                    logger.debug("[FILE] Extract %s: %s ", file_path, file.getnames())
            elif file_path.lower().endswith('.zip'):
                with zipfile.ZipFile(file_path) as file:
                    file.extractall(os.sep.join(file_path.split(os.sep)[:-1]))
                    logger.debug("[FILE] Extract %s: %s ", file_path, file.namelist())
        except Exception as e:
            raise AloErrors['ALO-PIP-012'](file_path) from e


def tar_dir(_path, _save_path, last_dir):
    """ compress directory as tar.gz

    Args:
        _path       (str): path tobe compressed
        _save_path  (str): tar.gz file save path
        last_dir   (str): last directory for _path

    Returns: -

    """
    tar = tarfile.open(_save_path, 'w:gz')
    for root, dirs, files in os.walk(_path):
        base_dir = root.split(last_dir)[-1] + '/'
        for file_name in files:
            # Arcname: Compress starting not from the absolute path beginning with /home,
            # but from train_artifacts/ or models/
            tar.add(os.path.join(root, file_name), arcname=base_dir + file_name)
    tar.close()


def zip_dir(_path, _save_path):
    """ compress directory as zip

    Args:
        _path       (str): path tobe compressed
        _save_path  (str): zip file save path
        _last_dir   (str): last directory for _path

    Returns: -

    """
    # remove .zip extension
    _save_path = os.path.splitext(_save_path)[0]
    shutil.make_archive(_save_path, 'zip', _path)


def add_logger_handler(func):
    """ 데코레이터 함수

    특정 함수의 로그를 별로도 분리하기 위해 default logger에
    파일 핸들러를 추가 후 자동 제거 합니다.

    Args:
        func    (function): original function

    Returns:
        wrapper (function): wrapped function

    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        _handler = create_pipline_handler(os.path.join(args[2], "log", LOG_PIPELINE_FILE_NAME), logger.level)
        _logger = logger
        _logger.addHandler(_handler)
        try:
            result = func(self, *args, **kwargs)
            return result
        except Exception as e:
            _logger.exception(e)
            raise e
        finally:
            _logger.removeHandler(_handler)
            _handler.close()
    return wrapper


RESOURCE_MESSAGE_FORMAT = "".join(["\033[93m",
                                   "\n------------------------------------ %s < CPU/MEMORY/SUMMARY> Info ------------------------------------",
                                   "\n%s",
                                   "\n%s",
                                   "\n%s",
                                   "\033[0m"])


def profile_resource(func):
    """ cpu/memory profiling decorator

    Args:
        func    (function): original function

    Returns:
        wrapper (function): wrapped function

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not settings.experimental_plan.control.check_resource:
            return func(*args, **kwargs)
        pid = os.getpid()
        ppid = psutil.Process(pid)
        cpu_usage_start = ppid.cpu_percent(interval=None)  # 단순 cpu 사용률
        mem_usage = ResourceProfile(ppid, cpu_usage_start)
        thread = Thread(target=mem_usage.run, daemon=True)
        thread.start()
        result = func(*args, **kwargs)
        mem_usage.enable = False
        cpu, mem = mem_usage.info()
        msg_cpu = "- CPU (min/max/avg) : {:5.1f}% / {:5.1f}% / {:5.1f}%".format(*cpu)
        msg_mem = "- MEM (min/max/avg) : {} / {} / {}".format(*mem)
        pipes = []
        context = args[1]
        stage_name = args[2]
        for pipe_name in context[stage_name][RUN_PIPELINE_NAME]:
            pipes.append(f"{stage_name} - {pipe_name:<15} : "
                         f"Elapsed time ({(context[stage_name][pipe_name]['finishAt'] - context[stage_name][pipe_name]['startAt']).total_seconds():8.3f}) "
                         f"[{context[stage_name][pipe_name]['finishAt'].strftime('%Y-%m-%d %H:%M:%S.%f')}"
                         f" - {context[stage_name][pipe_name]['startAt'].strftime('%Y-%m-%d %H:%M:%S.%f')}]")
        logger.debug(RESOURCE_MESSAGE_FORMAT, stage_name, msg_cpu, msg_mem, "\n".join(pipes))
        return result

    return wrapper


def save_summary(solution_metadata_version: str, file_path: str, result="", score="", note="", probability={}):
    """ Save train_summary.yaml (when summary is also conducted during train) or inference_summary.yaml.
        e.g. self.asset.save_summary(result='OK', score=0.613, note='alo.csv', probability={'OK':0.715, 'NG':0.135, 'NG1':0.15}

    Args:
        solution_metadata_version (str) : version of solution_metadata
        file_path   (str): Path where the file will be saved
        result      (str): Inference result summarized info. (length limit: 25)
        score       (float): model performance score to be used for model retraining (0 ~ 1.0)
        note        (str): optional & additional info. for inference result (length limit: 100) (optional)
        probability (dict): probability per class prediction if the solution is classification problem.  (optional)
                            e.g. {'OK': 0.6, 'NG':0.4}

    Returns:
        summaray_data   (dict): data tobe saved in summary yaml

    """
    result_len_limit = 32
    note_len_limit = 128
    if result is None:
        result = None
    elif not isinstance(result, str) or len(result) > result_len_limit:  # check result length limit 12
        logger.warning("The summary['result'] value must be a str type and the length must be less than %d characters. "
                       "Any characters exceeding the string length are ignored.", result_len_limit)
        result = str(result)[:result_len_limit]
    if score is None:
        score = None
    elif not type(score) in (int, float) or not 0 <= score <= 1.0:  # check score range within 0 ~ 1.0
        logger.warning("The summary['score'] value must be python float or int. Also, the value must be between 0.0 and 1.0. "
                       "Your current score value: %s", score)
        score = 0.0
    if not isinstance(note, str) or len(note) > note_len_limit:  # check note length limit 100
        logger.warning("The summary['note'] value must be a str type and the length must be less than %d characters. "
                       "Any characters exceeding the string length are ignored.", note_len_limit)
        note = str(note)[:note_len_limit]
    if (probability is not None) and (not isinstance(probability, dict)):  # check probability type (dict)
        raise AloErrors['ALO-SMM-001']("The 'probability' property of the pipeline function result summary must be of dict data type.",
                                       doc={'keyType': type(probability).__name__})
    if len(probability.keys()) > 0:  # check type - probability key: string,value: float or int
        prob_sum = 0
        for k, v in probability.items():
            if not isinstance(k, str) or type(v) not in (float, int):
                raise AloErrors['ALO-SMM-002']("The 'probability' dict item in summary can only store key(str):value(int or float) data types.",
                                               doc={'key':k, 'keyType': type(k).__name__, 'value': v, 'valueType': type(v).__name__})
            prob_sum += v
        if round(prob_sum) != 1:  # check probability values sum = 1
            raise AloErrors['ALO-SMM-003']("The sum of the summary probability values must equal 1.0.",
                                           doc={'values': list(probability.values()), 'sumValues':prob_sum})
    else:
        pass
        # FIXME e.g. 0.50001, 0.49999 case?

    # FIXME it is necessary to check whether the sum of the user-entered dict is 1, anticipating a floating-point error
    def make_addup_1(prob):
        # Process the probabilities to sum up to 1, displaying up to two decimal places
        max_value_key = max(prob, key=prob.get)
        proc_prob_dict = dict()
        for k, v in prob.items():
            if k == max_value_key:
                proc_prob_dict[k] = 0
                continue
            proc_prob_dict[k] = round(v, 2)
        proc_prob_dict[max_value_key] = round(1 - sum(proc_prob_dict.values()), 2)
        return proc_prob_dict

    if (probability is not None) and (probability != {}):
        probability = make_addup_1(probability)
    else:
        probability = {}

    if score is not None:
        summary_data = {
            'result': result,
            'score': round(score, 2),
            'date': datetime.now(timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S'),
            'note': note,
            'probability': probability,
            'version': solution_metadata_version
        }
    else:
        summary_data = {
            'result': result,
            'score': score,
            'date': datetime.now(timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S'),
            'note': note,
            'probability': probability,
            'version': solution_metadata_version
        }

    with open(file_path, 'w') as file:
        yaml.dump(summary_data, file, default_flow_style=False)
    logger.debug("[SUMMARY] Successfully saved summary yaml : %s", file_path)

    return summary_data


class WorkspaceDict(dict):
    """workspace 이하의 파일 관리를 위한 객체

    Keys:
        - workspace (str): 작업 경로

    """
    def __init__(self, workspace: str):
        """
        작업 경로 폴더를 생성 후 workspace를 등록합니다.
        Args:
            workspace: 작업 기본 경로
        """
        super().__init__()
        self.update_workspace(workspace)
        Path(self['workspace']).mkdir(exist_ok=True)

    def update_workspace(self, value):
        super().__setitem__('workspace', value)

    def __setitem__(self, key, value):
        """ 신규 키-값 을 추가합니다.

        Args:
            key: 키
            value: 값
        Raises:
            - ALO-CTX-001 : key 데이터 유형이 문자가 아닌 경우
            - ALO-CTX-002 : 시스템 예약어 workspace 속성을 수정하려는 경우
            - ALO-CTX-003 : key 명명 규칙 위반 시

        """
        if not isinstance(key, str):
            raise AloErrors['ALO-CTX-001'](f'"{str(key)}({type(key)})" is not allowed as a key value. The key value must be of type string.',
                                           doc={'key': key, 'type': type(key).__name__})
        if key == 'workspace' and key in self:
            raise AloErrors['ALO-CTX-002']('The word "workspace" is a system reserved word and cannot be update. Change the "workspace" keyword to another name.',
                                           doc={'key': 'workspace'})

        # if not re.match(r'^[ㄱ-힣a-zA-Z0-9 _\-,\.\/]+$', key):
        #     raise AloErrors['ALO-CTX-003']('The key contains an invalid string.',
        #                                    doc={'invalidKey': key, 'allowedRegex': r'^[ㄱ-힣a-zA-Z0-9 _\-,\.\/]+$'})

        if not re.match(r'^[ㄱ-힣a-zA-Z0-9 _\-,\.\/]+$', key):
            logger.warning('The key contains a special symbols.')
                                           #doc={'invalidKey': key, 'allowedRegex': r'^[ㄱ-힣a-zA-Z0-9 _\-,\.\/]+$'})

        super().__setitem__(key, value)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self['workspace']

    def __radd__(self, other):
        return other + str(self)

    def __add__(self, other):
        return str(self) + other


class ArtifactModel(WorkspaceDict):
    """ 학습/추론 작업에 의한 산출물(파일)을 관리하기 위한 객체

    """
    def __init__(self, stage_name: str, stage_workspace: str):
        super().__init__(f"{stage_workspace}{os.sep}output")
        self.__stage_name = stage_name

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

    def validate(self):
        """ 산출물 파일들에 대한 검증

        Raises:
            ALO-ART-001 : 산출물 파일이 없는 경우
            ALO-ART-002 : 2개를 초과하여 파일을 저장한 경우
            ALO-ART-003 : 허용 가능한 파일 확장자가 아닌 경우.
                저장 가능 확장자(csv, jpg, jpeg, png, svg)
        """
        files = [file.lower() for file in os.listdir(self['workspace']) if os.path.isfile(os.path.join(self['workspace'], file))]
        # if self.__stage_name == INFERENCE and not files:
        #     raise AloErrors['ALO-ART-001']("The output file could not be found. In the inference phase, you must create one or two files under the path `pipeline['artifact']['workspace']`.",
        #                                    doc={"stage": self.__stage_name})
        if not files:
            return
        if len(files) > 2:
            raise AloErrors['ALO-ART-002']('You have to save inference output file. The number of output files must be 1 or 2.',
                                           doc={"stage": self.__stage_name, "files": files})
        if not all([file.lower().endswith((".csv", ".jpg", ".jpeg", ".png", ".svg")) for file in files]):
            raise AloErrors['ALO-ART-003']('output file extension must be one of ["csv", "jpg", "jpeg", "png", "svg"].',
                                           doc={"stage": self.__stage_name, "files": files})

class ExtraOutputModel(WorkspaceDict):
    """ 추가 출력물을 관리하기 위한 객체 """
    def __init__(self, stage_workspace: str):
        super().__init__(f"{stage_workspace}{os.sep}extra_output")
        Path(self['workspace']).mkdir(parents=True, exist_ok=True)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

class TrainModel(WorkspaceDict):
    """학습의 모델과 관련된 파일 및 workspace 경로 정보를 관리하기 위한 객체

    workspace이하의 pkl(pickle) 파일을 메모리로 로드 후 해당 객체를 전달한다.

    Keys:
        - workspace (str): 작업 경로

    Raises:
        AloErrors: ALO-PIP-007 (저장된 모델이 없는 경우 예외 발생)

    Examples:
        >>> context['model']['workspace']
           /home/alo/test
        >>> str(context['model'])  # context['model']['workspace'] 와 동일한 값을 리턴함
           /home/alo/test
        >>> context['model']['titanic_model']
           RandomForestClassifier 객체를 리턴함
        >>> context['model']['titanic_model'] = RandomForestClassifier(n_estimators=n_estimators, max_depth=5, random_state=1)
           RandomForestClassifier 객체를 titanic_model 이름으로 파일로 저장됨

    """
    MODEL_FILE_NAME_FORMAT = "{0}.pkl"

    def __init__(self, workspace: str):
        super().__init__(workspace)

    def __getitem__(self, key):
        if key in self:
            return super().get(key)

        file = f"{super().get('workspace')}{os.sep}{self.MODEL_FILE_NAME_FORMAT.format(key)}"
        if not os.path.isfile(file):
            raise AloErrors['ALO-MDL-001'](f'"{key}" cannot be found in context["model"]. Check model name or model_uri',
                                           doc={"key": key, "file": file})

        with open(file, 'rb') as f:
            try:
                self[key] = pickle.load(f)
            except Exception as e:
                raise AloErrors['ALO-MDL-002'](f'Failed to unpickle : {key}',
                                               doc={"key": key, "file": file}) from e
        logger.debug('[MODEL] Load context["model"]["%s"] : %s', key, file)
        return super().get(key)

    def __setitem__(self, key, value):
        try:
            with open(os.path.join(self['workspace'], self.MODEL_FILE_NAME_FORMAT.format(key)), 'wb') as f:
                pickle.dump(value, f)
                super().__setitem__(key, value)
                logger.debug('[MODEL] save context["model"]["%s"] : %s/%s', key, self['workspace'], self.MODEL_FILE_NAME_FORMAT.format(key))
        except Exception as e:
            raise AloErrors['ALO-MDL-003'](f'Failed to save model "{key}".',
                                           doc={"key": key,
                                                "file": os.path.join(self['workspace'], self.MODEL_FILE_NAME_FORMAT.format(key))}) from e

    def __deepcopy__(self, memodict={}):
        return self

    def validate(self, phase: str = None):
        workspace = self['workspace']
        files = [f.lower() for f in os.listdir(workspace) if os.path.isfile(os.path.join(workspace, f))]
        directories = [d.lower() for d in os.listdir(workspace) if os.path.isdir(os.path.join(workspace, d))]

        if phase == TRAIN and not (files or directories):
            raise AloErrors['ALO-MDL-004']("When training, you must save at least one model/config file or directory.",
                                        doc={
                                            "phase": phase,
                                            "files": files,
                                            "directories": directories
                                        })


class Dataset(WorkspaceDict):
    """
    train/inference 시 입력 데이터셋으로 활용할 파일들에 대한 폴더 및 파일 목록

    Keys:
        - workspace (str): 작업 경로
    """

    def __init__(self, stage_name: str, stage_workspace: str):
        super().__init__(f"{stage_workspace}{os.sep}dataset")
        self.__stage_name = stage_name

    def __getitem__(self, key):
        if key not in self:
            raise AloErrors['ALO-DTS-001'](f'"{key}" not exists in pipeline["dataset"]. Check dataset in {self.__stage_name}',
                                           doc={"stage": self.__stage_name, "key": key})
        if key == 'workspace':
            return super().__getitem__(key)
        if not os.path.isfile(f'{self["workspace"]}{os.sep}{key}'):
            raise AloErrors['ALO-DTS-002'](f'"{key}" file cannot be found in {self["workspace"]}.',
                                           doc={"stage": self.__stage_name, "key": key, "file": f'{self["workspace"]}{os.sep}{key}'})
        return super().__getitem__(key)

    def add(self, files: list):
        prefix_len = len(f'{self["workspace"]}{os.sep}')
        for file in files:
            self[file[prefix_len:]] = file

    def __deepcopy__(self, memodict={}):
        return self


class Context(WorkspaceDict):
    """ ALO 수행과 관련된 환경 정보를 담고 있는 객체

    Keys:
        - workspace (str): 작업 경로
        - startAt (datetime): 시작 시각
        - finishAt (datetime): 종료 시각(완료된 후 key 값이 추가됨)

    """
    def __init__(self):
        start_at = datetime.now()
        super().__init__(f"{settings.history_path}{os.sep}{start_at.strftime(HISTORY_FOLDER_FORMAT)}")
        self['startAt'] = start_at
        Path(self['workspace']).mkdir(parents=True, exist_ok=True)
        self['id'] = str(uuid.uuid4())
        self['name'] = settings.name
        self['version'] = settings.version
        self['host'] = settings.host
        self['logger'] = logger
        self['logging'] = {
            'name': 'alo',
            'level': settings.log_level,
        }
        self['model'] = TrainModel(settings.model_artifacts_path)
        self['external'] = WorkspaceDict(f"{self['workspace']}{os.sep}external")
        self['stage'] = None
        self['solution_metadata_version'] = settings.experimental_plan.solution.version

    def __enter__(self):
        return self

    def __getitem__(self, key):
        if key not in self and key in MODES:
            stage_ws = f"{self['workspace']}{os.sep}{key}"
            Path(stage_ws).mkdir(parents=True, exist_ok=True)
            self[key] = {
                'name': key,
                'workspace': stage_ws,
                'logger': self['logger'],
                'model': self['model'],
                'external': self['external'],
                'dataset': Dataset(key, stage_ws),
                ARTIFACT: ArtifactModel(key, stage_ws),
                'extra_output': ExtraOutputModel(stage_ws),  # 추가된 부분
                RUN_PIPELINE_NAME: []
            }
            Path(os.path.join(stage_ws, "score")).mkdir()
        return super().__getitem__(key)

    def __create_result_info(self):
        def order_dict(dictionary: dict):
            return {k: order_dict(v) if isinstance(v, dict) else v for k, v in sorted(dictionary.items())}

        shutil.copy2(settings.experimental_plan.uri, os.path.join(self['workspace'], EXP_FILE_NAME))
        with open(settings.experimental_plan.uri, 'rb') as plan_f, open(os.path.join(self['workspace'], RESULT_INFO_FILE), 'w') as json_f:
            info = {
                'start_time': self['startAt'].isoformat() if self.get('startAt') else None,
                'end_time': self['finishAt'].isoformat() if self.get('finishAt') else None,
                EXP_FILE_NAME: {
                    'modify_date': datetime.fromtimestamp(os.path.getmtime(settings.experimental_plan.uri)).isoformat()
                },
                **{mode: {'start_time': self[mode]['startAt'].isoformat() if self[mode].get('startAt') else None,
                          'end_time': self[mode]['finishAt'].isoformat() if self[mode].get('finishAt') else None,
                          'argument': {pipe: order_dict(self[mode][pipe].get('argument', {})) for pipe in self[mode][RUN_PIPELINE_NAME]}
                          }
                   for mode in MODES if mode in self}
            }
            json.dump(info, json_f)

    def __exit__(self, exc_type, exc_val, exc_tb):
        latest = 'latest'
        if isinstance(exc_val, Exception):
            logger.error("An error occurred: %s", exc_val)
            rename_ws = f"{self['workspace']}-error"
            os.rename(self['workspace'], rename_ws)
            self.update_workspace(rename_ws)
            latest = f'{latest}-error'
            logger.error("Please check the detailed log: %s", rename_ws)
            for stage_name in MODES:
                if stage_name in self:
                    self[stage_name]['workspace'] = f"{self['workspace']}{os.sep}{stage_name}"
        latest_link = os.path.join(settings.history_path, latest)
        if os.path.islink(latest_link):
            os.unlink(latest_link)
        os.symlink(self['workspace'], latest_link)
        self['finishAt'] = datetime.now()
        if settings.experimental_plan.uri:
            self.__create_result_info()

        logger.info('[CONTEXT] Total elapsed second : %.2f', self.elapsed_seconds)
        self.retain_history()

    def retain_history(self):
        paths = settings.experimental_plan.control.backup.retain(settings.history_path)
        logger.debug("[HISTORY] remove old directory : %s", paths)

    @property
    def elapsed_seconds(self):
        return ((self['finishAt'] if self.get('finishAt') else datetime.now()) - self['startAt']).total_seconds()

    def summary(self, phase_name: str):
        phase = self.get(phase_name)
        if not phase:
            return None
        summaries = {}
        for pipe_name in phase.get(RUN_PIPELINE_NAME, []):
            summary = phase.get(pipe_name, {}).get('summary', None)
            if summary:
                summaries[pipe_name] = summary
        if len(summaries) == 1:
            for _, v in summaries.items():
                return v
        return summaries


def _v1_convert_sol_args(stage_name, _args):
    """ - Delete any args in the selected user parameters that have empty values.
        - Convert string type comma splits into a list.

    Args:
        _args   (dict): args tobe converted

    Returns:
        _args   (dict): converted args
    """
    # TODO Should we check the types of user parameters to ensure all selected_user_parameters types are validated?
    if not isinstance(_args, dict):
        raise AloErrors['ALO-PIP-009'](f"selected_user_parameters args. in solution_medata must have << dict >> type : {_args}", pipeline=stage_name)
    if not _args:
        return _args
    # when a multi-selection comes in empty, the key is still sent \
    # e.g. args : { "key" : [] }
    _args_copy = deepcopy(_args)
    for k, v in _args_copy.items():
        # single(multi) selection
        # FIXME Although a dict type might not exist, just in case... \
        # (perhaps if a dict needs to be represented as a str, it might be possible?)
        if isinstance(v, list) or isinstance(v, dict):
            if len(v) == 0:
                del _args[k]
        elif isinstance(v, str):
            if (v is None) or (v == ""):
                del _args[k]
            else:
                # 'a, b' --> ['a', 'b']
                converted_string = [i.strip() for i in v.split(',')]
                if len(converted_string) == 1:
                    # ['a'] --> 'a'
                    _args[k] = converted_string[0]
                elif len(converted_string) > 1:
                    # ['a', 'b']
                    _args[k] = converted_string
                    # int, float
        else:
            if v is None:
                del _args[k]
    return _args


class Computing(metaclass=ABCMeta):
    """ 학습/추론 기능 구현을 위한 추상클래스

    """

    def __init__(self):
        self.experimental_plan = None
        self.solution_metadata = None
        print_copyright(COPYRIGHT)
        self.reload()


    def init(self):
        settings.update()
        self.experimental_plan = settings.experimental_plan
        self.solution_metadata = settings.solution_metadata
        if not self.experimental_plan:
            raise AloErrors['ALO-INI-000']('experimental_plan.yaml information is missing.')

    def install(self):
        source_path = self.checkout_git()
        # self.install_with_uv(source_path)
        # self.install_pip(source_path)
        self.install_with_uv(source_path)
        self.load_module()

    def reload(self):
        """ 환경 설정 정보 및 library 재설정
        """
        self.init()
        self.install()
        self.show_version()

    def run(self):
        try:
            self.solve()
        except Exception as e:
            error = e if isinstance(e, AloError) else AloError(str(e))
            logger.exception(error)
            raise error

    def show_version(self):
        logger.info("\033[96m\n=========================================== Info ==========================================="
                    f"\n- Time (UTC)        : {datetime.now(timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S')}"
                    f"\n- Alo               : {__version__}"
                    f"\n- Solution Name     : {self.experimental_plan.name}"
                    f"\n- Solution Version  : {self.experimental_plan.version}"
                    f"\n- Solution Plan     : {self.experimental_plan.uri}"
                    f"\n- Solution Meta     : {self.solution_metadata.uri if self.solution_metadata else ''}"
                    f"\n- Home Directory    : {settings.home}"
                    "\n============================================================================================\033[0m")

    def load_module(self):
        if self.experimental_plan.solution:
            self.experimental_plan.solution.update_pipeline()

    @abstractmethod
    def solve(self):
        pass

    def exec_stage(self, context, stage_name):
        context['stage'] = stage_name
        pipeline = self.stage(context, stage_name, f'{context["workspace"]}/{stage_name}')
        context['model'].validate(stage_name)
        context[stage_name][ARTIFACT].validate()
        return pipeline

    @add_logger_handler
    @log_start_finish(logger, "{}", highlight=True, args_indexes=[1])
    @profile_resource
    def stage(self, context, stage_name, stage_workspace):
        stage = getattr(self.experimental_plan.solution, stage_name)
        if not stage:
            logger.debug("[PIPELINE] Empty %s info. Skip %s", stage_name, stage_name)
            return
        for pipe_name, function in stage.pipeline.items():
            logger.debug("[PIPELINE] %10s : %15s - %s.%s", stage_name, pipe_name, function.def_.__module__, function.def_.__name__)

        pipeline = context[stage_name]
        dataset_files = stage.get_dataset(pipeline['dataset']['workspace'])
        pipeline['dataset'].add(dataset_files)

        logger.debug('[PIPELINE] List of imported dataset:\n%s', "\n".join(dataset_files))
        extract_file(dataset_files, pipeline['dataset']['workspace'])
        model_files = stage.get_model(context['model']['workspace'])
        logger.debug('[PIPELINE] List of imported model:\n%s', "\n".join(model_files))
        extract_file(model_files, context['model']['workspace'])
        pipeline['startAt'] = datetime.now()

        for i, (pipe_name, function) in enumerate(stage.pipeline.items()):
        # for pipe_name, function in stage.pipeline.items():
            if settings.mode_pipeline and pipe_name not in settings.mode_pipeline:
                logger.warning("[PIPELINE] Skip solution.%s.%s : --mode_pipeline %s", stage_name, pipe_name, settings.mode_pipeline)
                continue
            pipeline[pipe_name] = {
                'startAt': datetime.now(),
                'workspace': pipeline['workspace'],
                ARTIFACT: pipeline[ARTIFACT],
            }
            # Get data files
            is_last_iteration = (i == len(stage.pipeline) - 1)
            self.pipeline(context, pipeline, pipeline[pipe_name], pipe_name, function, is_last_iteration)
            pipeline[pipe_name]['finishAt'] = datetime.now()
            pipeline[RUN_PIPELINE_NAME].append(pipe_name)
        pipeline['finishAt'] = datetime.now()

        return pipeline

    def __get_func_args(self, context, pipeline, handler, handler_kwargs):
        kwargs = handler_kwargs
        if handler.__defaults__ is None:
            kwargs = {}

        args_cnt = handler.__code__.co_argcount - (0 if handler.__defaults__ is None else len(handler.__defaults__))
        if args_cnt == 0:
            return [], kwargs
        elif args_cnt == 1:
            return [pipeline], kwargs
        elif args_cnt == 2:
            return [context, pipeline], kwargs
        else:
            raise AloErrors["ALO-USR-002"]("Invalid arguments of function handler",
                                           doc={"file": inspect.getfile(handler),
                                                "function": f"{handler.__name__}()",
                                                "message": "The number of positional arguments for a function handler cannot exceed two."})

    @log_start_finish(logger, "{} pipline", highlight=False, args_indexes=[3])
    def pipeline(self, context: dict, pipeline: OrderedDict, pipe: dict, name: str, function, is_last_iteration: bool) -> dict:
        func_kwargs = function.get_argument()
        # before
        pipeline[name]['argument'] = func_kwargs
        clone_context = deepcopy(context)
        logger_fn = logger.error
        try:
            args, kwargs = self.__get_func_args(clone_context, clone_context[context['stage']], function.def_, func_kwargs)
            # try:
                # result, responese = function.def_(*args, **kwargs)
                # pass
            # except:
            result = function.def_(*args, **kwargs)

            is_default = False
            # 함수 이름이 train 또는 inference인 경우 summary 키 검증
            # if 'train' in function.def_.__name__ or 'inference' in function.def_.__name__: # train inf가 모두 포함되게 수정
            def make_summary(result, name):
                is_default = False
                if not isinstance(result, dict):
                    logger.warning(
                        "[PIPELINE] '%s' function should return a dict with 'summary' key. Creating default summary.",
                        name # function.def_.__name__
                    )
                    result = {}

                if 'summary' not in result:
                    logger.warning(
                        "[PIPELINE] Missing 'summary' key in '%s' function result. Creating default summary.",
                        name # function.def_.__name__
                    )
                    result['summary'] = {}

                required_summary_keys = {'result', 'note', 'score'}
                missing_keys = required_summary_keys - set(result['summary'].keys())

                if missing_keys:
                    logger.warning(
                        "[PIPELINE] Missing required keys %s in summary dict. Adding default values.",
                        list(missing_keys)
                    )

                    # 누락된 키에 대한 기본값 설정
                    default_values = {
                        'result': None,
                        'note': None,
                        'score': None
                    }

                    # 누락된 키만 기본값으로 채움
                    for key in missing_keys:
                        result['summary'][key] = default_values[key]
                        is_default = True

                return result, is_default

            if self.experimental_plan.api is None:
                result, is_default = make_summary(result, function.def_.__name__)

            context['model'].update(clone_context['model'])
            context['external'].update(clone_context['external'])
            pipeline[name]['result'] = result
            # after
            summary = self.save_output(context, pipeline['name'], pipe, result, is_last_iteration, is_default)
            logger_fn = logger.info
        except AloError as e:
            raise e
        except Exception as e:
            raise AloErrors["ALO-USR-001"](str(e), doc={"file": inspect.getfile(function.def_), "function": f"{function.def_.__name__}()", "message": str(e)}) from e
        finally:
            logger_fn(
                "[PIPELINE] function call info\n"
                "***************************** Invoke Pipline Function *****************************\n"
                "* Target File             : %s\n"
                "* function[name]          : %s\n"
                "* function[name].def      : %s.%s\n"
                "* function[name].argument : %s\n"
                "* summary                 : %s\n"
                "***********************************************************************************",
                inspect.getfile(function.def_), name, function.def_.__module__, function.def_.__name__, func_kwargs, pipe.get('summary', ''))

            #FIXME 여기 어떻게 할지 고민
            # return 'test'

    def checkout_git(self):
        try:
            if self.experimental_plan.solution is None or self.experimental_plan.solution.git is None:
                logger.info('[GIT] "git" property is not set.')
                return
            name = self.experimental_plan.solution.git.url.path.split('/')[-1].split('.')[0]
            path = f"{settings.workspace}/{name}"
            self.experimental_plan.solution.git.checkout(path)
            logger.debug("[GIT] checkout : %s -> %s", self.experimental_plan.solution.git.url, path)
            return path
        except Exception as e:
            raise AloErrors["ALO-PIP-001"](str(e)) from e

    # Add the new install_with_uv function here
    def install_with_uv(self, source_path: str):
        """
        Installs dependencies using uv into a .venv in the ALO home directory.
        """
        try:
            if self.experimental_plan.solution is None or not self.experimental_plan.solution.pip:
                logger.info("[UV] Skip uv install: solution.pip is not configured.")
                return

            venv_path = os.path.join(settings.home, ".venv") ## venv 가 없다면 현재 설정된 가상환경에 uv로 설치
            logger.info(f"[UV] Ensuring virtual environment exists at {venv_path}")

            # Create the virtual environment if it doesn't exist
            # You will need to run this command manually via the terminal or integrate it differently
            # The following line is for demonstration/logging the command, not direct execution:
            # print(f"Command to create venv: uv venv {venv_path}")

            install_args = []
            pip_requirements = self.experimental_plan.solution.pip.requirements

            if pip_requirements is True:
                # Install requirements.txt from the source path
                if source_path is None:
                    source_path = os.path.dirname(self.experimental_plan.uri)
                req_file = os.path.join(source_path, 'requirements.txt')
                if not os.path.exists(req_file):
                    raise AloErrors["ALO-INI-003"](req_file)
                install_args.append(f"-r {req_file}")
            elif isinstance(pip_requirements, list):
                # Install packages or requirement files from the list
                for req in pip_requirements:
                    if isinstance(req, str) and req.endswith('.txt'):
                        # Resolve path for requirement files relative to the plan file directory if needed
                        req_file_path = req
                        # Assuming requirements listed in plan relative to plan file location
                        if not os.path.isabs(req_file_path):
                            plan_dir = os.path.dirname(self.experimental_plan.uri)
                            req_file_path = os.path.join(plan_dir, req)

                        if not os.path.exists(req_file_path):
                            raise AloErrors["ALO-INI-003"](req_file_path)
                        install_args.append(f"-r {req_file_path}")
                    elif isinstance(req, str):
                        # Assume it's a package name or path
                        install_args.append(req)
                    else:
                        logger.warning(f"[UV] Skipping invalid requirement item: {req} (type: {type(req).__name__})")

            if not install_args:
                logger.debug("[UV] No packages or requirements to install.")
                return

            # Construct the uv pip install command targeting the created venv
            # Use --verbose for more detailed output during installation
            uv_executable = os.path.join(venv_path, "bin", "uv") #  POSIX-like path
            command = f"uv pip install --verbose {' '.join(install_args)}"
            logger.info(f"[UV] Running install command: {command}")
            try:
                result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
                logger.info("[UV] Installation command output:\n%s", result.stdout)
                if result.stderr:
                    logger.warning("[UV] Installation command stderr:\n%s", result.stderr)
            except subprocess.CalledProcessError as e:
                logger.error("[UV] Installation command failed with error code %d:\n%s", e.returncode, e.stderr)
                raise AloErrors['ALO-INI-002'](f"UV installation command failed: {e.stderr.strip()}") from e
            except FileNotFoundError:
                 logger.error("[UV] 'uv' command not found. Please ensure uv is installed and in your PATH.")
                 raise AloErrors['ALO-INI-002']("'uv' command not found. Please ensure uv is installed and in your PATH.") from None
            except Exception as e:
                logger.exception("[UV] Unexpected error during subprocess execution.")
                raise AloErrors['ALO-INI-002'](f"Unexpected error during uv installation subprocess: {str(e)}") from e


        except Exception as e:
            logger.exception("[UV] Error during uv installation.")
            # Use ALO-INI-002 for initialization errors, including dependency installation
            raise AloErrors['ALO-INI-002'](f"UV installation failed: {str(e)}") from e

    def install_pip(self, source_path: str):
        try:
            if self.experimental_plan.solution is None or not self.experimental_plan.solution.pip:
                return
            if source_path is None:
                source_path = os.path.dirname(self.experimental_plan.uri)
            req_file = os.path.join(source_path, 'requirements.txt')
            if self.experimental_plan.solution.pip.requirements is True and not os.path.exists(req_file):
                raise AloErrors["ALO-INI-003"](req_file)

            install_packages = []
            if self.experimental_plan.solution.pip.requirements is True:
                install_packages.append(f"-r {req_file}")
            elif isinstance(self.experimental_plan.solution.pip.requirements, list):
                for req in self.experimental_plan.solution.pip.requirements:
                    if req.endswith('.txt'):
                        req_file = os.path.join(os.path.dirname(self.experimental_plan.uri), req)
                        if not os.path.exists(req_file):
                            raise AloErrors["ALO-INI-003"](req_file)
                        req = f"-r {req_file}"
                    install_packages.append(req)
            else:
                logger.debug("[PIP] Skip pip install")
                return

            installed_packages = []
            self.experimental_plan.solution.pip.convert_req_to_list(self.experimental_plan.solution.pip.requirements)
            for package in install_packages:
                try:
                    exists_package = pkg_resources.get_distribution(package)
                    installed_packages.append(package)
                    logger.debug("[PIP] %s already installed: %s", package, exists_package)
                except Exception:
                    logger.debug("[PIP] Start installing package - %s", package)
                    self.experimental_plan.solution.pip.install(package)
                    installed_packages.append(package)
        except Exception as e:
            raise AloErrors['ALO-INI-002'](str(e)) from e

    def save_output(self, context: dict, pipe_name: str, pipe: dict, output, is_last_iteration: bool, is_default: bool):
        if output is None:
            return
        if isinstance(output, dict):
            summary_file_path = os.path.join(pipe['workspace'], "score", f"{pipe_name}_summary.yaml")
            if output.get('summary'):
                if is_last_iteration or is_default: # 마지막 iter이거나 default인 경우 작성
                    if not os.path.exists(summary_file_path): # 이전에 작성한 summary가 있으면 작성하지 않음
                        summary_data = save_summary(context['solution_metadata_version'], summary_file_path, **output.get('summary'))
                if not is_default: # default 가 아닌 경우는 무조건 작성
                    summary_data = save_summary(context['solution_metadata_version'], summary_file_path, **output.get('summary'))
                    pipe['summary'] = summary_data

    def artifact(self, context, stage_name):
        # artifacts control 설정이 있는지 확인하고 False인 경우에만 저장 건너뛰기
        if hasattr(self.experimental_plan.control, 'artifacts') and not self.experimental_plan.control.artifacts:
            logger.info("[ARTIFACT] Artifact saving is disabled in experimental plan")
            return

        stage = getattr(self.experimental_plan.solution, stage_name)
        pipeline = context[stage_name]
        put_files = []

        def filter_compress(info):  # dataset 폴더는 압축 대상에서 제외
            if re.search(r'^[^\/]+\/dataset(\/|$)', info if isinstance(info, str) else info.name):
                return None
            else:
                return info

        if stage_name == TRAIN:
            put_files.extend(stage.put_data(settings.model_artifacts_path, "model"))  # model.tar.gz
        shutil.copy2(os.path.join(settings.log_path, LOG_PROCESS_FILE_NAME), os.path.join(pipeline['workspace'], 'log'))
        put_files.extend(stage.put_data(os.path.join(pipeline['workspace'], "log", LOG_PIPELINE_FILE_NAME), LOG_PIPELINE_FILE_NAME))  # pipeline.log
        put_files.extend(stage.put_data(os.path.join(settings.log_path, LOG_PROCESS_FILE_NAME), LOG_PROCESS_FILE_NAME))  # process.log
        put_files.extend(stage.put_data(pipeline['workspace'], f"{stage_name}_artifacts", filter=filter_compress,
                                        compress_type=None if stage_name == TRAIN else 'zip'))  # train targ.gz, inference zip
        logger.debug('[ARTIFACT] List of artifacts :\n%s', "\n".join(put_files))
        logger.debug("[ARTIFACT] Success save to : %s", stage.artifact_uri)

    def update_experimental_plan(self, stage_name: str):
        # todo overwrite plan.
        # todo Hardcoded.
        # todo Need more generic convention method.
        if not self.solution_metadata:
            logger.info("[YAML] Skip update experimental_plan property:  Empty solution_metadata.")
            return
        source = self.solution_metadata.get_pipeline(stage_name)
        if not source:
            logger.info("[YAML] Skip update experimental_plan property: Empty %s pipeline information in solution_metadata.", stage_name)
            return
        target = getattr(self.experimental_plan.solution, stage_name)
        if not target:
            logger.info("[YAML] Skip update experimental_plan property: Empty %s pipeline information in experimental_plan.", stage_name)
            return

        # update uri, aws credential
        for uri in ['dataset_uri', 'model_uri', 'artifact_uri']:
            source_uri = getattr(source, uri, None)
            if not source_uri:
                setattr(target, uri, [])  # None 인 경우 미동작으로 설정
                continue
            setattr(target, uri, source_uri)
            update_storage_credential(self.experimental_plan.solution.credential, target)

        # update selected_user_parameters
        for func_name, function in target.pipeline.items():
            if not source.parameters or not source.parameters.get_type_args("selected_user_parameters", func_name):
                logger.debug("[YAML] Skip update: pipeline.paramters.[%s] not define in solution_metadata.", func_name)
                continue
            sol_args = _v1_convert_sol_args(stage_name, source.parameters.get_type_args("selected_user_parameters", func_name))
            if sol_args:
                function.update(sol_args)  # 정의되지 않은 속성의 경우 기존 값을 그대로 사용하게 됨 v1 로직 유지

        self.experimental_plan.solution.version = self.solution_metadata.metadata_version


    def history(self, data_id="", param_id="", code_id="", parameter_steps=[], type=MODES, head: int = None, tail: int = None, show_table=False):
        """ Deliver the experiment results stored in history as a table,
            allowing for solution registration by history id.
            After verifying the identity between experimental_plan.yaml in the
            history folder and each id, create a table.

        Args:
            data_id         (str): data id
            param_id        (str): parameters id
            code_id         (str): source code id
            parameter_steps (list): decide which step's parameters to display when creating a table
            type            (str): train or inference (default: [train, inference])
            head            (int): output the first part of history
            tail            (int): output the first part of history

        Returns: -

        """
        if self.experimental_plan is None:
            self.init()
        scores = []

        def make_score(event: str, mode: str, status: str, result_info: dict, summary: dict):
            score = {
                'id': event,
                'status': status,
                'type': mode,
                **result_info.get(mode, {}),
                **{i: summary.get(i, None) for i in ['pipeline_name', 'score', 'result', 'note', 'probability', 'version']},
                'checksum': {**summary.get('checksum', {}),
                             EXP_FILE_NAME: result_info.get('checksum', None)}
            }
            scores.append(score)

        pipeline_type = type if isinstance(type, list) else [type]
        dirs = [(folder, os.path.join(settings.history_path, folder),) for folder in os.listdir(settings.history_path) if not folder.startswith('latest')]
        dirs = sorted(dirs, key=lambda x: x[0])
        dir_size = len(dirs)
        if head:
            dirs = dirs[:head]
        if tail:
            dirs = dirs[-tail:]
        for folder, folder_path in dirs:
            name_group = HISTORY_PATTERN.search(folder)
            if not name_group:
                continue

            result_info_file = os.path.join(folder_path, RESULT_INFO_FILE)
            if not os.path.exists(result_info_file):
                scores.append({'id': name_group[1], 'status': 'error' if name_group[2] else 'success'})
                continue
            with open(result_info_file, 'r') as f, open(os.path.join(folder_path, EXP_FILE_NAME), 'r') as plan_f:
                try:
                    result_info = json.load(f)
                except Exception as e:
                    result_info = {}
                result_info['checksum'] = hashlib.md5(plan_f.read().encode()).hexdigest()[:8]

            for mode in [pipe for pipe in pipeline_type if pipe in MODES]:
                if mode not in result_info:
                    continue
                summary_files = [(os.path.join(folder_path, mode, "score", temp), temp.replace('_summary.yaml', ''))
                                 for temp in os.listdir(os.path.join(folder_path, mode, "score")) if not folder.endswith('_summary.yaml')]
                for file_path, pipeline_name in summary_files:
                    summary = {'pipeline_name': pipeline_name}
                    if os.path.isfile(file_path):
                        try:
                            with open(file_path, 'r') as f:
                                summary = yaml.safe_load(f)
                                summary['pipeline_name'] = pipeline_name
                        except Exception as e:
                            logger.warning("An error occurred while reading the file : %s", file_path)
                    summary['checksum'] = {'argument': hashlib.md5(json.dumps(result_info.get(mode, {}).get('argument', {})).encode()).hexdigest()[:8],
                                           'dataset': {}}
                    len_dir_path = len(os.path.join(folder_path, mode, 'dataset'))
                    for root, _, files in os.walk(os.path.join(folder_path, mode, 'dataset')):
                        for file in files:
                            file_path = os.path.join(root, file)
                            with open(file_path, 'r') as f:
                                summary['checksum']['dataset'][file_path[len_dir_path + 1:]] = hashlib.md5(f.read().encode()).hexdigest()[:8]
                    make_score(name_group[1], mode, 'error' if name_group[2] else 'success', result_info, summary)

        if show_table:
            print_table(scores, **(show_table if isinstance(show_table, dict) else {}))

        return scores


class OneTime(Computing, metaclass=ABCMeta):
    """ 학습/추론 과정을 1회만 수행하는 클래스

    프로그램 종료됨

    """

    def solve(self, phases: list = None):
        if phases is None:
            modes = MODES if settings.mode is None else [settings.mode]
        else:
            modes = phases
        with Context() as context:
            for name in MODES:
                if name not in modes:
                    logger.info("Skip %s()", name)
                    continue
                if not getattr(self.experimental_plan.solution, name):
                    logger.info("Skip solution.%s : Not define in experimental_plan.yaml", name)
                    continue

                try:
                    if name == TRAIN:
                        self.init_train()
                    self.update_experimental_plan(name)
                    self.exec_stage(context, name)
                except Exception as e:
                    self.artifact(context, name)
                    raise e
                else:
                    self.artifact(context, name)

    def init_train(self):
        files = glob.glob(os.path.join(settings.model_artifacts_path, "*"))
        for f in files:
            os.remove(f) if os.path.isfile(f) else shutil.rmtree(f)

    def __update_func_kwargs(self, stage_name: str, argument: dict):
        stage = getattr(self.experimental_plan.solution, stage_name, None)
        if stage is None or argument is None:
            return
        if not isinstance(argument, dict):
            raise ValueError("""train/inference function argument must be dict type. Ex)
{
    'preprocess': {
        'x_columns': [ 'Pclass', 'Sex', 'SibSp', 'Parch' ],
        'y_column': 'Survived',
        'n_estimators': 100
    },
    'train': {
        'x_columns': [ 'Pclass', 'Sex', 'SibSp', 'Parch' ]
    }
}""")
        for k, v in argument.items():
            if k not in stage.pipeline:
                continue
            stage.pipeline[k].update(v)

    def train(self, argument: dict = None):
        self.__update_func_kwargs(TRAIN, argument)
        self.solve([TRAIN])

    def inference(self, argument: dict = None):
        self.__update_func_kwargs(INFERENCE, argument)
        self.solve([INFERENCE])

    def run_inference_api(self, request_data: dict):
        """API 요청을 처리하는 메서드"""
        try:
            # 기존 argument 업데이트
            self.__update_func_kwargs(INFERENCE, request_data.get('argument'))

            # Context 생성 및 inference 실행
            with Context() as context:
                if not getattr(self.experimental_plan.solution, INFERENCE):
                    raise AloErrors['ALO-INI-000']('Inference pipeline not defined in experimental_plan.yaml')

                try:
                    self.update_experimental_plan(INFERENCE)
                    self.exec_stage(context, INFERENCE)
                except Exception as e:
                    self.artifact(context, INFERENCE)
                    raise e
                else:
                    self.artifact(context, INFERENCE)
                    return {
                        "status": "success",
                        "summary": context.summary(INFERENCE),
                        "workspace": context[INFERENCE]['workspace']
                    }
        except Exception as e:
            logger.exception(e)
            error_msg = str(e) if isinstance(e, AloError) else f"Internal server error: {str(e)}"
            raise AloErrors['ALO-API-001'](error_msg)

class Standalone(OneTime):
    pass


class Sagemaker(OneTime):
    pass


class DaemonStatusType(Enum):
    """ 백그라운드 작업 상태 코드

    """
    WAITING = 'waiting'
    SETUP = 'setup'
    LOAD = 'load'
    RUN = 'run'
    SAVE = 'save'
    FAIL = 'fail'

class Server(Computing):
    """
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("Server computing mode initialized.")

    def solve(self):
        """Starts the FastAPI server using uvicorn."""
        logger.info("Attempting to start the ALO API server...")

        def is_port_in_use(port, host='0.0.0.0'):
            """주어진 포트가 사용 중인지 확인"""
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind((host, port))
                    return False
                except socket.error:
                    return True

        def find_available_port(start_port=8000, max_attempts=100):
            """사용 가능한 포트 찾기"""
            import random
            ports = list(range(start_port, 65536))
            random.shuffle(ports)  # 포트 목록을 무작위로 섞음

            for port in ports[:max_attempts]:
                if not is_port_in_use(port):
                    return port

            raise AloErrors['ALO-API-001']("사용 가능한 포트를 찾을 수 없습니다.")

        def validate_port(port):
            """포트 번호 유효성 검사"""
            try:
                port = int(port)
                if port < 1024 or port > 65535:
                    logger.warning(f"포트 번호는 1024에서 65535 사이여야 합니다. 입력된 포트: {port}")
                    return find_available_port(8000)
                return port
            except ValueError:
                logger.warning(f"잘못된 포트 번호입니다. 기본값 8000를 사용합니다.")
                return find_available_port(8000)

        # API 서버 설정 (settings 또는 기본값 사용)
        # settings 객체에 api_host, api_port가 정의되어 있다고 가정
        # API 서버 설정
        api_host = getattr(settings, 'api_host', "0.0.0.0")
        api_port = validate_port(getattr(settings, 'port', 8000))

        # 포트가 이미 사용 중인 경우 새로운 포트 찾기
        if is_port_in_use(api_port):
            original_port = api_port
            # Attempt to find an available port, specifically trying for 8000.
            found_port_after_check = find_available_port(8000)

            if found_port_after_check != 8000:
                # If find_available_port did not return 8000, it's an error.
                logger.error(f"포트 {original_port}가 사용 중이었고, 8000번 포트를 확보하려 했으나 실패했습니다. "
                             f"대신 {found_port_after_check}번 포트가 찾아졌습니다. 8000번 포트만 허용됩니다.")
                raise AloErrors['ALO-API-001'](
                    f"8000번 포트가 필수입니다. 포트 {original_port}는 사용 중이었고, "
                    f"자동으로 찾은 포트 {found_port_after_check}는 8000이 아닙니다."
                )

            # If we reach here, found_port_after_check is 8000.
            api_port = found_port_after_check # Update api_port to the confirmed 8000.

            # Log the successful acquisition of port 8000.
            logger.info(f"포트 {original_port}가 사용 중으로 감지되었으나, 8000번 포트를 성공적으로 확보했습니다.")

        logger.info(f"Configuring API server to run on {api_host}:{api_port}")

        # run_server 함수를 호출하고, API 요청을 처리할 메소드를 전달
        # self.handle_api_request가 '/run' 엔드포인트 호출 시 실행될 함수가 됨
        run_server(host=api_host, port=api_port, run_function=self.handle_api_request)

    def handle_api_request(self, args: argparse.Namespace):
        """
        Handles an individual ALO execution request received via the API.
        This function will be called by the FastAPI endpoint.
        """
        logger.info(f"Handling API request with args: {vars(args)}")
        try:
            # --- 중요 ---
            # API 요청마다 settings를 업데이트해야 할 수 있습니다.
            # args에 따라 experimental_plan 등을 다시 로드해야 할 수도 있습니다.
            # 예시: settings.update_from_namespace(args) 같은 함수 필요 가능성
            # 예시: self.init() # 요청에 따라 재초기화가 필요할 수 있음
            # 이 부분은 ALO의 전반적인 설정 관리 방식에 따라 구현해야 합니다.
            # 현재 코드는 Server 인스턴스 생성 시 로드된 설정을 사용한다고 가정합니다.

            # 요청된 모드 결정
            modes_to_run = MODES if args.mode == "all" or args.mode is None else [args.mode]
            logger.info(f"API Request: Determined modes to run: {modes_to_run}")

            # Context 내에서 실행
            with Context() as context:
                logger.info(f"API Request: Created context {context['id']}")
                pipelines = {}

                for name in MODES:
                    if name not in modes_to_run:
                        continue

                    # 해당 모드의 파이프라인 존재 여부 확인
                    stage_plan = getattr(self.experimental_plan.solution, name, None)
                    if not stage_plan:
                        logger.warning(f"API Request: Skipping solution.{name} - Not defined in plan. Context: {context['id']}")
                        continue

                    logger.info(f"API Request: Starting stage '{name}'. Context: {context['id']}")
                    try:
                        # 학습 모드 특별 처리 (필요시)
                        if name == TRAIN:
                            self.init_train() # 학습 전 모델 경로 정리 등

                        # 실험 계획 업데이트 (API 인자에 따라 달라질 수 있음)
                        self.update_experimental_plan(name)

                        # 스테이지 실행
                        pipeline = self.exec_stage(context, name)
                        # pipeline = self.stage(context, name, f'{context["workspace"]}/{name}')
                        pipelines[name] = pipeline
                        logger.info(f"API Request: Stage '{name}' completed. Context: {context['id']}")

                    except Exception as stage_exc:
                        logger.exception(f"API Request: Error during stage '{name}'. Context: {context['id']}")
                        # 에러 발생 시에도 아티팩트 저장 시도
                        try:
                            self.artifact(context, name)
                        except Exception as artifact_exc:
                            logger.error(f"API Request: Failed to save artifact after error in stage '{name}'. Context: {context['id']}: {artifact_exc}")
                        raise stage_exc # 에러를 다시 발생시켜 FastAPI 핸들러가 처리하도록 함
                    else:
                        # 성공 시 아티팩트 저장
                        self.artifact(context, name)

                logger.info(f"API Request: Execution finished for context {context['id']}")
                # 성공/실패는 FastAPI 핸들러가 HTTP 응답으로 처리
                # 필요시 context.summary(name) 등을 반환하여 API 응답에 포함 가능

                inference_result = None
                if 'inference' in pipelines:
                    inference_result = pipelines['inference']['inference'].get('result')
                return {
                    "status": "success",
                    "inference_result": inference_result,
                    "summary": context.summary('inference'),
                    "context_id": context['id'],
                }

        except Exception as handler_exc:
            logger.exception(f"API Request: Unhandled error in handle_api_request.")
            raise handler_exc # 에러를 다시 발생시켜 FastAPI 핸들러가 처리하도록 함



class Daemon(Computing):
    """ 백그라운드에서 실행되며, redis를 통해 추론 데이터 수신시 작업 수행하는 데몬 클래스

    """
    CHANNEL_STATUS = "alo_status"
    CHANNEL_FAIL = "alo_fail"

    def __init__(self, **kwargs):
        self.__redis_status = None
        self.__redis_pubsub = None
        self.__status = None
        super().__init__(**kwargs)
        error_table_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'redis_error_table.json')
        try:
            with open(error_table_path, 'r', encoding='utf-8') as file:
                self.redis_error_table = json.load(file)
        except FileNotFoundError:
            logger.warning(f"redis_error_table.json not found at {error_table_path}. Using empty error table.")
            self.redis_error_table = {}
        except json.JSONDecodeError:
             logger.warning(f"Failed to decode redis_error_table.json at {error_table_path}. Using empty error table.")
             self.redis_error_table = {}

    def init(self):
        super().init()
        if self.solution_metadata is None:
            raise AloErrors['ALO-INI-000']('solution_meta.yaml information is missing. "--system solution_meta.yaml option" must be specified.')
        try:
            self.__redis_status = self.get_redis(False,
                                                 self.solution_metadata.edgeapp_interface.redis_server_uri.host,
                                                 self.solution_metadata.edgeapp_interface.redis_server_uri.port,
                                                 self.solution_metadata.edgeapp_interface.redis_db_number)
            self.__redis_pubsub = self.get_redis(True,
                                                 self.solution_metadata.edgeapp_interface.redis_server_uri.host,
                                                 self.solution_metadata.edgeapp_interface.redis_server_uri.port,
                                                 self.solution_metadata.edgeapp_interface.redis_db_number)
            logger.debug("Redis Server(DB): %s(%s)",
                         self.solution_metadata.edgeapp_interface.redis_server_uri,
                         self.solution_metadata.edgeapp_interface.redis_db_number)
        except Exception as e:
            raise AloErrors['ALO-INI-004'](str(e)) from e
        self.pubsub_edgeapp('publish', self.CHANNEL_STATUS, "booting")

    def get_redis(self, is_strict, host, port, db_num):
        return (redis.StrictRedis if is_strict else redis.Redis)(host, port, db_num)

    def __send_edgeapp(self, redis, method, *args, **kwargs):
        try:
            result = getattr(redis, method)(*args, **kwargs)
            logger.debug("[REDIS] %s(%s, %s) : %s", method, args, kwargs, result)
            return result
        except Exception as e:
            raise AloErrors['ALO-INI-004'](f"{method}({args},{kwargs})") from e

    def interface_edgeapp(self, method, *args, **kwargs):
        return self.__send_edgeapp(self.__redis_status, method, *args, **kwargs)

    def pubsub_edgeapp(self, method, *args, **kwargs):
        if len(args) >= 2 and args[0] == self.CHANNEL_STATUS:
            self.__status = args[1]
            logger.debug(f"[REDIS] Status changed to: {self.__status}")
        return self.__send_edgeapp(self.__redis_pubsub, method, *args, **kwargs)

    def error_to_code(self, error):
        code = "E000"
        comment = None
        if isinstance(error, AloError):
            # todo
            # error.code == ''
            comment = str(error)

        return {**self.redis_error_table[code], 'COMMENT': comment} if comment else self.redis_error_table[code]

    def publish_alo_style_error(self, error):
        """발생한 예외를 alo 스타일 메시지로 변환하여 alo_fail 채널에 publish"""
        # 기존 error_to_code 로직을 사용하여 기본 에러 정보 가져옴
        # error_to_code는 {"code": "...", "message": "...", "COMMENT": "..."} 형태 반환
        error_info_v2 = self.error_to_code(error)

        # alo 스타일 포맷에 맞게 변환 (ERROR_CODE, ERROR_NAME, COMMENT)
        # error_to_code의 'code' -> alo 스타일 'ERROR_CODE'
        # error_to_code의 'message' -> alo 스타일 'ERROR_NAME' (가장 가까움)
        # error_to_code의 'COMMENT' -> alo 스타일 'COMMENT'
        alo_style_error_msg = {
            "ERROR_CODE": error_info_v2.get("code", "E000"),
            "ERROR_NAME": error_info_v2.get("message", "UnknownError"), # v2의 message를 name으로 사용
            "COMMENT": error_info_v2.get("COMMENT", str(error)) # v2의 COMMENT를 그대로 사용, 없으면 예외 메시지
        }

        logger.debug(f"Publishing alo style failure message to {self.CHANNEL_FAIL}: {json.dumps(alo_style_error_msg)}")
        # pubsub_edgeapp을 사용하여 publish 실행
        self.pubsub_edgeapp("publish", self.CHANNEL_FAIL, json.dumps(alo_style_error_msg))

    def solve(self):
        try:
            self.update_experimental_plan(INFERENCE)
            stage = getattr(self.experimental_plan.solution, INFERENCE)
            model_files = stage.get_model(settings.model_artifacts_path)
            logger.debug('[MODEL] List of imported model:\n%s', "\n".join(model_files))
            extract_file(model_files, settings.model_artifacts_path)
        except Exception as e:
            logger.exception(e)
            self.publish_alo_style_error(e) # publish 추가
            self.interface_edgeapp('rpush', 'inference_summary', json.dumps({'status': 'fail', 'message': str(e)}))
            self.interface_edgeapp('rpush', 'inference_artifacts', json.dumps({'status': 'fail', 'message': str(e)}))
            raise e

        logger.debug('[DAEMON] Get ready.')
        while True:
            try:
                self.pubsub_edgeapp('publish', self.CHANNEL_STATUS, DaemonStatusType.WAITING.value)
                response = self.interface_edgeapp('blpop', "request_inference", timeout=0)
                if response is None:
                    continue

                self.pubsub_edgeapp('publish', self.CHANNEL_STATUS, DaemonStatusType.SETUP.value)

                with Context() as context:
                    try:
                        self.solution_metadata = load_model(json.loads(response[1].decode('utf-8')).get('solution_metadata'), SolutionMetadata)
                        self.update_experimental_plan(INFERENCE)
                        self.pubsub_edgeapp('publish', self.CHANNEL_STATUS, DaemonStatusType.RUN.value)
                        self.pubsub_edgeapp('publish', self.CHANNEL_STATUS, DaemonStatusType.RUN.value)
                        self.exec_stage(context, INFERENCE)
                    except Exception as e:
                        self.artifact(context, INFERENCE)
                        self.publish_alo_style_error(e)
                        # rpush를 통한 실패 상태 저장 (기존 로직 유지)
                        fail_message = {'status': 'fail', 'message': str(e)}
                        self.interface_edgeapp('rpush', 'inference_summary', json.dumps(fail_message))
                        self.interface_edgeapp('rpush', 'inference_artifacts', json.dumps(fail_message))
                        raise e
                    else:
                        summary = json.dumps({'status': 'success', 'message': context.summary(INFERENCE)})
                        self.interface_edgeapp('rpush', 'inference_summary', summary)
                        self.pubsub_edgeapp('publish', self.CHANNEL_STATUS, DaemonStatusType.SAVE.value)
                        self.artifact(context, INFERENCE)
                        self.interface_edgeapp('rpush', 'inference_artifacts', summary)
            except Exception as e:
                logger.exception(e)
                logger.error('[DAEMON] Due to an error, the current step is skipped. Waiting for the next request')

                self.publish_alo_style_error(e)
                # self.pubsub_edgeapp('publish', self.CHANNEL_STATUS, DaemonStatusType.FAIL.value)
                # self.pubsub_edgeapp("publish", self.CHANNEL_FAIL, json.dumps(self.error_to_code(e)))
                fail_message = {'status': 'fail', 'message': str(e)}
                if self.__status == DaemonStatusType.SAVE.value:
                    self.interface_edgeapp('rpush', 'inference_artifacts', json.dumps(fail_message))
                else:
                    self.interface_edgeapp('rpush', 'inference_summary', json.dumps(fail_message))
                    self.interface_edgeapp('rpush', 'inference_artifacts', json.dumps(fail_message))
                # backoff 적용시 현재 위치에 적용


alo_mode = {
    'local': Standalone,
    'standalone': Standalone,
    'sagemaker': Sagemaker,
    'loop': Daemon,
    'batch': Daemon,
    'daemon': Daemon,
    'server': Server,  # API 서버 모드 추가 (Standalone 기반)
}


def Alo():
    """ 실행 옵션에 따른 실행 방식 선택

    Returns: alo 객체

    """
    compute_mode = settings.computing
    alo_class = alo_mode.get(compute_mode)
    if alo_class is None:
        # 유효하지 않은 모드 처리 또는 기본값 설정
        raise ValueError(f"Invalid computing mode: '{compute_mode}'. Available modes: {list(alo_mode.keys())}")
    logger.info(f"Initializing ALO with computing mode '{compute_mode}' using class {alo_class.__name__}")
    return alo_class() # Server() 또는 다른 클래스 인스턴스 반환
    # return alo_mode.get(settings.computing)()
