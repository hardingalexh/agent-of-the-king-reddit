FROM python:3.9-buster
RUN mkdir /code
WORKDIR /code
COPY ./ .
RUN pip install -r requirements.txt
CMD ["python3", "/code/agent-of-the-king.py"]