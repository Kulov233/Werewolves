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
      <main class="content" :class="{ 'show-create-room': showCreateRoomPanel }">
        <!-- 房间列表部分 -->
        <section class="room-list" :class="{ 'shrink': showCreateRoomPanel }" ref="roomList">
          
          <div class="room-list-header">
            <h2>房间列表</h2>
            <div class="search-bar" @click.stop>
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
                @keyup.enter="searchRoom"
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
              <transition name="fade">
                <div v-show="showHistory && searchQuery.length === 0" class="history">
                  <div class="history-header">
                    <span>搜索历史</span>
                    <button @click.stop="clearAllHistory" class="clear-all-button" title="清空历史记录">
                      <img src="@/assets/clearAll.svg" alt="Clear" class="clear-icon" />
                    </button>
                  </div>
                  <ul>
                    <li v-for="item in history" 
                        :key="item" 
                        @click.stop="selectHistory(item)" 
                        class="history-item">
                      <img src="@/assets/history.svg" alt="History" class="history-icon"/>
                      <span>{{ item }}</span>
                      <button @click.stop="removeHistoryItem(item)" class="remove-item" title="删除历史记录">
                        <img src="@/assets/clear.svg" alt="Clear" class="clear-icon" />
                      </button>
                    </li>
                  </ul>
                </div>
              </transition>
            </div>

            <!-- 在搜索框右边添加一个创建房间按钮 -->
            <button class="create-Room-button" @click="toggleCreateRoom" title="创建房间">
              <img src="@/assets/createRoom.svg" alt="Create Room" />
            </button>
          </div>
          <!-- 添加过渡动画容器 -->
          <transition-group 
            name="room-card" 
            tag="div" 
            class="room-cards">
            <div v-for="room in filteredRooms" 
                :key="room.id" 
                class="room-card">
              <div class="room-card-header">
                <h3>{{ room.name }}</h3>
                <span class="room-type" :class="{ 'ai': room.type === '有AI' }">
                  {{ room.type }}
                </span>
                <!-- 添加房主头像 -->
                <div class="owner-avatar" @click.stop="showProfile(room.id)">
                  <img src="@/assets/profile-icon.png" alt="房主头像" />
                  <!-- 个人资料卡弹窗 -->
                  <transition name="profile">
                    <div v-if="selectedRoom === room.id" class="profile-card" @click.stop>
                      <div class="profile-header">
                         <img src="@/assets/profile-icon.png"
                            alt="房主头像" 
                            class="large-avatar"/>
                        <div class="profile-info">
                          <h4>{{ userProfile.name || '房主昵称' }}</h4>
                          <span class="profile-status" :class="{'online': userProfile.isOnline}">
                            {{ userProfile.isOnline ? '在线' : '离线' }}
                          </span>
                        </div>
                      </div>
                      <div class="profile-stats">
                        <div v-for="(stat, index) in userProfile.stats" 
                            :key="index" 
                            class="stat-item">
                          <span class="stat-value">{{ stat.value }}</span>
                          <span class="stat-label">{{ stat.label }}</span>
                        </div>
                      </div>
                      <div class="profile-actions">
                        <button class="action-btn add-friend-btn" 
                                @click="sendFriendRequest(userProfile.userId)"
                                :disabled="userProfile.isFriend">
                          <img src="@/assets/addFriend.svg" alt="加好友" class="action-icon"/>
                          {{ userProfile.isFriend ? '已是好友' : '加好友' }}
                        </button>
                        <button class="action-btn report-btn" @click="reportUser(userProfile.userId)">
                          <img src="@/assets/report.svg" alt="举报" class="action-icon"/>
                          举报
                        </button>
                      </div>
                      <div class="recent-games">
                        <h5>最近对战</h5>
                        <div class="game-list">
                          <div v-for="game in userProfile.recentGames" 
                              :key="game.id" 
                              class="game-item">
                            <span class="game-result" :class="game.result">
                              {{ game.result === 'win' ? '胜利' : '失败' }}
                            </span>
                            <span class="game-date">{{ game.date }}</span>
                          </div>
                        </div>
                    </div>
                    </div>
                  </transition>
                </div>
              </div>

              <div class="room-description">
                <span class="description">
                    {{ room.description }}
                </span>
              </div>

              <div class="room-info">
                <div class="info-item">
                  <img src="@/assets/people.svg" alt="Users" class="info-icon" />
                  <span class="player-count">
                    {{ room.currentPeople }}/{{ room.maxPeople }}
                  </span>
                </div>
                
                <!-- 可以根据需要添加更多房间信息 -->
                <div class="info-item">
                  <img src="@/assets/status.svg" alt="Status" class="info-icon" />
                  <span :class="{'status-full': room.currentPeople === room.maxPeople}">
                    {{ room.currentPeople === room.maxPeople ? '已满' : '可加入' }}
                  </span>
                </div>
              </div>

              <button 
                class="join-button" 
                @click.stop="joinRoom(room.id)"
                :disabled="room.currentPeople === room.maxPeople">
                <span v-if="room.currentPeople === room.maxPeople">房间已满</span>
                <span v-else>加入房间</span>
              </button>
            </div>
          </transition-group>
        </section>
    
        <!-- 创建房间面板 -->
        <transition name="slide-create">
          <section v-if="showCreateRoomPanel" class="create-room">
            <div class="create-room-header">
              <button class="close-create-room" @click="toggleCreateRoom" title="关闭">
                <img src="@/assets/close-createRoom.svg" alt="Close" />
              </button>
              <h2>创建房间</h2>
            </div>

            <div class="create-room-content">

              <!-- 房间名称输入 -->
              <div class="form-group">
                <label for="roomName">房间名称</label>
                <input 
                  type="text" 
                  id="roomName" 
                  v-model="newRoom.name" 
                  class="text-input"
                  placeholder="输入房间名称"
                >
              </div>

              <!-- 房间简介输入 -->
              <div class="form-group">
                <label for="roomDescription">房间简介</label>
                <textarea 
                  id="roomDescription" 
                  v-model="newRoom.description" 
                  class="text-input"
                  placeholder="输入房间简介"
                  rows="3"
                ></textarea>
              </div>
              <!-- 选择人数 -->
              <div class="form-group">
                <label for="peopleCount">选择人数</label>
                <select id="peopleCount" v-model="selectedPeopleCount" class="select-input">
                  <option v-for="count in peopleOptions" :key="count" :value="count">
                    {{ count }} 人
                  </option>
                </select>
              </div>

              <!-- 房间类型选择 -->
              <div class="form-group">
                <label>房间类型</label>
                <div class="radio-group">
                  <label class="radio-label">
                    <input type="radio" value="有AI" v-model="roomType" />
                    <span class="radio-text">有AI</span>
                  </label>
                  <label class="radio-label">
                    <input type="radio" value="无AI" v-model="roomType" />
                    <span class="radio-text">无AI</span>
                  </label>
                </div>
              </div>

              <!-- 按钮组 -->
              <div class="action-buttons">
                <button class="create-room-button" @click="createRoom">
                  创建房间
                </button>
              </div>
            </div>
          </section>
        </transition>
      </main>

      <!-- 浮动快速匹配按钮 -->
      <div
        class="quick-match-button-container"
        @mousedown="startDrag"
        @touchstart="startDrag"
        :style="{ top: buttonPosition.y + 'px', left: buttonPosition.x + 'px' }"
      >
        <button class="quick-match-button" @click.stop="toggleQuickMatchPanel" title="快速匹配">
          <img src="@/assets/quickMatch.svg" alt="快速匹配" />
        </button>
      </div>

      <!-- 快速匹配选项窗口 -->
      <transition name="fade">
        <div v-if="showQuickMatchPanel" class="quick-match-panel" @click.stop>
          <h3>快速匹配</h3>
          <div class="form-group">
            <label for="matchPeopleCount">选择人数</label>
            <select id="matchPeopleCount" v-model="matchPeopleCount" class="select-input">
              <option v-for="count in peopleOptions" :key="count" :value="count">
                {{ count }} 人
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>是否有AI</label>
            <div class="radio-group">
              <label class="radio-label">
                <input type="radio" value="有AI" v-model="matchAI" />
                <span class="radio-text">有AI</span>
              </label>
              <label class="radio-label">
                <input type="radio" value="无AI" v-model="matchAI" />
                <span class="radio-text">无AI</span>
              </label>
            </div>
          </div>
          <div class="action-buttons">
            <button class="confirm-match-button" @click="performQuickMatch">
              确认匹配
            </button>
            <button class="cancel-match-button" @click="toggleQuickMatchPanel">
              取消
            </button>
          </div>
        </div>
      </transition>
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

      roomType: "无AI", // 房间类型（默认无AI）
      filteredRooms: [
      { id: 1, name: "房间1", type: "有AI", description:"这是一个六人局房间且有AI", currentPeople: 2, maxPeople: 6 },
      { id: 2, name: "房间2", type: "无AI", description:"无", currentPeople: 4, maxPeople: 10 },
      { id: 3, name: "房间3", type: "有AI", description:"无", currentPeople: 1, maxPeople: 4 },
    ],
      selectedPeopleCount: 2, // 默认选中2人
      peopleOptions: [4, 6, 8, 10, 12, 16], // 可选人数列表
      
      showMenuSidebar: false, // 控制侧边栏的显示与否
      showFriendsSidebar: false,
      showHistorySidebar: false,

      showCreateRoomPanel: false, // 控制创建房间面板的显示
      selectedRoom: null, // 用于控制显示哪个房间的个人资料卡
      

      userProfile: {
          userId: "user1",
          name: "云想衣裳花想容",
          avatar: require("@/assets/profile-icon.png"),
          isOnline: true,
          isFriend: false,
          stats: [
            { label: '游戏场数', value: 128 },
            { label: '胜率', value: '76%' },
            { label: '评分', value: 4.8 }
          ],
          recentGames: [
            { id: 'g1', result: 'win', date: '2024-12-04' },
            { id: 'g2', result: 'win', date: '2024-12-03' },
            { id: 'g3', result: 'lose', date: '2024-12-03' }
          ]
      },
      //userProfile: null,
      newRoom: {
        name: `云想衣裳花想容的房间`,  // 这里需要替换实际的用户名
        description: "无",
        type: "无AI",
        currentPeople: 1,
        maxPeople: 2
      },

      buttonPosition: {
        x: 20, // 初始X位置（右下角）
        y: 20, // 初始Y位置
      },
      isDragging: false,
      dragOffset: { x: 0, y: 0 },
      showQuickMatchPanel: false, // 显示快速匹配窗口
      matchPeopleCount: 6, // 快速匹配人数
      matchAI: "有AI", // 快速匹配是否有AI

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
  mounted() {
    // 设置按钮初始位置为右下角
    this.$nextTick(() => {
      const roomList = this.$refs.roomList;
      if (roomList) {
        const rect = roomList.getBoundingClientRect();
        this.buttonPosition.x = rect.width - 70; // 根据容器宽度设置X位置
        this.buttonPosition.y = rect.height - 70; // 根据容器高度设置Y位置
      }
    });

    // 添加全局的鼠标事件监听器
    window.addEventListener("mousemove", this.onDragging);
    window.addEventListener("mouseup", this.stopDrag);
    window.addEventListener("touchmove", this.onDragging);
    window.addEventListener("touchend", this.stopDrag);
  },
  beforeUnmount() {
    // 移除事件监听器
    window.removeEventListener("mousemove", this.onDragging);
    window.removeEventListener("mouseup", this.stopDrag);
    window.removeEventListener("touchmove", this.onDragging);
    window.removeEventListener("touchend", this.stopDrag);
  },




  methods: {
    //async showProfile(roomId) {
    //  this.selectedRoom = this.selectedRoom === roomId ? null : roomId;
    //  if (this.selectedRoom) {
    //    // 获取用户资料
    //    try {
    //      const response = await this.getUserProfile(roomId);
    //      this.userProfile = response.data;
    //    } catch (error) {
    //      console.error('Failed to fetch user profile:', error);
    //    }
    //  }
    //},
//
    //// 获取用户资料接口
    //async getUserProfile(roomId) {
    //  // TODO: 实现接口调用
    //  // return await api.get(`/api/user/profile/${roomId}`);
    //},
//
    //// 发送好友请求
    //async sendFriendRequest(userId) {
    //  try {
    //    // await api.post('/api/friend/request', { userId });
    //    // 处理成功响应
    //  } catch (error) {
    //    console.error('Failed to send friend request:', error);
    //  }
    //},
//
    //// 举报用户
    //async reportUser(userId) {
    //  try {
    //    // await api.post('/api/user/report', { userId });
    //    // 处理成功响应
    //  } catch (error) {
    //    console.error('Failed to report user:', error);
    //  }
    //},
    // 输入框点击事件，展开左侧 search.svg 图标
    // 开始拖动
    startDrag(event) {
      this.isDragging = true;
      const touch = event.type === "touchstart" ? event.touches[0] : event;
      this.dragOffset.x = touch.clientX - this.buttonPosition.x;
      this.dragOffset.y = touch.clientY - this.buttonPosition.y;
    },
    // 拖动中
    onDragging(event) {
      if (!this.isDragging) return;
      const touch = event.type === "touchmove" ? event.touches[0] : event;
      let newX = touch.clientX - this.dragOffset.x;
      let newY = touch.clientY - this.dragOffset.y;

      // 限制在容器内
      const roomList = this.$refs.roomList;
      if (roomList) {
        const rect = roomList.getBoundingClientRect();
        const buttonSize = 50; // 按钮的大小（px）
        newX = Math.max(0, Math.min(newX, rect.width - buttonSize));
        newY = Math.max(0, Math.min(newY, rect.height - buttonSize));
      }

      this.buttonPosition.x = newX;
      this.buttonPosition.y = newY;
    },
    // 停止拖动
    stopDrag() {
      this.isDragging = false;
    },

    // 切换快速匹配窗口的显示状态
    toggleQuickMatchPanel() {
      this.showQuickMatchPanel = !this.showQuickMatchPanel;
    },

    // 执行快速匹配
    performQuickMatch() {
      // 过滤符合条件的房间
      const matchedRooms = this.filteredRooms.filter(room => {
        const matchesPeople = room.maxPeople === this.matchPeopleCount;
        const matchesAI = room.type === this.matchAI;
        return matchesPeople && matchesAI && room.currentPeople < room.maxPeople;
      });

      if (matchedRooms.length > 0) {
        // 加入第一个匹配的房间
        this.joinRoom(matchedRooms[0].id);
        this.toggleQuickMatchPanel();
      } else {
        alert("符合条件的房间不存在！");
      }
    },

    onFocus() {
      this.showSearchIcon = true;
      this.showHistory = true; // 显示历史记录
    },
    onBlur() {
      if (this.searchQuery.length === 0) {
        this.showSearchIcon = false;
      }
    },
    // 清空输入框内容
    clearSearch() {
      this.searchQuery = '';
      this.showHistory = true;
    },
    // 执行搜索操作
    searchRoom() {
      if (this.searchQuery.trim()) {
        // 添加到历史记录
        if (!this.history.includes(this.searchQuery)) {
          this.history.unshift(this.searchQuery);
        }
        alert(`搜索内容：${this.searchQuery}`);
      }
    },
    // 选择历史搜索项
    selectHistory(item) {
      this.searchQuery = item;
      this.showHistory = false;
    },
    removeHistoryItem(item) {
      this.history = this.history.filter(h => h !== item);
    },
    clearAllHistory() {
      this.history = [];
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
      this.selectedRoom = null
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
      const roomId = this.filteredRooms.length + 1;
      const newRoom = {
        id: roomId,
        name: this.newRoom.name,
        type: this.roomType,
        description: this.newRoom.description,
        currentPeople: 1,
        maxPeople: this.selectedPeopleCount
      };
      
      this.filteredRooms.push(newRoom);
      this.toggleCreateRoom(); // 关闭创建面板
      
      // 重置表单
      this.newRoom.name = `云想衣裳花想容的房间`;
      this.newRoom.description = "无";
      this.roomType = "无AI";
      this.selectedPeopleCount = 2;
    },
    joinRoom(roomId) {
    alert(`加入房间 ID: ${roomId}`);
    },

    toggleCreateRoom() {
      this.showCreateRoomPanel = !this.showCreateRoomPanel;
      // 添加延迟以确保动画效果同步
      if (this.showCreateRoomPanel) {
        setTimeout(() => {
          this.$refs.roomList.classList.add('shrink');
        }, 50);
      } else {
        this.$refs.roomList.classList.remove('shrink');
      }
    },

    

    showProfile(roomId) {
      this.selectedRoom = this.selectedRoom === roomId ? null : roomId;
    }
    
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
  width: 40%;
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
  margin-top: -1px;
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
  top: 20%;
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
  top: 12%;
  right: -8%; /* 右侧对齐 */
}

