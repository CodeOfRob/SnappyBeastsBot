FROM python:3.10-slim

RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

ENV PATH="/.venv/bin:${PATH}"

COPY . .

CMD ["python", "bot.py"]