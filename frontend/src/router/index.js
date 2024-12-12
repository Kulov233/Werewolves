import { createRouter, createWebHistory } from 'vue-router';

// 路由组件导入
const GameInterface = () => import('../components/GameInterface.vue');
const UserProfile = () => import('../components/Profile.vue');
const Login = () => import('@/components/Login.vue');
const Register = () => import('@/components/Register.vue');
const RoomCard = () => import('@/components/RoomCard.vue');
const Search = () => import('@/components/search.vue');
const Room = () => import('@/components/Room.vue');

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: UserProfile,
    meta: { requiresAuth: true }
  },
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
    path: '/room-card',
    name: 'RoomCard',
    component: RoomCard,
    meta: { requiresAuth: false }
  },
  {
    path: '/GameInterface',
    name: 'GameInterface',
    component: GameInterface,
    meta: { requiresAuth: false }
  },
  {
    path: '/search',
    name: 'Search',
    component: Search,
    meta: { requiresAuth: false }
  },
  {
    path: '/room/:id?',
    name: 'room',
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