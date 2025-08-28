FROM python

WORKDIR /ositah

ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt update
RUN apt upgrade -qy
RUN apt install -qy libsasl2-dev python-dev libldap2-dev libssl-dev

RUN python -c 'from urllib.request import urlopen; print(urlopen("https://install.python-poetry.org").read().decode())' | python -

COPY ./pyproject-poetry.toml ./pyproject.toml

# Ensure to get latest ositah version
RUN poetry add ositah@latest

RUN poetry install --no-interaction --no-ansi -vvv
