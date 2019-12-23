FROM python:3.7.6-buster
ADD . /app
ENV PYTHONPATH=/app
RUN pip install -r /app/requirements.txt
ENTRYPOINT ["python", "-m", "ip-checker"]