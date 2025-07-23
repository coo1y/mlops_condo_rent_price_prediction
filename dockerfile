FROM public.ecr.aws/lambda/python:3.10
# FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.10

RUN pip install -U pip
RUN pip install pipenv

COPY ["Pipfile", "Pipfile.lock", "./"]
RUN pipenv install --system --deploy

COPY ["inference/app.py", "inference/predictor.py", "./"]

RUN mkdir model
COPY ["inference/model", "./model"]

RUN mkdir utils
COPY ["inference/utils", "./utils"]

CMD [ "app.handler" ]
