ARG ALO_BASE_IMAGE=public.ecr.aws/docker/library/python:3.12.0-slim-bullseye
FROM ${ALO_BASE_IMAGE}

ARG ALO_CUDA_VER
ARG ALO_CUDNN_VER
ARG ALO_PYTHON_VER

RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get install -y --no-install-recommends \
         build-essential \
         wget \
         ca-certificates \
         git \
         gcc \
         jq \
         libgl1-mesa-glx \
         libglib2.0-0 \
         libhdf5-dev \
    && rm -rf /var/lib/apt/lists/*


# install python3.10
RUN if [ ! -z "$ALO_PYTHON_VER" ]; then \
        apt-get update  \
        && apt-get install -y apt-utils software-properties-common  \
        && add-apt-repository ppa:deadsnakes/ppa \
        && apt-get update  \
        && apt-get install -y python${ALO_PYTHON_VER} python${ALO_PYTHON_VER}-dev python${ALO_PYTHON_VER}-distutils  \
        && wget https://bootstrap.pypa.io/get-pip.py  \
        && "python${ALO_PYTHON_VER}" get-pip.py \
        && ln -s /usr/bin/python3 /usr/bin/python \
        && rm get-pip.py  \
        && rm -rf /var/lib/apt/lists/* ; \
    else \
        echo "Skip install python" ; \
    fi


# install cuda
RUN echo "CUDA/CUDNN : $ALO_CUDA_VER / $ALO_CUDNN_VER"
RUN if [ ! -z "$ALO_CUDA_VER" ] && [ ! -z "$ALO_CUDNN_VER" ]; then \
        apt-get update  \
        && CUDA_VER=$(apt list -a "libcudnn8" | grep "${ALO_CUDNN_VER}" | grep "${ALO_CUDA_VER}" | awk '{print $2}') \
        && apt-get install -y --no-install-recommends libcudnn8=$CUDA_VER libcudnn8-dev=$CUDA_VER \
        && apt-mark hold libcudnn8 \
        && rm -rf /var/lib/apt/lists/* ; \
    else \
        echo "Skip install cuda" ; \
    fi

# cuda LD
ENV LD_LIBRARY_PATH "/usr/local/cuda-$ALO_CUDA_VER/lib64:$LD_LIBRARY_PATH"
ENV CUDA_HOME "/usr/local/cuda-$ALO_CUDA_VER"

# Specify encoding
ENV LC_ALL=C.UTF-8

# Set some environment variables
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE

ENV PATH="/framework:${PATH}"

ENV OPENAI_API_KEY=""
ENV LANGCHAIN_TRACING_V2=true
ENV LANGCHAIN_ENDPOINT=""
ENV LANGCHAIN_API_KEY=""
ENV LANGCHAIN_PROJECT=""


# Set up the program in the image
COPY /register_source /framework

WORKDIR /framework

RUN python3 -m venv /framework/.venv
ENV VIRTUAL_ENV=/framework/.venv
ENV PATH="/framework/.venv/bin:$PATH"

# install requirements (기존 pip 대신 uv를 사용하면 더 빠릅니다)
RUN . /framework/.venv/bin/activate && uv pip install --no-cache-dir -r /framework/requirements.txt
RUN if [ -f /framework/solution/requirements.txt ]; then \
      echo "solution requirements.txt exists!" \
      && . /framework/.venv/bin/activate && uv pip install --no-cache-dir -r /framework/solution/requirements.txt ; \
    else \
      echo "solution requirements.txt not exist."; \
    fi

ENV ALO_HOME=/framework/solution

# additional command of user(Do not remove/modify this comment)

CMD ["python", "main.py"]
