<template>
    <div class="home-page">
      <!-- 顶部导航栏 -->
      <a-layout-header class="header">
  <router-link to="/" class="logo">首页</router-link>
  <router-link to="/help" class="help">帮助</router-link>
  <router-link to="/Profile" class="Profile">个人主页</router-link>
  <img class="profile-pic" src="https://via.placeholder.com/40" alt="头像" />
</a-layout-header>
  
      <!-- 主体内容 -->
      <div class="content">
        <div class="header-row">
          <h3>可用房间</h3>
          <div class="search-bar">
            <a-button type="primary" shape="circle" icon="plus" />
            <a-input
              placeholder="房间名称/ID..."
              v-model="search"
              allow-clear
              @change="onSearch"
            />
            <a-button icon="search" />
          </div>
        </div>
        <div class="room-list">
          <!-- 房间卡片 -->
          <a-card
            v-for="(room, index) in rooms"
            :key="index"
            class="room-card"
            :title="room.title"
          >
            <p>{{ room.description }}</p>
            <div class="room-info">
              <span>{{ room.participants }}/{{ room.capacity }}</span>
              <div class="avatars">
                <img
                  v-for="(avatar, i) in room.avatars"
                  :key="i"
                  class="avatar"
                  :src="avatar"
                  alt="头像"
                />
              </div>
              <a-button type="primary" shape="circle" icon="arrow-right" />
            </div>
          </a-card>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        search: "",
        rooms: [
          {
            title: "房间标题",
            description: "这里是房间简介",
            participants: 5,
            capacity: 8,
            avatars: [
              "https://via.placeholder.com/40",
              "https://via.placeholder.com/40",
              "https://via.placeholder.com/40",
              "https://via.placeholder.com/40",
            ],
          },
          {
            title: "房间标题",
            description: "这里是房间简介",
            participants: 5,
            capacity: 8,
            avatars: [
              "https://via.placeholder.com/40",
              "https://via.placeholder.com/40",
              "https://via.placeholder.com/40",
              "https://via.placeholder.com/40",
            ],
          },
        ],
      };
    },
    methods: {
      onSearch() {
        console.log("Search:", this.search);
        // 添加搜索逻辑
      },
    },
  };
  </script>
  
  <style scoped>
  /* 顶部导航栏 */
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #3b82f6;
    color: #fff;
    padding: 0 20px;
    height: 64px;
  }
  .header .logo {
    font-size: 20px;
    font-weight: bold;
  }
  .header .help {
    margin-right: auto;
    margin-left: 20px;
  }
  .header .profile-pic {
    width: 40px;
    height: 40px;
    border-radius: 50%;
  }
  
  /* 主体内容 */
  .content {
    padding: 20px;
  }
  .header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }
  .search-bar {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .room-list {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
  }
  .room-card {
    width: 250px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  .room-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .avatars {
    display: flex;
    gap: 5px;
  }
  .avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
  }
  </style>
  