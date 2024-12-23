<template>
    <div class="game-container"
         @click="closeALL">

      <!-- 左侧玩家列表 -->
      <div class="player-list" v-if="Boolean(players && aiPlayers)">
        <!-- 使用 Object.values() 将对象的值转换为数组，并确保通过 .value 访问 ref 的值 -->
        <div v-for="(player, index) in [...Object.values(players), ...Object.values(aiPlayers)].sort((a, b) => a.index - b.index)" :key="index"
             :class="['player-container', { 'selected-player': index + 1 === selectedPlayer }]">
            <div class="player" :class="{ 'dead': ![...Object.values(gameData.players), ...Object.values(gameData.ai_players)].sort((a, b) => a.index - b.index)[index].alive }">
              <img
                :src="player.avatar"
                alt="avatar"
                class="avatar0"
                @click.stop="showPlayerProfile(player.userId, player)"
              />
              <div class="player-name-container">
                <p>
                  {{ player.index }}号{{" "}}{{ player.name }}
                  <span v-if="player.userId === currentPlayer.userId"> (你)</span>
                </p>
                  <!-- 发言提示 -->
                  <div
                    v-if="gameData.current_phase === 'Speak' && String(index + 1) === currentSpeakingPlayer"
                    class="speaking-status"
                  >
                    <img
                      src="@/assets/speaking.svg"
                      alt="speaking"
                      class="speaking-icon"
                    />
                    <span class="speaking-indicator-text">发言中</span>
                  </div>

              </div>
              <!-- 添加个人资料卡弹窗 -->
              <transition name="profile">
                <div v-if="selectedProfileId === player.userId" class="profile-card" @click.stop>
                  <div class="profile-header">
                     <img :src="selectedProfile.avatar"
                        alt="头像"
                        class="large-avatar"/>
                    <div class="profile-info">
                      <h4>{{ selectedProfile.name }}</h4>
                      <span class="profile-status" :class="{'online': selectedProfile.isOnline}">
                        {{ selectedProfile.isOnline ? '在线' : '离线' }}
                      </span>
                    </div>
                  </div>
                  <div class="profile-stats">
                    <div v-for="(stat, index) in selectedProfile.stats"
                        :key="index"
                        class="stat-item">
                      <span class="stat-value">{{ stat.value }}</span>
                      <span class="stat-label">{{ stat.label }}</span>
                    </div>
                  </div>
                  <div class="profile-actions">
                    <button class="action-btn add-friend-btn"
                            @click="sendFriendRequest(selectedProfile.userId)"
                            :disabled="selectedProfile.isFriend">
                      <img src="@/assets/addFriend.svg" alt="加好友" class="action-icon"/>
                      {{ selectedProfile.isFriend ? '已是好友' : '加好友' }}
                    </button>
                  </div>
                  <div class="recent-games">
                    <h5>最近对战</h5>
                    <div class="game-list">
                      <div v-for="game in selectedProfile.recentGames"
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
              <!-- 同步目标显示 -->
              <div class="sync-targets-wrapper" v-if="syncTargets[String(index + 1)]">
                <div class="sync-targets-content">
                  <!-- 头像组 -->
                  <div class="teammate-avatars">
                    <div v-for="(teamMate, idx) in syncTargets[String(index + 1)]"
                         :key="idx"
                         class="teammate-number">
                      {{ teamMate }}
                    </div>
                  </div>
                  <!-- 提示文本 -->
                  <div class="sync-targets-tooltip">
                    {{ '队友' + syncTargets[String(index + 1)].join('号, ') + '号已选择此目标' }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <button
              v-if="Boolean(selectableIndices.indexOf(index + 1) !== -1 && selectablePhaseAction !== '' && !isDead)"
              class="target-button"
              @click.stop="targetPlayer(index + 1)"
            >
              <span class="button-content">
                <span class="button-text">{{ selectablePhaseAction }}</span>
                <span class="button-arrow">→</span>
              </span>
            </button>
          </div>
      </div>

      <!-- 确认选择按钮 -->
      <div
        class="confirm-button"
        v-if="selectablePhaseAction !== '' && !isDead"
        @click="confirmTarget"
      >
        确认选择
      </div>



      <!-- 中间聊天框 -->
      <div class="chat-section">
        <!-- 当前阶段显示 -->
        <div class="phase-display">
          <div class="phase-text">
            <GamePhase :phase="$translate(gameData.current_phase)" />
          </div>
        </div>
        <div class="chat-box" ref="chatBox" @scroll="handleScroll">
          <div class="chat-messages">
            <div  v-for="message in messages" :key="message.senderindex"
                   :class="['message', { 'system-message': message.senderindex === 0 }]">
                <!-- 系统消息使用不同的样式 -->
                <template v-if="message.senderindex === 0">
                  <div class="system-message-content">
                    <div class="system-message-text">{{ message.text }}</div>
                  </div>
                </template>
                <!-- 玩家消息保持原有样式 -->
                <template v-else>
                  <div class="message-avatar-container">
                    <div class="message-avatar">
                      <img :src="message.avatar" alt="avatar" class="avatar1"/>
                    </div>
                    <span class="recipient-label">
                      <div class="message-sender">
                        <p>
                          {{ message.senderindex }}号{{" "}}{{ message.sendername }}
                          <span v-if="message.senderindex === currentPlayer.userId"> (你)</span>
                        </p>
                      </div>
                    </span>
                  </div>
                  <div class="message-content">
                    <div class="message-text">{{ message.text }}</div>
                  </div>
                </template>
            </div>
          </div>

          <!-- 滚动到底部按钮 -->
          <div class="scroll-bottom-wrapper">
            <div v-if="showScrollButton" class="scroll-bottom-button" @click="scrollToBottom">
              <img src="@/assets/toBottom.svg" alt="滚动到底部" class="scroll-bottom-icon" />
              <div v-if="hasUnreadMessages" class="unread-indicator"></div>
            </div>
          </div>
        </div>


        <!-- 输入框和发送按钮在聊天框外部 -->
        <div class="message-input-section">
          <!-- 结束发言按钮 -->
          <!-- TODO: 需要美化 -->
          <button @click="handleTalkEnd" class="end-talk-button" v-if="talkStart">
            <span class="button-text"> {{returnButtonText}} </span>
          </button>
          <input
            v-model="userMessage"
            @keyup.enter="sendChatMessage"
            placeholder="输入消息"
            class="message-input"
          />
          <!-- 图标按钮 -->
          <button @click="sendChatMessage" class="send-button" :disabled="!talkStart">
            <img class="send-icon" src="@/assets/send.svg" alt="发送图标" /> <!-- 或者使用一个自定义图标图片 -->
          </button>


        </div>
      </div>

      <!-- 大图标，显示在右上角 -->
      <div class="sun-moon-icon">
        <img :src="currentIcon"
             :alt="isDayTime ? 'Day Time' : 'Night Time'"
             class="sun-moon-icon-img" />
      </div>


      <!-- 右侧信息区域容器 -->
      <div class="right-info-container">
        <!-- 倒计时器 -->
        <CountdownTimer
          :seconds="timerSeconds"
          :initial-seconds="gameData.phase_timer[gameData.current_phase]"
        />
      <!-- 右侧角色信息 -->
      <div class="role-info">
        <div class="role-item">
            <span class="label">你的身份：</span>
            <span class="value" style="font-size: 1.3em; font-weight: bold;">{{ $translate(roleInfo.role) }}</span>
        </div>
        <div class="role-item">
            <span class="label">阵营目标：</span>
            <span class="value">{{ roleGoalsConfig[roleInfo.role] }}</span>

        </div>

        <div class="role-item" v-if="roleInfo.teammates">
            <span class="label">存活队友：</span>
            <span class="value">{{ roleInfo.teammates.map(number => `${number}号`).join('，') }}</span>
        </div>
        <!-- 角色能力图标部分 -->
        <div class="role-abilities">

          <div class="abilities-container" v-if="roleInfo">
            <!-- 动态显示技能图标 -->
            <template v-for="ability in roleAbilitiesConfig[roleInfo.role]" :key="ability.id">
              <!-- 如果当前技能数量为0，仍然继续显示 -->
              <div class="ability-item">
                <img 
                  :src="require(`@/assets/${ability.icon}`)" 
                  :alt="ability.name"
                  class="ability-icon"
                  :title="ability.description"
                />
                <div class="ability-info">
                  <span class="ability-name">{{ ability.name }}</span>
                  <span class="ability-count" v-if="ability.hasCount">
                    剩余：{{ roleInfo.role_skills[ability.id + '_count'] }}
                  </span>
                </div>
              </div>
            </template>
          </div>
        </div>
    </div>
      </div>
      <!--  弹出查验结果   -->
      <ConfirmDialog
      :show="showDialog"
      :title="dialogTitle"
      :message="dialogMessage"
      :showConfirm="dialogShowConfirm"
      @confirm="handleDialogConfirm"
      @cancel="handleDialogCancel"
    />
      <!-- 系统通知组件 -->
      <SystemNotice
        v-if="currentNotification"
        v-bind="currentNotification"
        @close="closeNotification"
      />


    </div>

    <!-- 配置按钮 -->
    <button
      @click="toggleRoleConfig"
      class="config-toggle-button"
      title="查看角色配置"
    >
      <img src="@/assets/config.svg" alt="配置" class="config-icon" />
    </button>

    <!-- 配置面板 -->
    <transition name="slide-config">
      <div v-if="showRoleConfig" class="role-config-panel">
        <div class="role-config-header">
          <h3>角色配置 ({{ gameData.max_players }}人局)</h3>
          <button @click="toggleRoleConfig" class="close-config-button">
            <span>×</span>
          </button>
        </div>

        <div class="role-config-content">
          <!-- 角色分布 -->
          <div class="config-section">
            <h4 class="section-title">角色分布</h4>
            <div class="roles-grid">
              <div v-for="(count, role) in roleConfigs[gameData.max_players].roles"
                   :key="role"
                   :class="['role-item', { 'current-player': role === roleInfo.role }]">
                <div class="role-icon-name">
                  <img :src="getRoleIcon(role)"
                       :alt="roleNames[role]"
                       class="role-svg-icon" />
                  <span class="role-name">{{ roleNames[role] }}</span>
                </div>
                <span class="role-count">× {{ count }}</span>
              </div>
            </div>
          </div>

          <!-- 女巫道具 -->
          <div class="config-section" v-if="roleConfigs[gameData.max_players].witchItems">
            <h4 class="section-title">女巫道具</h4>
            <div class="items-grid">
              <div class="item">
                <div class="item-icon-name">
                  <img src="@/assets/cure.svg" alt="解药" class="item-svg-icon" />
                  <span class="item-name">解药</span>
                </div>
                <span class="item-count">× {{ roleConfigs[gameData.max_players].witchItems.cure }}</span>
              </div>
              <div class="item">
                <div class="item-icon-name">
                  <img src="@/assets/poison.svg" alt="毒药" class="item-svg-icon" />
                  <span class="item-name">毒药</span>
                </div>
                <span class="item-count">× {{ roleConfigs[gameData.max_players].witchItems.poison }}</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </transition>
  </template>

<script>
import {onMounted, ref, onUnmounted, onBeforeMount,} from 'vue';
import { getCurrentInstance } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { useWebSocket } from '@/composables/useWebSocket';
import SystemNotice from './shared_components/SystemNotice.vue';
import GamePhase from './shared_components/GamePhase.vue';
import CountdownTimer from './shared_components/CountdownTimer.vue';
// import { validateGame } from '@/schemas/schemas.js';
import axios from 'axios';
import ConfirmDialog from "@/components/shared_components/ConfirmDialog.vue";


const router = useRouter();
// 创建axios实例
const api = axios.create({
  baseURL: '/'
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
        const response = await axios.post('api/token/refresh/', {
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
        router.push('/login');  // 跳转到登录页面
        
        // 可以添加一些用户提示信息，提醒用户重新登录
        alert('您的会话已过期，请重新登录。');
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);


export default {
  components: {
    ConfirmDialog,
    SystemNotice,
    GamePhase,
    CountdownTimer,
  },
  data() {
    return {
      showRoleConfig: false,
      roleConfigs: {
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
        },
        8: {
          roles: {
            Werewolf: 3,
            Prophet: 1,
            Witch: 1,
            Idiot: 1,
            Villager: 2
          },
          witchItems: { cure: 1, poison: 1 },
        },
        12: {
          roles: {
            Werewolf: 4,
            Prophet: 1,
            Witch: 1,
            Villager: 6
          },
          witchItems: { cure: 2, poison: 2 }
        },
        16: {
          roles: {
            Werewolf: 6,
            Prophet: 1,
            Witch: 1,
            Villager: 8
          },
          witchItems: { cure: 2, poison: 2 }
        }
      },
      roleNames: {
        Werewolf: "狼人",
        Prophet: "预言家",
        Witch: "女巫",
        Villager: "平民",
        Idiot: "白痴"
      },

      showScrollButton: false,
      // 计时方式
      timer: null,
      // 角色能力配置
      roleAbilitiesConfig: {
        // Werewolf技能配置
        Werewolf: [
          {
            id: 'kill',
            name: '杀人',
            icon: 'kill.svg',
            description: '每晚可以杀死一名玩家',
            hasCount: false, // 无限次数的技能
          }
        ],
        // Witch技能配置
        Witch: [
          {
            id: 'cure',
            name: '解药',
            icon: 'cure.svg',
            description: '可以救活一名被杀的玩家',
            hasCount: true,
            count: 1
          },
          {
            id: 'poison',
            name: '毒药',
            icon: 'poison.svg',
            description: '可以毒死一名玩家',
            hasCount: true,
            count: 1
          }
        ],
        // Prophet技能配置
        Prophet: [
          {
            id: 'check',
            name: '查验',
            icon: 'prophet.svg',
            description: '每晚可以查验一名玩家的身份',
            hasCount: false
          }
        ],
        // Hunter技能配置
        Hunter: [
          {
            id: 'shoot',
            name: '开枪',
            icon: 'kill.svg',
            description: '死亡时可以开枪带走一名玩家',
            hasCount: true,
            count: 1
          }
        ],
        // Guard技能配置
        Guard: [
          {
            id: 'protect',
            name: '守护',
            icon: 'kill.svg',
            description: '每晚可以守护一名玩家',
            hasCount: false
          }
        ]
        // ... 可以继续添加其他角色的技能配置
      },
      roleGoalsConfig: {
        Werewolf: "杀死所有狼人之外的角色",
        Prophet: "使用查验结果引导村民，放逐所有狼人",
        Witch: "灵活利用解药与毒药，放逐所有狼人",
        Villager: "分辨好人与狼人，放逐所有狼人",
        Idiot: "引导他人投票将你放逐",
        Guard: "保护好阵营关键角色，放逐所有狼人",
      },
      userMessage: "",



      objective: "淘汰全部人类",
      victoryCondition: "再淘汰1名人类",
      livingTeammates: 0,
      showDetails: false,   // 控制显示详细信息

      showMenuSidebar: false, // 控制侧边栏的显示与否
      showFriendsSidebar: false,
      showHistorySidebar: false,

      playerDetailsTop: 0,  // 玩家详情框的top位置
      playerDetailsLeft: 0,  // 玩家详情框的left位置

      // （小）阶段标记
      phase: null,

      selectedShowPlayer: -1,

      // 日夜切换

      messageRecipient: "all", // 消息的接收者，默认为"所有人"

    };
  },


  setup() {
    const router = useRouter();

    const onlineFriends = ref( []);
    const offlineFriends = ref( []);

    const gameEnd = ref(false);


    // 处理弹窗取消
    const handleDialogCancel = () => {
      showDialog.value = false;
    };

    // 检查是否是好友
    const checkIsFriend = (userId) => {
      // 统一转换为字符串进行比较
      const targetId = String(userId);

      // 检查是否是自己
      if (targetId === String(userProfile.value.userId)) {
        return true;
      }

      // 检查好友列表，确保类型一致
      return onlineFriends.value.some(friend => String(friend.id) === targetId) ||
             offlineFriends.value.some(friend => String(friend.id) === targetId);
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


    const { proxy } = getCurrentInstance();
    const $translate = (text) => proxy.$translate(text);

    const selectedProfileId = ref(null); // 当前选中的玩家ID
    const selectedProfile = ref({
      userId: '',
      name: '',
      avatar: '',
      isOnline: false,
      isFriend: false,
      stats: [],
      recentGames: []
    });

    const showPlayerProfile = async (playerId, player) => {
      // 从使用序号改为使用userId
      if (selectedProfileId.value === player.userId) {
        selectedProfileId.value = null;
        return;
      }

      // 如果是AI玩家，显示基本信息
      if (player.isAI) {
        selectedProfile.value = {
          userId: player.userId, // AI的userId是uuid
          name: player.name,
          avatar: player.avatar,
          isOnline: true,
          isFriend: true,
          stats: [
            { label: '身份', value: 'AI玩家' },
          ],
          recentGames: []
        };
        selectedProfileId.value = player.userId;
        return;
      }

      // 获取玩家资料
      const profile = await fetchSelectedProfile(player.userId);
      if (profile) {
        selectedProfile.value = profile;
        selectedProfileId.value = player.userId; // 存储userId而不是序号
      }
    };


    const hasUnreadMessages = ref(false);
    // 弹窗以及websocket建立
    const store = useStore();
    
    // const router = useRouter();

    const roomData = ref(store.state.currentRoom);

    const userProfile = ref(store.state.userProfile);

    const token = localStorage.getItem('access_token');
    // 获取当前room
    const roomId = roomData.value.id;
    const { connectToGame, sendMessage, onType, disconnect, isLobbyConnected, isGameConnected } = useWebSocket(token);


    // 弹窗相关的状态
    const showDialog = ref(false);
    const dialogTitle = ref('');
    const dialogMessage = ref('');
    const dialogShowConfirm = ref(true);
    const currentDialogAction = ref('');

    const handleDialogConfirm = () => { showDialog.value = false; }

    // 消息列表
    const messages= ref([]);
    // 成员列表
    const players = ref({});
    const aiPlayers = ref({});
    const roleInfo = ref({
      role: "",
      role_skills: {},
      teammates: [],
    });

    // const selectedPlayerId = ref(null);
    const gameData = ref({
      id: "1c134013-3b54-4ccd-a2b9-e42ef088d9a9",
      title: "一个房间",
      description: "房间简介",
      max_players: 6,
      night_count: 1,
      roles: {},
      witch_config: {},
      players: {
          1: {
              index: "1",
              name: "apifox",
              alive: true,
              online: true
          }
      },
      ai_players: {
          "987ada2b-7263-4475-9864-77bf34ed0a1e": {
              index: "2",
              name: "AI",
              alive: true
          },
          "96fc46bf-c540-41a2-ad65-a123f586f4ac": {
              index: "3",
              name: "AI",
              alive: true
          },
          "aa561e5c-95f8-4d16-88fa-56f8ac78e1b5": {
              index: "4",
              name: "AI",
              alive: true
          },
          "010d703a-edd5-4390-b998-2c464321d3f6": {
              index: "5",
              name: "AI",
              alive: true
          },
          "57bf3e0a-ee1b-4772-83b9-155b4081e63e": {
              index: "6",
              name: "AI",
              alive: true
          }
      },
      current_phase: "Waiting",
      phase_timer: {
          Initialize: 1,
          Werewolf: 40,
          Prophet: 40,
          Witch: 40,
          Day: 3,
          Speak: 40,
          Vote: 40,
          End: 3,
          Cleanup: 120,
      }
    })

    // 其他狼人的投票
    const syncTargets = ref({});

    
    const currentPlayer = ref({
      userId: "",      // 添加 userId 字段
      index: "",       // 游戏中的序号
      name: "",
      alive: true,
      online: true
    });

    // 添加当前发言玩家的响应式引用
    const currentSpeakingPlayer = ref(null);

    // 计时器
    const timerSeconds = ref(10);
    // 一个用于管理select里面时间长度的变量，如果到时间结束会变成0（重置），点击结束则是会变成剩余时间
    const timeElapsed = ref(0);

    // 当前可选的角色，选中的角色，当前具体的选择阶段，是否确认选项
    const selectableIndices = ref([1, 2, 3]);
    const selectedPlayer = ref(-1);
    const selectablePhaseAction = ref("");
    const confirmed = ref(false);
    const isDayTime = ref(true);
    // 当前为你的发言阶段
    const talkStart = ref(false);
    // 你是否死亡
    const isDead = ref(false);

    const currentNotification = ref(null);  // 当前显示的通知

    // 添加处理通知的方法
    function sendSystemMessage(content) {
      // 创建聊天消息
      const chatMessage = {
        senderindex: 0,
        sendername: "系统信息: ",
        avatar: require('@/assets/head.png'),
        text: content,
        recipients: "all"
      };
      messages.value.push(chatMessage);



    }
    function sendNotification(content, type = 'info', subMessage = '', players = []){
      // 创建新通知
      currentNotification.value = {
        type: type,
        message: content,
        subMessage: subMessage,
        players: players,
      };
    }

    // 关闭通知的方法
    const closeNotification = () => {
      currentNotification.value = null;
    };

    // 通知玩家角色
    function handleRoleInfo(message) {
      // 获取角色中文名
      const roleNames = {
        'Werewolf': '狼人',
        'Witch': '女巫',
        'Prophet': '预言家',
        'Guard': '守卫',
        'Hunter': '猎人',
        'Villager': '村民'
      };

      // 获取角色技能说明
      const roleDescriptions = {
        'Werewolf': '每晚可以杀害一名玩家',
        'Witch': '拥有一瓶解药和一瓶毒药',
        'Prophet': '每晚可以查验一名玩家的身份',
        'Guard': '每晚可以守护一名玩家',
        'Hunter': '死亡时可以开枪带走一名玩家',
        'Villager': '没有特殊技能，靠推理找出狼人'
      };

      roleInfo.value = message.role_info;
      const roleName = roleNames[roleInfo.value.role] || roleInfo.value.role;
      const description = roleDescriptions[roleInfo.value.role] || '';

      sendSystemMessage(`你的角色是：${roleName}`);
      sendNotification(
          '你的角色是：${roleName}',
          'info',
          description,
      )
    }
    // 修改原有的系统消息处理方法
    function handleNightPhase(message) {
      // sendSystemMessage("天黑请闭眼");
      sendNotification("天黑请闭眼", "night")
      isDayTime.value = false;
      updateGame(message.game);
    }

    function handleDayPhase(message) {
      sendNotification("天亮请睁眼", "day");
      isDayTime.value = true;
      updateGame(message.game);
    }

    function handleNightDeathInfo(message) {
      const victims = message.victims;
      if (victims.length === 0) {
        sendNotification("昨晚是平安夜", "death");
      } else {
        // 获取死亡玩家的信息
        const deadPlayers = victims.map(index => {
          const player = [...Object.values(players.value), ...Object.values(aiPlayers.value)]
            .find(p => p.index === index);
          return {
            name: `${index}号 ${player.name}`,
            avatar: player.avatar
          };
        });

        sendNotification(
          "昨晚以下玩家被杀害：",
          "death",
          "",
          deadPlayers
        );
      }

      for (const victim of message.victims) {
        if (victim === currentPlayer.value.index) {
          sendNotification("你在这个晚上被杀死了", "death",
              "接下来你可以与其他死亡玩家聊天，静待阵营胜利");
          talkStart.value = true;
          isDead.value = true;
        }
      }
    }

    //
    function handleTalkStart(message) {

      currentSpeakingPlayer.value = message.player;

      if (currentPlayer.value.index === message.player){
        talkStart.value = true;
        sendNotification(
        `${currentPlayer.value.index}号玩家，轮到你发言`,
        "speak",
          "请在规定时间内发表意见",
        [],
      );
      }
      else {
        sendSystemMessage("接下来请" + message.player + "号玩家发言：")
      }
      gameData.value.current_phase = "Speak"
      timerSeconds.value = gameData.value.phase_timer[gameData.value.current_phase];
    }

    const fetchSelectedProfile = async (userId) => {
      try {
        const avatarResponse = await api.get(`/api/accounts/avatar/${userId}/`);
        const userResponse = await api.get(`/api/accounts/public_info/${userId}/`);

        if (userResponse.status === 200) {
          const userData = userResponse.data;
          return {
            userId: userData.id,
            name: userData.username,
            avatar: (avatarResponse.status === 200 && avatarResponse.data.avatar_url)
              ? avatarResponse.data.avatar_url
              : require('@/assets/profile-icon.png'),
            isOnline: true, // 这里可以从websocket获取在线状态
            isFriend: checkIsFriend(userId), // 这里可以从好友列表判断
            stats: [
              { label: '游戏场数', value: userData.profile.wins + userData.profile.loses },
              { label: '胜率', value: calculateWinRate(userData.profile.games) },
              //{ label: '评分', value: userData.profile.rating || 0 }
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

    let initialized = false;



    // 这里的信息以后就不动了
    const initializeGameInterface = async () => {

      if (!initialized){
        players.value = gameData.value.players;
        aiPlayers.value = gameData.value.ai_players;

        // 获取并设置所有玩家信息
        const playerProfiles = {};
        for (const playerId of Object.keys(gameData.value.players)) {
          const profile = await fetchSelectedProfile(playerId);
          playerProfiles[playerId] = {
            index: gameData.value.players[playerId].index,
            name: profile.name,
            avatar: profile.avatar,
            isAI: false,
            userId: playerId,
            isOnline: profile.isOnline,
            isFriend: profile.isFriend,
            stats: profile.stats,
            recentGames: profile.recentGames
            };

          if (String(userProfile.value.userId) === String(playerId)){
            currentPlayer.value = {
              userId: playerId,  // 添加 userId
              index: gameData.value.players[playerId].index,
              name: profile.name,
              alive: true,
              online: true
            };
          }
        }



        // 添加AI玩家信息
        const aiPlayerProfiles = {};

        for (const id of Object.keys(gameData.value.ai_players)) {
          aiPlayerProfiles[id] = {
            name: gameData.value.ai_players[id].name,
            index: gameData.value.ai_players[id].index,
            avatar: require("@/assets/ai.svg"),
            isAI: true,
            userId: id,
            isOnline: true,
            stats: []
          };
        }
        // 展开并合并所有玩家信息
        players.value = playerProfiles;
        aiPlayers.value = aiPlayerProfiles;
        initialized = true;

        // TODO: 添加对玩家自身信息的初始化
      }



    };

    // 工具函数，用于阶段转换时更新信息; 要求为GameData类型
    function updateGame(game){

      if (!game){
        console.error("gameData is false");
      }
      else {
        const prev_phase = gameData.value.current_phase;
        gameData.value = game
        if (prev_phase !== gameData.value.current_phase){
          timerSeconds.value = gameData.value.phase_timer[gameData.value.current_phase]
        }

      }

    }

    // 等待一定时间用工具函数
    const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // 投票用工具函数
    async function select(title, content, time, players, alive_as_target = false, select_self = false) {
      // players: List[str], str为序号
      selectablePhaseAction.value = content;

      selectableIndices.value = [];
      if (alive_as_target){  // 选择所有活着的人，除了自己
        for (const player of [...Object.values(gameData.value.players), ...Object.values(gameData.value.ai_players)]){

          if (player.alive && ((player.index !== currentPlayer.value.index) || select_self)){
            selectableIndices.value.push(Number(player.index));
          }
        }
      }
      else {  // 当前列表中的人
        for (const index of players){
          selectableIndices.value.push(Number(index));
        }
      }


      // 等待函数

      // 等待此阶段对应的时间
      for(let i=1; i<=time; i++){
        await wait(1000);
        if (confirmed.value){
          selectableIndices.value = [];
          confirmed.value = false;
          let tmp = selectedPlayer.value;
          selectedPlayer.value = -1
          selectablePhaseAction.value = ""
          // 将已经度过的时间提升
          timeElapsed.value += i;
          return tmp;
        }
      }

      // 不能再选了

      // 如果没选中，返回-1
      timeElapsed.value = 0;
      selectableIndices.value = [];
      let tmp = selectedPlayer.value;
      selectedPlayer.value = -1
      selectablePhaseAction.value = ""
      return tmp;
    }

    // 展示信息用工具函数
    function showInfo(title, content){
      // TODO: 美化，按网易的做？
      dialogTitle.value = title;
      dialogMessage.value = content;
      currentDialogAction.value = "showInfo";
      dialogShowConfirm.value = true;
      showDialog.value= true;
      return 0;
    }

    // 狼人投票方法
    function handleKillVote(seq_num){
      const actionToSend = {
        type: "kill_vote",
        target: String(seq_num)
      }
      if (seq_num === -1){
        actionToSend.target = null
      }
      sendMessage(actionToSend,
        "game")
      if (gameData.value.current_phase === "Werewolf" && roleInfo.value.role === "Werewolf"){
        handleMultipleKillVotes();
      }
      else {
        syncTargets.value = {};
        timeElapsed.value = 0;
      }
    }

    async function handleMultipleKillVotes(){
      if (gameData.value.current_phase === "Werewolf" && roleInfo.value.role === "Werewolf") {
        // 这里可能会被执行多次，所以要保证时间不会过长
        const killVoteTarget = await select("选择要杀死的目标", "杀死",
            gameData.value.phase_timer[gameData.value.current_phase] - timeElapsed.value, null, true, true);
        handleKillVote(killVoteTarget);
      }
    }

    // 预言家查人
    function handleCheck(seq_num){
      const actionToSend = {
        type: "check",
        target: String(seq_num)
      }
      if (seq_num === -1){
        actionToSend.target = null
      }
      sendMessage(actionToSend,
        "game")
    }

    // 女巫操作
    function handleWitchAction(cure_num, poison_num){
      const actionToSend = {
        type: "witch_action",
        cure: String(cure_num),
        poison: String(poison_num),
      }
      if (cure_num === -1){
        actionToSend.cure = null;
      }
      if (poison_num === -1){
        actionToSend.poison = null;
      }
      sendMessage(actionToSend,
        "game"
      );
    }
    function handleTalkEnd(){
      // 不能确定成功发过去了，所以等待服务器回消息再改为false
      // talkStart.value = false;

      if (gameEnd.value || isDead.value){
        handleRoomCleanup();
        router.push('/GameLobby');
        return;
      }

      const actionToSend = {
        type: "talk_end",
        player: currentPlayer.value.index,
      }
      sendMessage(actionToSend,
      "game")
    }


    // // 白天投票
    function handleVote(seq_num){
      const actionToSend = {
        type: "vote",
        target: String(seq_num),
      }
      if (seq_num === -1){
        actionToSend.target = null;
      }
      sendMessage(
          actionToSend,
          "game"
      )
    }


    /* WebSocket实时监听部分*/
    function handlePlayerJoined(message){
      // 有人加入，更新内容
      sendSystemMessage("玩家加入游戏");
      updateGame(message.game);
      // 进行初始化（如果还没有初始化过）
      initializeGameInterface();
    }


    async function handleKillPhase(message) {
      // 处理Werewolf投票阶段
      updateGame(message.game);
      if (roleInfo.value.role === "Werewolf") {
        sendNotification("狼人请行动", "action", "请选择要杀害的对象");
        await handleMultipleKillVotes();
      }
    }

    function handleWolfSync(message) {
      // 处理Werewolf投票同步
      const targetDict = {}
      for (const vote of Object.values(message.targets)){
        if (vote){
          // 对于每个存在的目标，建立一个列表
          targetDict[vote] = [];
        }
      }
      for (const wolf of Object.keys(message.targets)){
        if (message.targets[wolf]){  // 如果这只狼已经投票
          // 那么将这个狼人加入目标对应的列表中
          targetDict[message.targets[wolf]].push(wolf);
        }
      }
      syncTargets.value = targetDict;

    }

    function handleKillResult(message) {
      // 处理刀人结果
      if (message.kill_result){
        sendNotification( "今晚你们选择杀死" + message.kill_result + "号玩家");
        sendSystemMessage( "今晚你们选择杀死" + message.kill_result + "号玩家");
      }
    }

    function handleKillPhaseEnd(message) {
      // 刀人阶段结束的同步。
      updateGame(message.game);
    }

    async function handleCheckPhase(message) {
      // 处理Prophet查人阶段, 不能告诉他谁死了

      updateGame(message.game);
      if (roleInfo.value.role === "Prophet" && gameData.value.current_phase === "Prophet"){
        sendNotification("预言家请行动", "action", "请选择要查验的玩家");
        const checkTarget = await select("选择要查验的目标", "查验",
            gameData.value.phase_timer[gameData.value.current_phase], null, true);

        handleCheck(checkTarget)
      }

    }

    function handleCheckResult(message) {
      // 处理查人结果
      sendNotification(message.target + "号玩家的身份为" +  $translate(message.role) );
      sendSystemMessage(message.target + "号玩家的身份为" +  $translate(message.role) );

    }

    function handleWitchPhase(message) {
      // 处理Witch阶段
      updateGame(message.game);
      gameData.value.current_phase = message.game.current_phase;
    }

    async function handleWitchInfo(message) {
      // 处理Witch信息
      if(roleInfo.value.role === "Witch"){
        roleInfo.value.role_skills = message.role_skills;
        sendNotification("女巫请行动", "action", "请选择使用解药和毒药");
        let cure_target = -1, poison_target = -1;

        if (roleInfo.value.role_skills.cure_count && message.cure_target){
          cure_target = await select("解药选择", "解救",
              gameData.value.phase_timer.Witch / 2, message.cure_target, false);

        }
        if (roleInfo.value.role_skills.poison_count){
           poison_target = await select("毒药选择", "毒杀",
              gameData.value.phase_timer.Witch / 2, null, true);
        }
        timerSeconds.value = 0;


        handleWitchAction(cure_target, poison_target);
      }

    }

    function handleWitchActionResult(message) {
      // 处理Witch操作结果
      let line = ""
      if (message.cure){
        roleInfo.value.role_skills.cure_count -= 1;
        line += "你选择对" + message.cure + "号玩家使用解药\n";
      }
      if (message.poison){
        roleInfo.value.role_skills.poison_count -= 1;
        line += "你选择对" + message.poison + "号玩家使用毒药\n";
      }
      if (line !== ""){
        sendSystemMessage(line);
        showInfo("女巫行动", line);
      }

    }


    function handleTalkPhase(message) {
      // 处理发言阶段
      gameData.value = message.game;

      sendNotification("发言阶段开始", "speak");
    }

    function handleTalkUpdate(message) {
      // 处理聊天消息更新

      const speaker = [...Object.values(players.value), ...Object.values(aiPlayers.value)]
          .sort((a, b) => a.index - b.index)[Number(message.source) - 1];

      const newMessage = {
        senderindex: Number(message.source),
        sendername: speaker.name,
        avatar: speaker.avatar,
        text: message.message,
        recipients: "all" // 死亡玩家只能发送给"dead"
      };

      messages.value.push(newMessage);
    }

    function handleTalkUpdateDead(message) {
      // 处理聊天消息更新
      const speaker = [...Object.values(players.value), ...Object.values(aiPlayers.value)]
          .sort((a, b) => a.index - b.index)[Number(message.source) - 1]

      const newMessage = {
        senderindex: Number(message.source),
        sendername: speaker.name,
        avatar: speaker.avatar,
        text: message.message,
        recipients: "all" // 死亡玩家只能发送给"dead"
      };

      // 将消息推送到消息列表
      messages.value.push(newMessage);


    }

    function handleTalkEndByServer(message) {
      // 处理服务器发过来的聊天结束
      // this.userMessage = "";  // 没必要直接清空
      // TODO: 消息按钮重新变成灰的
      if (currentPlayer.value.index === message.player){
        sendNotification("你的发言时间结束。", "speak")
        talkStart.value = false;
      }

      currentSpeakingPlayer.value = null; // 清除当前发言玩家

    }

    async function handleVotePhase(message) {
      // 处理投票阶段
      updateGame(message.game)
      sendNotification("投票阶段开始，请选择你要放逐的玩家", "vote");
      const target = await select("投票放逐", "放逐", gameData.value.phase_timer[gameData.value.current_phase],
          null, true);
      handleVote(target);
    }

    function handleVoteResult(message) {
      // 处理投票结果
      if (!message.result){
        sendSystemMessage("投票结果: 由于出现平票，没有人被放逐")
        sendNotification("投票结果: 由于出现平票，没有人被放逐", "vote");
      }
      else {
        sendSystemMessage(message.result + "号玩家被放逐");
        sendNotification("投票结果: "+ message.result + "号玩家被放逐", "death");
      }

    }

    function handleDayDeathInfo(message) {
      // 处理白天死掉的人
      for (const victim of message.victims){
        if (victim === currentPlayer.value.index){
          sendNotification("你在这个白天死去了", "death",
          "接下来你可以与其他死亡玩家聊天，静待阵营胜利");
          talkStart.value = true;
          isDead.value = true;
        }
      }
    }

    function handleGameEnd(message) {
      // 处理游戏结束
      // TODO: 有空可以再改个胜利/失败界面

      if (message.end){
        if (message.victory[roleInfo.value.role]){
          if (roleInfo.value.role === "Werewolf") {
            sendNotification("游戏结束，狼人获胜！", "Night",
                "狼人们成功杀死村民与守护者，占领了村庄……从此屈膝于血月之下。");
          } else if (roleInfo.value.role === "Idiot") {
            sendNotification("游戏结束，白痴获胜！", "Day",
              "愚者看似游于争斗之外，但博弈中棋子们却均投出如此无用之票，命运是否在向他们展示，生命不过一场游戏？");
          } else {
            sendNotification("游戏结束，好人阵营获胜！", "Day",
              "恭喜，您成功地守护了村庄免受狼人威胁！……继往圣之绝学，为万世开太平。");
          }
        } else {
          if (roleInfo.value.role === "Werewolf") {
            sendNotification("游戏结束，好人阵营获胜。你的阵营失败了……再接再厉！", "day",
            "狼人们一一被发现后被驱逐，亦或是被女巫的毒药杀害。但复仇的时刻会来的……总有一天。");
          } else if (roleInfo.value.role === "Idiot") {
            // If Idiot loses, either werewolf or villagers won
            if (message.victory["Werewolf"]) {
              sendNotification("游戏结束，狼人获胜。你失败了……再接再厉！", "night",
              "可惜的是，愚者还没来得及展示所有人的愚蠢，就被狼人杀害了。毕竟，人死了又能说出什么来呢？");
            } else {
              sendNotification("游戏结束，好人阵营获胜。你失败了……再接再厉！", "day",
              "你看着村民的狂欢，他们似乎已不在意你的存在。也罢，也罢。如此得过且过，也算一幸事。");
            }
          } else {
            sendNotification("游戏结束，狼人获胜！你的阵营失败了……再接再厉！", "night",
            "狼人将村民与守护者们屠戮殆尽，村庄沦为怪物们的巢穴。但我们仍相信人类的勇气、胆识与正义，邪不压正，它们总有被消灭的一天。");
          }
        }
        // 游戏结束的聊天室
        talkStart.value = true;
        gameData.value.current_phase = "Cleanup";
        timerSeconds.value = gameData.value.phase_timer[gameData.value.current_phase];
        gameEnd.value = true;
      }
      // TODO: 展示所有人的角色并留两分钟复盘
    }

    function handleRoomCleanup(){
      sendNotification("游戏结束，返回大厅", "info",)
      wait(1000);
      router.push('/GameLobby')
    }

    const setupWebsocketListeners = () => {
        // 处理各个阶段和事件
        const playerJoinedCleanup = onType('player_joined', handlePlayerJoined);
        const roleInfoCleanup = onType('role_info', handleRoleInfo);
        const nightPhaseCleanup = onType('night_phase', handleNightPhase);
        const killPhaseCleanup = onType('kill_phase', handleKillPhase);
        const wolfSyncCleanup = onType('wolf_sync', handleWolfSync);
        const killResultCleanup = onType('kill_result', handleKillResult);
        const killPhaseEndCleanup = onType('kill_phase_end', handleKillPhaseEnd)
        const checkPhaseCleanup = onType('check_phase', handleCheckPhase);
        const checkResultCleanup = onType('check_result', handleCheckResult);
        const witchPhaseCleanup = onType('witch_phase', handleWitchPhase);
        const witchInfoCleanup = onType('witch_info', handleWitchInfo);
        const witchActionResultCleanup = onType('witch_action_result', handleWitchActionResult);
        const dayPhaseCleanup = onType('day_phase', handleDayPhase);
        const nightDeathInfoCleanup = onType('night_death_info', handleNightDeathInfo);
        const talkPhaseCleanup = onType('talk_phase', handleTalkPhase);
        const talkUpdateCleanup = onType('talk_update', handleTalkUpdate);
        const talkUpdateDeadCleanup = onType('talk_update_dead', handleTalkUpdateDead);
        const talkStartCleanup = onType('talk_start', handleTalkStart);
        const talkEndCleanup = onType('talk_end', handleTalkEndByServer);
        const votePhaseCleanup = onType('vote_phase', handleVotePhase);
        const voteResultCleanup = onType('vote_result', handleVoteResult);
        const dayDeathInfoCleanup = onType('day_death_info', handleDayDeathInfo);
        const gameEndCleanup = onType('game_end', handleGameEnd);
        const roomCleanupCleanup = onType('room_cleanup', handleRoomCleanup)

        // 返回清理函数
        onUnmounted(() => {
          playerJoinedCleanup();
          roleInfoCleanup();
          nightPhaseCleanup();
          killPhaseCleanup();
          wolfSyncCleanup();
          killResultCleanup();
          killPhaseEndCleanup();
          checkPhaseCleanup();
          checkResultCleanup();
          witchPhaseCleanup();
          witchInfoCleanup();
          witchActionResultCleanup();
          dayPhaseCleanup();
          nightDeathInfoCleanup();
          talkPhaseCleanup();
          talkUpdateCleanup();
          talkUpdateDeadCleanup();
          talkStartCleanup();
          talkEndCleanup();
          votePhaseCleanup();
          voteResultCleanup();
          dayDeathInfoCleanup();
          gameEndCleanup();
          roomCleanupCleanup();
        });
    }

    onBeforeMount(() =>{
      setupWebsocketListeners();
    }
    )

    onMounted(() => {
      // 只在未连接时初始化游戏房间连接
      if (!isGameConnected.value) {
        // 这里使用游戏房间的连接，而不是大厅连接
        connectToGame(roomId);
      }
      fetchFriendsList();

    });

    onUnmounted(() => {
      sendMessage({
        type: 'quit',
        action: 'leave_combat',
        player_id: currentPlayer.value.index,
      }, 'game');
      disconnect('game');
      // clearInterval(intervalId);
    });



    return{
      currentSpeakingPlayer,
      gameEnd,

      sendFriendRequest,
      selectedProfileId,
      selectedProfile,
      showPlayerProfile,

      talkStart,
      isDead,
      messages,
      isGameConnected,
      isLobbyConnected,
      connectToGame,
      sendMessage,
      handleTalkEnd,
      gameData,
      userProfile,
      players,
      aiPlayers,
      roleInfo,
      syncTargets,
      currentPlayer,
      selectablePhaseAction,
      selectedPlayer,
      selectableIndices,
      confirmed,
      isDayTime,
      timerSeconds,

      // 对话框相关
      currentNotification,
      closeNotification,
      handleDialogConfirm,
      handleDialogCancel,
      showDialog,
      dialogTitle,
      dialogMessage,
      dialogShowConfirm,
      hasUnreadMessages,
      // ...
    }
  },
  created() {
    // 初始化数据
    this.startTimer();
  },

  computed: {

    returnButtonText: function() {
      return (this.gameEnd || this.isDead) ? '返回大厅' : '结束发言';
    },

    currentIcon() {
      return this.isDayTime
        ? require('@/assets/sun.svg')
        : require('@/assets/night.svg');
    },

    formattedTime() {
      const minutes = Math.floor(this.timerSeconds / 60);
      const seconds = this.timerSeconds % 60;
      return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    }

  },

  methods: {

    toggleRoleConfig() {
      this.showRoleConfig = !this.showRoleConfig;
    },

    getRoleIcon(role) {
      switch(role) {
        case 'Werewolf':
          return require('@/assets/wolf.svg');
        case 'Prophet':
          return require('@/assets/prophet.svg');
        case 'Witch':
          return require('@/assets/wolf.svg');
        case 'Villager':
          return require('@/assets/villager.svg');
        case 'Idiot':
          return require('@/assets/wolf.svg');
        default:
          return '';
      }
    },

    handleScroll() {
      const chatBox = this.$refs.chatBox;
      const isNearBottom = chatBox.scrollHeight - chatBox.scrollTop - chatBox.clientHeight <= 100;

      // 当距离底部超过100px时显示滚动按钮
      this.showScrollButton = !isNearBottom;

      // 如果用户将聊天框滚动到底部，清除未读消息提示
      if (isNearBottom) {
        this.hasUnreadMessages = false;
      }
    },
    scrollToBottom() {
      const chatBox = this.$refs.chatBox;
      chatBox.scrollTop = chatBox.scrollHeight;
      this.showScrollButton = false;
      this.hasUnreadMessages = false; // 清除未读消息提示
    },

    startTimer() {  // 计时器
      this.timer = setInterval(() => {
        if (this.timerSeconds > 0) {
          this.timerSeconds--;
        }
      }, 1000);
    },

    targetPlayer(index) {
      // 投票选中目标玩家的逻辑
      if (this.selectedPlayer === index){
        this.selectedPlayer = -1;
      }
      else {
        this.selectedPlayer = index;
      }


    },

    confirmTarget(){
      // 确认选择
      this.confirmed = true;
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
      this.showRoleConfig = null;
      this.selectedProfileId = null;
    },

    closeMenuSidebar() {
      this.showMenuSidebar = false;
    },
    closeFriendsSidebar() {
      this.showMenuSidebar = false;
    },
    closeHistorySidebar() {
      this.showMenuSidebar = false;
    },
    closePlayerDetails() {
      this.showDetails = false;
      this.selectedShowPlayer = null;
    },


    // 阻止点击菜单内部时关闭
    stopClick(event) {
      event.stopPropagation();
    },



    sendChatMessage() {

      if (this.userMessage.trim() && this.talkStart) {
        // 把消息发到服务器
        if (this.isDead || this.gameEnd){
          this.sendMessage({
            type: "talk_content_dead",
            content: this.userMessage,
          }, "game")
        }
        else {
          this.sendMessage({
            type: "talk_content",
            content: this.userMessage,
          }, "game")
        }
        // 清空输入框
        this.userMessage = "";
      }
    },

    exitGame() {
      alert("退出游戏");
    },
    showPlayerDetails(player, event) {
      this.selectedShowPlayer = player;
      this.showDetails = true;

      // 获取头像的位置
      const avatar = event.target; // 头像元素
      const rect = avatar.getBoundingClientRect(); // 获取头像的位置信息

      // 设置玩家详情框的位置
      this.playerDetailsTop = rect.top + window.scrollY; // 距离页面顶部的距离
      this.playerDetailsLeft = rect.left + window.scrollX + avatar.offsetWidth + 10; // 距离页面左侧的距离，加10像素的间隔
    },

    reportPlayer(player) {
      alert(`${player.name} 已被举报！`);
    },
    addFriend(player) {
      alert(`已向 ${player.name} 发送好友请求！`);
    },


  },
  watch: {

    showDetails(newVal) {
      // 如果玩家信息框被打开，页面滚动到顶部
      if (newVal) {
        window.scrollTo(0, 0);
      }
    },

  }
};
</script>

<style scoped>
/* 设置页面背景色 */
body {
  background: linear-gradient(135deg, #f1f1f1, #e0e0e0); /* 渐变背景色 */
  font-family: 'Roboto', sans-serif;  /* 设置字体 */
  margin: 0;
  padding: 0;
}

/* 用于调整字体和颜色 */
h3, h5, h6, p {
  color: #333;
  margin: 10px 0;
}

h3 {
  font-size: 1.5em;
}

h5, h6 {
  font-size: 1.1em;
}

p {
  font-size: 1.2em;
}

.avatar0 {
  max-width: 100%; /* 设置图像最大宽度 */
  max-height: 100%; /* 设置图像最大高度 */
  width: 50px; /* 固定宽度 */
  height: 50px; /* 固定高度 */
}

.avatar1 {
  max-width: 100%; /* 设置图像最大宽度 */
  max-height: 100%; /* 设置图像最大高度 */
  width: 50px; /* 固定宽度 */
  height: 50px; /* 固定高度 */
}
.avatar0, .avatar1, .avatar-modal {
  border-radius: 50%;  /* 让头像保持圆形 */
  border: 2px solid #f2f2f2;  /* 添加边框 */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);  /* 给头像添加轻微阴影 */
  transition: transform 0.3s ease;  /* 增加缩放动画效果 */
}

.avatar0:hover, .avatar1:hover, .avatar-modal:hover {
  transform: scale(1.1);  /* 鼠标悬浮时头像放大 */
}
.game-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;  /* 使游戏容器充满整个视窗 */
  padding: 20px;
  background: var(--background-color);
}

.phase_header {
  background-color: #f8f8f8;
  padding: 20px;
  text-align: center;
  font-size: 48px;
  font-weight: bold;
  position: absolute;
  top: 100px; /* 距离顶部100px */
  left: 50%; /* 水平方向上居中 */
  transform: translateX(-50%); /* 使用 transform 来精确水平居中 */
  width: 100%; /* 确保元素宽度占满整个容器 */
}

.player-list {
  width: 18%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.player {
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  flex: 1; /* 让玩家信息占据剩余空间 */
  margin-right: 20px; /* 与按钮保持距离 */
}

.player.dead {
  text-decoration: line-through;
  background-color: #e0e0e0; 
  color: #b0b0b0;
  opacity: 0.6;
  width: 100%;
}

.avatar0 {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  transition: filter 0.3s ease; 
}

.player.dead .avatar0 {
  filter: grayscale(100%) brightness(0.5); 
}

.player.dead p {
  font-style: italic; 
}
.player p {
  margin: 0;
  font-size: 14px;
  font-weight: bold;
  color: var(--name-color);
}

/* 狼人的同步目标 */
.player .sync-targets {
  color: red; /* 设置文字颜色为红色 */
  font-size: 12px; /* 设置文字大小 */
  white-space: nowrap; /* 防止文字换行 */
  overflow: hidden; /* 隐藏超出容器的部分 */
  text-overflow: ellipsis; /* 超出部分显示省略号 */
  max-width: 100%; /* 限制最大宽度 */
  margin-top: 5px; /* 添加顶部外边距 */
}

.player span {
  font-size: 12px;
  color: var(--name-color);
}
.chat-section {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 60%;
}

.chat-box {
  width: 100%;
  height: 500px;
  border: 1px solid #3d3d3d;
  padding: 10px;
  margin-bottom: 10px;
  overflow-y: auto;
  border-radius: 15px;
}



/* 聊天框 */
.chat-box {
  background: #fff;
  border-radius: 15px;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);  /* 添加轻微阴影 */
  overflow-y: auto;
  padding: 20px;
  margin-bottom: 20px;
  max-height: 500px;
  transition: box-shadow 0.3s ease;  /* 增加过渡效果 */
}

.chat-box:hover {
  box-shadow: 0 0 25px rgba(0, 0, 0, 0.2);  /* 鼠标悬浮时改变阴影 */
}
.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
/* 聊天消息 */

/* 系统消息样式 */
.system-message {
  display: flex;
  justify-content: center;
  margin: 10px 0;
  background-color: transparent !important;
  padding: 0 !important;
}

.system-message-content {
  display: inline-block;
  text-align: center;
  max-width: 80%;
}

.system-message-text {
  display: inline-block;
  background-color: rgba(0, 0, 0, 0.1);
  color: #666;
  padding: 8px 16px;
  border-radius: 15px;
  font-size: 0.9em;
}

/* 滚动到底部按钮样式 */
.scroll-bottom-wrapper {
  position: sticky;
  bottom: 20px;
  width: 100%;
  display: flex;
  justify-content: center;
  pointer-events: none;
}

.scroll-bottom-button {
  pointer-events: auto;
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.scroll-bottom-button:hover {
  transform: scale(1.1);
}

.scroll-bottom-icon {
  width: 24px;
  height: 24px;
}

.message {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 10px;
  transition: transform 0.3s ease;
}

/* 未读消息提示红点 */
.unread-indicator {
  position: absolute;
  top: -5px;
  right: -5px;
  width: 12px;
  height: 12px;
  background-color: #ff4444;
  border-radius: 50%;
  border: 2px solid #ffffff;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.message:hover {
  transform: translateX(10px);  /* 消息框悬浮时向右偏移 */
}

.message-avatar-container {
  display: flex;
  align-items: center;  /* 使头像和标签垂直居中 */
  gap: 3px;  /* 控制头像与标签之间的距离 */
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.message-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: #f0f0f0;
}

.recipient-label {
  font-size: 0.9em;
  color: #999;
  margin-left: 0;  /* 去除与头像的距离 */
}
.message-content {
  display: flex;
  flex-direction: column;
  max-width: 80%;
}
.message-sender {
	display: flex;
  background-color: transparent;
  padding: 5px;
  border-radius: 5px;
  font-weight: bold;
  text-align: left
}
.message-text {
	display: flex;
  background-color: #f1f1f1;
  padding: 8px;
  border-radius: 5px;
  margin-top: 5px;
}
.message-content strong {
  font-weight: bold;
}
.message-input-section {
  background-color: transparent;
  display: flex;
  width: 100%;
  align-items: center;
  gap: 10px; 
}

/* 结束发言按钮样式 */
.end-talk-button {
  background: linear-gradient(135deg, #ff4d4d 0%, #ff0000 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  box-shadow: 0 4px 12px rgba(255, 0, 0, 0.2);
  position: relative;
  overflow: hidden;
  white-space: nowrap;
}

.end-talk-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transform: translateX(-100%);
  transition: transform 0.6s;
}

.end-talk-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(255, 0, 0, 0.3);
}

.end-talk-button:hover::before {
  transform: translateX(100%);
}

.end-talk-button:active {
  transform: translateY(1px);
  box-shadow: 0 2px 8px rgba(255, 0, 0, 0.2);
}

.button-text {
  margin-right: 5px;
  letter-spacing: 0.5px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
}

.message-input {
  border: 1px solid #ccc;
  border-radius: 15px;
  padding: 10px;
  font-size: 1em;
  background-color: transparent;
  width: 100%;
  transition: border 0.3s ease;
}

.message-input:focus {
  border-color: #007bff; /* 聚焦时改变边框颜色 */
  outline: none;
}

.send-button {
  background-color: transparent;
  border: none;
  cursor: pointer;
  border-radius: 50%; 
  font-size: 1.5em;
  margin-left: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.send-button img {
  width: 40px;  /* 设置图标的宽度 */
  height: 40px; /* 设置图标的高度 */
  transition: transform 0.3s ease;
  filter: brightness(0); /* 将图标变为黑色 */
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #f0f0f0;
  transform: none;
  transition: all 0.3s ease;
  border: 1px solid #ddd;
}

.send-button:disabled img {
  filter: grayscale(100%);
  opacity: 0.6;
  transform: none;
}

.send-button:disabled:hover {
  background-color: #f0f0f0;
  transform: none;
  box-shadow: none;
}
.send-button:hover{
  background-color: #aaa;
  border-color: transparent;
  transform: scale(1.1);
}
/*TODO:改悬浮样式*/

.right-info-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 400px; /* 与role-info相同的宽度 */
}

/* 角色信息容器 */
.role-info {
  position: relative;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 16px;
  padding: 24px;
  margin-left: 15px; /* 额外的左侧间距 */
  box-shadow:
    0 4px 20px rgba(0, 0, 0, 0.08),
    0 1px 3px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 400px;
  transition: all 0.3s ease;
  overflow: hidden;
}

.role-info:hover {
  transform: translateY(-2px);
  box-shadow:
    0 6px 24px rgba(0, 0, 0, 0.12),
    0 2px 4px rgba(0, 0, 0, 0.08);
}

/* 角色信息项 */
.role-item {
  position: relative;
  display: flex;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 12px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.role-item:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateX(4px);
}

/* 标签样式 */
.label {
  font-size: 0.9em;
  font-weight: 600;
  color: #4a5568;
  letter-spacing: 0.5px;
  min-width: 90px;
  position: relative;
  padding-left: 12px;
}

.label::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 16px;
  background: linear-gradient(to bottom, #3b82f6, #60a5fa);
  border-radius: 2px;
}

/* 值的样式 */
.value {
  flex: 1;
  font-size: 1em;
  color: #1a202c;
  padding-left: 16px;
  font-weight: 500;
  text-align: left;
  position: relative;
  transition: all 0.2s ease;
}

/* 特殊样式：角色名称 */
.role-item:first-child .value {
  font-size: 1.2em;
  font-weight: 700;
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 队友信息特殊样式 */
.role-item:last-child {
  background: linear-gradient(to right, rgba(59, 130, 246, 0.05), rgba(96, 165, 250, 0.1));
}

/* 响应式调整 */
@media (max-width: 768px) {
  .role-info {
    padding: 16px;
  }

  .role-item {
    padding: 10px 12px;
    margin-bottom: 8px;
  }

  .label {
    font-size: 0.85em;
    min-width: 80px;
  }

  .value {
    font-size: 0.95em;
  }
}
.role-abilities {
  margin-top: -15px;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.abilities-header {
  margin-bottom: 10px;
}

.abilities-container {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  justify-content: center;
}

.ability-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
  width: 80px;
}

.ability-item:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.2);
}

.ability-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ability-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 5px;
  transition: transform 0.3s ease;
}

.ability-item:hover .ability-icon {
  transform: scale(1.1);
}

.ability-info {
  text-align: center;
}

.ability-name {
  font-size: 12px;
  color: #333;
  margin-bottom: 2px;
  display: block;
}

.ability-count {
  font-size: 11px;
  color: #666;
  display: block;
}


/* 玩家详细信息框样式 */
.player-details-box {
  position: absolute;
  top: 10%;
  left: 30%;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
  z-index: 10;
  width: 250px;
  max-width: 90%;
  transition: opacity 0.3s ease;
  pointer-events: auto; /* 确保框内的按钮可以点击 */
}

/* 玩家详细信息 */
.player-details {
  text-align: center;
}

.avatar-modal {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  margin-bottom: 10px;
}

h4 {
  margin: 10px 0;
  font-size: 1.2em;
}

p {
  font-size: 1em;
  margin: 5px 0;
}

/* 按钮样式 */
.btn-report, .btn-add-friend {
  background-color: var( --button-bg);
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  margin: 10px 5px;
  cursor: pointer;
  transition: transform 0.3s ease, filter 0.3s ease;
  display: inline-block;
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

.btn-report:hover, .btn-add-friend:hover {
  transform: scale(1.1);
}

/* 遮罩层（点击其他地方关闭信息框） */
.game-container {
  position: relative;
  transition: filter 0.5s ease;
}



/* 关闭按钮 */
.close {
  position: absolute;
  top: 5px;
  right: 5px;
  cursor: pointer;
  font-size: 24px;
  color: #888;
}
/* 响应式样式 */
@media (max-width: 768px) {
  .chat-section {
    width: 100%;
  }

  .message-input {
    font-size: 0.9em;
  }
}
@media (max-width: 768px) {
  .game-container {
    flex-direction: column;
    align-items: center;
  }

  .player-list, .role-info {
    width: 100%;
    margin-bottom: 20px;
  }

  .chat-section {
    position: relative;
    width: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .message-input {
    padding: 8px;
    font-size: 0.9em;
  }
}
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
  z-index: 100;
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
  gap: 10px; /* 让右边的按钮之间有间距 */
}

/* 侧边栏的样式 */
.sidebar {
  position: fixed;
  top: 5%;
  width: 250px;
  height: calc(95%);
  background-color: #fff;
  color: black;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.5);
  border-radius: 0 10px 10px 0; /* 圆角 */
  transition: transform 0.5s ease, opacity 0.5s ease; /* 控制平滑过渡 */
  z-index: 999;
  overflow: hidden;
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



/* 大的日夜切换图标样式 */
.sun-moon-icon {
  position: absolute;
  top: 100px;
  right: 20px;
  left: 85%;  /* 将其水平居中 */
  background-color: transparent;
  border: none;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.sun-moon-icon-img {
  width: 100px;
  height: 100px;
  transition: transform 0.3s ease;
}

.sun-moon-icon:hover .sun-moon-icon-img {
  transform: scale(1.1);
}

/* 确认按钮样式 */
.confirm-button {
  position: absolute;
  bottom: 80px; /* 调整到底部20px处 */
  left: 30px; /* 调整到左边20px处 */
  height: 50px;
  width: 100px;
  background-color: rgba(110, 110, 218, 0.87); /* 设置背景颜色为蓝色 */
  border: crimson;
  cursor: pointer;
  transition: transform 0.3s ease;
}

/* 鼠标悬停时的效果 */
.confirm-button:hover .confirm-icon {
  transform: scale(1.05);
}




/* 玩家容器样式优化 */
.player-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px;
  border-radius: 12px;
  transition: all 0.3s ease;
  width: 100%;
}

/* 玩家发言状态样式优化 */
.player-name-container {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
}

.player-name-container p {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
  font-size: 0.95em;
}

/* 发言指示器容器 */
.speaking-indicator {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  background: linear-gradient(45deg, #3b82f6, #60a5fa);
  border-radius: 12px;
  margin-left: 6px;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
}

.speaking-indicator-text {
  color: white;
  font-size: 0.8em;
  font-weight: 500;
  margin-left: 4px;
}

/* 说话状态样式 */
.speaking-status {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: linear-gradient(45deg, rgba(59, 130, 246, 0.1), rgba(147, 197, 253, 0.1));
  border-radius: 12px;
  animation: fadeInOut 2s infinite;
}

.speaking-icon {
  width: 16px;
  height: 16px;
  animation: speakingPulse 1.5s infinite;
}

/* 发言图标动画 */
@keyframes speakingPulse {
  0% {
    transform: scale(0.95) translateY(0);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.05) translateY(-2px);
    opacity: 1;
  }
  100% {
    transform: scale(0.95) translateY(0);
    opacity: 0.6;
  }
}

/* 说话状态背景动画 */
@keyframes fadeInOut {
  0% {
    background: linear-gradient(45deg, rgba(59, 130, 246, 0.05), rgba(147, 197, 253, 0.05));
  }
  50% {
    background: linear-gradient(45deg, rgba(59, 130, 246, 0.15), rgba(147, 197, 253, 0.15));
  }
  100% {
    background: linear-gradient(45deg, rgba(59, 130, 246, 0.05), rgba(147, 197, 253, 0.05));
  }
}


/* 添加资料卡动画 */
.profile-enter-active,
.profile-leave-active {
  transition: all 0.3s ease;
}

.profile-enter-from,
.profile-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

/* 个人资料卡样式 */
/* 确保资料卡不会被其他元素遮挡 */
.profile-card {
  position: absolute;
  left: 70px;
  top: 150px;
  transform: translateY(-50%);
  width: 240px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 16px;
  z-index: 1000;
}


/* 调整箭头位置，让它指向头像 */
.profile-card::before {
  content: '';
  position: absolute;
  top: 30px; /* 调整箭头垂直位置以对齐头像 */
  left: -8px; /* 将箭头放在左侧 */
  width: 16px;
  height: 16px;
  background: #fff;
  transform: rotate(45deg);
  box-shadow: -2px 2px 5px rgba(0, 0, 0, 0.04);
  z-index: -1;
}
.profile-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  background: #fff ;
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
  cursor: not-allowed;
}

.report-btn {
  background-color: transparent;
  color: red;
}

/* 禁用状态下保持相同的悬停效果 */
.add-friend-btn:hover,
.add-friend-btn:disabled:hover {
  transform: translateY(-2px);
  filter: brightness(1.1);
  background-color: #f5f5f5;
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

.report-btn:hover {
  transform: translateY(-2px);
  filter: brightness(1.1);
  background-color: #fff1f0;
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

/* 同步目标包装器 */
.sync-targets-wrapper {
  position: absolute;
  top: 5%;  /* 将位置改为父元素的底部 */
  left: 60px;
  z-index: 5;
}

.sync-targets-content {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 20px;
  padding: 4px 12px;
  transition: all 0.3s ease;
}

/* 队友头像组 */
.teammate-avatars {
  display: flex;
  margin-right: 8px;
}

.teammate-number {
  width: 24px;
  height: 24px;
  background: #3B82F6;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  margin-left: -8px;
  border: 2px solid white;
}

/* 提示文本 */
.sync-targets-tooltip {
  font-size: 12px;
  color: #3B82F6;
  white-space: nowrap;
}

.target-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  background: transparent;
  border: 2px solid rgba(59, 130, 246, 0.5);
  color: #3B82F6;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 80px;
  position: relative;
  overflow: hidden;
  margin-left: auto;
}

.button-content {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 2;
}

.button-text {
  font-weight: 500;
  transition: transform 0.2s ease;
}

.button-arrow {
  font-size: 16px;
  transition: transform 0.2s ease;
  opacity: 0.8;
}

/* 悬浮效果 */
.target-button:hover {
  border-color: #3B82F6;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.2);
  transform: translateY(-1px);
}

.target-button:hover .button-arrow {
  transform: translateX(4px);
}

/* 点击效果 */
.target-button:active {
  transform: translateY(1px);
}

/* 为选中状态添加样式 */
.selected-player .target-button {
  background: rgba(59, 130, 246, 0.1);
  border-color: #3B82F6;
}

.selected-player {
  background-color: rgba(56, 73, 204, 0.55);
  width: 100%;
}
/* 确保死亡玩家状态不影响同步目标显示 */
.player.dead + .sync-targets-wrapper {
  opacity: 1;
  filter: none;
}

.player.dead + .target-button {
  opacity: 0.7;
  pointer-events: none;
}
/* 确认按钮的基础样式 */
.confirm-button {
  position: absolute;
  bottom: 80px;
  left: 30px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  box-shadow: 0 4px 6px rgba(99, 102, 241, 0.25);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 140px;
  text-align: center;
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

/* 鼠标悬停效果 */
.confirm-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(99, 102, 241, 0.3);
  background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
}

/* 点击效果 */
.confirm-button:active {
  transform: translateY(1px);
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
}

/* 禁用状态 */
.confirm-button:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 添加脉冲动画效果 */
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(99, 102, 241, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(99, 102, 241, 0);
  }
}

.confirm-button:not(:disabled) {
  animation: pulse 2s infinite;
}

:root {
  --base-unit: min(1vh, 1vw);
  --min-width: 320px;
  --max-width: 1920px;
}

/* 头像相关 */
.avatar0, .avatar1 {
  width: min(50px, 4vw);
  height: min(50px, 4vw);
  min-width: 40px;
  min-height: 40px;
}

.avatar-modal {
  width: min(60px, 5vw);
  height: min(60px, 5vw);
  min-width: 45px;
  min-height: 45px;
}

/* 游戏容器 */
.game-container {
  min-height: 600px;
  height: 100vh;
  padding: calc(var(--base-unit) * 2);
}

.player-list {
  width: min(18%, 300px);
  min-width: 200px;
}

.chat-section {
  width: min(60%, 800px);
  min-width: 300px;
}

.phase-display {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  z-index: 1;
  margin-top: -60px;
  margin-bottom: 38px;
  width: 100%;
}

/* 聊天框相关 */
.chat-box {
  height: min(500px, 50vh);
  min-height: 300px;
}

.message-input-section {
  min-height: 50px;
  height: min(60px, 6vh);
}

.message {
  padding: min(12px, 1.5vw);
  margin-bottom: min(10px, 1vh);
}

/* 侧边栏 */
.sidebar {
  width: min(250px, 25vw);
  min-width: 200px;
  height: calc(95vh - 20px);
  min-height: 400px;
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

/* 按钮相关 */
.confirm-button {
  width: min(140px, 12vw);
  height: min(50px, 5vh);
  min-width: 100px;
  min-height: 40px;
}

.end-talk-button {
  padding: min(12px, 1.5vw) min(24px, 2vw);
  min-width: 100px;
  min-height: 35px;
}

/* 标题和文字大小 */
.phase_header {
  font-size: min(48px, 4vw);
  min-height: 40px;
}

h3 {
  font-size: min(1.5em, 3vw);
}

h5, h6 {
  font-size: min(1.1em, 2vw);
}

p {
  font-size: min(1.2em, 2vw);
}

/* 工具栏 */
.top-bar {
  height: min(5vh, 60px);
  min-height: 40px;
}

.sun-moon-icon-img {
  width: min(100px, 8vw);
  height: min(100px, 8vw);
  min-width: 60px;
  min-height: 60px;
}

/* 配置按钮样式 */
.config-toggle-button {
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  width: 48px;
  height: 48px;
  border-radius: 24px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
  transition: all 0.3s ease;
  z-index: 100;
}

.config-toggle-button:hover {
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
}

.config-icon {
  width: 24px;
  height: 24px;
  filter: brightness(0) invert(1);
}

/* 配置面板样式 */
.role-config-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 320px;
  height: 100vh;
  background: white;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
  padding: 24px;
  z-index: 1000;
  overflow-y: auto;
  border-radius: 20px 0 0 20px;
}

.role-config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.role-config-header h3 {
  font-size: 1.2em;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.close-config-button {
  background: transparent;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 8px;
  line-height: 1;
  transition: all 0.3s ease;
}

.close-config-button:hover {
  color: #333;
  transform: scale(1.1);
}

/* 内容样式 */
.role-config-content {
  padding-right: 10px;
}

.section-title {
  font-size: 1.1em;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 16px 0;
}

.roles-grid, .items-grid {
  display: grid;
  gap: 12px;
}

.role-item, .item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f7fafc;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.role-item:hover, .item:hover {
  background: #edf2f7;
  transform: translateX(4px);
}

/* 当前玩家的角色特殊标注 */
.role-item.current-player {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(79, 70, 229, 0.1) 100%);
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.role-item.current-player .role-name::after {
  content: ' (你)';
  color: #4f46e5;
  font-weight: 600;
}

.role-icon-name, .item-icon-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-icon-name, .item-icon-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-svg-icon, .item-svg-icon {
  width: 24px;
  height: 24px;
}

.role-name, .item-name {
  font-size: 0.95em;
  color: #4a5568;
}

.role-count, .item-count {
  font-size: 0.95em;
  font-weight: 500;
  color: #2d3748;
}

.camp-stats {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.stat-label {
  color: #4a5568;
  font-size: 0.9em;
}

.stat-value {
  color: #2d3748;
  font-weight: 500;
  font-size: 0.9em;
}

/* 滑动动画 */
.slide-config-enter-active,
.slide-config-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-config-enter-from,
.slide-config-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
