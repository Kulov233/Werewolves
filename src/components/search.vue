<template>
  
    <div class="main-page" @click="closeALL" >
      <!-- 顶部菜单栏 -->
      <div class="top-bar">
        <button class="icon-button left" @click.stop="toggleSidebar('menu')">
          <img class="icon" src="@/assets/menu.svg" alt="Menu" />
        </button>
        <!-- 右侧按钮组 -->
        <div class="right-buttons">
          <button class="icon-button" @click.stop="toggleSidebar('friends')">
            <img class="icon" src="@/assets/friends.svg" alt="Friends" />
          </button>
          <button class="icon-button" @click.stop="toggleSidebar('history')">
            <img class="icon" src="@/assets/history.svg" alt="History" />
          </button>
        </div>
      </div>

      <!-- 左侧滑出菜单 -->
      <transition name="slide-left">
        <div v-if="showMenuSidebar" class="sidebar menu-sidebar" @click.stop>
          <div class="sidebar-content">
            <h3>菜单内容</h3>
            <p>这里是一些内容。</p>
            <button @click="toggleSidebar('menu')">关闭</button>
          </div>
        </div>
      </transition>

      <!-- 右侧滑出菜单 Friends -->
      <transition name="slide-right">
        <div v-if="showFriendsSidebar" class="sidebar friends-sidebar" @click.stop>
          <div class="sidebar-content">
            <h3>朋友列表</h3>
            <p>这里显示朋友的信息。</p>
            <button @click="toggleSidebar('friends')">关闭</button>
          </div>
        </div>
      </transition>

      <!-- 右侧滑出菜单 History -->
      <transition name="slide-right">
        <div v-if="showHistorySidebar" class="sidebar history-sidebar" @click.stop>
          <div class="sidebar-content">
            <h3>历史记录</h3>
            <p>这里显示历史记录信息。</p>
            <button @click="toggleSidebar('history')">关闭</button>
          </div>
        </div>
      </transition>
  
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
              <button class="join-button" @click.stop="joinRoom(room.id)">加入房间</button>
            </div>
          </div>
        </section>
    
          <!-- 创建房间 -->
        <section class="create-room">
          <h2>创建房间</h2>
          <div class="search-bar" @click="handleBarClick">
            <!-- 左侧 search.svg 组件 -->
            <div class="search-icon" v-show="showSearchIcon">
              <img src="@/assets/search.svg" alt="Search" />
            </div>

            <!-- 中间输入框 -->
            <input
              type="text"
              v-model="searchQuery"
              @focus="onFocus"
              @blur="onBlur"
              placeholder="搜索房间"
              ref="inputBox"

            />

            <!-- 删除按钮和分隔符 -->
            <div v-if="searchQuery.length > 0" class="clear-container">
              <button class="clear-button" @click="clearSearch" title="清空输入">
                <img src="@/assets/clear.svg" alt="Clear" />
              </button>
              <div class="separator"></div>
            </div>

            <!-- 右侧搜索按钮 -->
            <button class="search-button" @click="searchRoom" title="点击搜索">
              <img src="@/assets/search.svg" alt="Search" />
            </button>

            <!-- 历史搜索（点击输入框时显示） -->
            <div v-show="showHistory && searchQuery.length === 0" class="history">
              <ul>
                <li v-for="item in history" :key="item" @click="selectHistory(item)">
                  {{ item }}
                </li>
              </ul>
            </div>
          </div>
          
          <!-- 添加下拉框 -->
          <div class="select-people">
            <label for="peopleCount">选择人数：</label>
            <select id="peopleCount" v-model="selectedPeopleCount">
              <option v-for="count in peopleOptions" :key="count" :value="count">
                {{ count }} 人
              </option>
            </select>
          </div>
          <div class="room-type">
            <label>
              <input type="radio" value="AI" v-model="roomType" />
              有AI
            </label>
            <label>
              <input type="radio" value="NoAI" v-model="roomType" />
              无AI
            </label>
          </div>
          <div class="action-buttons">
            <button class="quick-match-button" @click="quickMatch">快速匹配</button>
            <button class="create-room-button" @click="createRoom">创建房间</button>
          </div>
        </section>
      </main>
    </div>
</template>
  