/* 淡入淡出动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.history {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  width: 100%;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 2;
  overflow: hidden;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
}

.history-header span {
  color: #666;
  font-size: 14px;
  font-weight: 500;
}


.history ul {
  margin: 0;
  padding: 8px 0;
  list-style: none;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.history-item:hover {
  background-color: #f5f5f5;
}

.history-icon {
  width: 16px;
  height: 16px;
  margin-right: 12px;
  opacity: 0.5;
}

.history-item span {
  flex: 1;
  color: #333;
  font-size: 14px;
}
.clear-all-button,
.remove-item {
  background-color: transparent !important;
  border: none;
  padding: 6px;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.clear-all-button:hover .clear-icon,
.remove-item:hover .clear-icon {
  filter: invert(31%) sepia(98%) saturate(1640%) hue-rotate(201deg) brightness(96%) contrast(107%);
}

.clear-icon {
  width: 16px;
  height: 16px;
  transition: filter 0.3s ease;
}

.remove-item {
  visibility: hidden;
  opacity: 0;
  transition: all 0.3s ease;
}

.history-item:hover .remove-item {
  visibility: visible;
  opacity: 1;
}

.history-item:hover .remove-item {
  visibility: visible;
}


  .header-actions button {
    margin-left: 10px;
    background-color: #007bff;
    color: white;
    border: none;
    padding: 5px 10px;
    cursor: pointer;
  }
  
/* 主内容区域样式调整 */
.content {
  display: flex;
  flex: 1;
  padding: 20px;
  gap: 20px;
  overflow-x: hidden;
  position: relative;
  transition: all 0.3s ease;
}
  
