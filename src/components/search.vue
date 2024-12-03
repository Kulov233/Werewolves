<template>
    <div class="main-page">
      <!-- 顶部导航栏 -->
      <header class="header">
        <button class="menu-btn" @click="toggleSidebar">☰</button>
        <div class="search-bar">
          <input type="text" v-model="searchQuery" placeholder="搜索房间" />
          <button @click="searchRoom">🔍</button>
        </div>
        <div class="header-actions">
          <button @click="inviteFriend">好友列表</button>
          <button @click="friendRecord">历史记录</button>
        </div>
      </header>
  
      <!-- 主体内容 -->
      <main class="content">
        <!-- 房间列表 -->
  <section class="room-list">
    <h2>房间列表</h2>
    <div class="room-cards">
      <div class="room-card" v-for="room in filteredRooms" :key="room.id">
        <h3>{{ room.name }}</h3>
        <p>房间类型: {{ room.type }}</p>
        <p>人数: {{ room.currentPeople }}/{{ room.maxPeople }}</p>
        <button @click="joinRoom(room.id)">加入房间</button>
      </div>
    </div>
  </section>
  
        <!-- 创建房间 -->
        <section class="create-room">
            <div class="search-bar">
          <input type="text" v-model="searchQuery" placeholder="搜索房间" />
          <button @click="searchRoom">🔍</button>
        </div>
        <!-- 添加下拉框 -->
  <div class="select-people">
    <label for="peopleCount">选择人数：</label>
    <select id="peopleCount" v-model="selectedPeopleCount">
      <option v-for="count in peopleOptions" :key="count" :value="count">
        {{ count }} <!--人-->
      </option>
    </select>
  </div>
          <!--<h2>创建房间</h2>-->
          <div>
            <label>
              <input type="radio" value="AI" v-model="roomType" />
              有AI
            </label>
            <label>
              <input type="radio" value="NoAI" v-model="roomType" />
              无AI
            </label>
          </div>
          <button @click="quickMatch">快速匹配</button>
          <button @click="createRoom">创建房间</button>
        </section>
      </main>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        searchQuery: "", // 搜索输入
        roomType: "NoAI", // 房间类型（默认无AI）
        filteredRooms: [
        { id: 1, name: "房间1", type: "有AI", currentPeople: 2, maxPeople: 6 },
        { id: 2, name: "房间2", type: "无AI", currentPeople: 4, maxPeople: 10 },
        { id: 3, name: "房间3", type: "有AI", currentPeople: 1, maxPeople: 4 },
      ],
        selectedPeopleCount: 2, // 默认选中2人
      peopleOptions: [2,3, 4,5, 6,7, 8,9, 10,11,12,13,14,15,16,17,18,19,20,21,22,23,24], // 可选人数列表
      };
    },
    computed: {
      // 根据搜索过滤房间列表
      //filteredRooms() {
      //  return this.rooms.filter((room) =>
      //    room.name.includes(this.searchQuery)
      //  );
     // },
    },
    methods: {
        
      toggleSidebar() {
        alert("展开侧边栏功能！");
      },
      searchRoom() {
        alert(`搜索房间：${this.searchQuery}`);
      },
      inviteFriend() {
        alert("好友邀请功能！");
      },
      friendRecord() {
        alert("好友记录功能！");
      },
      quickMatch() {
        alert(`快速匹配：${this.roomType}`);
      },
      createRoom() {
        alert(`创建房间：${this.roomType}`);
      },
      joinRoom(roomId) {
      alert(`加入房间 ID: ${roomId}`);
    },
    },
  };
  </script>
  
  <style scoped>
  .main-page {
    display: flex;
    flex-direction: column;
    height: 100vh;
  }
  
  /* 顶部导航栏样式 */
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #f5f5f5;
    padding: 10px;
    border-bottom: 1px solid #ccc;
  }
  
  .menu-btn {
    font-size: 20px;
    border: none;
    background: none;
    cursor: pointer;
  }
  
  .search-bar {
    display: flex;
    align-items: center;
  }
  
  .search-bar input {
    padding: 5px;
    font-size: 14px;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
  
  .search-bar button {
    margin-left: 5px;
    background-color: #007bff;
    color: white;
    border: none;
    padding: 5px 10px;
    cursor: pointer;
  }
  
  .header-actions button {
    margin-left: 10px;
    background-color: #007bff;
    color: white;
    border: none;
    padding: 5px 10px;
    cursor: pointer;
  }
  
  /* 主体内容样式 */
  .content {
    display: flex;
    flex: 1;
    padding: 10px;
    gap: 20px;
  }
  
  /* 房间列表样式 */
  .room-list {
    flex: 1;
    background-color: #f9f9f9;
    padding: 10px;
    border-radius: 5px;
    border: 1px solid #ccc;
  }
  
  .room-list ul {
    list-style: none;
    padding: 0;
  }
  
  .room-list li {
    padding: 5px;
    border-bottom: 1px solid #eee;
  }
  
  /* 创建房间样式 */
  .create-room {
    flex: 1;
    background-color: #f9f9f9;
    padding: 10px;
    border-radius: 5px;
    border: 1px solid #ccc;
  }
  
  .create-room div {
    margin-bottom: 10px;
  }
  
  .create-room button {
    margin-right: 10px;
    background-color: #007bff;
    color: white;
    border: none;
    padding: 5px 10px;
    cursor: pointer;
  }
  .select-people {
  margin: 10px 0;
}

.select-people select {
  padding: 5px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.room-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 16px;
}

.room-card {
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  width: 200px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.room-card h3 {
  margin: 0 0 8px;
  font-size: 18px;
}

.room-card p {
  margin: 4px 0;
  color: #555;
}

.room-card button {
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  margin-top: 8px;
  font-size: 14px;
}

.room-card button:hover {
  background-color: #0056b3;
}
  </style>
  