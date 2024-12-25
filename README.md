## 智狼之夜  

请完成backend/docker-compose.yml中的TODO；修改backend/.env.example中的内容，并将其重命名为.env；此外，还需要在backend/game/ai/keys.py中配置AI Key。所给的Key需要有智谱GLM 4 Plus的token余额。如果Key不正确，AI将无法正常工作。  
配置完后，请在frontend目录下运行```npm install```，然后运行```npm run build```即可编译前端服务。编译完后，将生成的dist目录复制到backend目录下。  
完成以上操作后，在backend目录下运行```docker compose up -d --build```即可启动服务。