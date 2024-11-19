### 智狼之夜  
欢迎来到后端分支。  

项目中的Dockerfile和docker-compose.yml文件只是一个示例，请暂时将mysql和redis的端口暴露到本机，并单独启动后端以进行调试。调试时，请修改redis的默认端口，以防止公网扫描。  

Django的数据库配置backend/app/settings.py中103-112行，redis的配置在backend/app/settings.py中170-207行，可以视情况修改。  

完成配置并启动项目时，请使用uvicorn以获得WebSocket支持。以下是一个示例：  
```shell
# 在backend/下
uvicorn app.asgi:application --host 127.0.0.1 --port 8000 --reload
```  
接口文档请见：[接口设计与文档](https://apifox.com/apidoc/shared-78bc5d54-d6f2-4d57-a7de-6950273258d8)