FROM phidata/python:3.9.12

ARG USER=app
ARG APP_DIR=${USER_LOCAL_DIR}/${USER}
ENV APP_DIR=${APP_DIR}
# Add APP_DIR to PYTHONPATH
ENV PYTHONPATH="${APP_DIR}:${PYTHONPATH}"

# Create user and home directory
RUN groupadd -g 61000 ${USER} \
  && useradd -g 61000 -u 61000 -ms /bin/bash -d ${APP_DIR} ${USER}

COPY . ${APP_DIR}
# Update pip
RUN pip install --upgrade pip
# Install pinned requirements
RUN pip install -r ${APP_DIR}/requirements.txt
# Install project for the `api` and `app` cli commands
RUN pip install ${APP_DIR}

WORKDIR ${APP_DIR}

COPY scripts /scripts
ENTRYPOINT ["/scripts/entrypoint.sh"]
CMD ["chill"]
