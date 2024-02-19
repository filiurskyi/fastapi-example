FROM python:3.11-slim

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY .. .

#VOLUME $APP_HOME/storage

EXPOSE 8001

#RUN alembic revision --autogenerate -m "init"
#RUN alembic upgrade head

#ENTRYPOINT ["uvicorn", "main:app", "--port=8001", "--host=0.0.0.0"]

RUN chmod +x start.sh
ENTRYPOINT ["./start.sh"]