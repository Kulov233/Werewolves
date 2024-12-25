<template>
  <div>
    <!-- 顶部菜单栏 -->
    <div class="top-bar">
      <button class="icon-button left" @click.stop="toggleSidebar('menu')">
        <img class="icon" src="@/assets/menu.svg" alt="Menu" />
      </button>
      <!-- 中间内容插槽 -->
      <slot name="center"></slot>
      <!-- 右侧按钮组 -->
      <div class="right-buttons">
        <button class="icon-button" @click.stop="toggleSidebar('friends')">
          <img class="icon" src="@/assets/friends.svg" alt="Friends" />
        </button>
        <button class="icon-button" @click.stop="toggleSidebar('history')">
          <img class="icon" src="@/assets/history.svg" alt="History" />
        </button>
        <!-- 额外按钮插槽 -->
        <slot name="extra-buttons"></slot>
      </div>
    </div>

    <!-- 左侧滑出菜单 -->
    <transition name="slide-left">
      <div v-if="showMenuSidebar" class="sidebar menu-sidebar" @click.stop>
        <div class="sidebar-content">
          <!-- 个人信息头部 -->
          <div class="profile-header-menu">
            <div class="profile-avatar" @click="toggleAvatarEdit" @mouseenter="showChangeAvatar" @mouseleave="hideChangeAvatar">
              <img :src="userProfile.avatar" alt="用户头像" />
              <!-- 头像编辑遮罩 -->
              <div class="avatar-overlay" v-show="isHoveringAvatar">
                <input type="file" 
                      @change="handleAvatarChange" 
                      accept="image/*"
                      class="avatar-input"
                      ref="avatarInput">
                <div class="avatar-edit-text">更换头像</div>
              </div>
              <div class="online-status" :class="{ 'is-online': userProfile.isOnline }"></div>
            </div>
            <div class="profile-basic">
              <h3 class="profile-name">{{ userProfile.name }}</h3>
              <!-- 个性签名编辑区 -->
              <div class="signature-container" @click="startEditSignature" v-if="!userProfile.isEditingSignature">
                <span class="signature-text">{{ userProfile.signature }}</span>
                <img src="@/assets/edit.svg" alt="Edit" class="edit-icon"/>
              </div>
              <input v-else
                    ref="signatureInput"
                    v-model="userProfile.tempSignature"
                    @blur="saveSignature"
                    @keyup.enter="saveSignature"
                    class="signature-input"
                    placeholder="输入个性签名"
                    maxlength="30">
            </div>
          </div>

          <!-- 个人统计数据 -->
          <div class="profile-stats">
            <div v-for="stat in userProfile.stats" :key="stat.label" class="stat-card">
              <span class="stat-value">{{ stat.value }}</span>
              <span class="stat-label">{{ stat.label }}</span>
            </div>
          </div>

          <!-- 功能区块 -->
          <div class="menu-sections">
            <!-- 游戏中心 -->
            <div class="menu-section">
              <h4 class="section-title">
                <img src="@/assets/wolf.svg" alt="Game" class="section-icon" />
                游戏中心
              </h4>
              <div class="section-content">
                <button class="menu-button" @click="goToHistory">
                  <img src="@/assets/history.svg" alt="History" />
                  游戏记录
                </button>
                <button class="menu-button" @click="goToAchievements">
                  <img src="@/assets/wolf.svg" alt="Achievements" />
                  我的成就
                </button>
              </div>
            </div>

            <!-- 好友系统 -->
            <div class="menu-section">
              <h4 class="section-title">
                <img src="@/assets/wolf.svg" alt="Friends" class="section-icon" />
                社交中心
              </h4>
              <div class="section-content">
                <button class="menu-button" @click="goToFriends">
                  <img src="@/assets/wolf.svg" alt="Friend List" />
                  好友列表
                </button>
                <button class="menu-button" @click="goToInvites">
                  <img src="@/assets/wolf.svg" alt="Invites" />
                  邀请管理
                </button>
              </div>
            </div>

            <!-- 设置中心 -->
            <div class="menu-section">
              <h4 class="section-title">
                <img src="@/assets/wolf.svg" alt="Settings" class="section-icon" />
                设置中心
              </h4>
              <div class="section-content">
                <button class="menu-button" @click="goToProfile">
                  <img src="@/assets/wolf.svg" alt="Profile" />
                  资料设置
                </button>
                <button class="menu-button" @click="goToPreferences">
                  <img src="@/assets/wolf.svg" alt="Preferences" />
                  偏好设置
                </button>
              </div>
            </div>
          </div>

          <!-- 底部操作区 -->
          <div class="menu-footer">
            <button class="logout-button" @click="handleLogout">
              <img src="@/assets/logout.svg" alt="Logout" />
              退出登录
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- 右侧滑出菜单 Friends -->
    <transition name="slide-right">
      <div v-if="showFriendsSidebar" class="sidebar friends-sidebar" @click.stop>
        <div class="sidebar-header">
          <h3>好友列表</h3>
          <div class="header-actions">
            <button class="icon-btn" @click="toggleFriendRequests" title="好友请求">
              <img src="@/assets/wolf.svg" alt="Requests"/>
              <span class="badge" v-if="friendRequests.length > 0">{{friendRequests.length}}</span>
            </button>
            <button class="icon-btn" @click="toggleAddFriend" title="添加好友">
              <img src="@/assets/addFriend.svg" alt="Add Friend"/>
            </button>
            <button class="close-btn" @click="toggleSidebar('friends')">
              <img src="@/assets/close-createRoom.svg" alt="Close"/>
            </button>
          </div>
        </div>

        <!-- 好友请求面板 -->
        <div v-if="showFriendRequests" class="friend-requests-panel">
          <div class="panel-header">
            <h4>好友请求</h4>
            <span class="request-count">{{friendRequests.length}}个待处理</span>
          </div>
          <div class="requests-list">
            <div v-for="request in friendRequests" 
                :key="request.id" 
                class="request-item">
              <img :src="request.avatar" alt="Avatar" class="request-avatar"/>
              <div class="request-info">
                <span class="request-name">{{request.name}}</span>
                <span class="request-time">{{request.time}}</span>
              </div>
              <div class="request-actions">
                <button class="accept-btn" @click="handleFriendRequest(request.id, 'accept')">接受</button>
                <button class="reject-btn" @click="handleFriendRequest(request.id, 'reject')">拒绝</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 添加好友面板 -->
        <div v-if="showAddFriend" class="add-friend-panel">
          <div class="search-friend">
            <input type="text" 
                  v-model="friendSearchQuery"
                  placeholder="输入用户ID或昵称"
                  @keyup.enter="searchFriend"/>
            <button @click="searchFriend">搜索</button>
          </div>
        </div>

        <!-- 好友列表 -->
        <div class="friends-list">
          <!-- 在线好友 -->
          <div class="friend-group">
            <div class="group-header">
              <span>在线好友</span>
              <span class="count">{{onlineFriends.length}}</span>
            </div>
            <div class="friend-items">
              <div v-for="friend in onlineFriends" 
                  :key="friend.id" 
                  class="friend-item">
                <img :src="friend.avatar" alt="Avatar" class="friend-avatar"/>
                <div class="friend-info">
                  <span class="friend-name">{{friend.name}}</span>
                  <span class="friend-status">{{friend.status}}</span>
                </div>
                <div class="friend-actions">
                  <button class="action-btn" @click="inviteFriend(friend.id)">
                    <img src="@/assets/invite.svg" alt="Invite"/>
                  </button>
                  <button class="action-btn" @click="showFriendMenu(friend)">
                    <img src="@/assets/more.svg" alt="More"/>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 离线好友 -->
          <div class="friend-group">
            <div class="group-header">
              <span>离线好友</span>
              <span class="count">{{offlineFriends.length}}</span>
            </div>
            <div class="friend-items">
              <div v-for="friend in offlineFriends" 
                  :key="friend.id" 
                  class="friend-item offline">
                <img :src="friend.avatar" alt="Avatar" class="friend-avatar"/>
                <div class="friend-info">
                  <span class="friend-name">{{friend.name}}</span>
                  <span class="friend-status">{{friend.lastSeen}}</span>
                </div>
                <div class="friend-actions">
                  <button class="action-btn" @click="showFriendMenu(friend)">
                    <img src="@/assets/more.svg" alt="More"/>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 右侧滑出菜单 History -->
    <transition name="slide-right">
      <div v-if="showHistorySidebar" class="sidebar history-sidebar" @click.stop>
        <div class="sidebar-header">
          <h3>游戏记录</h3>
          <div class="header-actions">
            <button class="close-btn" @click="toggleSidebar('history')">
              <img src="@/assets/close-createRoom.svg" alt="Close"/>
            </button>
          </div>
        </div>

        <!-- 数据统计 -->
        <div class="stats-cards">
          <div class="stat-card">
            <span class="stat-number">{{totalGames}}</span>
            <span class="stat-label">总场次</span>
          </div>
          <div class="stat-card">
            <span class="stat-number">{{winRate}}%</span>
            <span class="stat-label">胜率</span>
          </div>

        </div>

        <!-- 筛选器 -->
        <div class="history-filters">
          <select v-model="timeFilter" class="filter-select">
            <option value="all">全部时间</option>
            <option value="week">最近7天</option>
            <option value="month">最近30天</option>
          </select>
          <select v-model="resultFilter" class="filter-select">
            <option value="all">全部结果</option>
            <option value="win">胜利</option>
            <option value="lose">失败</option>
          </select>
        </div>

        <!-- 历史记录列表 -->
        <div class="game-history-list">
          <div v-for="game in filteredGameHistory" 
              :key="game.id" 
              class="game-record">
            <div class="game-header">
              <span class="game-result" :class="game.result">
                {{game.result === 'win' ? '胜利' : '失败'}}
              </span>
              <span class="game-time">{{game.time}}</span>
            </div>
            <div class="game-details">
              <div class="role-info">
                <img :src="game.roleIcon" alt="Role" class="role-icon"/>
                <span class="role-name">{{game.role}}</span>
              </div>
              <div class="game-stats">
                <div class="stat">
                  <span class="label">场次时长</span>
                  <span class="value">{{game.duration}}</span>
                </div>
              </div>
            </div>
            <div class="game-players">
              <div class="team good-team">
                <div v-for="player in game.goodTeam" 
                    :key="player.id" 
                    class="player">
                  <img :src="player.avatar" alt="Avatar" class="player-avatar"/>
                  <span class="player-name">{{player.name}}</span>
                </div>
              </div>
              <div class="team bad-team">
                <div v-for="player in game.badTeam" 
                    :key="player.id" 
                    class="player">
                  <img :src="player.avatar" alt="Avatar" class="player-avatar"/>
                  <span class="player-name">{{player.name}}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  userProfile: {
    type: Object,
    required: true
  },
  onlineFriends: {
    type: Array,
    default: () => []
  },
  offlineFriends: {
    type: Array,
    default: () => []
  },
  friendRequests: {
    type: Array,
    default: () => []
  },
  totalGames: {
    type: Number,
    default: 0
  },
  winRate: {
    type: Number,
    default: 0
  },

  gameHistory: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits([
  'updateAvatar',
  'updateSignature',
  'logout',
  'friendRequest',
  'inviteFriend',
  'showFriendMenu',
  'searchFriend'
])