/* 房间列表样式 */
.room-list {
  flex: 2;
  background-color: #f4f7fc;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}
.room-list {
  transition: transform 0.3s ease, flex 0.3s ease;
}
.room-list.shrink {
  transform: translateX(-2%);
}

/* 房间列表头部布局 */
.room-list-header {
  display: flex;
  justify-content: space-between; /* 元素分布在两端和中间 */
  align-items: center;
  margin-bottom: 24px;
  padding: 0 10px;
  height: 50px;
}
.create-Room-button {
  background-color: transparent !important;;
  border: none;
  cursor: pointer;
  padding: 10px;
}

.create-Room-button:hover {
  transform: scale(1.1);
  filter: brightness(0) saturate(100%) invert(41%) sepia(93%) saturate(390%) hue-rotate(188deg) brightness(98%) contrast(89%);
}

.create-Room-button img {
  width: 30px; /* 设置图标的大小 */
  height: 30px;
}

/* 右侧创建房间面板动画 */
.content {
  overflow: hidden;
}

/* 创建房间面板滑动动画 */
.slide-create-enter-active,
.slide-create-leave-active {
  transition: transform 0.3s ease;
}

.slide-create-enter-from,
.slide-create-leave-to {
  transform: translateX(100%);
}

.room-list-header h2 {
  font-size: 1.5em;
  color: #2c3e50;
  margin: 0;
}

/* 房间卡片网格布局 */
.room-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  padding: 8px 4px;
}

