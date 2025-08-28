import os
import sys
import argparse
import shutil

from alo.__version__ import __version__

def __run(args):
    from alo.alo import Alo
    from alo.model import settings, Git
    if args.name:
        settings.name = args.name
    if args.config:
        settings.config = args.config
    if args.system:
        settings.system = args.system
    if args.computing:
        settings.computing = args.computing
    settings.mode = None if args.mode == 'all' else args.mode
    if args.loop:
        settings.computing = 'daemon'
    if args.server:
        settings.computing = 'server'
    if args.port:  # 추가된 부분
        settings.port = args.port  # port로 변경
    if getattr(args, "git.url"):
        settings.git = Git(url=getattr(args, 'git.url'),
                           branch=getattr(args, 'git.branch') if getattr(args, 'git.branch') else 'main')
    if args.log_level:
        settings.log_level = args.log_level
    alo = Alo()
    alo.run()


def __template(args):
    # todo
    print("Coming soon.")

# def __server(args):
#     from alo.api.api_server import run_server
#     run_server(host=args.host, port=args.port, run_function=__run)

def __history(args):
    from alo.alo import Alo
    from alo.model import settings
    if args.config:
        settings.config = args.config
    alo = Alo()
    alo.history(type=args.mode, show_table=True, head=args.head, tail=args.tail)


