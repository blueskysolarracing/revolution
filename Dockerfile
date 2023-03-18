FROM --platform=linux/arm64 python:3.10

RUN pip install --upgrade pip \
	&& pip install blueskysolarracing-revolution==0.0.0.dev0

CMD ["python3", "-m", "revolution"]
