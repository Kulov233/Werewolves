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
      <div class="player-list">
        <div v-for="(player, index) in players" :key="index" :class="['player', { dead: player.isDead }]">
          <img 
            :src="player.avatar" 
            alt="avatar" 
            class="avatar0"
            @click.stop="showPlayerDetails(player, $event)" 
            /><!-- 点击头像触发查看详情 -->
          <p>{{ player.id }}号{{" "}}{{ player.name }}<span v-if="player.id === currentPlayerId"> (你)</span></p> <!-- 如果是当前玩家，显示 "(你)" -->
        </div>
      </div>
  
      <!-- 中间聊天框 -->
      <div class="chat-section">
        <div class="chat-box" ref="chatBox">
          <div class="chat-messages">
            <div  v-for="message in filteredMessages" :key="message.senderid" class="message">
            <div class="message-avatar-container">
              <div class="message-avatar">
                <img :src="message.avatar" alt="avatar" class="avatar1"/>
              </div>
              <span class="recipient-label">
                 <!-- 根据接收者判断是否是“所有人”、“团队”或“死亡者” -->
                ({{ getRecipientLabel(message.recipients) }})
              </span>
            </div>
            <div class="message-content">
              <div class="message-sender">
                <p>
                  {{ message.senderid }}号{{" "}}{{ message.sendername }}
                  <span v-if="message.senderid === currentPlayerId"> (你)</span>
                </p>
              </div>
              <div class="message-text">{{ message.text }}</div>
            </div>
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
      
      <!-- 右侧角色信息 -->
      <div class="role-info">
        <div class="role-item">
            <span class="label">你的身份：</span>
            <span class="value">{{ role }}</span>
        </div>
        <div class="role-item">
            <span class="label">阵营目标：</span>
            <span class="value">{{ objective }}</span>
        </div>
        <div class="role-item">
            <span class="label">胜利条件：</span>
            <span class="value">{{ victoryCondition }}</span>
        </div>
        <div class="role-item">
            <span class="label">存活队友：</span>
            <span class="value">{{ livingTeammates }}人</span>
        </div>
        <!-- 角色能力图标部分 -->
        <div class="role-abilities">

          <div class="abilities-container">
            <!-- 动态显示技能图标 -->
            <template v-for="ability in roleAbilities" :key="ability.id">
              <div class="ability-item" :class="{ 'disabled': ability.count === 0 }">
                <img 
                  :src="require(`@/assets/${ability.icon}`)" 
                  :alt="ability.name"
                  class="ability-icon"
                  :title="ability.description"
                />
                <div class="ability-info">
                  <span class="ability-name">{{ ability.name }}</span>
                  <span class="ability-count" v-if="ability.hasCount">
                    剩余：{{ ability.count }}
                  </span>
                </div>
              </div>
            </template>
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
          <img :src="selectedPlayer.avatar" alt="avatar" class="avatar-modal" />
          <h4>{{ selectedPlayer.name }}</h4>
          <p>角色：{{ selectedPlayer.role }}</p>
          <p>阵营：{{ selectedPlayer.team }}</p>
          <p>状态：{{ selectedPlayer.isDead ? '已死亡' : '存活' }}</p>
          <button class="btn-report" @click="reportPlayer(selectedPlayer)">
            <img class="icon" src="@/assets/report.svg" alt="举报" />
          </button>
          <button class="btn-add-friend" @click="addFriend(selectedPlayer)">
            <img class="icon" src="@/assets/addFriend.svg" alt="添加好友" />
          </button>
        </div>
      </div>
    </div>
  </template>
  
<script lang="ts">
import ConfirmDialog from './shared_components/ConfirmDialog.vue'
import { onMounted, ref , onUnmounted} from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { useWebSocket } from '@/composables/useWebSocket';
import { validateGame, type GameData } from '@/schemas/schemas';
import axios from 'axios';



