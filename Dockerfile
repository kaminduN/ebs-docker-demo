FROM python:2.7

# Add sample application
ADD application.py /tmp/application.py
RUN pip install --no-cache-dir boto3 && mkdir -p /tmp/sample-app/
EXPOSE 8000

# Run it
ENTRYPOINT ["python", "/tmp/application.py"]
