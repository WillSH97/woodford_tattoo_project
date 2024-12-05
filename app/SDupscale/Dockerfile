FROM python:3.11

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

ARG HF_HOME='~/.cache/huggingface/hub'

ENV HF_HOME=$HF_HOME

COPY  . /app

#janky way of predownloading the karlo files into local cache
RUN python3 jank_buildfile.py

CMD ["uvicorn", "SDUpscale_server:app", "--host", "0.0.0.0", "--port", "1337"]