import { createRouter, createWebHistory } from 'vue-router';

// 路由组件导入
import GameInterface from '../components/GameInterface.vue';
import Login from '@/components/Login.vue';
import Register from '@/components/Register.vue';
import GameLobby from '@/components/GameLobby.vue';
import Room from '@/components/GameRoom.vue';
// 路由配置
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAuth: false }
  },
  {
    path: '/GameInterface',
    name: 'GameInterface',
    component: GameInterface,
    meta: { requiresAuth: true }
  },
  {
    path: '/GameLobby',
    name: 'GameLobby',
    component: GameLobby,
    meta: { requiresAuth: true }
  },
  {
    path: '/GameRoom/:id?',
    name: 'GameRoom',
    component: Room,
    props: true, // 允许通过 props 传递参数
    meta: { requiresAuth: true }
  }
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

// 添加路由解析守卫
router.beforeResolve(async (to, from, next) => {
  try {
    // 确保异步组件已加载
    if (to.matched.length) {
      await Promise.all(
        to.matched.map(record => {
          const { component } = record;
          if (typeof component === 'function') {
            return component();
          }
          return Promise.resolve();
        })
      );
    }
    next();
  } catch (error) {
    next(false);
  }
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('access_token');

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' });
  } else {
    next();
  }
});


export default router;