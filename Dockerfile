FROM jjanzic/docker-python3-opencv

COPY ./ ./app
WORKDIR ./app
VOLUME /data

## install git
#RUN apk update && apk upgrade && \
#    apk add --no-cache bash git openssh
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#ENTRYPOINT ["/bin/bash"]

CMD ["python", "run_bt.py", "/data", "/data/output.csv"]
#CMD ["bars_detection.py"]