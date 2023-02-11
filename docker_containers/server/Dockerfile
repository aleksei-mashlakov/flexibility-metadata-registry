FROM frolvlad/alpine-miniconda3

COPY ./docker_containers/server/app /app
ADD ./logs /app/logs
ADD ./platform /app/platform
ADD ./config /app/config
ADD ./docker_containers/server/app/run_server.py /app/platform/run_server.py

RUN conda update conda
RUN conda env create -f app/conda_env.yml && conda clean -afy
RUN echo "source activate ioe" > ~/.bashrc
ENV PATH /opt/conda/envs/ioe/bin:$PATH

WORKDIR /app

ENTRYPOINT ["python", "/app/platform/run_server.py"]
