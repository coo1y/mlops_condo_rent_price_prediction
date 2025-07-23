FROM public.ecr.aws/lambda/python:3.10

RUN pip install -U pip
RUN pip install pipenv

COPY ["Pipfile", "Pipfile.lock", "./"]
RUN pipenv install --system --deploy

COPY ["inference/app.py", "inference/predictor.py", "./"]
COPY ["model/", "utils/", "./"]

CMD [ "app.handler" ]
