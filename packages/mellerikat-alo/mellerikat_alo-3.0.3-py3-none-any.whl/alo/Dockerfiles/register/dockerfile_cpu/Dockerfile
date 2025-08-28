ARG ALO_BASE_IMAGE=public.ecr.aws/docker/library/python:3.12.0-slim-bullseye
FROM ${ALO_BASE_IMAGE}

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

# Specify encoding
ENV LC_ALL=C.UTF-8

# Set some environment variables
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE

ENV PATH="/framework:${PATH}"

# Set up the program in the image
COPY /register_source /framework

WORKDIR /framework

RUN pip3 install uv

# Create and activate a virtual environment
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