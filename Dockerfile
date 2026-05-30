FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY stock_checker.py .
COPY mcp_server.py .

ARG GIT_REV=unknown
RUN echo "${GIT_REV} Build: $(date -u +'%Y-%m-%d %H:%M:%S %Z')" > version.txt

EXPOSE 8000

ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

CMD ["python3", "mcp_server.py"]
