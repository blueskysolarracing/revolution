FROM python:3.13.5-bookworm

RUN echo 'Acquire::AllowInsecureRepositories "true";' > /etc/apt/apt.conf.d/99insecure && \
    echo 'Acquire::AllowDowngradeToInsecureRepositories "true";' >> /etc/apt/apt.conf.d/99insecure && \
    echo 'APT::Get::AllowUnauthenticated "true";' >> /etc/apt/apt.conf.d/99insecure && \
    apt-get update || true

RUN apt-get update && apt-get install -y git iproute2 vim
RUN git clone https://github.com/blueskysolarracing/revolution.git
WORKDIR /revolution
RUN pip install --upgrade pip && pip install -r requirements.txt
ENV REVOLUTION_CONFIGURATIONS_MODULE=configurations

CMD ["python", "-m", "revolution"]
