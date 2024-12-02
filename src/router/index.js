import { createRouter, createWebHistory } from 'vue-router'
import GameInterface from '../components/GameInterface.vue'
import UserProfile from '../components/Profile.vue' // 新页面组件
import Login from '@/components/Login.vue'
import Register from '@/components/Register.vue'
import Home from '@/components/Home.vue'
import RoomCard from '@/components/RoomCard.vue'
const routes = [
  { path: '/', name: 'GameInterface', component: GameInterface },
  { path: '/profile', name: 'UserProfile', component: UserProfile }, // 新页面路由
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/Home', name: 'Home', component: Home },
  { path: '/RoomCard', name: 'RoomCard', component: RoomCard },
  { path: '/GameInterface', name: 'GameInterface', component: GameInterface },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router