<script>
export default {
  data() {
    return {
      searchQuery: "", // 搜索输入
      showSearchIcon: false,   // 控制 search.svg 是否显示
      showHistory: false,      // 控制历史搜索的显示
      history: ['房间1', '房间2', '房间3'], // 历史记录

      roomType: "NoAI", // 房间类型（默认无AI）
      filteredRooms: [
      { id: 1, name: "房间1", type: "有AI", currentPeople: 2, maxPeople: 6 },
      { id: 2, name: "房间2", type: "无AI", currentPeople: 4, maxPeople: 10 },
      { id: 3, name: "房间3", type: "有AI", currentPeople: 1, maxPeople: 4 },
    ],
      selectedPeopleCount: 2, // 默认选中2人
      peopleOptions: [2,3, 4,5, 6,7, 8,9, 10,11,12,13,14,15,16,17,18,19,20,21,22,23,24], // 可选人数列表
      
      showMenuSidebar: false, // 控制侧边栏的显示与否
      showFriendsSidebar: false,
      showHistorySidebar: false,
    };
  },
  computed: {
    // 根据搜索和房间类型过滤房间列表
    //filteredRooms() {
    //  return this.rooms.filter((room) => {
    //    const matchesSearch = room.name.includes(this.searchQuery);
    //    const matchesType = this.roomType === "All" || room.type === this.roomType;
    //    return matchesSearch && matchesType;
    //  });
    //},
  },
  methods: {
    // 输入框点击事件，展开左侧 search.svg 图标
    onFocus() {
      this.showSearchIcon = true;
    },
    onBlur() {
      if (this.searchQuery.length === 0) {
        this.showSearchIcon = false;
      }
    },
    // 清空输入框内容
    clearSearch() {
      this.searchQuery = '';
    },
    // 执行搜索操作
    searchRoom() {
      alert(`搜索内容：${this.searchQuery}`);
      // 这里可以执行后台搜索接口调用
    },
    // 选择历史搜索项
    selectHistory(item) {
      this.searchQuery = item;
      this.showHistory = false;
    },
    // 点击搜索框外部区域关闭左侧的 search.svg
    handleBarClick(event) {
      const inputBox = this.$refs.inputBox;
      if (inputBox && !inputBox.contains(event.target)) {
        this.showSearchIcon = false;
      }
    },



    handleInput() {
      // 监听输入事件，方便以后扩展
    },

    toggleSidebar(type) {
      if (type === 'menu') {
        this.showMenuSidebar = !this.showMenuSidebar;
        this.showFriendsSidebar = false;
        this.showHistorySidebar = false;
      } else if (type === 'friends') {
        this.showFriendsSidebar = !this.showFriendsSidebar;
        this.showMenuSidebar = false;
        this.showHistorySidebar = false;
      } else if (type === 'history') {
        this.showHistorySidebar = !this.showHistorySidebar;
        this.showMenuSidebar = false;
        this.showFriendsSidebar = false;
      }
    },
    // 关闭侧边栏
    closeALL(){
      this.closeMenuSidebar();
      this.closeFriendsSidebar();
      this.closeHistorySidebar();
      this.closePlayerDetails();
      this.closeHistory();
    },
    
    closeMenuSidebar() {
      this.showMenuSidebar = false;
    },
    closeFriendsSidebar() {
      this.showFriendsSidebar = false;
    },
    closeHistorySidebar() {
      this.showHistorySidebar = false;
    },
    closePlayerDetails() {
      this.showDetails = false;
      this.selectedPlayer = null;
    },
    closeHistory() {
      this.showHistory = false; 
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

/* 横向工具栏样式 */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  padding: 10px 20px;
  position: fixed;
  top: 0;
  width: 100%;
  height: 5%;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 图标按钮样式 */
.icon-button {
  background-color: transparent;
  border: none;
  cursor: pointer;
  margin-right: 20px;
  transition: transform 0.3s ease;
}

.icon-button:last-child {
  margin-right: 0;
}

.icon-button:hover {
  transform: scale(1.1);
}

/* 特别设置左侧菜单按钮 */
.top-bar .left {
  margin-left: 0; /* 保证左侧按钮不会被推到中间 */
}

/* 右侧按钮组 */
.right-buttons {
  display: flex;
  align-items: center;
  gap: 10px; /* 让右边的按钮之间有间距 */
}

/* 侧边栏的样式 */
.sidebar {
  position: fixed;
  top: 5%;
  width: 250px;
  height: calc(95%);
  background-color: var(--sidebar-bg);
  color: var(--text-color);
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.5);
  border-radius: 10px; /* 圆角 */
  transition: transform 0.5s ease, opacity 0.5s ease; /* 控制平滑过渡 */
  z-index: 999;
  overflow-y: auto;
}

.sidebar-content {
  padding: 20px;
}
.menu-sidebar {
  left: 0; 
}

.friends-sidebar, .history-sidebar {
  right: 0;
}

/* 左侧滑动动画 */
.slide-left-enter-active,
.slide-left-leave-active {
  transition: transform 0.3s ease;
}

.slide-left-enter-from {
  transform: translateX(-100%);
}

.slide-left-leave-to {
  transform: translateX(-100%);
}

/* 右侧滑动动画 */
.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.3s ease;
}

.slide-right-enter-from {
  transform: translateX(100%);
}

.slide-right-leave-to {
  transform: translateX(100%);
}

.icon {
  width: 24px;
  height: 24px;
  filter: var(--img-filter);
  transition: filter 0.3s ease;
}

/* 悬停状态 */
.icon-button:active .icon {
  transform: scale(1.1);
}



/* 全局样式 */
.main-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--background-color);
  font-family: Arial, sans-serif;
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
  justify-content: space-between;  /* 确保左右两侧元素均匀分布 */
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 25px;
  width: 100%;
  position: relative;
  background-color: #fff;
}

