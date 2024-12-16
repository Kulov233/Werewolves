import { createRouter, createWebHistory } from 'vue-router';

// 路由组件导入
const GameInterface = () => import('../components/GameInterface.vue');
const Login = () => import('@/components/Login.vue');
const Register = () => import('@/components/Register.vue');
const Search = () => import('@/components/GameLobby.vue');
const Room = () => import('@/components/GameRoom.vue');
const test = () => import('@/components/test.vue');
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
    meta: { requiresAuth: false }
  },
  {
    path: '/GameLobby',
    name: 'GameLobby',
    component: Search,
    meta: { requiresAuth: false }
  },
  {
    path: '/test',
    name: 'test',
    component: test,
    meta: { requiresAuth: false }
  },
  {
    path: '/GameRoom/:id?',
    name: 'GameRoom',
    component: Room,
    props: true, // 允许通过 props 传递参数
    meta: { requiresAuth: false }
  }
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

// 路由守卫
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('access_token');
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' });
  } else {
    next();
  }
});

export default router;