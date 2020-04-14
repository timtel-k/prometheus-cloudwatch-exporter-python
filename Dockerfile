FROM python:3.6-alpine

COPY src/* /home/app/
RUN adduser -D -h /home/app app && pip install -r /home/app/requirements.txt

WORKDIR /home/app
ENV PYTHONPATH '/home/app/'
EXPOSE 9106

USER app

CMD [ "python", "jbt-athena-exporter.py"]
