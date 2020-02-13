FROM python:3.7-slim

ENV API_URL="https://kubernetes.default.svc"
ENV NAMESPACE="test"
ENV MAX_DAYS="5"
ENV POD_STATUS="Succeeded, Failed"
ENV TOKEN=""
ENV DEBUG="WARN"

ENV PYTHONUNBUFFERED=0

WORKDIR /app
COPY clean.py ./

RUN pip install --no-cache-dir requests

CMD ["python", "clean.py"]