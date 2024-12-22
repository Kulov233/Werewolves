<template>

    <div class="main-page" @click="closeALL" >

      <div class="room-container" :class="{ 'show-create-room': showCreateRoomPanel }">
        <!-- 主要房间区域 -->
        <div class="room-list" :class="{ 'shrink': showCreateRoomPanel }" ref="roomList">
            <!-- 房间标题区域 -->
            <div class="room-list-header">
              <div class="title-section">
                <button class="leave-room-btn" @click="leaveRoom">
                  <img src="@/assets/leaveRoom.svg" alt="Leave" />
                </button>
                <h1 class="room-title">{{ currentRoom.title }}</h1>
              </div>
              <div class="control-buttons">
                <button
                  v-if="isHost"
                  class="remove-room-btn"
                  @click="removeRoom"
                >
                  <img src="@/assets/removeRoom.svg" alt="Remove" />
                </button>
                <button class="create-Room-button" @click="toggleCreateRoom" title="修改配置">
                  <img src="@/assets/modifyRoom.svg" alt="Create Room" />
                </button>
              </div>
            </div>

            <!-- 房间描述 -->
            <div class="room-description">
              {{ currentRoom.description }}
            </div>

            <!-- 房间ID (放在room-list底部) -->
            <div class="room-id">
              房间 ID: {{ currentRoom.id }}
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
                        <img :src="hostProfile.avatar"
                            alt="房主头像"
                            class="large-avatar"/>
                        <div class="profile-info">
                            <h4>{{ hostProfile.name }}</h4>
                            <span class="profile-status" :class="{'online': hostProfile.isOnline}">
                            {{ hostProfile.isOnline ? '在线' : '离线' }}
                            </span>
                        </div>
                        </div>
                        <div class="profile-stats">
                        <div v-for="(stat, index) in hostProfile.stats"
                            :key="index"
                            class="stat-item">
                            <span class="stat-value">{{ stat.value }}</span>
                            <span class="stat-label">{{ stat.label }}</span>
                        </div>
                        </div>
                        <div class="profile-actions">
                        <button class="action-btn add-friend-btn"
                                @click="sendFriendRequest(hostProfile.userId)"
                                :disabled="hostProfile.isFriend">
                            <img src="@/assets/addFriend.svg" alt="加好友" class="action-icon"/>
                            {{ hostProfile.isFriend ? '已是好友' : '加好友' }}
                        </button>

                        </div>
                        <div class="recent-games">
                        <h5>最近对战</h5>
                        <div class="game-list">
                            <div v-for="game in hostProfile.recentGames"
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
            <h2 class="section-title">成员（{{ currentRoom.currentPeople }}/{{ currentRoom.max_players }}）</h2>
            <div class="members-grid">
            <!-- 成员头像 -->
            <div v-for="member in members"
                :key="member.id"
                class="player-avatar"
                @click.stop="!member.isAI && showProfile(member.id)">
                <img :src="member.avatar" :alt="member.name" />
                <span class="player-name">{{ displayName(member.name) }}</span>
                <button v-if="isHost && (member.isAI || !member.isAI)"
                        class="kick-button"
                        @click.stop="member.isAI ? removeAIPlayer(member.id) : handleKickMember(member.id)">×</button>

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
                        <span class="profile-status" :class="{'online': member.isOnline}">
                        {{ member.isOnline ? '在线' : '离线' }}
                        </span>
                    </div>
                    </div>
                    <div class="profile-stats">
                    <div v-for="(stat, index) in member.stats"
                        :key="index"
                        class="stat-item">
                        <span class="stat-value">{{ stat.value }}</span>
                        <span class="stat-label">{{ stat.label }}</span>
                    </div>
                    </div>
                    <div class="profile-actions">
                    <button class="action-btn add-friend-btn"
                            @click="sendFriendRequest(member.userId)"
                            :disabled="member.isFriend">
                        <img src="@/assets/addFriend.svg" alt="加好友" class="action-icon"/>
                        {{ member.isFriend ? '已是好友' : '加好友' }}
                    </button>

                    </div>
                    <div class="recent-games">
                    <h5>最近对战</h5>
                    <div class="game-list">
                        <div v-for="game in member.recentGames"
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
            <button class="action-btn add-ai"
                    @click="addAIPlayer"
                    :disabled="!isHost || currentRoom.currentPeople >= currentRoom.max_players || currentRoom.type === '无AI'"
                    :style="(!isHost || currentRoom.currentPeople >= currentRoom.max_players || currentRoom.type === '无AI') ? {
                      background: '#9ca3af',
                      cursor: 'not-allowed',
                      opacity: '0.6'
                    } : {}">
              <img src="@/assets/ai.svg" alt="AI" />
              添加AI
            </button>
            <button class="action-btn invite-player" @click="showInviteDialog = true">
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
            :disabled="needMorePlayers || !isHost"
            :class="{ 'disabled': needMorePlayers || !isHost }"
            @click="startGame"
            >
            开始游戏
            </button>
        </div>
        </div>

        <!-- 右侧好友列表 -->
        <div class="friends-list" :class="{ 'hidden': showCreateRoom }">
          <div class="friends-header">
            <h2 class="friends-title">
              好友列表 ({{onlineFriends.length}}/{{onlineFriends.length + offlineFriends.length}})
            </h2>
            <button class="refresh-btn" @click="refreshOnline" title="刷新">
              <img src="@/assets/refresh.svg" alt="Refresh" />
            </button>
          </div>

        <!-- 在线好友 -->
        <div class="friends-section">
            <h3 class="friends-subtitle">
              <span class="subtitle-text">在线好友</span>
              <span class="friend-count">({{ onlineFriends.length }})</span>
            </h3>
            <div class="friend-list" v-if="onlineFriends.length > 0">
              <div v-for="friend in onlineFriends"
                   :key="friend.id"
                   class="friend-item online">
                <div class="friend-avatar">
                  <img :src="friend.avatar" :alt="friend.name" />
                  <span class="status-dot online"></span>
                </div>
                <div class="friend-info">
                  <span class="friend-name">{{ friend.name }}</span>
                  <span class="friend-status online">{{ friend.status }}</span>
                </div>
                <button
                  class="invite-btn"
                  @click="inviteFriend(friend.id)"
                  :disabled="friend.isInvited"
                  :class="{ 'success': friend.isInvited }"
                >
                  <span class="invite-text">
                    {{ friend.isInvited ? '已邀请' : '邀请' }}
                  </span>
                </button>
              </div>
            </div>
        </div>

        <!-- 离线好友 -->
        <div class="friends-section">
            <h3 class="friends-subtitle">
              <span class="subtitle-text">离线好友</span>
              <span class="friend-count">({{ offlineFriends.length }})</span>
            </h3>
            <div class="friend-list" v-if="offlineFriends.length > 0">
              <div v-for="friend in offlineFriends"
                   :key="friend.id"
                   class="friend-item offline">
                <div class="friend-avatar">
                  <img :src="friend.avatar" :alt="friend.name" />
                  <span class="status-dot offline"></span>
                </div>
                <div class="friend-info">
                  <span class="friend-name">{{ friend.name }}</span>
                  <span class="friend-status offline">{{ friend.lastSeen || '离线' }}</span>
                </div>
              </div>
            </div>
        </div>

        <!-- 无好友提示 -->
        <div v-if="!onlineFriends.length && !offlineFriends.length"
             class="no-friends">
          <img src="@/assets/friends.svg" alt="No Friends" class="no-friends-icon" />
          <p class="no-friends-text">还没有好友哦，快去添加吧！</p>
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
                    <img :src="hostProfile.avatar" alt="房主" class="info-icon"/>
                    <span>房主：{{ hostProfile.name }}</span>
                </div>
                <div class="room-info-item">
                    <img src="@/assets/people.svg" alt="当前人数" class="info-icon"/>
                    <span>当前人数：{{ currentRoom.currentPeople }}</span>
                </div>
                </div>

                <!-- 角色配置展示区域 -->
                <div class="role-config-section">
                  <h3 class="section-title">
                    <img src="@/assets/roles.svg" alt="角色" class="section-icon"/>
                    角色配置
                  </h3>

                  <!-- 当前配置展示 -->
                  <div class="role-display">
                    <div class="role-count-grid">
                      <template v-if="editRoomForm.roleConfig?.roles">
                        <div
                          v-for="(count, role) in roleCountMap"
                          :key="role"
                          v-memo="[role, count]"
                          class="role-count-item"
                          :class="ROLE_COLOR_MAP[role]"
                        >
                          <span class="role-name">{{ ROLE_NAME_MAP[role] }}</span>
                          <span class="role-number">× {{ count }}</span>
                        </div>
                      </template>
                    </div>
                  </div>

                  <!-- 女巫道具信息 -->
                  <div class="witch-items-section" v-if="editRoomForm.roleConfig?.witchItems">
                    <h4>女巫道具配置</h4>
                    <div class="witch-items-grid">
                      <div class="witch-item">
                        <img src="@/assets/cure.svg" alt="解药" class="item-icon"/>
                        <span class="item-name">解药</span>
                        <span class="item-count">× {{ editRoomForm.roleConfig.witchItems.cure }}</span>
                      </div>
                      <div class="witch-item">
                        <img src="@/assets/medicine.svg" alt="毒药" class="item-icon"/>
                        <span class="item-name">毒药</span>
                        <span class="item-count">× {{ editRoomForm.roleConfig.witchItems.poison }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 可修改的设置部分 -->
                <div class="settings-section">
                <h3>房间设置</h3>

                <!-- 房间名称设置 -->
                <div class="form-group">
                  <label class="setting-label">
                    <img src="@/assets/roomTitle.svg" alt="房间" class="setting-icon"/>
                    房间名称
                  </label>
                  <input
                    v-model="editRoomForm.title"
                    type="text"
                    class="setting-control"
                    placeholder="请输入房间名称"
                  />
                </div>

                <!-- 房间简介设置 -->
                <div class="form-group">
                  <label class="setting-label">
                    <img src="@/assets/description.svg" alt="简介" class="setting-icon"/>
                    房间简介
                  </label>
                  <textarea
                    v-model="editRoomForm.description"
                    class="setting-control"
                    placeholder="请输入房间简介"
                    rows="3"
                  ></textarea>
                </div>

                <!-- 人数设置 -->
                <div class="form-group">
                    <label class="setting-label">
                    <img src="@/assets/people.svg" alt="人数" class="setting-icon"/>
                    房间人数
                    </label>
                    <select v-model="editRoomForm.max_players" class="select-input setting-control">
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
                        <input type="radio" value="有AI" v-model="editRoomForm.allowAI" />
                        <span class="radio-text">启用AI</span>
                    </label>
                    <label class="radio-label setting-option">
                        <input type="radio" value="无AI" v-model="editRoomForm.allowAI" />
                        <span class="radio-text">关闭AI</span>
                    </label>
                    </div>
                </div>
                </div>

                <!-- 保存按钮 -->
                <div class="action-buttons">
                <button
                   class="save-settings-btn"
                   @click="saveRoomSettings"
                   :disabled="!isHost"
                   :class="{ 'disabled': !isHost }"
                   >
                    <img src="@/assets/wolf.svg" alt="保存" class="btn-icon"/>
                    保存设置
                </button>
                </div>
            </div>
          </section>
        </transition>
    </div>
     <!-- 添加确认弹窗组件 -->
    <ConfirmDialog
      :show="showDialog"
      :title="dialogTitle"
      :message="dialogMessage"
      :showConfirm="dialogShowConfirm"
      @confirm="handleDialogConfirm"
      @cancel="handleDialogCancel"
    />

      <!-- 添加搜索组件 -->
    <InvitePlayerDialog
      :show="showInviteDialog"
      :search-results="searchResults"
      :has-searched="hasSearched"
      :invited-users="invitedUsers"
      @close="resetInviteDialog"
      @search="debouncedSearch"
      @invite="handleInvite"
    />
    </div>



</template>

<script>
import ConfirmDialog from './shared_components/ConfirmDialog.vue'
import InvitePlayerDialog from './shared_components/InvitePlayerDialog.vue';
import { onMounted, ref , onUnmounted, watch, computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { useWebSocket } from '@/composables/useWebSocket';
import axios from 'axios';
import debounce from 'lodash/debounce';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000'
});

