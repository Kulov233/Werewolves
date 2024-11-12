import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // 引入路由
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/reset.css';
const app = createApp(App)
app.use(router) // 使用路由
app.use(Antd);
app.mount('#app')
//createApp(App).mount('#app')
