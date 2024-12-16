<template>
    <div class="game-container" @click="closeALL" >

  
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

      <!-- 左侧玩家列表 -->
      <div class="player-list" v-if="Boolean(players && aiPlayers)">
        <!-- 使用 Object.values() 将对象的值转换为数组，并确保通过 .value 访问 ref 的值 -->
        <div v-for="(player, index) in [...Object.values(players), ...Object.values(aiPlayers)]" :key="index"
             :class="['player-container', { 'selected-player': index + 1 === selectedPlayer }]">
          <div :class="['player', { dead: ![...Object.values(gameData.players), ...Object.values(gameData.ai_players)][index].alive }]">
            <img
              :src="player.avatar"
              alt="avatar"
              class="avatar0"
              @click.stop="showPlayerDetails(player, $event)"
              /><!-- 点击头像触发查看详情 -->
            <p>{{ index + 1 }}号{{" "}}{{ player.name }}<span v-if="player.userId === currentPlayer.index"> (你)</span></p> <!-- 如果是当前玩家，显示 "(你)" -->
            <div class="sync-targets" v-if="syncTargets[String(index + 1)]">
              {{ '队友' + syncTargets[String(index + 1)].join('号, ') + '号已选择此目标' }}
            </div>
          </div>
          <!-- 添加按钮，根据 是否是目标以及当前是否为可选择阶段 决定是否显示 -->
          <button v-if="Boolean(selectableIndices.indexOf(index + 1) !== -1 &&
          selectablePhaseAction !== '' )" class="target-button" @click.stop="targetPlayer(index + 1)">
            {{ selectablePhaseAction }}
          </button>
        </div>
      </div>

      <!-- 确认选择按钮 -->
      <div class="confirm-button" @click="confirmTarget">
        确认选择
      </div>



      <!-- 中间聊天框 -->
      <div class="chat-section">
        <!-- 当前阶段显示 -->
      <GamePhase :phase="gameData.current_phase" />
        <div class="chat-box" ref="chatBox" @scroll="handleScroll">
          <div class="chat-messages">
            <div  v-for="message in messages" :key="message.senderid"
                   :class="['message', { 'system-message': message.senderid === 0 }]">
                <!-- 系统消息使用不同的样式 -->
                <template v-if="message.senderid === 0">
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
                          {{ message.senderid }}号{{" "}}{{ message.sendername }}
                          <span v-if="message.senderid === currentPlayer.index"> (你)</span>
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
          <select v-model="messageRecipient" class="recipient-select">
            <option value="all">所有人</option>
            <option value="team">团队</option>
            <option value="dead" v-if="isDead">死亡</option> <!-- 死亡玩家只能选择死亡 -->
          </select>
          <input
            v-model="userMessage"
            @keyup.enter="sendChatMessage"
            placeholder="输入消息"
            class="message-input"
          />
          <!-- 图标按钮 -->
          <button @click="sendChatMessage" class="send-button">
            <img class="send-icon" src="@/assets/send.svg" alt="发送图标" /> <!-- 或者使用一个自定义图标图片 -->
          </button>
        </div>
      </div>

      <!-- 大图标，显示在右上角 -->
      <div class="sun-moon-icon" @click="toggleDayNight">
        <img :src="sunMoonIcon" alt="Day Night Toggle" class="sun-moon-icon-img" />
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
            <span class="value">{{ roleInfo.role }}</span>
        </div>
        <div class="role-item">
            <span class="label">阵营目标：</span>
<!--          TODO: 后端改好后这里改为roleInfo.objective-->
            <span class="value">{{ objective }}</span>

        </div>
        <div class="role-item">
            <span class="label">胜利条件：</span>
<!--            <span class="value">{{ gameData.victory_condition }}</span>-->
            <span class="value">{{ victoryCondition }}</span>
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
      <!-- 玩家详细信息弹出框 -->
      
       <div 
        v-if="showDetails" 
        class="player-details-box" 
        :style="{ top: playerDetailsTop + 'px', left: playerDetailsLeft + 'px' }"
        @click.stop
        >
        <div class="player-details">
          <img :src="selectedShowPlayer.avatar" alt="avatar" class="avatar-modal" />
          <h4>{{ selectedShowPlayer.name }}</h4>
          <p>角色：{{ selectedShowPlayer.role }}</p>
          <p>阵营：{{ selectedShowPlayer.team }}</p>
          <p>状态：{{ selectedShowPlayer.isDead ? '已死亡' : '存活' }}</p>
          <button class="btn-report" @click="reportPlayer(selectedShowPlayer)">
            <img class="icon" src="@/assets/report.svg" alt="举报" />
          </button>
          <button class="btn-add-friend" @click="addFriend(selectedShowPlayer)">
            <img class="icon" src="@/assets/addFriend.svg" alt="添加好友" />
          </button>
        </div>
      </div>
      <!--  弹出查验结果   -->
      <ConfirmDialog
      :show="showDialog"
      :title="dialogTitle"
      :message="dialogMessage"
      :showConfirm="dialogShowConfirm"
      @confirm="handleDialogConfirm"
    />
      <!-- 系统通知组件 -->
      <SystemNotice
        v-if="currentNotification"
        v-bind="currentNotification"
        @close="closeNotification"
      />


    </div>

  </template>
  
