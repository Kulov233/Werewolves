FROM python:3.11 AS app

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

COPY . .