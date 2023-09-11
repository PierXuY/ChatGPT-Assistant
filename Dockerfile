FROM python:3.10

WORKDIR /opt/chatgpt-ai

ADD ./ ./

RUN pip install --no-cache-dir --upgrade -r requirements.txt --timeout 1000

# 下面这条命令，通过nginx做反向代理可以生效
ENTRYPOINT  streamlit run app.py --server.port=8501 --server.enableCORS false --server.enableXsrfProtection false