/* 卡片动画效果 */
.room-card-enter-active,
.room-card-leave-active {
  transition: all 0.5s ease;
}

.room-card-enter-from,
.room-card-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.room-card-move {
  transition: transform 0.5s ease;
}

/* 房间卡片样式 */
.room-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  border: 1px solid #eef1f5;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.room-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.08);
  border-color: #e1e8f0;
  z-index: 15;
}

/* 卡片头部样式 */
.room-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

/* 房主头像样式 */
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.owner-avatar {
  position: relative;
  width: 32px;
  height: 32px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.owner-avatar:hover {
  transform: scale(1.1);
}

.owner-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 个人资料卡动画 */
.profile-enter-active,
.profile-leave-active {
  transition: all 0.3s ease;
}

.profile-enter-from,
.profile-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 个人资料卡样式 */
.profile-card {
  position: absolute;
  top: calc(100% + 8px);
  left: -8px;
  width: 240px; /* 减小宽度 */
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 16px;
  z-index: 10;
}

.profile-card::before {
  content: '';
  position: absolute;
  top: -8px;
  left: 20px;
  width: 16px;
  height: 16px;
  background: #fff;
  transform: rotate(45deg);
  box-shadow: -2px -2px 5px rgba(0, 0, 0, 0.04);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.large-avatar {
  width: 80px !important;
  height: 80px !important;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.profile-info {
  flex: 1;
}

.profile-info h4 {
  margin: 0 0 4px;
  font-size: 0.95em;
  color: #2c3e50;
}

.profile-status {
  display: inline-block;
  padding: 2px 6px;
  background: #ecf5ff;
  color: #409eff;
  border-radius: 12px;
  font-size: 0.85em;
}

.profile-status.online {
  background: #ecf5ff;
  color: #409eff;
}

.profile-stats {
  display: flex;
  justify-content: space-around;
  padding: 12px 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
  margin-bottom: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1em;
  font-weight: 600;
  color: #2c3e50;
}

.stat-label {
  font-size: 0.75em;
  color: #666;
}

.profile-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px;
  border: none;
  border-radius: 6px;
  font-size: 0.8em;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: transparent;
}

.add-friend-btn {
  background-color: transparent;
  color: #333;
}

.add-friend-btn:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.report-btn {
  background-color: transparent;
  color: red;
}

.action-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  filter: brightness(1.1);
}

.action-icon {
  width: 14px;
  height: 14px;
  opacity: 0.9;
}

.action-btn img{
  width: 24px;
  height: 24px;
}


.recent-games {
  background: #f8fafc;
  border-radius: 6px;
  padding: 12px;
}

.recent-games h5 {
  margin: 0 0 8px;
  color: #2c3e50;
  font-size: 0.85em;
}

.game-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px;
  background: #fff;
  border-radius: 4px;
  font-size: 0.8em;
  margin-bottom: 4px;
}

