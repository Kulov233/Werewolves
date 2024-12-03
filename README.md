### 智狼之夜  
欢迎来到后端分支。  

项目中的Dockerfile和docker-compose.yml文件只是一个示例，请暂时将mysql和redis的端口暴露到本机，并单独启动后端以进行调试。调试时，请修改redis的默认端口，以防止公网扫描。  

Django的数据库配置在backend/app/settings.py:105-114，redis的配置在backend/app/settings.py:172-215，可以视情况修改。  

完成配置并启动项目时，请使用uvicorn以获得WebSocket支持，并开启Celery以处理任务队列。  
需要额外注意的是，如果在Windows下使用Celery，需要在环境变量中设置`FORKED_BY_MULTIPROCESSING`为`1`。  
在设置好后，可以通过以下指令启动：  
```shell
# 在backend/下
uvicorn app.asgi:application --host 127.0.0.1 --port 8000 --reload
celery -A app worker --loglevel=info
```  
接口文档请见：[接口设计与文档](https://apifox.com/apidoc/shared-78bc5d54-d6f2-4d57-a7de-6950273258d8)