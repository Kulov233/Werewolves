<template>
  <div id="app">
    <nav class="navigation">
      <router-link 
        v-for="route in navigationRoutes" 
        :key="route.path"
        :to="route.path"
        class="nav-link"
        active-class="active">
        {{ route.label }}
      </router-link>
    </nav>

    <!-- 添加加载状态指示器 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>

    <!-- 修改路由视图处理 -->
    <div class="router-view-container">
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
    // 定义需要缓存的组件名称列表
    const cachedViews = ref(['GameLobby', 'GameRoom', 'GameInterface']);

    const navigationRoutes = [
      { path: '/login', label: '登录' },
      { path: '/register', label: '注册' },
      { path: '/GameLobby', label: '大厅' },
      { path: '/GameRoom', label: '房间内部' },
      { path: '/GameInterface', label: '对战房间' },
      { path: '/test', label: '测试页面' },
    ];

    // 优化路由加载处理
    router.beforeEach(async (to, from, next) => {
      isLoading.value = true;
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
      // 减少延迟时间
      setTimeout(() => {
        isLoading.value = false;
      }, 100);
    });

    // 处理组件激活事件
    const handleActivated = () => {
      isLoading.value = false;
    };

    onMounted(() => {
      // 确保初始路由正确加载
      const currentRoute = router.currentRoute.value;
      if (currentRoute.name) {
        router.replace(currentRoute);
      }
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
  padding-top: 80px;
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