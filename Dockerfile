FROM python:3.8.2

WORKDIR /opt/covidcyl

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .
COPY coronavirus.csv .

CMD ["streamlit", "run", "app.py"]