.search-icon img,
.search-button img {
  width: 24px;
  height: 24px;
  transition: filter 0.3s;
  
}

.search-icon {
  margin-right: 8px;
  transition: width 0.3s ease;
  display: flex;
  margin-top: 10px;
}


.search-bar input {
  flex-grow: 1; /* 输入框占据大部分空间 */
  height: 30px;
  padding: 8px;
  font-size: 14px;
  line-height: 20px;
  border: none;
  outline: none;
  box-sizing: border-box;
  overflow: hidden;
  resize: none;
  padding-right: 25%; /* 保证删除按钮不会遮挡文字 */
  width: 100%;  /* 确保输入框填满可用空间 */
}
  
.clear-container {
  top: 23%;
  display: flex;
  align-items: center;
  position: absolute;
  right: 10%; /* 右侧对齐 */

}

.clear-button img {
  width: 24px;
  height: 24px;
  transition: filter 0.3s;
}
.clear-button:hover {
  filter: brightness(0) saturate(100%) invert(41%) sepia(93%) saturate(390%) hue-rotate(188deg) brightness(98%) contrast(89%);
  /* 鼠标悬停时给图标添加颜色变化 */
}
.search-bar .clear-button, .search-bar .search-button {
  background-color: transparent;
  border: none;
  cursor: pointer;
}

.search-bar .search-button {
  position: absolute;
  right: 1%;
  top: 50%;
  transform: translateY(-50%);
  background-color: transparent;
  border-radius: 50%; /* 圆形按钮 */
  /*border: 2px solid #007bff; /* 给按钮加一个蓝色边框 */
  border: none;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.3s; /* 添加过渡效果 */
}


.search-bar .search-button:hover {
  filter: brightness(0) saturate(100%) invert(41%) sepia(93%) saturate(390%) hue-rotate(188deg) brightness(98%) contrast(89%);
  /* 鼠标悬停时给图标添加颜色变化 */
}
  

.separator {

  border-radius: 50%; /* 圆角效果，显得更精致 */
  width: 2px;
  height: 20px;
  background-color: #333;
  position: absolute;
  top: 21%;
  right: 15%; /* 右侧对齐 */
}

.history {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  background-color: #fff;
  border: 1px solid #ccc;
  z-index: 10;
}

.history ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.history li {
  padding: 8px;
  cursor: pointer;
}

.history li:hover {
  background-color: #f1f1f1;
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
  padding: 10px; /* 顶部留出导航栏空间 */
  gap: 20px;
  overflow-y: auto;
}
  
/* 房间列表样式 */
.room-list {
  flex: 2;
  background-color: #ffffff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.room-list h2 {
  margin-bottom: 20px;
  color: var(--text-color);
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
  background-color: #ffffff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
  
.create-room h2 {
  margin-bottom: 20px;
  color: var(--text-color);
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
  margin-bottom: 15px;
}

.select-people label {
  margin-right: 10px;
  color: var(--text-color);
}

.select-people select {
  padding: 8px 12px;
  font-size: 14px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  outline: none;
}

.room-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}
.room-card {
  background-color: #f9f9f9;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  width: 220px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform var(--transition-speed) ease, box-shadow var(--transition-speed) ease;
}

.room-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.room-card h3 {
  margin: 0 0 10px;
  color: var(--text-color);
}

.room-card p {
  margin: 5px 0;
  color: var(--text-color);
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
  border: none;
  transition: background-color var(--transition-speed) ease;
}

.room-card button:hover {
  background-color: #0056b3;
}

.room-type {
  margin-bottom: 15px;
}

.room-type label {
  margin-right: 20px;
  color: var(--text-color);
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.quick-match-button,
.create-room-button {
  flex: 1;
  padding: 10px 0;
  background-color: var(--primary-color);
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color var(--transition-speed) ease;
}

.quick-match-button:hover,
.create-room-button:hover {
  background-color: var(--button-hover);
}
  </style>
  