FROM amazon/aws-lambda-python:3.8
COPY src/. ./
CMD [ "index.lambda_handler" ]