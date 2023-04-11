FROM phidata/python:3.9.12

ARG USER=server
ARG HOME_DIR=${USER_LOCAL_DIR}/${USER}
ENV HOME_DIR=${HOME_DIR}
# Add HOME_DIR to PYTHONPATH
ENV PYTHONPATH="${HOME_DIR}:${PYTHONPATH}"

# Create user and home directory
RUN groupadd -g 61000 ${USER} \
  && useradd -g 61000 -u 61000 -ms /bin/bash -d ${HOME_DIR} ${USER}

# Install build dependencies for duckdb
RUN apt-get update && apt-get install -y build-essential

COPY . ${HOME_DIR}
# Update pip
RUN pip install --upgrade pip
# Install pinned requirements
RUN pip install -r ${HOME_DIR}/requirements.txt
# Install project for the `api` and `app` cli commands
RUN pip install ${HOME_DIR}

USER ${USER}
WORKDIR ${HOME_DIR}

COPY scripts /scripts
ENTRYPOINT ["/scripts/entrypoint.sh"]
CMD ["chill"]
