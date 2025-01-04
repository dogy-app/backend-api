FROM python:3.12

WORKDIR /app

RUN pip install uv

COPY . .

RUN uv install

EXPOSE 8000

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