def __register(args):
    import yaml
    import re

    def check_str_bytes(s, encoding='utf-8', bytes_limit = 5000):
            """ Check if string bytes is under 5000

            Args:
                s: string tobe checked
                encoding: method of string encoding(default: 'utf-8')

            Returns:
                True: bytes < 5000
                False: bytes >= 5000
            """
            byte_length = len(s.encode(encoding))
            if byte_length >= bytes_limit:
                raise ValueError(f"Input exceeds {bytes_limit} bytes limit (current: {byte_length} bytes)")
            return True

    def validate_name(name):
        if not name:  # Empty input is allowed
            return True

        if len(name) > 50:
            raise ValueError("Name must be 50 characters or less")

        # Check for Korean characters
        if any(ord(char) >= 0x3131 and ord(char) <= 0xD7A3 for char in name):
            raise ValueError("Name cannot contain Korean characters")

        # Only allow alphanumeric and hyphen
        if not re.match("^[a-zA-Z0-9-]*$", name):
            raise ValueError("Name can only contain letters, numbers, and hyphens")

        # Check for spaces
        if ' ' in name:
            raise ValueError("Name cannot contain spaces")

        return True

    def read_yaml(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        return data

    def write_yaml(data, file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, default_flow_style=False, allow_unicode=True)

    def update_yaml(data, name=None, overview=None, detail=None):
        # Only update if the input is not empty
        if name and name.strip():  # name이 존재하고 공백이 아닌 경우에만 업데이트
            data['name'] = name
        if overview and overview.strip():  # overview가 존재하고 공백이 아닌 경우에만 업데이트
            data['overview'] = overview
        if detail:  # detail 리스트가 비어있지 않은 경우에만 업데이트
            data['detail'] = detail
        return data

    def copy_file_to_folder(src_file, dest_folder):
    # 복사하려는 파일이 존재하는지 확인합니다.
        if not os.path.isfile(src_file):
            print(f"{src_file} 파일을 찾을 수 없습니다.")
            return

        # 대상 폴더가 존재하지 않으면 생성합니다.
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        # 파일명을 가져와 대상 폴더의 경로를 만듭니다.
        dest_file = os.path.join(dest_folder, os.path.basename(src_file))

        # 파일을 복사합니다.
        shutil.copy2(src_file, dest_file)
        print(f"{src_file} 파일이 {dest_file} 위치로 복사되었습니다.")

    from alo.solution_register import SolutionRegister
    src = os.getcwd()# os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'alo', 'example')
    settings = os.path.join(src, 'setting')
    solution_info = os.path.join(settings, 'solution_info.yaml')
    infra_config = os.path.join(settings, 'infra_config.yaml')

    data = read_yaml(solution_info)

    skip = False
    if args.id != None and args.password != None:
        skip = True
    try:
        if data['ai_conductor_id'] != None and (args.id == None or args.id == ''):
            args.id = data['ai_conductor_id']
            print(f"User id from solution_info :{args.id}")
            skip = True
    except Exception as e:
        print('There is no AIC id information in the setting/solution_info file.')
        if args.id == None or args.id == '':
            while args.id == '' or args.id == None:
                args.id = input("Please enter your AI Conductor ID: ")
            skip = False

    try:
        if data['ai_conductor_pw'] != None and args.password == None:
            args.password = data['ai_conductor_pw']
            print(f"User pw from solution_info : **********")
            skip = True
    except Exception as e:
        print('There is no AIC pw information in the setting/solution_info file.')
        if args.password == None:
            while args.password == '' or args.password == None:
                args.password = input("Please enter your AI Conductor password: ")
            skip = False

    if not skip:
        name = input("Enter the new name (leave empty to keep current): ")
        validate_name(name)
        overview = input("Enter the new overview (leave empty to keep current): ")

        detail = []
        while True:
            add_detail = input("Do you want to add a detail? (If yes, type 'yes'; to skip, press enter): ").strip().lower()
            if add_detail == 'yes':
                content = input("Enter the content for the detail: ")
                check_str_bytes(content)
                title = input("Enter the title for the detail: ")
                check_str_bytes(title)
                detail.append({"content": content, "title": title})
            elif add_detail =='' :
                break
            else :
                raise ValueError("Invalid input! You must type 'yes' or press enter to skip.")
        data = update_yaml(data, name, overview, detail)
        write_yaml(data, solution_info)

        current_settings_dir = os.path.join(os.getcwd(), 'setting')
        os.makedirs(current_settings_dir, exist_ok=True)

    solution_register = SolutionRegister(args.id, args.password)
    solution_register.register()


def __update(args):
    from alo.solution_register import SolutionRegister
    solution_register = SolutionRegister(args.id, args.password)
    solution_register.update()


def __delete(args):
    from alo.solution_register import SolutionRegister
    solution_register = SolutionRegister(args.id, args.password)
    solution_register.delete()


def __example(args):
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'example', args.name)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(os.getcwd(), item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

    print(f"A {args.name} template file has been created in the current path.")
    print("Run alo")

def __docker(args):

    def print_ubuntu_package_instructions():

        instructions = """
        ### 우분투 패키지 설치 안내문 🌈

        안녕하세요! Dockerfile을 통해 우분투 패키지를 설치해보겠습니다. 아래의 단계를 따라 패키지를 추가해보세요:

        1. Dockerfile에서 `apt-get update` 명령을 포함하여 APT 패키지 목록을 업데이트하세요.

        2. `apt-get install` 명령을 사용하여 패키지를 설치하세요. `--no-install-recommends` 옵션을 사용하면 불필요한 의존성을 최소화할 수 있습니다.

        **예제**:
        우분투 패키지 `curl`을 설치하고 싶다면, Dockerfile의 해당 부분에 다음과 같이 추가하세요:

        ```dockerfile
        RUN apt-get update && \\
            apt-get install -y --no-install-recommends \\
            curl \\
            && rm -rf /var/lib/apt/lists/*

        추가된 curl 패키지는 Docker 컨테이너 내에서 사용 가능합니다.
        즐거운 ALO 생활 되세요 🐧
        """

        print(instructions)

    def print_cuda_instructions():

        instructions = """
        ### alo docker --gpu 를 실행한 GPU용 Dockerfile 작성자 용
        ### Docker container cuda와 cudnn 설정에 관한 안내문 🌈

        - CUDA 버전 및 CuDNN 버전을 환경 변수로 정의합니다. tensorflow, torch 버전에 따라
        호환되는 CUDA_VER 및 CUDNN_VER 버전을 작성합니다.
        << 작성 예시 >>
        ## torch >= 2.1.0
        FROM nvidia/cuda:11.8.0-devel-ubuntu22.04
        ARG CUDA_VER=11.8
        ############################################################
        ##  torch <= 2.0.1
        FROM nvidia/cuda:11.7.1-devel-ubuntu22.04
        ARG CUDA_VER=11.7
        ############################################################
        ## tensorflow 2.15
        FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04
        ARG CUDA_VER=12.2
        ############################################################
        ## tensorflow 2.14
        FROM nvidia/cuda:11.8.0-devel-ubuntu22.04
        ARG CUDA_VER=11.8
        ARG CUDNN_VER=8.7.0
        ############################################################
        ## tensorflow 2.12 ~ 2.13
        FROM nvidia/cuda:11.8.0-devel-ubuntu22.04
        ARG CUDA_VER=11.8
        ARG CUDNN_VER=8.6.0
        ############################################################

        가령, torch나 tensorflow 2.15 버전 이상부터는 CUDNN_VER은 미작성합니다.

        - 참고 사항
        CUDA 및 CuDNN 설치는 CUDA 버전과 CuDNN의 호환성을 반드시 확인해야 합니다.
        NVIDIA 사이트에서 버전별 설치 가이드를 참고하면 더욱 정확한 설치가 가능합니다.
        주의사항: 호환성을 잘못 맞추면 예상치 못한 에러가 발생할 수 있습니다.
        도움이 되셨길 바랍니다! 필요에 따라 Dockerfile을 수정하여 나만의 Docker 이미지를 만들어보세요. 🚀 """

        print(instructions)

    subdir = 'dockerfile_gpu' if args.gpu else 'dockerfile_cpu'
    dockerfile_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Dockerfiles', 'register', subdir, 'Dockerfile')
    dockerfile_dest = os.path.join(os.getcwd(), 'Dockerfile')
    print_ubuntu_package_instructions()
    print_cuda_instructions()
    if os.path.exists(dockerfile_src):
        shutil.copy2(dockerfile_src, dockerfile_dest)
        print(f"Dockerfile has been copied to the current path.")
    else:
        print("Error: Dockerfile not found.")

def main():
    if len(sys.argv) > 1:
        if sys.argv[-1] in ['-v', '--version']:
            print(__version__)
            return
        if sys.argv[1] in ['-h', '--help']:
            pass
        elif sys.argv[1] not in ['run', 'history', 'register', 'update', 'delete', 'template', 'example', 'docker', 'server']:  # v1 호환
            sys.argv.insert(1, 'run')
    else:
        sys.argv.insert(1, 'run')

    parser = argparse.ArgumentParser('alo', description='ALO(AI Learning Organizer)')
    parser.add_argument('-v', '--version', action='version', version=__version__)
    subparsers = parser.add_subparsers(dest='command')

    cmd_exec = subparsers.add_parser('run', description='Run alo')
    cmd_exec.add_argument('--name', type=str, help='name of solution')
    cmd_exec.add_argument('--mode', type=str, default='all', choices=['train', 'inference', 'all'], help='ALO mode: train, inference, all')
    cmd_exec.add_argument("--loop", dest='loop', action='store_true', help="On/off infinite loop: True, False")
    cmd_exec.add_argument("--computing", type=str, default="local", choices=['local', 'daemon', 'server'], help="training resource: local, ...")
    cmd_exec.add_argument('--config', type=str, help='path of experimental_plan.yaml')
    cmd_exec.add_argument('--system', type=str, help='path of solution_metadata.yaml')
    cmd_exec.add_argument('--git.url', type=str, help='url of git repository')
    cmd_exec.add_argument('--git.branch', type=str, help='branch name of git repository')
    cmd_exec.add_argument('--log_level', type=str, default="DEBUG", choices=['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR'], help='log level')
    cmd_exec.add_argument("--server", dest='server', action='store_true', help="On/off server mode: True, False")
    cmd_exec.add_argument("--port", type=int, default=8000, help="Port for API server (default: 8000)")

    cmd_history = subparsers.add_parser('history', description='Run history')
    cmd_history.add_argument('--config', type=str, help='path of experimental_plan.yaml')
    cmd_history.add_argument('--mode', default=['train', 'inference'], choices=['train', 'inference'], nargs='+', help='train, inference')
    cmd_history.add_argument("--head", type=int, default=None, help="output the last part of history")
    cmd_history.add_argument("--tail", type=int, default=None, help="output the first part of history")

    cmd_template = subparsers.add_parser('template', description='Create titanic template')

    cmd_register = subparsers.add_parser('register', description='Create new solution')
    cmd_register.add_argument('--id', required=False, help='user id of AI conductor')
    cmd_register.add_argument('--password', required=False, help='user password of AI conductor')

    cmd_update = subparsers.add_parser('update', description='Update a solution')
    cmd_update.add_argument('--id', required=True, help='user id of AI conductor')
    cmd_update.add_argument('--password', required=True, help='user password of AI conductor')

    cmd_delete = subparsers.add_parser('delete', description='Delete a solution')
    cmd_delete.add_argument('--id', required=True, help='user id of AI conductor')
    cmd_delete.add_argument('--password', required=True, help='user password of AI conductor')

    cmd_example = subparsers.add_parser('example', description='Create ALO example')
    cmd_example.add_argument('--name', default='titanic', choices=['titanic'], help='Example of ALO')

    # Add docker command parser
    cmd_docker = subparsers.add_parser('docker', description='Create Dockerfile for ALO')
    cmd_docker.add_argument('--gpu', action='store_true', help='Provide GPU Dockerfile sample')

    # cmd_server = subparsers.add_parser('server', description='Run ALO as API server')
    # cmd_server.add_argument('--port', type=int, default=8000, help='Port for API server')
    # cmd_server.add_argument('--host', type=str, default="0.0.0.0", help='Host for API server')

    args = parser.parse_args()

    commands = {'run': __run,
                'template': __template,
                'history': __history,
                'register': __register,
                'update': __update,
                'delete': __delete,
                'example': __example,
                'docker': __docker,
                # 'server': __server
                }
    commands[args.command](args)
