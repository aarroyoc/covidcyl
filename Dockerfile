FROM python:3.8.2

WORKDIR /opt/covidcyl

COPY poetry.lock .
COPY pyproject.toml .
RUN pip install poetry
RUN poetry install --no-root

COPY app.py .

CMD ["poetry", "run", "streamlit", "run", "app.py"]