FROM python:3.11-alpine
WORKDIR /home/fsub
COPY . ./
RUN pip install -r requirements.txt
CMD ["python", "-m", "fsub"]