const router = useRouter()

// 状态管理
const showMenuSidebar = ref(false)
const showFriendsSidebar = ref(false)
const showHistorySidebar = ref(false)
const showFriendRequests = ref(false)
const showAddFriend = ref(false)
const isHoveringAvatar = ref(false)
const friendSearchQuery = ref('')
const timeFilter = ref('all')
const resultFilter = ref('all')

// 控制侧边栏显示
const toggleSidebar = (type) => {
  if (type === 'menu') {
    showMenuSidebar.value = !showMenuSidebar.value
    showFriendsSidebar.value = false
    showHistorySidebar.value = false
  } else if (type === 'friends') {
    showFriendsSidebar.value = !showFriendsSidebar.value
    showMenuSidebar.value = false
    showHistorySidebar.value = false
  } else if (type === 'history') {
    showHistorySidebar.value = !showHistorySidebar.value
    showMenuSidebar.value = false
    showFriendsSidebar.value = false
  }
}

// 头像相关
const showChangeAvatar = () => {
  isHoveringAvatar.value = true
}

const hideChangeAvatar = () => {
  isHoveringAvatar.value = false
}

const toggleAvatarEdit = () => {
  if (isHoveringAvatar.value) {
    avatarInput.value?.click()
  }
}

const handleAvatarChange = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    emit('updateAvatar', file)
  }
}

