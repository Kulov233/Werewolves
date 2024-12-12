<template>
    <div class="home">
      <!-- 顶栏 -->
      <div class="navbar">
        <div class="navbar-item active">首页</div>
        <div class="navbar-item">帮助</div>
        <img class="avatar" src="avatar.png" alt="avatar" />
      </div>
  
      <!-- 搜索区域 -->
      <div class="search-bar">
        <span>可用房间 共 {{ rooms.length }} 个</span>
        <button class="add-room-button">+</button>
        <input v-model="search" placeholder="房间名称/ID..." />
        <button class="search-button">🔍</button>
      </div>
  
      <!-- 房间列表 -->
      <div class="room-list">
        <div v-for="room in filteredRooms" :key="room.id" class="room-card">
          <div class="room-header">
            <h3>{{ room.title }}</h3>
            <span>{{ room.currentUsers }} / {{ room.maxUsers }}</span>
          </div>
          <p class="room-description">{{ room.description }}</p>
          <div class="room-footer">
            <div class="user-avatars">
              <img v-for="user in room.users" :key="user.id" :src="user.avatar" alt="user avatar" />
            </div>
            <button class="enter-button">→</button>
          </div>
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
            id: 1,
            title: "房间标题",
            description: "这里是房间简介",
            currentUsers: 5,
            maxUsers: 8,
            users: [
              { id: 1, avatar: "avatar1.png" },
              { id: 2, avatar: "avatar2.png" },
              { id: 3, avatar: "avatar3.png" },
              { id: 4, avatar: "avatar4.png" },
            ],
          },
          // 添加更多房间数据
        ],
      };
    },
    computed: {
      filteredRooms() {
        return this.rooms.filter(room => 
          room.title.includes(this.search) || room.id.toString().includes(this.search)
        );
      },
    },
  };
  </script>
  
  <style scoped>
  /* 顶栏样式 */
  .navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #2196f3;
    color: white;
    padding: 10px;
  }
  .navbar-item {
    padding: 0 20px;
    cursor: pointer;
  }
  .navbar-item.active {
    border-bottom: 2px solid white;
  }
  .avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
  }
  
  /* 搜索栏样式 */
  .search-bar {
    display: flex;
    align-items: center;
    margin: 10px 0;
    padding: 10px;
  }
  .add-room-button,
  .search-button {
    background-color: #2196f3;
    color: white;
    border: none;
    padding: 5px 10px;
    border-radius: 50%;
    cursor: pointer;
  }
  input {
    margin: 0 10px;
    padding: 5px;
    flex-grow: 1;
  }
  
  /* 房间列表样式 */
  .room-list {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }
  .room-card {
    width: 200px;
    background: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
  }
  .room-header {
    display: flex;
    justify-content: space-between;
    font-size: 16px;
    font-weight: bold;
  }
  .room-description {
    color: gray;
    margin: 5px 0;
  }
  .room-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .user-avatars img {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    margin-right: 5px;
  }
  .enter-button {
    background-color: #2196f3;
    color: white;
    border: none;
    padding: 5px;
    border-radius: 50%;
    cursor: pointer;
  }
  </style>
  