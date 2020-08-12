# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim-buster

# streamlit-specific commands
RUN mkdir -p /root/.streamlit
RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'
RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
" > /root/.streamlit/config.toml'

# exposing default port for streamlit
EXPOSE 8501

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Install pip requirements
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt && \
pip3 install --no-cache-dir torch==1.5.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

WORKDIR /app
ADD . /app

COPY . .

# Switching to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights
USER ROOT

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD streamlit run app_scientific_summarizer.py