.game-result {
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.game-result.win {
  background: #f0f9eb;
  color: #67c23a;
}

.game-result.lose {
  background: #fef0f0;
  color: #f56c6c;
}

.game-date {
  color: #666;
  font-size: 0.85em;
}

/* 添加 room-description 样式 */
.room-description {
  padding: 8px 0;
  border-top: 1px solid #f0f2f5;
  border-bottom: 1px solid #f0f2f5;
}

.room-description .description {
  color: #666;
  font-size: 0.9em;
  line-height: 1.4;
  display: block;
  /* 超出两行显示省略号 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.room-card-header h3 {
  margin: 0;
  font-size: 1.1em;
  color: #2c3e50;
  font-weight: 600;
}

.room-type {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85em;
  background-color: #f0f2f5;
  color: #606a78;
}

.room-type.ai {
  background-color: #ecf5ff;
  color: #409eff;
}

/* 房间信息样式 */
.room-info {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606a78;
  font-size: 0.9em;
}

.info-icon {
  width: 16px;
  height: 16px;
  opacity: 0.7;
}

.player-count {
  font-family: 'Monaco', monospace;
}

.status-full {
  color: #f56c6c;
}

/* 加入按钮样式 */
.join-button {
  margin-top: auto;
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 8px;
  background-color: #409eff;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.join-button:hover:not(:disabled) {
  background-color: #3a8ee6;
  transform: translateY(-2px);
}

.join-button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
  transform: none;
}

  
/* 创建房间面板样式 */
.create-room {
  position: relative;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
  padding: 24px;
  width: 400px;
  transition: all 0.3s ease;
  overflow-y: auto;
}

/* 创建房间滑动动画 */
.slide-create-enter-active,
.slide-create-leave-active {
  transition: transform 0.3s ease;
}

.slide-create-enter-from,
.slide-create-leave-to {
  transform: translateX(100%);
}

/* 创建房间头部样式 */
.create-room-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  position: relative;
}