// 添加请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 添加响应拦截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // 如果是401错误且不是刷新token的请求
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // 使用refresh token获取新的access token
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post('http://localhost:8000/api/token/refresh/', {
          refresh: refreshToken
        });

        // 更新access token
        const newAccessToken = response.data.access;
        localStorage.setItem('access_token', newAccessToken);

        // 更新原始请求的Authorization header
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

        // 重试原始请求
        return api(originalRequest);
      } catch (refreshError) {
        // refresh token也过期了，需要重新登录
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        // 重定向到登录页面
        this.router.push('/login');  // 跳转到登录页面

        // 可以添加一些用户提示信息，提醒用户重新登录
        alert('您的会话已过期，请重新登录。');
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);
const ROLE_CONFIGS = {
  4: {
    roles: {
      Werewolf: 1,
      Villager: 3
    },
    witchItems: { cure: 1, poison: 1 }
  },
  6: {
    roles: {
      Werewolf: 2,
      Prophet: 1,
      Witch: 1,
      Villager: 2
    },
    witchItems: { cure: 1, poison: 1 },
    priorityRoles: ["Witch", "Prophet"]
  },
  8: {
    roles: {
      Werewolf: 2,
      Prophet: 1,
      Witch: 1,
      Idiot: 1,
      Villager: 3
    },
    witchItems: { cure: 1, poison: 1 },
    priorityRoles: ["Witch", "Idiot"]
  },
  12: {
    roles: {
      Werewolf: 3,
      Prophet: 1,
      Witch: 1,
      Villager: 7
    },
    witchItems: { cure: 2, poison: 2 }
  },
  16: {
    roles: {
      Werewolf: 4,
      Prophet: 1,
      Witch: 1,
      Villager: 10
    },
    witchItems: { cure: 2, poison: 2 }
  }
};