// 签名相关
const startEditSignature = () => {
  props.userProfile.isEditingSignature = true
  props.userProfile.tempSignature = props.userProfile.signature
}

const saveSignature = () => {
  if (props.userProfile.tempSignature?.trim()) {
    emit('updateSignature', props.userProfile.tempSignature.trim())
  }
}

// 好友系统
const toggleFriendRequests = () => {
  showFriendRequests.value = !showFriendRequests.value
  showAddFriend.value = false
}

const toggleAddFriend = () => {
  showAddFriend.value = !showAddFriend.value
  showFriendRequests.value = false
}

const handleFriendRequest = (requestId, action) => {
  emit('friendRequest', { requestId, action })
}

const inviteFriend = (friendId) => {
  emit('inviteFriend', friendId)
}

const showFriendMenu = (friend) => {
  emit('showFriendMenu', friend)
}

const searchFriend = () => {
  if (friendSearchQuery.value.trim()) {
    emit('searchFriend', friendSearchQuery.value.trim())
  }
}

// 导航功能
const goToHistory = () => {
  router.push('/history')
  toggleSidebar('menu')
}

const goToAchievements = () => {
  router.push('/achievements')
  toggleSidebar('menu')
}

const goToFriends = () => {
  router.push('/friends')
  toggleSidebar('menu')
}

const goToInvites = () => {
  router.push('/invites')
  toggleSidebar('menu')
}

const goToProfile = () => {
  router.push('/profile')
  toggleSidebar('menu')
}

const goToPreferences = () => {
  router.push('/preferences')
  toggleSidebar('menu')
}

// 历史记录过滤
const filteredGameHistory = computed(() => {
  let filtered = props.gameHistory

  if (timeFilter.value !== 'all') {
    const now = new Date()
    const days = timeFilter.value === 'week' ? 7 : 30
    const timeLimit = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
    
    filtered = filtered.filter(game => {
      const gameTime = new Date(game.time)
      return gameTime >= timeLimit
    })
  }

  if (resultFilter.value !== 'all') {
    filtered = filtered.filter(game => game.result === resultFilter.value)
  }

  return filtered
})

// 登出
const handleLogout = () => {
  emit('logout')
}

// 关闭所有侧边栏
const closeAll = () => {
  showMenuSidebar.value = false
  showFriendsSidebar.value = false
  showHistorySidebar.value = false
  showFriendRequests.value = false
  showAddFriend.value = false
}

// 暴露方法给父组件
defineExpose({
  closeAll,
  toggleSidebar
})
</script>