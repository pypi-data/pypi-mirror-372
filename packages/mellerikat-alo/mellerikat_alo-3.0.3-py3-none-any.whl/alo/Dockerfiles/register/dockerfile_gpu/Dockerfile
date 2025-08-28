## torch >= 2.1.0 
FROM nvidia/cuda:11.8.0-devel-ubuntu22.04
ARG CUDA_VER=11.8
# ############################################################
# ##  torch <= 2.0.1
# FROM nvidia/cuda:11.7.1-devel-ubuntu22.04
# ARG CUDA_VER=11.7
# ############################################################
# ## tensorflow 2.15 
# FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04
# ARG CUDA_VER=12.2
# ############################################################
# ## tensorflow 2.14
# FROM nvidia/cuda:11.8.0-devel-ubuntu22.04
# ARG CUDA_VER=11.8
# ARG CUDNN_VER=8.7.0 
# ############################################################
# ## tensorflow 2.12 ~ 2.13 
# FROM nvidia/cuda:11.8.0-devel-ubuntu22.04
# ARG CUDA_VER=11.8
# ARG CUDNN_VER=8.6.0 
# ############################################################

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    apt-utils \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa
 
# Install Python 3.10 and pip
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3.10-distutils \
    wget \
    build-essential \
    ca-certificates \
    git \
    gcc \
    jq \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libhdf5-dev \
    && wget https://bootstrap.pypa.io/get-pip.py \
    && python3.10 get-pip.py \
    && rm get-pip.py \
    && rm -rf /var/lib/apt/lists/*

RUN if [ ! -z "$CUDA_VER" ] && [ ! -z "$CUDNN_VER" ]; then \
        apt-get update  \

        && apt-get install -y --no-install-recommends libcudnn8=$CUDNN_VER.*-1+cuda$CUDA_VER libcudnn8-dev=$TF_CUDNN_VER.*-1+cuda$CUDA_VER \
        && apt-mark hold libcudnn8 \
        && rm -rf /var/lib/apt/lists/* ; \
    else \
        echo "Skip install libcudnn" ; \
    fi

# Set environment variables for TensorFlow GPU
ENV LD_LIBRARY_PATH /usr/local/cuda-$CUDA_VER/lib64:$LD_LIBRARY_PATH
ENV CUDA_HOME /usr/local/cuda-$CUDA_VER
 
# Specify encoding
ENV LC_ALL=C.UTF-8
 
# Set some environment variables
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
 
ENV PATH="/framework:${PATH}"
 
# Set up the program in the image
COPY /register_source /framework
 
WORKDIR /framework
 
RUN pip3 install --no-cache-dir -r /framework/requirements.txt
RUN if [ -f /framework/solution/requirements.txt ]; then \
        echo "solution requirements.txt exists!" \
        && pip3 install --no-cache-dir -r /framework/solution/requirements.txt ; \
    else \
        echo "solution requirements.txt not exist."; \
    fi

ENV ALO_HOME=/framework/solution

CMD ["python3.10", "main.py"]