.close-create-room {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  padding: 8px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.close-create-room:hover {
  transform: translateY(-50%) scale(1.1);
}

.close-create-room img {
  width: 24px;
  height: 24px;
}

.create-room h2 {
  flex: 1;
  text-align: center;
  margin: 0;
  color: #333;
  font-size: 1.5em;
}

/* 表单样式美化 */
.create-room-content {
  padding: 20px 0;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #666;
  font-weight: 500;
  text-align: left; /* 确保文本左对齐 */
}
.text-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  background-color: #fff;
  transition: all 0.3s ease;
  outline: none;
}

.text-input:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64,158,255,0.1);
}

textarea.text-input {
  resize: vertical;
  min-height: 80px;
}
.select-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  background-color: #fff;
  transition: border-color 0.3s ease;
}

.select-input:focus {
  border-color: #007bff;
  outline: none;
}

/* 单选按钮组样式 */
.radio-group {
  display: flex;
  gap: 20px;
}

.radio-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.radio-label input[type="radio"] {
  margin-right: 8px;
}

.radio-text {
  color: #666;
}

/* 按钮样式美化 */
.action-buttons {
  display: flex;
  gap: 16px;
  margin-top: 32px;
}

.create-room-button {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}


.create-room-button {
  background-color: #007bff;
  color: white;
}


