<template>
    <div class="game-container">
      <!-- 左侧玩家列表 -->
      <div class="player-list">
        <div v-for="(player, index) in players" :key="index" :class="['player', { dead: player.isDead }]">
          <img :src="player.avatar" alt="avatar" class="avatar0"/>
          <p>{{ player.name }}</p>
        </div>
      </div>
  
      <!-- 中间聊天框 -->
      <div class="chat-section">
        <div class="chat-box" ref="chatBox">
          <div class="chat-messages">
            <div v-for="(message, index) in messages" :key="index" class="message">
            <div class="message-avatar">
              <img :src="message.avatar" alt="avatar" class="avatar1"/>
            </div>
            <div class="message-content">
              <div class="message-sender">{{ message.sender }}</div>
              <div class="message-text">{{ message.text }}</div>
            </div>
          </div>
          </div>
        </div>
        <!-- 输入框和发送按钮在聊天框外部 -->
      <div class="message-input-section">
        <input
          v-model="userMessage"
          @keyup.enter="sendMessage"
          placeholder="输入消息"
          class="message-input"
        />
        <!-- 图标按钮 -->
        <button @click="sendMessage" class="send-button">
			<img class="send-icon" src="@/assets/send.png" alt="发送图标" /> <!-- 或者使用一个自定义图标图片 -->
        </button>
      </div>
      </div>
  
      <!-- 右侧角色信息 -->
      <div class="role-info">
        <p>你的身份：</p>
        <h3>{{ role }}</h3>
        <h6>阵营目标：</h6>
        <h3>{{ objective }}</h3>
        <h5>胜利条件：</h5>
        <h3>{{ victoryCondition }}</h3>
        <h4>存活的队友：</h4>
        <h3>{{ livingTeammates }}人</h3>
        <button class="exit-button" @click="exitGame">退出游戏</button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        players: [
          { name: "1号 Wang", avatar: require('@/assets/head.png'), isDead: false },
          { name: "2号 Huang", avatar: require('@/assets/head.png'), isDead: false },
          { name: "3号 Zhao", avatar: require('@/assets/head.png'), isDead: false },
          { name: "4号 Li", avatar: require('@/assets/head.png'), isDead: true },
          { name: "5号 Liu", avatar: require('@/assets/head.png'), isDead: true }
        ],
        messages: [
        { sender: "1号 Wang", avatar: require('@/assets/head.png'), text: "天亮请睁眼。昨晚，4号玩家被杀了。" },
        { sender: "2号 Huang", avatar: require('@/assets/head.png'), text: "我只是个平民，什么也不知道，但我们绝对找出狼人了。" },
        { sender: "3号 Zhao", avatar: require('@/assets/head.png'), text: "他肯定有问题！" }
      ],
        userMessage: "",
        role: "狼人",
        objective: "淘汰全部人类",
        victoryCondition: "再淘汰1名人类",
        livingTeammates: 0
      };
    },
    methods: {
      sendMessage() {
        if (this.userMessage.trim()) {// 假设当前玩家的名字和头像
        const currentPlayer = { sender: "你", avatar: require('@/assets/head.png'), text: this.userMessage };
        this.messages.push(currentPlayer);
          this.userMessage = "";
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
      }
    },
	watch: {
    messages() {
      this.scrollToBottom();
    }
  }
  };
  </script>
  
  <style scoped>
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
  .game-container {
    display: flex;
    justify-content: space-between;
    padding: 20px;
  }
  
  .player-list {
    width: 20%;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .player {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .player.dead {
    text-decoration: line-through;
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
  
  .chat-messages {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }
  
  .message {
    background-color: #ffffff;
    padding: 5px;
    border-radius: 5px;
  }
  .message-avatar {
	
  width: 30px;
  height: 30px;
  border-radius: 50%;
}
.message-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f0f0f0;
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
  background-color: #ffffff;
  display: flex;
  width: 100%;
  align-items: center;
}
  .message-input {
	background-color: #f1f1f1;
    width: 100%;
    padding: 8px;
    font-size: 1em;
    border: 1px solid #3f3f3f;
    border-radius: 9px;
    outline: none;
  }
  .send-button {
  background-color: transparent;
  border: none;
  cursor: pointer;
  font-size: 1.5em;
  margin-left: 5px;
}
  .role-info {
    width: 20%;
  }
  
.exit-button {
  background-color: #d9534f; /* 背景颜色 */
  color: black; /* 字体颜色 */
  border: 2px solid #090909; /* 边框和边框颜色 */
  border-radius: 8px; /* 圆角半径，值越大越圆 */
  padding: 1px 11px; /* 内边距 */
  font-family: Arial, sans-serif; /* 字体样式 */
  font-size: 11px; /* 字体大小 */
  font-weight: bold; /* 字体加粗 */
  cursor: pointer; /* 鼠标悬停样式 */
  transition: background-color 0.3s, color 0.3s; /* 添加过渡效果 */
  /*position: absolute;
  top: 50px; /* 距离顶部 50 像素 */
  /*left: 30px; /* 距离左侧 30 像素 */
}

.exit-button:hover {
  background-color: white; /* 悬停时背景颜色 */
  color: #d9534f; /* 悬停时字体颜色 */
  border-color: #d9534f; /* 悬停时边框颜色 */
}
  </style>