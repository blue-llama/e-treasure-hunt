FROM python:3.9

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt && rm requirements.txt

ENV DEVELOPMENT_SERVER=1
ENV DJ_KEY=ThisIsASecret

EXPOSE 8000
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
