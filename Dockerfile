FROM python:3.7-alpine
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN pip install pipenv
RUN pipenv --python 3.7 install
ENTRYPOINT ["pipenv", "run", "python", "main.py"]
