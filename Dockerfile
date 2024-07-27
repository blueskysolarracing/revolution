FROM python:3.11-alpine

RUN apk update && apk add --no-cache build-base git libffi-dev
RUN git clone https://github.com/blueskysolarracing/revolution.git
WORKDIR /revolution
RUN pip install --upgrade pip && pip install -r requirements.txt
ENV REVOLUTION_CONFIGURATIONS_MODULE=configurations

CMD ["python", "-m", "revolution"]
