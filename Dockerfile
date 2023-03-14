FROM python:3.11

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
    Flask uWSGI requests redis

COPY app /app
COPY entrypoint.sh /entrypoint.sh

WORKDIR /app
USER www-data
EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
