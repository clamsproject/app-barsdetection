FROM jjanzic/docker-python3-opencv

COPY ./ ./app
WORKDIR ./app

## install git
#RUN apk update && apk upgrade && \
#    apk add --no-cache bash git openssh
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["bars_detection.py"]