FROM python:3.11-bookworm

RUN apt-get update && apt-get install -y git iproute2
RUN git clone https://github.com/blueskysolarracing/revolution.git
WORKDIR /revolution
RUN pip install --upgrade pip && pip install -r requirements.txt
ENV REVOLUTION_CONFIGURATIONS_MODULE=configurations

CMD ["python", "-m", "revolution"]