export default {
  data() {
    return {
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
            id: 'heal',
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
      players: [
        {
          id: 1,
          name: "Wang",
          avatar: require('@/assets/head.png'),
          isDead: false,
          role: "Werewolf",
          team: "Werewolf阵营",
          victoryCondition: "淘汰所有人类"
        },
        {
          id: 2,
          name: "Huang",
          avatar: require('@/assets/head.png'),
          isDead: true,
          role: "平民",
          team: "人类阵营",
          victoryCondition: "找出所有Werewolf"
        },
        {
          id: 3,
          name: "Zhao",
          avatar: require('@/assets/head.png'),
          isDead: false,
          role: "Werewolf",
          team: "Werewolf阵营",
          victoryCondition: "淘汰所有人类"
        },
        {
          id: 4,
          name: "Li",
          avatar: require('@/assets/head.png'),
          isDead: true,
          role: "平民",
          team: "人类阵营",
          victoryCondition: "找出所有Werewolf"
        },
        {
          id: 5,
          name: "Liu",
          avatar: require('@/assets/head.png'),
          isDead: true,
          role: "平民",
          team: "人类阵营",
          victoryCondition: "找出所有Werewolf"
        }

      ],
      messages: [
        { senderid: 1, sendername: "Wang", recipients: "all", avatar: require('@/assets/head.png'), text: "天亮请睁眼。昨晚，4号玩家被杀了。" },
        { senderid: 2, sendername: "Huang", recipients: "dead", avatar: require('@/assets/head.png'), text: "我只是个平民，什么也不知道，但我们绝对找出Werewolf了。" },
        { senderid: 3, sendername: "Zhao", recipients: "all", avatar: require('@/assets/head.png'), text: "他肯定有问题！" }
      ],
      userMessage: "",


      role: "Witch",
      objective: "淘汰全部人类",
      victoryCondition: "再淘汰1名人类",
      livingTeammates: 0,
      showDetails: false,   // 控制显示详细信息

      showMenuSidebar: false, // 控制侧边栏的显示与否
      showFriendsSidebar: false,
      showHistorySidebar: false,

      isDead: false, // 当前玩家是否死亡
      selectedPlayer: null,  // 被选中的玩家

      playerDetailsTop: 0,  // 玩家详情框的top位置
      playerDetailsLeft: 0,  // 玩家详情框的left位置

      // （小）阶段标记
      phase: null,
      // 其他狼人的投票
      sync_targets: [],

      // 日夜切换
      isDayTime: true,  // 默认是白天
      sunMoonIcon: require('@/assets/sun.svg') , // 默认图标是太阳
      messageRecipient: "all", // 消息的接收者，默认为"所有人"

      currentPlayerId: 1,  // 当前玩家ID
      currentPlayerName: "Wang",
    };
  },

  setup() {
    // 弹窗以及websocket建立
    const aiCounter = ref(1);

    const store = useStore();
    const router = useRouter();
    const roomData = ref(store.state.currentRoom);
    const userProfile = ref(store.state.userProfile);
    const token = localStorage.getItem('access_token');
    const { connect, sendMessage, onType, isConnected } = useWebSocket(token);


    // 弹窗相关的状态
    const showDialog = ref(false);
    const dialogTitle = ref('');
    const dialogMessage = ref('');
    const dialogShowConfirm = ref(true);
    const currentDialogAction = ref('');

    // 游戏数据类型
    type GameData = {
    id: string;
    title: string;
    description: string;
    max_players: number;
    night_count: number;
    roles: {
      Werewolf: number;
      Prophet: number;
      Witch: number;
      Villager: number;
    };
    witch_config: {
      cure_count: number;
      poison_count: number;
    };
    players: {
      [key: string]: {
        index: string;
        name: string;
        alive: boolean;
        online: boolean;
      };
    };
    ai_players: {
      [key: string]: {
        index: string;
        name: string;
        alive: boolean;
      };
    };
    current_phase: 'Initialize' | 'Werewolf' | 'Prophet' | 'Witch' | 'Day' | 'Speak' | 'Vote' | 'End';
    phase_timer: {
      Initialize: number;
      Werewolf: number;
      Prophet: number;
      Witch: number;
      Day: number;
      Speak: number;
      Vote: number;
      End: number;
    };
  }

    // 工具函数，用于阶段转换时更新信息; 要求为GameData类型
    function updateGame(game){
      const result = validateGame(game)
      if (result){
        for (const player of this.players){
          player.isDead = game[player.id]["isDead"];
        }
      }
      else {
        console.error('Validation errors: GameData validate failed; ' +
            'stopped updating game data.', result.errors);
      }

    }

    // 投票用工具函数
    function selectPlayer(title, content, players){
      // TODO: 依据players列表展示相应的玩家，让玩家选中一个后弹窗消失
      dialogTitle.value = title;
      dialogMessage.value = content;
      currentDialogAction.value = "selectPlayer";
      dialogShowConfirm.value = true;
      showDialog.value= true;
      for (const player of players){
        player.show()
      }

      return 0;
    }

    // 展示信息用工具函数
    function showInfo(title, content){
      // TODO: 依据players列表展示相应的玩家，让玩家选中一个后弹窗消失
      dialogTitle.value = title;
      dialogMessage.value = content;
      currentDialogAction.value = "showInfo";
      dialogShowConfirm.value = true;
      showDialog.value= true;
      return 0;
    }

    // 狼人投票方法
    function handleKillVote(seq_num){
      sendMessage(
          {
            type: "kill_vote",
            target: seq_num,  // TODO: 需要把这里改为真实投票。弹窗？
          }
      )
    }

    // 预言家查人
    function handleCheck(seq_num){
      sendMessage(
          {
            type: "check",
            target: seq_num,
          }
      )
    }

    // 女巫操作
    function handleWitchAction(cure_num, poison_num){
      sendMessage(
          {
            type: "witch_action",
            cure: cure_num,
            poison: poison_num,
          }
      )
    }

    // 聊天说话
    function handleTalk(content){
      sendMessage(
          {
            type: "talk_content",
            content: content
          }
      )
    }

    // 主动结束发言
    function handleTalkEnd(){
      sendMessage(
          {
            type: "talk_end",
            player: this.currentPlayerId
          }
      )
    }

    // 白天投票
    function handleVote(seq_num){
      sendMessage(
          {
            type: "vote",
            target: seq_num,
          }
      )
    }

    /* WebSocket实时监听部分*/
    function handleRoleInfo(message) {
      // 处理分配角色信息
      this.role = message.role_info['role'];
      if(message.role_skills != null){
        if(this.role === 'Witch'){
          this.roleAbilitiesConfig.Witch[0].count = message.role_skills['cure_count']
          this.roleAbilitiesConfig.Witch[1].count = message.role_skills['poison_count']
        }
      }
    }

    function handleNightPhase(message) {
      // 处理夜晚阶段
      this.isDayTime = false;
      updateGame(message.game);
    }

    function handleKillPhase() {
      // 处理Werewolf投票阶段
      this.phase = 'kill';
    }

    function handleWolfSync(message) {
      // 处理Werewolf投票同步
      this.sync_targets = message.targets;
    }

    function handleKillResult(message) {
      // 处理刀人结果
      if (message.result != null){
        this.players[Number(message.result)].isDead = true;
      }
    }

    function handleKillPhaseEnd() {
      // 刀人阶段结束的同步。这里其实不应同步游戏信息，因为到第二天早上人才会死。
      // TODO: 这里该做什么？是不是什么都不需要做？
    }

    function handleCheckPhase() {
      // 处理Prophet查人阶段
      this.phase = 'check';
    }

    function handleCheckResult(message) {
      // 处理查人结果
      // TODO: 弹窗？需要改进，弹一个包含所有角色的窗出来
      // 然后点击一个选中，消掉弹窗
      selectPlayer("查验结果", String(message.target) + "号的身份: " + message.role, this.players);
    }

    function handleWitchPhase() {
      // 处理Witch阶段
      this.phase = "witch";
    }

    function handleWitchInfo(message) {
      // 处理Witch信息
      const victims = [];
      for (const num of message.cure_target){
        victims.push(this.players[num]);
      }
      const cure_target = selectPlayer("解药选择", "请选择你要使用解药救的角色", victims);
      const poison_target = selectPlayer("毒药选择", "请选择你要使用毒药杀死的角色", this.players);
      handleWitchAction(cure_target, poison_target);
    }

    function handleWitchActionResult() {
      // 处理Witch操作结果
      // let result1 , result2;
      // result1 = message.cure;
      // result2 = message.poison;
      // TODO: 其实这个信息没有必要提示给玩家，本来也是不知道的。理论上完全不会出现非法情况。
    }

    function handleDayPhase(message) {
      // 处理白天阶段
      this.isDayTime = true;
      updateGame(message.game);
    }

    function handleNightDeathInfo(message) {
      // 处理晚上死掉的人
      let line = "";
      for (const num of message.victims){
        line += String(num) + "号，";
      }
      if (message.victims === []){
        line = "昨晚是平安夜";
      }
      else {
        line = "昨晚" + line + "玩家被杀害了";
      }
      showInfo("夜晚报告", line)
    }

    function handleTalkPhase() {
      // 处理发言阶段
      this.phase = "talk";
    }

    function handleTalkUpdate(message) {
      // 处理聊天消息更新

      // 创建消息对象
      // if (!message.source){
      //   return;
      // }
      const newMessage = {
        senderid: message.source, // 假设当前玩家是“你”
        sendername: this.players[Number(message.source)].name,
        avatar: this.players[Number(message.source)].avatar,
        text: message.message,
        recipients: this.isDead ? "dead" : this.messageRecipient // 死亡玩家只能发送给"dead"
      };

      // 将消息推送到消息列表
      this.messages.push(newMessage);

      // 滚动到底部
      this.scrollToBottom();

    }

    function handleTalkStart() {
      // 处理聊天到你
      // TODO: 检测用户按下发消息案件；之前应该一直是灰的，只有这时候才能按。
    }

    function handleTalkEndByServer() {
      // 处理服务器发过来的聊天结束
      this.scrollToBottom();
      this.userMessage = "";  // 是不是有点残忍了
      // TODO: 消息按钮重新变成灰的
    }

    function handleVotePhase() {
      // 处理投票阶段
      this.phase = "vote";
    }

    function handleVoteResult(message) {
      // 处理投票结果
      if (message.result === null){
        showInfo("投票结果", "由于出现平票，没有人被放逐");
      }
      else {
        showInfo("投票结果", message.result + "号玩家被放逐");
      }

    }

    function handleDayDeathInfo(message) {
      // 处理白天死掉的人
      let line = "";
      for (const num of message.victims){
        line += String(num) + "号，";
      }
      if (message.victims === []){
        line = "今天白天没有人出局";
      }
      else {
        line = "白天" + line + "玩家出局了";
      }
      showInfo("白天报告", line)
    }

    function handleGameEnd(message) {
      // 处理游戏结束
      if (message.end){
        if (message.victory[this.role]){
          showInfo("游戏结束！", "你的阵营获胜！")
        }
        else {
          showInfo("游戏结束！", "你的阵营失败了……再接再厉！")
        }
      }
      // TODO: 展示所有人的角色并留两分钟复盘
    }

    const setupWebsocketListeners = () => {
        // 处理各个阶段和事件
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


    onMounted(() => {
      // 只在未连接时初始化连接
      if (!isConnected.value) {
        connect();
      }
      setupWebsocketListeners();
    });

    onUnmounted(() => {
      sendMessage({
        type: 'quit',
        action: 'leave_combat',
        player_id: this.currentPlayerId,
      });
    });




  },
  created() {
    // 初始化数据
    this.initializeMessages();
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

    // 根据当前角色获取对应的技能列表
    roleAbilities() {
      // 根据角色名获取对应的技能配置
      return this.roleAbilitiesConfig[this.role.toLowerCase()] || [];
    },
  },

  methods: {

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
    initializeMessages() {
      this.messages = [
        { senderid: 1, sendername: "Wang", recipients: "all", avatar: require('@/assets/head.png'), text: "天亮请睁眼。昨晚，4号玩家被杀了。" },
        { senderid: 2, sendername: "Huang", recipients: "dead", avatar: require('@/assets/head.png'), text: "我只是个平民，什么也不知道，但我们绝对找出Werewolf了。" },
        { senderid: 3, sendername: "Zhao", recipients: "all", avatar: require('@/assets/head.png'), text: "他肯定有问题！" }
      ];
    },
    // 可以设置一个动态方法来更新当前玩家名字,后续优化接口
    setCurrentPlayer(playerId) {
      this.currentPlayerId = playerId;  // 设置当前玩家ID
    },
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
      this.selectedPlayer = null;
    },


    // 阻止点击菜单内部时关闭
    stopClick(event) {
      event.stopPropagation();
    },

    sendChatMessage() {

      if (this.userMessage.trim()) {
        // 创建消息对象
        const newMessage = {
          senderid: this.currentPlayerId, // 假设当前玩家是“你”
          sendername: this.currentPlayerName,
          avatar: require('@/assets/head.png'),
          text: this.userMessage,
          recipients: this.isDead ? "dead" : this.messageRecipient // 死亡玩家只能发送给"dead"
        };

        // 将消息推送到消息列表
        this.messages.push(newMessage);

        // 清空输入框
        this.userMessage = "";

        // 滚动到底部
        this.scrollToBottom();
      }
    },

    scrollToBottom() {
      // 滚动聊天框到底部
      this.$nextTick(() => {
        const chatBox = this.$refs.chatBox;
        chatBox.scrollTop = chatBox.scrollHeight;
      });
    },
    exitGame() {
      alert("退出游戏");
    },
    showPlayerDetails(player, event) {
      this.selectedPlayer = player;
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
  messages() {
    this.scrollToBottom();
  },
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

.player-list {
  width: 20%;
  display: flex;
  flex-direction: column;
  gap: 10px;
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

.player span {
  font-size: 12px;
  color: var(--name-color);
}
.chat-section {
  width: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
/*border-radius: 50px;*/
}

.chat-box {
  width: 100%;
  height: 500px; /* 设置初始高度为 500px */
  border: 1px solid #3d3d3d;
  padding: 10px;
  margin-bottom: 10px;
  max-height: 300px;
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
.message {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 10px;
  transition: transform 0.3s ease;
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
  background-color: #ffffff;
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
    width: 100%;
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
</style>