FROM python:3.9-alpine

WORKDIR /devel

COPY ./lavoro-matching-coordinator/requirements.txt /devel/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /devel/requirements.txt

RUN apk add curl
RUN apk add bash

RUN curl -sS https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -o /wait-for-it.sh \
    && chmod +x /wait-for-it.sh

# Library
COPY ./lavoro-library/pre_install.sh /devel/pre_install.sh
RUN chmod +x /devel/pre_install.sh
RUN /devel/pre_install.sh

COPY ./lavoro-library/lavoro_library /devel/lavoro_library

COPY ./lavoro-matching-coordinator/lavoro_matching_coordinator /devel/lavoro_matching_coordinator

ENV PYTHONPATH "${PYTHONPATH}:/devel"

ENTRYPOINT ["/wait-for-it.sh", "pgsql:5432", "--timeout=150", "--"]

CMD ["python", "lavoro_matching_coordinator/matching_coordinator_service.py"]

