FROM public.ecr.aws/amazonlinux/amazonlinux:2

ARG CONTAINER_USER_ID=1000
ARG CONTAINER_GROUP_ID=100

ENV SHELL=/bin/bash \
    CONDA_DIR=/opt/conda

# Install the necessary packages
RUN yum update -y \
    && yum install -y python3 pip pip3 jq make wget tar gzip which sudo

RUN yum install shadow-utils.x86_64 -y

# Create a user named vanilla-jl-user with UID 1000 and GID 100
RUN groupmod -n vanilla-jl-user users && \
    useradd -u $CONTAINER_USER_ID -g $CONTAINER_GROUP_ID -d /home/vanilla-jl-user vanilla-jl-user && \
    mkdir -p /home/vanilla-jl-user && \
    chown vanilla-jl-user:vanilla-jl-user /home/vanilla-jl-user

# Set the user to be used when running the container
USER vanilla-jl-user
WORKDIR /home/vanilla-jl-user

# Install PIP stuff necessary for build
RUN pip3 install awscli boto3 jupyterlab

# Set aliases for pip and python to use pip3 and python3
RUN echo "alias pip='pip3'" >> /home/vanilla-jl-user/.bashrc \
    && echo "alias python='python3'" >> /home/vanilla-jl-user/.bashrc

# Add the local bin directory to PATH
ENV PATH="/home/vanilla-jl-user/.local/bin:${PATH}"

# Command to start jupyter lab inside the container
# jupyter lab --allow-root --no-browser  --ip=0.0.0.0