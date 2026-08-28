FROM mcr.microsoft.com/playwright/python:v1.62.0-noble

WORKDIR /app

RUN pip install --no-cache-dir requests playwright

COPY solution.py .

CMD ["python", "solution_1.py"]