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
  
      <div class="room-container" :class="{ 'show-create-room': showCreateRoomPanel }"> 
        <!-- 主要房间区域 -->
        <div class="room-list" :class="{ 'shrink': showCreateRoomPanel }" ref="roomList">
            <div class="room-list-header">
                <h1 class="room-title">{{ currentRoom.name }}</h1>
                <!-- 在搜索框右边添加一个创建房间按钮 -->
                <button class="create-Room-button" @click="toggleCreateRoom" title="修改配置">
                    <img src="@/assets/modifyRoom.svg" alt="Create Room" />
                </button>
             </div>
        
        <!-- 房主部分 -->
        <div class="section">
            <h2 class="section-title">房主</h2>
            <div class="player-avatar host-avatar" @click.stop="showProfile('host')">
                <img :src="hostProfile.avatar" :alt="hostProfile.name" />
                <span class="player-name">{{ hostProfile.name }}</span>

                <!-- 房主资料卡 -->
                <transition name="profile">
                    <div v-if="selectedPlayerId === 'host'" class="profile-card" @click.stop>
                        <div class="profile-header">
                        <img src="@/assets/profile-icon.png"
                            alt="房主头像" 
                            class="large-avatar"/>
                        <div class="profile-info">
                            <h4>{{ userProfile.name }}</h4>
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

        <!-- 成员部分 -->
        <div class="section">
            <h2 class="section-title">成员（{{ currentRoom.currentPeople }}/{{ currentRoom.maxPeople }}）</h2>
            <div class="members-grid">
            <!-- 成员头像 -->
            <div v-for="member in members" 
                :key="member.id" 
                class="player-avatar"
                @click.stop="!member.isAI && showProfile(member.id)">
                <img :src="member.avatar" :alt="member.name" />
                <span class="player-name">{{ member.name }}</span>
                <button v-if="isHost" 
                        class="kick-button" 
                        @click.stop="kickMember(member.id)">×</button>
                
                <!-- 成员资料卡 -->
                <transition name="profile">
                <div v-if="selectedPlayerId === member.id && !member.isAI" 
                    class="profile-card" 
                    @click.stop>
                    <div class="profile-header">
                    <img :src="member.avatar"
                        alt="成员头像" 
                        class="large-avatar"/>
                    <div class="profile-info">
                        <h4>{{ member.name }}</h4>
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
                            @click="sendFriendRequest(member.userId)"
                            :disabled="userProfile.isFriend">
                        <img src="@/assets/addFriend.svg" alt="加好友" class="action-icon"/>
                        {{ userProfile.isFriend ? '已是好友' : '加好友' }}
                    </button>
                    <button class="action-btn report-btn" @click="reportUser(member.userId)">
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
        </div>

        <!-- 操作按钮部分 -->
        <div class="action-buttons">
            <button class="action-btn add-ai">
            <img src="@/assets/ai.svg" alt="AI" />
            添加AI
            </button>
            <button class="action-btn invite-player">
            <img src="@/assets/addFriend.svg" alt="邀请" />
            邀请玩家
            </button>
        </div>

        <!-- 开始游戏按钮 -->
        <div class="start-game-section">
            <div v-if="needMorePlayers" class="players-needed">
            <span class="warning-dot"></span>
            还需要{{ requiredPlayers }}位玩家
            </div>
            <button 
            class="start-game-btn"
            :disabled="needMorePlayers"
            :class="{ 'disabled': needMorePlayers }"
            >
            开始游戏
            </button>
        </div>
        </div>

        <!-- 右侧好友列表 -->
        <div class="friends-list" :class="{ 'hidden': showCreateRoom }">
        <h2 class="friends-title">好友列表 (1/2)</h2>
        
        <!-- 在线好友 -->
        <div class="friends-section">
            <h3 class="friends-subtitle">在线好友</h3>
            <div class="friend-item online">
            <div class="friend-avatar">
                <img src="@/assets/profile-icon.png" alt="好友头像" />
                <span class="status-dot online"></span>
            </div>
            <div class="friend-info">
                <span class="friend-name">ymxd</span>
                <span class="friend-status online">在线</span>
            </div>
            <button class="invite-btn">邀请</button>
            </div>
        </div>

        <!-- 离线好友 -->
        <div class="friends-section">
            <h3 class="friends-subtitle">离线好友</h3>
            <div class="friend-item offline">
            <div class="friend-avatar">
                <img src="@/assets/profile-icon.png" alt="好友头像" />
                <span class="status-dot offline"></span>
            </div>
            <div class="friend-info">
                <span class="friend-name">未知</span>
                <span class="friend-status offline">离线</span>
            </div>
            </div>
        </div>
        </div>

        <!-- 房间设置面板部分 -->
        <transition name="slide-create">
          <section v-if="showCreateRoomPanel" class="create-room">
            <div class="create-room-header">
              <button class="close-create-room" @click="toggleCreateRoom" title="关闭">
                <img src="@/assets/close-createRoom.svg" alt="Close" />
              </button>
              <h2>房间设置</h2>
            </div>

            <div class="create-room-content">
                <!-- 当前房间信息概览 -->
                <div class="room-info-overview">
                <h3>房间信息</h3>
                <div class="room-info-item">
                    <img src="@/assets/profile-icon.png" alt="房主" class="info-icon"/>
                    <span>房主：{{ hostProfile.name }}</span>
                </div>
                <div class="room-info-item">
                    <img src="@/assets/people.svg" alt="当前人数" class="info-icon"/>
                    <span>当前人数：{{ currentRoom.currentPeople }}</span>
                </div>
                </div>

                <!-- 可修改的设置部分 -->
                <div class="settings-section">
                <h3>房间设置</h3>
                
                <!-- 人数设置 -->
                <div class="form-group">
                    <label class="setting-label">
                    <img src="@/assets/people.svg" alt="人数" class="setting-icon"/>
                    房间人数
                    </label>
                    <select v-model="currentRoom.maxPeople" class="select-input setting-control">
                    <option v-for="count in peopleOptions" :key="count" :value="count">
                        {{ count }} 人
                    </option>
                    </select>
                </div>

                <!-- AI设置 -->
                <div class="form-group">
                    <label class="setting-label">
                    <img src="@/assets/ai.svg" alt="AI" class="setting-icon"/>
                    AI设置
                    </label>
                    <div class="radio-group">
                    <label class="radio-label setting-option">
                        <input type="radio" value="有AI" v-model="roomType" />
                        <span class="radio-text">启用AI</span>
                    </label>
                    <label class="radio-label setting-option">
                        <input type="radio" value="无AI" v-model="roomType" />
                        <span class="radio-text">关闭AI</span>
                    </label>
                    </div>
                </div>
                </div>

                <!-- 保存按钮 -->
                <div class="action-buttons">
                <button class="save-settings-btn" @click="saveRoomSettings">
                    <img src="@/assets/wolf.svg" alt="保存" class="btn-icon"/>
                    保存设置
                </button>
                </div>
            </div>
          </section>
        </transition>
    </div>

    </div>
