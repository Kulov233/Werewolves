import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // 引入路由
import Antd from 'ant-design-vue';
import store from './store';
import 'ant-design-vue/dist/reset.css';
import TranslatorPlugin from './plugins/translator';


// 导入全局 CSS 文件
import './global.css'
const app = createApp(App)
app.use(TranslatorPlugin);
app.use(store);
app.use(router) // 使用路由
app.use(Antd);
app.mount('#app')
//createApp(App).mount('#app')