export default {
  components: {
    ConfirmDialog,
    InvitePlayerDialog,
  },

  setup() {

    const enableRolePriority = ref(true); // 控制是否启用角色优先选择
    const selectedPriorityRoles = ref([]); // 存储已选择的优先角色

    const aiCounter = ref(1);

    const store = useStore();
    const router = useRouter();
    const roomData = ref(store.state.currentRoom);
    const userProfile = ref(store.state.userProfile);
    const onlineFriends = ref( []);
    const offlineFriends = ref( []);
    const token = localStorage.getItem('access_token');
    const { connect, sendMessage, onType, isGameConnected, isLobbyConnected, disconnect } = useWebSocket(token);


    // 弹窗相关的状态
    const showDialog = ref(false);
    const dialogTitle = ref('');
    const dialogMessage = ref('');
    const dialogShowConfirm = ref(true);
    const currentDialogAction = ref('');

    // 搜索玩家
    const showInviteDialog = ref(false);
    const searchResults = ref([]);
    const hasSearched = ref(false);
    const invitedUsers = ref([]);

    // 是否为房主
    const isHost = ref(false);

    const currentRoom = ref({
      id: '',
      title: "",
      description: "",
      currentPeople: 0,
      max_players: 6,
      type: "无AI",
      aiPlayers: [],
      players: [],
      owner: null,
    });

    // 编辑房间的表单数据
    const editRoomForm = ref({
      title: "",
      description: "",
      max_players: 6,
      allowAI: "无AI",
      roleConfig: ROLE_CONFIGS[6],
    });

    // 角色颜色映射表改为静态常量
    const ROLE_COLOR_MAP = {
      'Werewolf': 'role-werewolf',
      'Villager': 'role-villager',
      'Prophet': 'role-prophet',
      'Witch': 'role-witch',
      'Idiot': 'role-idiot'
    };

    const ROLE_NAME_MAP = {
      'Werewolf': '狼人',
      'Villager': '村民',
      'Prophet': '预言家',
      'Witch': '女巫',
      'Idiot': '白痴'
    };

    // 简化的roleCountMap计算属性
    const roleCountMap = computed(() => {
      const config = ROLE_CONFIGS[currentRoom.value.max_players];
      if (!config?.roles) return {};
      return config.roles; // 直接返回角色配置对象
    });


    // 修改监听玩家数量变化
    watch(() => currentRoom.value.max_players, (newValue) => {
      editRoomForm.value.roleConfig = ROLE_CONFIGS[newValue];
    });

    // 控制创建房间面板的显示
    const showCreateRoomPanel=ref(false);

    // 房主信息
    const hostProfile = ref({
      name: "",
      avatar: "",
      isOnline: true,
      stats: []
    });

    // 成员列表
    const members = ref([]);
    const selectedPlayerId = ref(null);

    // 初始化房间信息
    const initializeRoom = async () => {
      if (!roomData.value) {
        router.push('/GameLobby');
        return;
      }

      editRoomForm.value = {
        title: roomData.value.title,
        description: roomData.value.description,
        max_players: roomData.value.max_players,
        allowAI: roomData.value.allow_ai_players ? "有AI" : "无AI",
        roleConfig: { ...ROLE_CONFIGS[roomData.value.max_players] }
      };

      // 设置房间基本信息
      currentRoom.value = {
        id: roomData.value.id,
        title: roomData.value.title,
        description: roomData.value.description,
        currentPeople: roomData.value.players.length + Object.keys(roomData.value.ai_players || {}).length,
        max_players: roomData.value.max_players,
        type: roomData.value.allow_ai_players ? "有AI" : "无AI",
        players: roomData.value.players,
        aiPlayers: roomData.value.ai_players,
        owner: roomData.value.owner,
      };

      // 获取并设置所有玩家信息
      const playerProfiles = await Promise.all(
        currentRoom.value.players.map(async (playerId) => {
          const profile = await fetchSelectedProfile(playerId);
          return {
            id: playerId,
            name: profile.name,
            avatar: profile.avatar,
            isAI: false,
            userId: playerId,
            isOnline: profile.isOnline,
            isFriend: profile.isFriend,
            stats: profile.stats,
            recentGames: profile.recentGames
          };
        })
      );

      // 从 playerProfiles 中找出房主信息
      const ownerProfile = playerProfiles.find(profile => profile.id === currentRoom.value.owner);
      if (ownerProfile) {
        hostProfile.value = {
          name: ownerProfile.name,
          avatar: ownerProfile.avatar,
          isOnline: ownerProfile.isOnline,
          stats: ownerProfile.stats,
          isFriend: ownerProfile.isFriend,
          userId: ownerProfile.id,
        };
      }

      // 添加AI玩家信息
      const aiPlayerProfiles = Object.entries(currentRoom.value.aiPlayers).map(([id, name]) => ({
        id,
        name,
        avatar: require("@/assets/ai.svg"),
        isAI: true,
        userId: id,
        isOnline: true,
        stats: []
      }));

      // 合并所有玩家信息
      members.value = [...playerProfiles, ...aiPlayerProfiles];

      // 判断当前用户是否为房主
      isHost.value = (userProfile.value.userId === currentRoom.value.owner);
    };

    // 踢人
    const handleKickMember = (memberId) => {
      if (!isHost.value) return; // 二次验证确保只有房主能踢人

      sendMessage({
        action: 'remove_player_from_room',
        room_id: currentRoom.value.id,
        user_id: memberId,
      });

    };

    // 处理搜索的函数
    const debouncedSearch = debounce(async (query) => {
      if (query.trim().length === 0) {
        searchResults.value = [];
        hasSearched.value = false;
        return;
      }

    const result = await handleSearch(query);
      if (result.success) {
        searchResults.value = result.users;
      } else {
        searchResults.value = [];
      }
      hasSearched.value = true;
    }, 300);

    // 搜索
    const handleSearch = async (keyword) => {
      try {
        const response = await api.get('/api/accounts/search/', {
          params: { keyword }
        });

        if (response.status === 200) {
          const users = await Promise.all(
            response.data.users.map(async (user) => {
              try {
                const avatarResponse = await api.get(`/api/accounts/avatar/${user.id}/`);
                return {
                  id: user.id,
                  username: user.username,
                  avatar: avatarResponse.status === 200
                      ? avatarResponse.data.avatar_url
                      : require('@/assets/profile-icon.png'),
                  isFriend: checkIsFriend(user.id)
                };
              } catch (error) {
                return {
                  id: user.id,
                  username: user.username,
                  avatar: require('@/assets/profile-icon.png'),
                  isFriend: checkIsFriend(user.id)
                };
              }
            })
          );

          return {
            success: true,
            users: users
          };
        }

        return {
          success: false,
          message: '搜索失败'
        };
      } catch (error) {
        console.error('Search error:', error);
        return {
          success: false,
          message: error.response?.data?.message || '搜索失败'
        };
      }
    };

    // 检查是否是好友
    const checkIsFriend = (userId) => {
      // 首先检查是否是自己
      if (userId === userProfile.value.userId) {
        return true;  // 如果是自己，返回true表示"已是好友"状态
      }
      // 其他情况检查是否在好友列表中
      return onlineFriends.value.some(friend => friend.id === userId) ||
             offlineFriends.value.some(friend => friend.id === userId);
    };

    // 显示对话框
    const showConfirmDialog = (title, message, showConfirm = false, action = '') => {
      dialogTitle.value = title;
      dialogMessage.value = message;
      dialogShowConfirm.value = showConfirm;
      currentDialogAction.value = action;
      showDialog.value = true;
    };

    const sendFriendRequest = async (targetId) => {
      try {
        const response = await api.post('/api/accounts/friends/add/',
            {
              player: userProfile.value.userId,
              target: targetId
            },
            {
              headers: {
                'Content-Type': 'application/json'
              }
            }
          );

        if (response.data.status === 'success') {
          showConfirmDialog('成功', '已发送好友请求');
          return {
            success: true,
            message: '好友请求已发送'
          };
        } else {
          showConfirmDialog('提示', response.data.message);
          return {
            success: false,
            message: response.data.message
          };
        }
      } catch (error) {
        console.error('发送好友请求失败:', error);
        showConfirmDialog('错误', error.response?.data?.message || '发送好友请求失败');
        return {
          success: false,
          message: error.response?.data?.message || '发送好友请求失败'
        };
      }
    };

    // 处理邀请的函数
    const handleInvite = async (userId) => {
      if (!currentRoom.value || invitedUsers.value.includes(userId)) return;

      try {
        // 发送邀请
        sendMessage({
          action: "invite_player",
          room_id: currentRoom.value.id,
          target: userId
        });

        // 添加到已邀请列表
        invitedUsers.value.push(userId);

      } catch (error) {
        console.error('邀请失败:', error);
      }
    };

    // 重置邀请对话框
    const resetInviteDialog = () => {
      showInviteDialog.value = false;
      searchResults.value = [];
      hasSearched.value = false;
    };

    const inviteFriend = async (friendId) => {
      try {
        // 确保有房间ID和好友ID
        if (!currentRoom.value.id || !friendId) {
          console.error('Missing required parameters for invitation');
          return;
        }

        // 显示加载状态
        const targetFriend = onlineFriends.value.find(f => f.id === friendId);
        if (!targetFriend) return;

        // 发送邀请WebSocket消息
        sendMessage({
          action: 'invite_player',
          room_id: currentRoom.value.id,
          target: friendId
        });

        // 临时禁用邀请按钮
        targetFriend.isInvited = true;

        // 3秒后重置邀请状态
        setTimeout(() => {
          if (targetFriend) {
            targetFriend.isInvited = false;
          }
        }, 3000);

      } catch (error) {
        console.error('邀请失败:', error);
      }
    };


    // 获取选中的人信息
    const fetchSelectedProfile = async (userId) => {
      try {
        const avatarResponse = await api.get(`/api/accounts/avatar/${userId}/`);
        const userResponse = await api.get(`/api/accounts/public_info/${userId}/`);

        if (userResponse.status === 200) {
          const userData = userResponse.data;
          return {
            userId: userData.id,
            name: userData.username,
            avatar: avatarResponse.status === 200
              ? avatarResponse.data.avatar_url
              : require('@/assets/profile-icon.png'),
            isOnline: true, // 这里可以从websocket获取在线状态
            isFriend: checkIsFriend(userId), // 这里可以从好友列表判断
            stats: [
              { label: '游戏场数', value: userData.profile.wins + userData.profile.loses },
              { label: '胜率', value: calculateWinRate(userData.profile.games) },
              { label: '评分', value: userData.profile.rating || 0 }
            ],
            recentGames: (userData.profile.recent_games || []).map((game, index) => ({
              id: index.toString(),
              result: game.won ? 'win' : 'lose',
              date: new Date(game.date).toLocaleDateString()
            }))
          };
        }
      } catch (error) {
        console.error('获取用户信息失败:', error);
        return null;
      }
    };

    // 辅助函数：计算胜率
    const calculateWinRate = (games) => {
      if (!games || games.length === 0) return '0%';
      const wins = games.filter(game => game.won).length;
      return `${Math.round((wins / games.length) * 100)}%`;
    };

    // 处理新玩家加入
    async function handlePlayerJoined(data){

      // 检查是否是当前房间
      if (data.room.id !== roomData.value.id) return;

      // 更新房间信息
      currentRoom.value = {
        ...currentRoom.value,
        players: data.room.players,
        currentPeople: data.room.players.length + Object.keys(data.room.ai_players || {}).length
      };

      // 找出当前成员列表中没有的新玩家
      const newJoinedPlayers = data.room.players.filter(
        playerId => !members.value.some(member => member.id === playerId)
      );
      // 为每个新玩家获取信息并添加到成员列表
      for (const newPlayerId of newJoinedPlayers) {
        const profile = await fetchSelectedProfile(newPlayerId);
        if (profile) {
          members.value.push({
            id: newPlayerId,
            name: profile.name,
            avatar: profile.avatar,
            isAI: false,
            userId: newPlayerId,
            isOnline: true,
            stats: profile.stats
          });
        }
      }

      // 遍历members，确保其中没有重复的玩家
      members.value = members.value.filter((member, index, self) =>
        index === self.findIndex(m => m.id === member.id)
      );

    }

    // 处理玩家离开
    async function handlePlayerLeft(data) {
      // 检查是否是当前房间
      if (data.room.id !== currentRoom.value.id) {
        return;
      }

      // 找出离开的玩家
      const leftPlayerId = currentRoom.value.players.find(
        id => !data.room.players.includes(id)
      );

      // 如果离开的玩家是自己，跳转到大厅
      if (leftPlayerId === userProfile.value.userId) {
        router.push('/GameLobby');
        return;
      }

      // 从成员列表中移除离开的玩家
      members.value = members.value.filter(member => member.id !== leftPlayerId);

      // 更新房间玩家列表和人数
      currentRoom.value = {
        ...currentRoom.value,
        players: data.room.players,
        currentPeople: data.room.players.length + Object.keys(data.room.ai_players || {}).length
      };

      // 检查是否是房主离开
      if (data.room.owner !== currentRoom.value.owner) {
        // 获取新房主信息并更新
        const newOwnerProfile = await fetchSelectedProfile(data.room.owner);
        if (newOwnerProfile) {
          hostProfile.value = {
            name: newOwnerProfile.name,
            avatar: newOwnerProfile.avatar,
            isOnline: newOwnerProfile.isOnline,
            stats: newOwnerProfile.stats
          };
        }

        // 如果当前用户成为新房主，更新UI相关状态
        if (data.room.owner === userProfile.value.userId) {
          // 例如显示房主特有的操作按钮等
          isHost.value = true;
        }
      }
    }

    const addAIPlayer = () => {
      if (!currentRoom.value || !isHost.value) return;

      const aiName = `AI_${aiCounter.value}`;

      sendMessage({
        action: "add_ai_player",
        room_id: currentRoom.value.id,
        player_info: {
          name: aiName
        }
      });
      aiCounter.value += 1;
    };

    // Method to remove AI player
    const removeAIPlayer = (playerId) => {
      if (!currentRoom.value || !isHost.value) return;


      sendMessage({
        action: "remove_ai_player",
        room_id: currentRoom.value.id,
        player_id: playerId
      });
      aiCounter.value -= 1;
    };

    const handleAIPlayerJoined = (data) => {

      if (data.room.id !== currentRoom.value.id) return;

      const aiPlayers = data.room.ai_players || {};

      const aiMembers = Object.entries(aiPlayers).map(([id, info]) => ({
        id,
        name: info.name,
        avatar: require("@/assets/ai.svg"),
        isAI: true,
        userId: id,
        isOnline: true
      }));


      const nonAiMembers = members.value.filter(m => !m.isAI);
      members.value = [...nonAiMembers, ...aiMembers];

      currentRoom.value = {
        ...currentRoom.value,
        aiPlayers,
        currentPeople: data.room.players.length + Object.keys(aiPlayers).length
      };
    };

    const handleAIPlayerLeft = (data) => {
      if (data.room.id !== currentRoom.value.id) return;

      const aiPlayers = data.room.ai_players || {};

      members.value = members.value.filter(member => {
        if (member.isAI) {
          return Object.keys(aiPlayers).includes(member.id);
        }
        return true;
      });

      currentRoom.value = {
        ...currentRoom.value,
        aiPlayers,
        currentPeople: data.room.players.length + Object.keys(aiPlayers).length
      };
    };

    const setupWebsocketListeners = () => {

      // 处理玩家加入
      const playerJoinedCleanup = onType('player_joined', handlePlayerJoined);

      // 处理玩家离开
      const playerLeftCleanup = onType('player_left', handlePlayerLeft);

      const aiPlayerJoinedCleanup = onType('ai_player_joined', handleAIPlayerJoined);
      const aiPlayerLeftCleanup = onType('ai_player_left', handleAIPlayerLeft);

      // 处理开始游戏
      const gameStartedCleanup = onType('game_prepared', (data) => {
        // TODO: 存储房间信息
        // 跳转到游戏界面

        // 确保是当前房间
        if (data.room.id === currentRoom.value.id) {
          router.push({
            name: 'GameInterface',
            params: {id: data.room.id}
          });
        }
      });

      // 处理房间被移除
      const roomRemovedCleanup = onType('room_removed', (data) => {
        if (data.room.id === currentRoom.value.id) {
          router.push('/GameLobby');
        }
      });

      // 处理房间更新
      const roomUpdatedCleanup = onType('room_updated', (data) => {
        if (data.room.id === currentRoom.value.id) {

          const currentConfig = ROLE_CONFIGS[currentRoom.value.max_players];
          currentRoom.value = {
            ...currentRoom.value,
            title: data.room.title,
            description: data.room.description,
            max_players: data.room.max_players,
            type: data.room.allow_ai_players ? "有AI" : "无AI",
            roleConfig: currentConfig,
          };
          // 同步更新编辑表单数据
          editRoomForm.value = {
            title: data.room.title,
            description: data.room.description,
            max_players: data.room.max_players,
            allowAI: data.room.allow_ai_players ? "有AI" : "无AI",
            roleConfig: currentConfig
          };

          // 如果设置为无AI，清除所有AI玩家
          if (!data.room.allow_ai_players) {
            members.value = members.value.filter(member => !member.isAI);
            currentRoom.value.aiPlayers = {};
            currentRoom.value.currentPeople = data.room.players.length;
            aiCounter.value = 1;
          }

        }
      });

      // 返回清理函数
      onUnmounted(() => {
        gameStartedCleanup();
        playerJoinedCleanup();
        playerLeftCleanup();
        roomRemovedCleanup();
        roomUpdatedCleanup();
        aiPlayerJoinedCleanup();
        aiPlayerLeftCleanup();
      });
    }


    // 离开房间
    const leaveRoom = () => {
      if (currentRoom.value) {
        sendMessage({
          action: 'leave_room',
          room_id: currentRoom.value.id
        });
        router.push('/GameLobby');
      }
    };

    // 销毁房间
    const removeRoom = () => {
      if (!isHost.value || !currentRoom.value) return;

      // 显示确认弹窗
      dialogTitle.value = '销毁房间';
      dialogMessage.value = '确定要销毁这个房间吗？此操作不可撤销。';
      dialogShowConfirm.value = true;
      currentDialogAction.value = 'removeRoom';
      showDialog.value = true;
    };

    // 处理弹窗确认
    const handleDialogConfirm = () => {
      if (currentDialogAction.value === 'removeRoom') {
        // 执行销毁房间操作
        if (currentRoom.value) {
          sendMessage({
            action: 'remove_room',
            room_id: currentRoom.value.id
          });
        }
        router.push('/GameLobby');
      }

      if (currentDialogAction.value === 'editRoom') {
        // 发送编辑房间的消息
        sendMessage({
          action: "edit_room",
          room_id: currentRoom.value.id,
          allow_ai_players: editRoomForm.value.allowAI === "有AI",
          max_players: editRoomForm.value.max_players,
          title: editRoomForm.value.title,
          description: editRoomForm.value.description
        });
      }
      showDialog.value = false;
    };

    // 处理弹窗取消
    const handleDialogCancel = () => {
      showDialog.value = false;
    };

    // 保存房间设置
    const saveRoomSettings = async () => {
      if (!isHost.value || !currentRoom.value) return;

      try {
        dialogTitle.value = '更新房间';
        dialogMessage.value = '确定要更新这个房间吗？';
        dialogShowConfirm.value = true;
        currentDialogAction.value = 'editRoom';
        showDialog.value = true;

      } catch (error) {
        console.error('保存房间设置失败:', error);
        // 可以添加错误提示
      }
    };


    onMounted(() => {
      // 只在未连接时初始化连接
      if (!isLobbyConnected.value) {
        connect();
      }
      initializeRoom();
      fetchFriendsList();
      setupWebsocketListeners();
    });

    onUnmounted(() => {

    });

    function refreshOnline() {
      // 刷新在线状态
      // 发个消息
      fetchFriendsList();
    }

    const handleOnlineFriends = (message) => {
      // 刷新在线好友
      const onlineList = message.friends;
      const allFriendsList = [...onlineFriends.value, ...offlineFriends.value];
      onlineFriends.value = [];
      offlineFriends.value = [];
      for (const friend of allFriendsList) {
        if (onlineList.indexOf(friend.id) !== -1) {
          // 如果在线
          friend.lastSeen = "在线";
          onlineFriends.value.push(friend);
        } else {
          friend.lastSeen = "离线";
          offlineFriends.value.push(friend);
        }
      }
    };

    // 获取好友列表
    const fetchFriendsList = async () => {
      try {
        const response = await api.get('/api/accounts/friends/list/');
        const friendIds = response.data.friends;

        // 获取每个好友的详细信息
        const friendsDetails = await Promise.all(
            friendIds.map(async (friendId) => {
              try {
                const userResponse = await api.get(`/api/accounts/public_info/${friendId}/`);
                const avatarResponse = await api.get(`/api/accounts/avatar/${friendId}/`);

                return {
                  id: friendId,
                  name: userResponse.data.username,
                  avatar: avatarResponse.status === 200
                      ? avatarResponse.data.avatar_url
                      : require('@/assets/profile-icon.png'),
                  status: '在线', // 目前都显示为在线
                  lastSeen: '在线'
                };
              } catch (error) {
                console.error('获取好友信息失败:', error);
                return null;
              }
            })
        );

        // 过滤掉获取失败的好友信息
        onlineFriends.value = friendsDetails.filter(friend => friend !== null);
        offlineFriends.value = [];
        // 更新在线状态
        sendMessage({
          action: "get_friends"
        });
        onType('online_friends', handleOnlineFriends);

      } catch (error) {
        console.error('获取好友列表失败:', error);
      }
    };

    // 开始游戏方法
    const startGame = () => {
      if (!currentRoom.value || !isHost.value) return;

      sendMessage({
        action: "start_game",
        room_id: currentRoom.value.id
      });
      // TODO：可以加个弹窗，然后弹窗点确定后跳转到游戏界面

    };
    const getRoleCountMap = (roles) => {
      return roles.reduce((acc, role) => {
        acc[role] = (acc[role] || 0) + 1;
        return acc;
      }, {});
    };

    const getRoleColorClass = (role) => {
      const roleClassMap = {
        'Werewolf': 'role-werewolf',
        'Villager': 'role-villager',
        'Prophet': 'role-prophet',
        'Witch': 'role-witch',
        'Idiot': 'role-idiot'
      };
      return roleClassMap[role] || '';
    };

    const getRoleDisplayName = (role) => {
      const roleNameMap = {
        'Werewolf': '狼人',
        'Villager': '村民',
        'Prophet': '预言家',
        'Witch': '女巫',
        'Idiot': '白痴'
      };
      return roleNameMap[role] || role;
    };

    const getAvailableRoles = () => {
      const config = ROLE_CONFIGS[currentRoom.value.max_players];
      if (!config?.roles) return [];
      return Object.keys(config.roles); // 返回角色配置对象的键数组
    };


    return {
      checkIsFriend,
      sendFriendRequest,
      router,
      showInviteDialog,
      searchResults,
      hasSearched,
      invitedUsers,
      inviteFriend,
      debouncedSearch,
      handleInvite,
      resetInviteDialog,
      ROLE_COLOR_MAP,
      ROLE_NAME_MAP,
      roleCountMap,
      enableRolePriority,
      selectedPriorityRoles,
      getRoleCountMap,
      getRoleColorClass,
      getRoleDisplayName,
      getAvailableRoles,
      isLobbyConnected,
      isGameConnected,
      disconnect,
      currentRoom,
      hostProfile,
      members,
      selectedPlayerId,
      userProfile,
      onlineFriends,
      offlineFriends,
      refreshOnline,
      isHost,
      handleKickMember,
      leaveRoom,
      removeRoom,
      handleDialogConfirm,
      handleDialogCancel,
      showDialog,
      dialogTitle,
      dialogMessage,
      dialogShowConfirm,
      editRoomForm,
      saveRoomSettings,
      showCreateRoomPanel,
      addAIPlayer,
      removeAIPlayer,
      aiCounter,
      startGame,
    };
  },
  data() {
    return {


      roomType: "无AI", // 房间类型（默认无AI）

      selectedPeopleCount: 2, // 默认选中2人
      peopleOptions: [4, 6, 8, 12, 16], // 可选人数列表

      showMenuSidebar: false, // 控制侧边栏的显示与否
      showFriendsSidebar: false,
      showHistorySidebar: false,


      selectedRoom: null, // 用于控制显示哪个房间的个人资料卡

      //userProfile: null,
      newRoom: {
        title: `云想衣裳花想容的房间`,  // 这里需要替换实际的用户名
        description: "无",
        type: "无AI",
        currentPeople: 1,
        max_players: 2
      },

      // 当前房间信息
      currentRoom_test: {
        title: "示例房间",
        currentPeople: 3,
        max_players: 6,
        type: "无AI"
      },

      // 房主信息
      hostProfile_test: {
        name: "云想衣裳花想容",
        avatar: require("@/assets/profile-icon.png"),
        isOnline: true,
        stats: [
          {label: '游戏场数', value: 128},
          {label: '胜率', value: '76%'},
          {label: '评分', value: 4.8}
        ]
      },

      userProfile_test: {
        name: "云想衣裳花想容",
        avatar: require("@/assets/profile-icon.png"), // 使用require导入图片
        isOnline: true,
        isFriend: false,
        userId: "host",
        stats: [
          {label: '游戏场数', value: 128},
          {label: '胜率', value: '76%'},
          {label: '评分', value: 4.8}
        ],
        recentGames: [
          {id: 'g1', result: 'win', date: '2024-12-04'},
          {id: 'g2', result: 'win', date: '2024-12-03'},
          {id: 'g3', result: 'lose', date: '2024-12-03'}
        ]
      },

      // 成员列表
      members_test: [
        {
          id: 1,
          name: '玩家1',
          avatar: require("@/assets/profile-icon.png"),
          isAI: false,
          userId: 'user1',
          isOnline: true,
          isFriend: false,
          stats: [
            {label: '游戏场数', value: 85},
            {label: '胜率', value: '65%'},
            {label: '评分', value: 4.2}
          ],
          recentGames: [
            {id: 'm1', result: 'win', date: '2024-12-04'},
            {id: 'm2', result: 'lose', date: '2024-12-03'}
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
            {label: '游戏场数', value: 85},
            {label: '胜率', value: '65%'},
            {label: '评分', value: 4.2}
          ],
          recentGames: [
            {id: 'm1', result: 'win', date: '2024-12-04'},
            {id: 'm2', result: 'lose', date: '2024-12-03'}
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
            {label: '游戏场数', value: 85},
            {label: '胜率', value: '65%'},
            {label: '评分', value: 4.2}
          ],
          recentGames: [
            {id: 'm1', result: 'win', date: '2024-12-04'},
            {id: 'm2', result: 'lose', date: '2024-12-03'}
          ]
        }
      ],

      // 选中的玩家ID (用于显示资料卡)
      selectedPlayerId_test: null,

    };
  },
  computed: {
    // 计算是否需要更多玩家
    needMorePlayers() {
      return this.currentRoom.currentPeople < this.currentRoom.max_players;
    },

    // 计算还需要多少玩家
    requiredPlayers() {
      return this.currentRoom.max_players - this.currentRoom.currentPeople;
    }
  },

  methods: {

    displayName(name) {
      if (typeof name === 'string') {
        return name;
      } else if (typeof name === 'object' && name !== null && 'name' in name) {
        return name.name;
      } else {
        // 如果name既不是字符串也不是包含name属性的对象，可以返回一个默认值或者错误信息
        return 'Invalid name';
      }
    },


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
    closeALL() {
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
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  padding: 16px;
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
  height: 100%;
  display: flex;
  flex-direction: column;
}

.friends-list.hidden {
  transform: translateX(100%);
  opacity: 0;
}

.friends-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 32px; /* 增加底部间距 */
}

.refresh-btn {
  background: transparent;
  border: none;
  padding: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.refresh-btn:hover {
  background: #f3f4f6;
  transform: rotate(180deg);
}

.refresh-btn img {
  width: 20px;
  height: 20px;
  filter: invert(45%) sepia(50%) saturate(1000%) hue-rotate(190deg) brightness(90%) contrast(95%);
}

/* 刷新按钮旋转动画 */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.refresh-btn:active img {
  animation: spin 0.6s linear;
}

.friends-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.friends-title {
  font-size: 20px;
  color: #2c3e50;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.friends-subtitle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e8eaf6;
}

.subtitle-text {
  font-size: 16px;
  color: #3949ab;
  font-weight: 500;
}

.friend-count {
  font-size: 14px;
  color: #5c6bc0;
  font-weight: normal;
}

.friend-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.friend-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 12px;
  background: #f8fafc;
  transition: all 0.2s ease;
  border: 1px solid #e8eaf6;
}

.friend-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.friend-item.online {
  background: #f3f6fd;
}

.friend-item.offline {
  background: #fafafa;
}

.friend-avatar {
  position: relative;
  margin-right: 12px;
}

.friend-avatar img {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  object-fit: cover;
}

.status-dot {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.status-dot.online {
  background: #10b981;
}

.status-dot.offline {
  background: #9ca3af;
}

.friend-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.friend-name {
  font-size: 16px;
  font-weight: 600;
  color: #1a237e;
}

.friend-status {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.friend-status.online {
  color: #10b981;
}

.friend-status.offline {
  color: #6b7280;
}

.invite-btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  position: relative;
  overflow: hidden;
}

.invite-btn:disabled {
  background: linear-gradient(135deg, #93c5fd, #60a5fa);
  cursor: not-allowed;
}

.invite-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
  transition: 0.5s;
}

.invite-btn:not(:disabled):hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.invite-btn:not(:disabled):hover::before {
  left: 100%;
}

.invite-btn:disabled .invite-text {
  opacity: 0.7;
}

.invite-text {
  font-weight: 500;
  position: relative;
}

/* 添加动画效果 */
@keyframes successPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.invite-btn.success {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  animation: successPulse 0.3s ease;
}

.invite-btn:hover {
  background: linear-gradient(135deg, #3949ab, #3f51b5);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(63, 81, 181, 0.2);
}

.invite-text {
  font-weight: 500;
}

.no-friends {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.no-friends-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.no-friends-text {
  color: #9e9e9e;
  font-size: 16px;
  line-height: 1.5;
}

/* 房间列表头部布局 */
.room-list-header {
  position: relative; /* 添加相对定位 */
  display: flex;
  justify-content: center; /* 居中对齐 */
  align-items: center;
  margin-bottom: 24px;
  padding: 0 10px;
  height: 50px;
}

.title-section {
  margin-top: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.leave-room-btn {
  position: absolute;
  left: 20px;
  background: transparent;
  border: none;
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 1; /* 确保按钮在标题上层 */
}

.leave-room-btn img {
  width: 24px;
  height: 24px;
  /* 使用适合的颜色, 例如蓝色系 */
  filter: invert(45%) sepia(50%) saturate(1000%) hue-rotate(190deg) brightness(90%) contrast(95%);
}

.leave-room-btn:hover {
  transform: scale(1.1);
}

/* 控制按钮区域 */
.control-buttons {
  position: absolute;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1; /* 确保按钮在标题上层 */
}

.remove-room-btn {
  background: transparent;
  border: none;
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.remove-room-btn img {
  width: 24px;
  height: 24px;
  /* 使用偏红色的颜色 */
  filter: invert(50%) sepia(75%) saturate(5000%) hue-rotate(330deg) brightness(90%) contrast(95%);
}

.remove-room-btn:hover {
  transform: scale(1.1);
}

/* 房间标题样式调整 */
.room-title {
  text-align: center;
  font-family: 'Roboto', sans-serif;
  font-weight: 800; /* 字体粗细 */
  font-size: 32px; /* 调整字体大小 */
  letter-spacing: 2px; /* 字符间距 */
  color: #2c3e50;
  margin: 0;
  position: absolute; /* 使用绝对定位 */
  left: 50%;
  transform: translateX(-50%); /* 确保完全居中 */
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

/* 房间描述样式 */
.room-description {
  text-align: center;
  font-size: 16px;
  color: #64748b;
  margin-bottom: 10px;
  padding: 0 20px;
}

/* 房间ID样式 */
.room-id {
  position: absolute;
  bottom: 16px;
  right: 16px;
  font-size: 12px;
  color: #94a3b8;
  font-family: monospace;
  opacity: 0.8;
}

/* 调整room-list以适应绝对定位的room-id */
.room-list {
  position: relative;
  padding-bottom: 40px; /* 为room-id留出空间 */
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

.action-btn img {
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

textarea.setting-control {
  resize: vertical;
  min-height: 80px;
}

.form-group {
  margin-bottom: 20px;
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

.save-settings-btn.disabled {
  background: #9ca3af;
  cursor: not-allowed;
  pointer-events: none;
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

.role-config-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid #e2e8f0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #2c3e50;
  font-size: 1.2em;
  margin-bottom: 16px;
}

.section-icon {
  width: 24px;
  height: 24px;
}

.role-display {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.role-count-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.role-count-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.9em;
}

/* 角色颜色类 */
.role-werewolf {
  background: #fee2e2;
  color: #991b1b;
}

.role-villager {
  background: #e0e7ff;
  color: #3730a3;
}

.role-prophet {
  background: #fef3c7;
  color: #92400e;
}

.role-witch {
  background: #f3e8ff;
  color: #6b21a8;
}

.role-idiot {
  background: #dcfce7;
  color: #166534;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #cbd5e1;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: .4s;
}

.switch input:checked + .slider {
  background-color: #3b82f6;
}

.switch input:checked + .slider:before {
  transform: translateX(24px);
}

.slider.round {
  border-radius: 24px;
}

.slider.round:before {
  border-radius: 50%;
}

.priority-selection {
  margin-top: 12px;
}

.priority-roles {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.role-checkbox {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.role-checkbox input {
  margin-right: 6px;
}

.witch-items-section {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
}

.witch-items-section h4 {
  margin: 0 0 16px 0;
  color: #2c3e50;
}

.witch-items-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.witch-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.item-icon {
  width: 24px;
  height: 24px;
}

.item-name {
  color: #4b5563;
}

.item-count {
  margin-left: auto;
  color: #2563eb;
  font-weight: 500;
}

:root {
  --base-unit: min(1vh, 1vw);
  --min-width: 320px;
  --max-width: 1920px;
}

/* 顶部工具栏 */
.top-bar {
  height: min(5vh, 60px);
  min-height: 40px;
  padding: min(10px, 1vw) min(20px, 2vw);
}

.icon-button {
  margin-right: min(20px, 2vw);
}

/* 侧边栏 */
.sidebar {
  width: min(250px, 25vw);
  min-width: 200px;
  padding: min(20px, 2vw);
}

/* 房间容器 */
.room-container {
  padding: min(20px, 2vw);
  gap: min(20px, 2vw);
}

/* 玩家头像和信息 */
.player-avatar img {
  width: min(64px, 6vw);
  height: min(64px, 6vw);
  min-width: 48px;
  min-height: 48px;
}

.host-avatar img {
  width: min(80px, 8vw);
  height: min(80px, 8vw);
  min-width: 60px;
  min-height: 60px;
}

.members-grid {
  gap: min(20px, 2vw);
  padding: min(16px, 1.5vw);
}

/* 按钮样式 */
.action-btn {
  padding: min(12px, 1.2vw);
  gap: min(8px, 0.8vw);
  min-height: 40px;
}

.start-game-btn {
  padding: min(16px, 1.5vw);
  font-size: min(18px, 1.8vw);
}

/* 好友列表 */
.friends-list {
  width: min(400px, 30vw);
  min-width: 280px;
  padding: min(24px, 2.4vw);
}

.friend-avatar img {
  width: min(48px, 4.8vw);
  height: min(48px, 4.8vw);
  min-width: 36px;
  min-height: 36px;
}

/* 创建房间面板 */
.create-room {
  width: min(400px, 40vw);
  min-width: 300px;
  padding: min(24px, 2.4vw);
}

/* 标题和文本大小 */
.room-title {
  font-size: min(32px, 3.2vw);
}

.room-description {
  font-size: min(16px, 1.6vw);
}

.section-title {
  font-size: min(20px, 2vw);
}

/* 个人资料卡 */
.profile-card {
  width: min(240px, 25vw);
  min-width: 200px;
}

.large-avatar {
  width: min(80px, 8vw) !important;
  height: min(80px, 8vw) !important;
  min-width: 60px !important;
  min-height: 60px !important;
}

/* 角色配置部分 */
.role-count-grid {
  grid-template-columns: repeat(auto-fill, minmax(min(120px, 15vw), 1fr));
  gap: min(12px, 1.2vw);
}

/* 女巫道具部分 */
.witch-items-grid {
  gap: min(16px, 1.6vw);
}

/* 按钮和图标大小 */
.action-icon {
  width: min(14px, 1.4vw);
  height: min(14px, 1.4vw);
  min-width: 12px;
  min-height: 12px;
}

.btn-icon {
  width: min(20px, 2vw);
  height: min(20px, 2vw);
  min-width: 16px;
  min-height: 16px;
}

/* 响应式布局调整 */
@media (max-width: 768px) {
  .room-container {
    flex-direction: column;
  }

  .friends-list {
    width: 100%;
  }

  .create-room {
    width: 100%;
  }

  .role-count-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .witch-items-grid {
    grid-template-columns: 1fr;
  }
}

/* 确保内容不会过小 */
.setting-control {
  min-height: min(40px, 4vh);
  padding: min(10px, 1vw);
}

textarea.setting-control {
  min-height: min(80px, 8vh);
}

.form-group {
  margin-bottom: min(20px, 2vh);
}

/* 动作按钮最小尺寸 */
.invite-btn {
  min-height: 36px;
  padding: min(8px, 0.8vw) min(16px, 1.6vw);
}

.refresh-btn {
  min-width: 32px;
  min-height: 32px;
}

/* 设置面板间距 */
.settings-section {
  padding: min(20px, 2vw);
  margin-bottom: min(24px, 2.4vh);
}
</style>
