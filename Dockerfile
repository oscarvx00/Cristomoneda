FROM python:3.8-slim-buster
WORKDIR /cristo
COPY ./ ./
RUN pip3 install -r requirements.txt
ENTRYPOINT [ "python", "-u", "git.py" ]