</template>
  
<script>
export default {
  data() {
    return {

      roomType: "无AI", // 房间类型（默认无AI）

      selectedPeopleCount: 2, // 默认选中2人
      peopleOptions: [4, 6, 8, 10, 12, 16], // 可选人数列表
      
      showMenuSidebar: false, // 控制侧边栏的显示与否
      showFriendsSidebar: false,
      showHistorySidebar: false,

      showCreateRoomPanel: false, // 控制创建房间面板的显示
      selectedRoom: null, // 用于控制显示哪个房间的个人资料卡
      
      //userProfile: null,
      newRoom: {
        name: `云想衣裳花想容的房间`,  // 这里需要替换实际的用户名
        description: "无",
        type: "无AI",
        currentPeople: 1,
        maxPeople: 2
      },
      
      // 当前房间信息
      currentRoom: {
        name: "示例房间",
        currentPeople: 3,
        maxPeople: 6,
        type: "无AI"
      },
      
      // 房主信息
      hostProfile: {
        name: "云想衣裳花想容",
        avatar: require("@/assets/profile-icon.png"),
        isOnline: true,
        stats: [
          { label: '游戏场数', value: 128 },
          { label: '胜率', value: '76%' },
          { label: '评分', value: 4.8 }
        ]
      },

      userProfile: {
        name: "云想衣裳花想容",
        avatar: require("@/assets/profile-icon.png"), // 使用require导入图片
        isOnline: true,
        isFriend: false,
        userId: "host",
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

      // 成员列表
      members: [
        { 
          id: 1, 
          name: '玩家1', 
          avatar: require("@/assets/profile-icon.png"),
          isAI: false,
          userId: 'user1',
          isOnline: true,
          isFriend: false,
          stats: [
            { label: '游戏场数', value: 85 },
            { label: '胜率', value: '65%' },
            { label: '评分', value: 4.2 }
          ],
          recentGames: [
            { id: 'm1', result: 'win', date: '2024-12-04' },
            { id: 'm2', result: 'lose', date: '2024-12-03' }
          ],
        },
        { 
          id: 2, 
          name: '玩家2', 
          avatar: require("@/assets/profile-icon.png"),
          isAI: false,
          userId: 'user2',
          isOnline: true,
          isFriend: false,
          stats: [
            { label: '游戏场数', value: 85 },
            { label: '胜率', value: '65%' },
            { label: '评分', value: 4.2 }
          ],
          recentGames: [
            { id: 'm1', result: 'win', date: '2024-12-04' },
            { id: 'm2', result: 'lose', date: '2024-12-03' }
          ]
        },
        { 
          id: 3, 
          name: 'GPT', 
          avatar: require("@/assets/ai.svg"),
          isAI: true,
          userId: 'gpt1',
          isOnline: true,
          isFriend: false,
          stats: [
            { label: '游戏场数', value: 85 },
            { label: '胜率', value: '65%' },
            { label: '评分', value: 4.2 }
          ],
          recentGames: [
            { id: 'm1', result: 'win', date: '2024-12-04' },
            { id: 'm2', result: 'lose', date: '2024-12-03' }
          ]
        }
      ],

      // 选中的玩家ID (用于显示资料卡)
      selectedPlayerId: null,
      
      // 是否是房主
      isHost: true,
    };
  },
  computed: {
    // 计算是否需要更多玩家
    needMorePlayers() {
      return this.currentRoom.currentPeople < this.currentRoom.maxPeople;
    },
    
    // 计算还需要多少玩家
    requiredPlayers() {
      return this.currentRoom.maxPeople - this.currentRoom.currentPeople;
    }
  },
  methods: {
    // 显示玩家资料
    showProfile(playerId) {
      if (playerId === 'host') {
        this.selectedProfile = this.userProfile;
      } else {
        const member = this.members.find(m => m.id === playerId);
        this.selectedProfile = member;
      }
      this.selectedPlayerId = playerId;
    },
    
    // 踢出成员
    kickMember(memberId) {
      const index = this.members.findIndex(m => m.id === memberId);
      if (index !== -1) {
        this.members.splice(index, 1);
        this.currentRoom.currentPeople--;
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
      this.selectedPlayerId = null;
      this.selectedRoom = null
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
  
.room-container {
  display: flex;
  height: 100vh;
  background-color: #f4f7fc;
  padding: 20px;
  gap: 20px;
}

.room-list {
  flex: 1;
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.room-list {
  transition: transform 0.3s ease, flex 0.3s ease;
}
.room-list.shrink {
  transform: translateX(-1%);
}

.room-title {
  text-align: center;
  font-size: 28px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 32px;
}

.section {
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  text-align: left; /* 内容水平靠左 */
  display: flex; /* 使用 flex 布局 */
  flex-direction: column; /* 垂直排列 */
  align-items: flex-start; /* 子元素垂直对齐 */
}

.section-title {
  font-size: 20px;
  color: #2c3e50;
  margin-bottom: 16px;
}

.host-section {
  display: flex;
  justify-content: center;
}

.player-avatar {
  position: relative;
  text-align: center;
}

.player-avatar img {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 3px solid #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.host-avatar img {
  width: 80px;
  height: 80px;
  border: 4px solid #fbbf24;
}

.player-name {
  display: block;
  margin-top: 8px;
  font-size: 14px;
  color: #4b5563;
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 20px;
  padding: 16px;
  grid-auto-flow: column;
}

.kick-button {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #ef4444;
  color: white;
  border: 2px solid white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.2s;
}

.kick-button:hover {
  transform: scale(1.1);
  background: #dc2626;
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  padding: 0 20px;

}

.action-btn {
  padding: 12px;
  border-radius: 8px;
  border: none;
  color: white;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
  width: auto; 
}

.add-ai {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  margin-left: 10%;
}

.invite-player {
  background: linear-gradient(135deg, #10b981, #059669);
  margin-left: 10%;
  margin-right: 10%;
}

.action-btn:hover {
  transform: translateY(-2px);
}

.start-game-section {
  margin-top: auto;
  padding: 20px;
}

.players-needed {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ef4444;
  margin-bottom: 12px;
  gap: 8px;
}

.warning-dot {
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 50%;
}

.start-game-btn {
  width: 100%;
  padding: 16px;
  border-radius: 8px;
  border: none;
  font-size: 18px;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  cursor: pointer;
  transition: all 0.2s;
}

.start-game-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

/* 右侧好友列表样式 */
.friends-list {
  width: 400px;
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.friends-list.hidden {
  transform: translateX(100%);
  opacity: 0;
}

.friends-title {
  font-size: 20px;
  color: #2c3e50;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.friends-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 12px;
}

.friend-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  background: #f8fafc;
}

.friend-avatar {
  position: relative;
  margin-right: 12px;
}

.friend-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.status-dot {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
}

.status-dot.online {
  background: #10b981;
}

.status-dot.offline {
  background: #9ca3af;
}

.friend-info {
  flex: 1;
}

.friend-name {
  display: block;
  font-weight: 500;
  color: #2c3e50;
}

.friend-status {
  font-size: 12px;
}

.friend-status.online {
  color: #10b981;
}

.friend-status.offline {
  color: #6b7280;
}

.invite-btn {
  padding: 6px 12px;
  border-radius: 6px;
  border: none;
  background: #3b82f6;
  color: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.invite-btn:hover {
  background: #2563eb;
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

.room-list-header h1 {
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3); /* 阴影效果 */
  color: #2c3e50;
  font-family: 'Roboto', sans-serif;
  font-weight: 800; /* 字体粗细 */
  font-size: 32px; /* 调整字体大小 */
  letter-spacing: 2px; /* 字符间距 */
  margin-top: 50px;
  margin-left: 120px;
  flex-grow: 1; /* 让 h1 占满剩余空间，从而实现居中 */
  text-align: center; /* 标题内容居中 */
  
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
  z-index: 1000;
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
  border: none !important;
  border-radius: 6px;
  font-size: 0.8em;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: transparent;
}

.add-friend-btn {
  background-color: transparent !important;
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
  


/* 创建房间滑动动画 */
.slide-create-enter-active,
.slide-create-leave-active {
  transition: transform 0.3s ease;
}

.slide-create-enter-from,
.slide-create-leave-to {
  transform: translateX(100%);
}

.create-room {
  position: relative;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
  padding: 24px;
  width: 400px;
  transition: all 0.3s ease;
  overflow-y: auto;
}


.create-room-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  position: relative;
  border-bottom: 2px solid #f0f2f5;
  padding-bottom: 20px;
}

.create-room-header h2 {
  flex: 1;
  text-align: center;
  color: #2c3e50;
  font-size: 1.6em;
  font-weight: 600;
  margin: 0;
}

/* 房间信息概览样式 */
.room-info-overview {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.room-info-overview h3 {
  color: #2c3e50;
  font-size: 1.1em;
  margin-bottom: 16px;
}

.room-info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  color: #64748b;
}

.info-icon {
  width: 20px;
  height: 20px;
  opacity: 0.7;
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

/* 设置区域样式 */
.settings-section {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid #e2e8f0;
}

.settings-section h3 {
  color: #2c3e50;
  font-size: 1.1em;
  margin-bottom: 20px;
}

.setting-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4b5563;
  font-weight: 500;
  margin-bottom: 12px;
  margin-top: 20px;
}

.setting-icon {
  width: 18px;
  height: 18px;
  opacity: 0.8;
}

.setting-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #4b5563;
  background: #f8fafc;
  transition: all 0.3s ease;
}

.setting-control:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.setting-option {
  padding: 8px 16px;
  border-radius: 6px;
  background: #f8fafc;
  transition: all 0.3s ease;
}

.setting-option:hover {
  background: #f1f5f9;
}

/* 保存按钮样式 */
.save-settings-btn {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  font-weight: 600;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-settings-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.btn-icon {
  width: 20px;
  height: 20px;
  filter: brightness(0) invert(1);
}


  </style>
  