.create-room-button:hover {
  background-color: #0056b3;
}

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

.create-room-button:hover {
  background-color: var(--button-hover);
}

/* 浮动快速匹配按钮的容器 */
.quick-match-button-container {
  position: absolute;
  cursor: grab;
  z-index: 10;
}

.quick-match-button-container:active {
  cursor: grabbing;
}

/* 浮动快速匹配按钮 */
.quick-match-button {
  width: 50px;
  height: 50px;
  background-color: #409eff;
  border: none;
  border-radius: 50%;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s ease, transform 0.3s ease;
}

.quick-match-button img {
  width: 24px;
  height: 24px;
  filter: brightness(0) invert(1);
}

.quick-match-button:hover {
  background-color: #3a8ee6;
  transform: scale(1.1);
}

/* 快速匹配选项窗口 */
.quick-match-panel {
  position: absolute;
  bottom: 70px; /* 位于按钮上方 */
  right: 0;
  width: 250px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 16px;
  z-index: 20;
  animation: slideIn 0.3s ease forwards;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

}

.quick-match-panel h3 {
  margin-top: 0;
  color: #2c3e50;
  font-size: 1.2em;
  text-align: center;
}

.quick-match-panel .form-group {
  margin-bottom: 16px;
}

.quick-match-panel .form-group label {
  display: block;
  font-size: 0.9em;
  margin-bottom: 8px;
  color: #777;
}

.quick-match-panel .select-input,
.quick-match-panel .radio-group {
  width: 100%;
}

.quick-match-panel .select-input {
  padding: 8px;
  font-size: 1em;
  border-radius: 8px;
  border: 1px solid #ccc;
}

.quick-match-panel .radio-group label {
  display: inline-block;
  margin-right: 10px;
}

.quick-match-panel .action-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quick-match-panel .action-buttons button {
  width: 45%;
  padding: 8px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.quick-match-panel .action-buttons button:hover {
  background-color: #3a8ee6;
}

  </style>
  