<script>
import {onMounted, ref, onUnmounted, onBeforeMount,} from 'vue';
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
            icon: 'medicine.svg',
            description: '可以救活一名被杀的玩家',
            hasCount: true,
            count: 1
          },
          {
            id: 'poison',
            name: '毒药',
            icon: 'medicine.svg',
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
            icon: 'kill.svg',
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
      userMessage: "",



      objective: "淘汰全部人类",
      victoryCondition: "再淘汰1名人类",
      livingTeammates: 0,
      showDetails: false,   // 控制显示详细信息

      showMenuSidebar: false, // 控制侧边栏的显示与否
      showFriendsSidebar: false,
      showHistorySidebar: false,

      isDead: false, // 当前玩家是否死亡

      playerDetailsTop: 0,  // 玩家详情框的top位置
      playerDetailsLeft: 0,  // 玩家详情框的left位置

      // （小）阶段标记
      phase: null,

      selectedShowPlayer: -1,

      // 日夜切换

      sunMoonIcon: require('@/assets/sun.svg') , // 默认图标是太阳
      messageRecipient: "all", // 消息的接收者，默认为"所有人"

    };
  },


  setup() {

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
          End: 3
      }
    })

    // 其他狼人的投票
    const syncTargets = ref({});

    
    const currentPlayer = ref({
      index: "6",
      name: "apifox",
      alive: true,
      online: true
    });

    // 计时器
    const timerSeconds = ref(10);
    // 一个用于管理select里面时间长度的变量，如果到时间结束会变成0（重置），点击结束则是会变成剩余时间
    const timeElapsed = ref(0);

    // 当前可选的角色，选中的角色，当前具体的选择阶段，是否确认选项
    const selectableIndices = ref([1, 2, 3]);
    const selectedPlayer = ref(-1);
    const selectablePhaseAction = ref("");
    const confirmed = ref(false);
    const isDayTime = ref(false);
    // 当前为你的发言阶段
    // TODO: 允许发言
    const talkStart = ref(false);

    const currentNotification = ref(null);  // 当前显示的通知

    // 添加处理通知的方法
    function sendSystemMessage(content, type = 'info', subMessage = '', players = [] ) {
      // 创建聊天消息
      const chatMessage = {
        senderid: 0,
        sendername: "系统信息",
        avatar: require('@/assets/head.png'),
        text: content,
        recipients: "all"
      };
      messages.value.push(chatMessage);

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

      sendSystemMessage(
        `你的角色是：${roleName}`,
        'role',
        description,
          [],
      );
    }
    // 修改原有的系统消息处理方法
    function handleNightPhase(message) {
      sendSystemMessage("天黑请闭眼", "night");
      isDayTime.value = false;
      updateGame(message.game);
    }

    function handleDayPhase(message) {
      sendSystemMessage("天亮请睁眼", "day");
      isDayTime.value = true;
      updateGame(message.game);
    }

    function handleNightDeathInfo(message) {
      const victims = message.victims;
      if (victims.length === 0) {
        sendSystemMessage("昨晚是平安夜", "death");
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

        sendSystemMessage(
          "昨晚以下玩家被杀害：",
          "death",
          "",
          deadPlayers
        );
      }
    }

    //
    function handleTalkStart() {
      sendSystemMessage(
        `${currentPlayer.value.index}号玩家，轮到你发言`,
        "speak",
          "请在规定时间内发表意见",
        [],

      );
      talkStart.value = true;
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
            isFriend: false, // 这里可以从好友列表判断
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

    let initialized = false;

    // 设置一个定时器，每过一段时间执行一次
    // const intervalId = setInterval(() => {
    //   console.log(Boolean(players.value && aiPlayers.value));
    // }, 1000); // 这里设置为每1000毫秒（1秒）打印一次


    // 这里的信息以后就不动了
    const initializeGameInterface = async () => {

      if (!initialized){
        players.value = gameData.value.players;
        aiPlayers.value = gameData.value.ai_players;

        // 获取并设置所有玩家信息
        const playerProfiles = {};
        for (const playerId of Object.keys(gameData.value.players)) {
          // console.log(playerId);
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
              index: gameData.value.players[playerId].index,
              name: profile.name,
              alive: true,
              online: true,
            }
            console.log("profile id: " + userProfile.value.userId);
            console.log("player id: " + playerId);
            console.log("index: " + gameData.value.players[playerId].index);
          }
        }



        // 添加AI玩家信息
        const aiPlayerProfiles = {};

        for (const id of Object.keys(gameData.value.ai_players)) {
          // console.log(id);
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
        // console.log("GameInterfaceInit: Done!!!");
        // console.log(JSON.stringify(players.value, null, 2));
        // console.log(JSON.stringify(aiPlayers.value, null, 2));
        initialized = true;

        // TODO: 添加对玩家自身信息的初始化
      }
      else {
        console.log("Already initialized, passing...")
      }



    };

    // 工具函数，用于阶段转换时更新信息; 要求为GameData类型
    function updateGame(game){
      // const result = validateGame(game)
      // if (result){
      //   gameData.value
      // }
      // else {
      //   console.error('Validation errors: GameData validate failed; ' +
      //       'stopped updating game data.', result.errors);
      // }
      if (!game){
        console.log("gameData is false");
      }
      else {
        const prev_phase = gameData.value.current_phase;
        gameData.value = game
        console.log(prev_phase+  " " + gameData.value.current_phase)
        if (prev_phase !== gameData.value.current_phase){
          timerSeconds.value = gameData.value.phase_timer[gameData.value.current_phase]
        }
      }

    }

    // 等待一定时间用工具函数
    const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // 投票用工具函数
    async function select(title, content, time, players, alive_as_target = false) {
      // players: List[str], str为序号
      selectablePhaseAction.value = content;
      console.log("selectedplayerbefore: " + selectedPlayer.value);

      selectableIndices.value = [];
      if (alive_as_target){  // 选择所有活着的人，除了自己
        for (const player of [...Object.values(gameData.value.players), ...Object.values(gameData.value.ai_players)]){

          if (player.alive && player.index !== currentPlayer.value.index){
            selectableIndices.value.push(Number(player.index));
          }
        }
      }
      else {  // 当前列表中的人
        for (const index of players){
          selectableIndices.value.push(Number(index));
          console.log("choose able players: " + index)
        }
      }


      // 显示结束按钮，显示计时器
      console.log(selectableIndices.value)
      console.log("phase start: " + selectablePhaseAction.value + "time: " + time);
      console.log("phase: " + selectablePhaseAction.value + "indices: " + selectableIndices.value);

      // 等待函数

      // 等待此阶段对应的时间
      for(let i=1; i<=time; i++){
        await wait(1000);
        if (confirmed.value){
          selectableIndices.value = [];
          confirmed.value = false;
          console.log("selectedplayerafter: " + selectedPlayer.value);
          let tmp = selectedPlayer.value;
          selectedPlayer.value = -1
          selectablePhaseAction.value = ""
          // 将已经度过的时间提升
          timeElapsed.value += i;
          return tmp;
        }
      }

      console.log("phase end: " + gameData.value.current_phase);
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
      if (gameData.value.current_phase === "Werewolf"){
        handleMultipleKillVotes();
      }
      else {
        syncTargets.value = {};
        timeElapsed.value = 0;
      }
    }

    async function handleMultipleKillVotes(){
      if (roleInfo.value.role === "Werewolf") {
        // 这里可能会被执行多次，所以要保证时间不会过长
        const killVoteTarget = await select("选择要杀死的目标", "杀死",
            gameData.value.phase_timer[gameData.value.current_phase] - timeElapsed.value, null, true);
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
      console.log(JSON.stringify(actionToSend));
      sendMessage(actionToSend,
        "game"
      );
    }

    // // 聊天说话
    // function handleTalk(content){
    //   sendMessage(
    //       {
    //         type: "talk_content",
    //         content: content
    //       }
    //   )
    // }

    // // 主动结束发言
    // function handleTalkEnd(){
    //   sendMessage(
    //       {
    //         type: "talk_end",
    //         player: this.currentPlayerId
    //       }
    //   )
    // }
    //
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

      sendSystemMessage("狼人请行动", "action", "请选择要杀害的对象");
      gameData.value = message.game;

      await handleMultipleKillVotes();
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
      console.log("syncTargets" + JSON.stringify(message.targets));
      console.log("syncTargetsProcessed" + JSON.stringify(targetDict));
      syncTargets.value = targetDict;

    }

    function handleKillResult(message) {
      // 处理刀人结果
      if (message.kill_result){
        sendSystemMessage(message.kill_result + "号玩家被你们杀死");
      }

      updateGame(message.game)
    }

    function handleKillPhaseEnd(message) {
      // 刀人阶段结束的同步。这里其实不应同步游戏信息，因为到第二天早上人才会死。
      sendSystemMessage("狼人阶段结束");
      updateGame(message.game);
    }

    async function handleCheckPhase(message) {
      // 处理Prophet查人阶段, 不能告诉他谁死了
      sendSystemMessage("预言家请行动", "action", "请选择要查验的玩家");
      updateGame(message.game);
      if (roleInfo.value.role === "Prophet"){

        const checkTarget = await select("选择要查验的目标", "查验",
            gameData.value.phase_timer[gameData.value.current_phase], null, true);

        handleCheck(checkTarget)
      }

    }

    function handleCheckResult(message) {
      // 处理查人结果
      sendSystemMessage(message.target + "号玩家的身份为" + message.role );

    }

    function handleWitchPhase(message) {
      // 处理Witch阶段
      updateGame(message.game);
      sendSystemMessage("女巫阶段开始");
      gameData.value.current_phase = message.game.current_phase;
    }

    async function handleWitchInfo(message) {
      // 处理Witch信息
      if(roleInfo.value.role === "Witch"){
        roleInfo.value.role_skills = message.role_skills;
        sendSystemMessage("女巫请行动", "action", "请选择使用解药和毒药");
        // console.log("phase: " + selectablePhase.value + "indices: " + selectableIndices.value);
        let cure_target = -1, poison_target = -1;

        if (roleInfo.value.role_skills.cure_count){
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
        roleInfo.value.cure_count -= 1;
        line += "你选择对" + message.cure + "号玩家使用解药";
      }
      if (message.poison){
        roleInfo.value.poison_count -= 1;
        line += "你选择对" + message.poison + "号玩家使用毒药";
      }
      if (line !== ""){
        showInfo("女巫行动", line);
      }
      // TODO: 其实这个信息没有必要提示给玩家，本来也是不知道的。理论上完全不会出现非法情况。
    }


    function handleTalkPhase(message) {
      // 处理发言阶段
      gameData.value = message.game;

      sendSystemMessage("发言阶段开始");
    }

    function handleTalkUpdate(message) {
      // 处理聊天消息更新

      // 创建消息对象
      // if (!message.source){
      //   return;
      // }
      const speaker = [...Object.values(players), ...Object.values(aiPlayers)][Number(message.source)]
      // console.log("source: " + message.source);
      // console.log("speaker: " + speaker);
      const newMessage = {
        senderid: Number(message.source),
        sendername: speaker.name,
        avatar: speaker.avatar,
        text: message.message,
        recipients: "all" // 死亡玩家只能发送给"dead"
      };

      // 将消息推送到消息列表
      messages.value.push(newMessage);

      // 检查是否需要显示未读消息提示
      const chatBox = this.$refs.chatBox;
      if (chatBox && (chatBox.scrollHeight - chatBox.scrollTop - chatBox.clientHeight > 100)) {
        hasUnreadMessages.value = true;
      }

    }

    function handleTalkEndByServer() {
      // 处理服务器发过来的聊天结束
      // this.userMessage = "";  // 没必要直接清空
      // TODO: 消息按钮重新变成灰的
      sendSystemMessage(currentPlayer.value.index + "号玩家，你的发言时间结束。")
      talkStart.value = false;
    }

    async function handleVotePhase(message) {
      // 处理投票阶段
      updateGame(message.game)
      sendSystemMessage("投票阶段开始，请选择你要放逐的玩家");
      const target = await select("投票放逐", "放逐", gameData.value.phase_timer[gameData.value.current_phase],
          null, true);
      handleVote(target);
    }

    function handleVoteResult(message) {
      // 处理投票结果
      if (message.result === null){
        sendSystemMessage("投票结果: 由于出现平票，没有人被放逐");
      }
      else {
        sendSystemMessage("投票结果: "+ message.result + "号玩家被放逐");
      }

    }

    function handleDayDeathInfo(message) {
      // 处理白天死掉的人
      let line = message.victims.join("号，");
      if (line === ""){
        sendSystemMessage("今天白天没有人出局");
      }
      else {
        sendSystemMessage("白天" + line + "号玩家出局了");
      }
      console.log("line: " + line);

    }

    function handleGameEnd(message) {
      // 处理游戏结束
      if (message.end){
        if (message.victory[roleInfo.value.role]){
          if (roleInfo.value.role === "Werewolf") {
            sendSystemMessage("游戏结束！狼人获胜！");
          } else if (roleInfo.value.role === "Idiot") {
            sendSystemMessage("游戏结束！白痴获胜！");
          } else {
            sendSystemMessage("游戏结束！好人阵营获胜！");
          }
        } else {
          if (roleInfo.value.role === "Werewolf") {
            sendSystemMessage("游戏结束！好人阵营获胜！你的阵营失败了……再接再厉！");
          } else if (roleInfo.value.role === "Idiot") {
            // If Idiot loses, either werewolf or villagers won
            if (message.victory["Werewolf"]) {
              sendSystemMessage("游戏结束！狼人获胜！你的阵营失败了……再接再厉！");
            } else {
              sendSystemMessage("游戏结束！好人阵营获胜！你的阵营失败了……再接再厉！");
            }
          } else {
            sendSystemMessage("游戏结束！狼人获胜！你的阵营失败了……再接再厉！");
          }
        }
      }
      // TODO: 展示所有人的角色并留两分钟复盘
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
        const talkStartCleanup = onType('talk_start', handleTalkStart);
        const talkEndCleanup = onType('talk_end', handleTalkEndByServer);
        const votePhaseCleanup = onType('vote_phase', handleVotePhase);
        const voteResultCleanup = onType('vote_result', handleVoteResult);
        const dayDeathInfoCleanup = onType('day_death_info', handleDayDeathInfo);
        const gameEndCleanup = onType('game_end', handleGameEnd);

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
          talkStartCleanup();
          talkEndCleanup();
          votePhaseCleanup();
          voteResultCleanup();
          dayDeathInfoCleanup();
          gameEndCleanup();
          console.log('WebSocket listeners cleaned up');
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
      messages,
      isGameConnected,
      isLobbyConnected,
      connectToGame,
      sendMessage,
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
     // 过滤消息，确保死亡玩家可以看到所有消息，活着的玩家不能看到死亡者的消息
    filteredMessages() {
      console.log('filteredMessages 被计算');
      if (this.isDead) {
        return this.messages;
      }
      return this.messages.filter(msg => msg.recipients !== 'dead');
    },
    formattedTime() {
      const minutes = Math.floor(this.timerSeconds / 60);
      const seconds = this.timerSeconds % 60;
      return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    }

  },

  methods: {

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
      this.selectedPlayer = index;
      // console.log("selectables: " + this.selectableIndices);
      //
      // console.log("selected number " + this.selectedPlayer);

    },

    confirmTarget(){
      // 确认选择
      this.confirmed = true;
      // console.log("confirm selected player: " + this.selectedPlayer)
    },

    // 使用技能的方法
    useAbility(ability) {
      if (ability.hasCount && ability.count > 0) {
        ability.count--;
        // 这里添加使用技能的具体逻辑
        console.log(`使用技能: ${ability.name}`);
      } else if (!ability.hasCount) {
        // 无限次数技能的使用逻辑
        console.log(`使用技能: ${ability.name}`);
      }
    },
    // 可以设置一个动态方法来更新当前玩家名字,后续优化接口
    getRecipientLabel(recipients) {
      if (recipients === 'all') {
        return '所有人';
      } else if (recipients === 'team') {
        return '团队';
      } else if (recipients === 'dead') {
        return '死亡';
      }
      else{
        return '未知';
      }
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

      if (this.userMessage.trim()) {
        // 创建消息对象
        // const newMessage = {
        //   senderid: this.currentPlayer.index, // 假设当前玩家是“你”
        //   sendername: this.currentPlayer.name,
        //   avatar: require('@/assets/head.png'),
        //   text: this.userMessage,
        //   recipients: this.isDead ? "dead" : this.messageRecipient // 死亡玩家只能发送给"dead"
        // };

        // 将消息推送到消息列表
        // 这里先不推了，等到服务器正常返回更新的时候再推上去
        // this.messages.push(newMessage);
        this.sendMessage({
          type: "talk_content",
          content: this.userMessage,
        }, "game")

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

     // 切换日夜模式
    toggleDayNight() {
      this.isDayTime = !this.isDayTime;
      this.sunMoonIcon = this.isDayTime
        ? require('@/assets/sun.svg')  // 白天显示太阳图标
        : require('@/assets/night.svg');  // 晚上显示月亮图标
    },

  },
  watch: {

    showDetails(newVal) {
      // 如果玩家信息框被打开，页面滚动到顶部
      if (newVal) {
        window.scrollTo(0, 0);
      }
    },
    isDead(newVal) {
      if (newVal) {
        this.messageRecipient = "dead"; // 死亡玩家自动选择“死亡”频道
      } else {
        this.messageRecipient = "all";  // 活着的玩家可以选择所有人频道
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

.player-container {
  display: flex; /* 使用flex布局 */
  align-items: center; /* 垂直居中对齐 */
  justify-content: space-between; /* 水平分布元素 */
}

.selected-player {
  background-color: rgba(56, 73, 204, 0.55); /* 替换 #your-color 为您想要的颜色 */
}


.currentPlayer {
  border: 3px solid #f39c12; /* 为当前玩家头像添加黄色边框 */
  box-shadow: 0px 0px 10px rgba(255, 165, 0, 0.8); /* 添加一个光辉效果 */
}

.player {
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;

}

.player.dead {
  text-decoration: line-through;
  background-color: #e0e0e0; 
  color: #b0b0b0;
  opacity: 0.6; 
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

.target-button {
  padding: 10px; /* 内边距可以根据需要调整 */
  width: 50px; /* 设置按钮的宽度 */
  height: 50px; /* 设置按钮的高度 */
  border: none; /* 移除边框 */
  background-color: #3586bb; /* 设置按钮的背景颜色 */
  color: white; /* 设置按钮文字颜色 */
  text-align: center; /* 文字居中 */
  line-height: 30px; /* 调整行高以适应按钮的高度 */
  border-radius: 50%; /* 设置边框半径为50%，使按钮成为圆形 */
  cursor: pointer; /* 鼠标悬停时显示指针 */
  outline: none; /* 移除点击时的轮廓线 */
  font-size: 8px; /* 设置按钮文字大小 */
  transition: background-color 0.3s; /* 添加背景颜色变化的过渡效果 */
}

/* 鼠标悬停时的按钮样式 */
.target-button:hover {
  background-color: #1150b9; /* 鼠标悬停时改变背景颜色 */
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
  width: 60%;
  display: flex;
  flex-direction: column;
  align-items: center;
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

.recipient-select {
  padding: 8px 30px 8px 12px;  /* 左边内边距用于文本，右边留出空间给箭头 */
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 25px; /* 更圆的边角 */
  background-color: var(--background-color);
  color: #333;
  outline: none; /* 去除默认的聚焦边框 */
  cursor: pointer;
  transition: border-color 0.3s ease, background-color 0.3s ease; /* 平滑过渡效果 */
}

.recipient-select:focus {
  border-color: #007bff; /* 聚焦时改变边框颜色 */
  background-color: #fff; /* 聚焦时改变背景颜色 */
}

.recipient-select option {
  background-color: var(--background-color);
  color: #333;
  padding: 10px;
}

.recipient-select::-ms-expand {
  display: none; /* 隐藏 IE 下拉箭头 */
}

.recipient-select::after {
  content: '\f078'; /* 使用Font Awesome的下拉箭头图标 */
  font-family: 'FontAwesome';
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none; /* 确保箭头不可点击 */
}

/* 自定义下拉箭头 */
.recipient-select {
  position: relative;
}

.recipient-select option:hover {
  background-color: #f1f1f1; /* 选项悬停时改变背景 */
}

/* 输入框 */
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

.role-info {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
    font-size: 1.2em; 
    color: #444; 
    margin: 20px; 
    background-color: #f4f4f9;
    border-radius: 10px; 
    padding: 20px; 
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    max-width: 400px;
    margin: 20px auto; 
}


.role-item {
    display: flex; 
    justify-content: space-between;
    align-items: center; 
    margin-bottom: 10px; 
}

/* 标签样式 */
.label {
    font-weight: bold;
    color: #4CAF50; 
    text-transform: uppercase;
    letter-spacing: 1px; 
    width: 120px; 
}


/* 值的样式 */
.value {
    font-weight: normal;
    color: #555; 
    text-align: center; 
    flex: 1;
    font-size: 1.1em;
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
  left: 80%;  /* 将其水平居中 */
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
</style>