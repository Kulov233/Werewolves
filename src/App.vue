<template>
    <div id="app">
		<router-view />
      <!-- 使用 GameInterface 组件 -->
      <GameInterface />
      <nav>
      
      <router-link to="/profile">UserProfile</router-link>
      <router-link to="/login">Login</router-link>
      <router-link to="/register">Register</router-link>
    </nav>
    <!-- 显示当前路由对应的页面内容 -->
    <router-view></router-view>
    </div>
  </template>
  
  <script>
  // 引入 GameInterface 组件
  import GameInterface from "./components/GameInterface.vue";
  
  export default {
    name: "App",
    components: {
      GameInterface // 注册 GameInterface 组件
    }
  };
  </script>
  
  <style>
  /* 可选的样式 */
  #app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    text-align: center;
    color: #2c3e50;
    margin-top: 20px;
  }
  </style>