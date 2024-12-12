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
    
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script>

export default {
  name: "App",
  
  setup() {
  
    const navigationRoutes = [
      { path: '/login', label: '登录' },
      { path: '/registre', label: '注册' },
      { path: '/GameLobby', label: '大厅' },
      { path: '/GameRoom', label: '房间内部' },
      { path: '/GameInterface', label: '对战房间' },
      
    ];

    return {
      navigationRoutes
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
}

.navigation {
  padding: 20px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center;
  gap: 20px;
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

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>