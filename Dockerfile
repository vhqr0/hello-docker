FROM python:3.11

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
    Flask uWSGI requests redis

COPY app /app
COPY entrypoint.sh /entrypoint.sh
RUN mkdir -p /data

EXPOSE 5000

WORKDIR /
CMD /entrypoint.sh
