#!/bin/bash

# 构建镜像
docker build -t coughoverflow-app .

# 启动容器，映射端口：容器 6400 -> 本地 8080
docker run -d -p 8080:8080 --name coughoverflow-container coughoverflow-app