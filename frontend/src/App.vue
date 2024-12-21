<template>
  <div id="app">

    <!-- 添加加载状态指示器 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>

    <!-- 修改路由视图处理 -->
    <div :class="['router-view-container', { 'no-padding': $route.path === '/GameInterface' }]">
      <router-view v-slot="{ Component, route }">
        <transition name="fade" mode="out-in">
          <keep-alive :include="cachedViews">
            <component
              :is="Component"
              :key="route.path"
              @activated="handleActivated"
            />
          </keep-alive>
        </transition>
      </router-view>
    </div>
  </div>
</template>


<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: "App",

  setup() {
    const router = useRouter();
    const isLoading = ref(false);
    const cachedViews = ref(['GameLobby', 'GameRoom', 'GameInterface']);

    const navigationRoutes = [
      { path: '/login', label: '登录' },
      { path: '/register', label: '注册' },
      { path: '/GameLobby', label: '大厅' },
      { path: '/GameRoom', label: '房间内部' },
      { path: '/GameInterface', label: '对战房间' },
      { path: '/test', label: '测试页面' },
    ];

    // 检查登录状态
    const checkLoginStatus = () => {
      // 从localStorage获取登录状态
      const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
      //const lastPath = localStorage.getItem('lastPath');

      if (!isLoggedIn) {
        // 未登录时重定向到登录页
        router.replace('/login');
      } //else if (lastPath && lastPath !== '/login' && lastPath !== '/register') {
        //// 已登录且存在上次访问路径时，跳转到上次访问的路径
        //router.replace(lastPath);
      //}
      else {
        // 已登录但没有上次访问路径时，跳转到大厅
        router.replace('/GameLobby');
      }
    };

    // 优化路由加载处理
    router.beforeEach(async (to, from, next) => {
      isLoading.value = true;

      // 保存当前路径（排除登录和注册页面）
      if (to.path !== '/login' && to.path !== '/register') {
        localStorage.setItem('lastPath', to.path);
      }

      // 确保组件加载完成
      if (to.matched.length) {
        try {
          await Promise.all(
            to.matched.map(record => {
              const { component } = record;
              return typeof component === 'function'
                ? component()
                : Promise.resolve(component);
            })
          );
        } catch (error) {
          console.error('路由组件加载失败:', error);
        }
      }
      next();
    });

    router.afterEach(() => {
      setTimeout(() => {
        isLoading.value = false;
      }, 100);
    });

    const handleActivated = () => {
      isLoading.value = false;
    };

    onMounted(() => {
      // 在组件挂载时检查登录状态
      checkLoginStatus();
    });

    return {
      navigationRoutes,
      isLoading,
      cachedViews,
      handleActivated
    };
  }
};
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  position: relative;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #409EFF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.navigation {
  padding: 20px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center;
  gap: 20px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.nav-link {
  color: #606266;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  color: #409EFF;
  background-color: #ecf5ff;
}

.nav-link.active {
  color: #409EFF;
  font-weight: 500;
}

.router-view-container {
  padding-top: 2.5%;
}

.router-view-container.no-padding {
  padding-top: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>