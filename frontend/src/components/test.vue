<template>
  <div class="flex flex-col items-center justify-center min-h-screen gap-4 p-8">
    <h1 class="text-2xl font-bold mb-4">系统通知测试页面</h1>

    <!-- 测试按钮组 -->
    <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
      <button
        v-for="(config, index) in notificationConfigs"
        :key="index"
        @click="showNotification(config)"
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
      >
        {{ config.label }}
      </button>
    </div>

    <!-- 系统通知组件 -->
    <SystemNotice
      v-if="currentNotification"
      v-bind="currentNotification"
      @close="closeNotification"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import SystemNotice from './shared_components/SystemNotice.vue';  // 确保路径正确

const currentNotification = ref(null);

// 测试用的玩家数据
const samplePlayers = [
  {
    name: "玩家1",
    avatar: "https://placekitten.com/100/100"  // 使用示例头像
  },
  {
    name: "玩家2",
    avatar: "https://placekitten.com/101/101"
  }
];

// 通知配置
const notificationConfigs = [
  {
    label: "夜晚通知",
    type: "night",
    message: "天黑请闭眼",
    subMessage: "狼人请睁眼",
    players: []
  },
  {
    label: "白天通知",
    type: "day",
    message: "天亮了",
    subMessage: "昨晚平安夜",
    players: []
  },
  {
    label: "死亡通知",
    type: "death",
    message: "玩家死亡",
    subMessage: "以下玩家被杀害",
    players: samplePlayers
  },
  {
    label: "角色通知",
    type: "role",
    message: "你的身份是狼人",
    subMessage: "请小心行事",
    players: []
  },
  {
    label: "行动通知",
    type: "action",
    message: "请选择要杀害的对象",
    players: samplePlayers
  },
  {
    label: "发言通知",
    type: "speak",
    message: "轮到你发言了",
    subMessage: "请简要陈述你的观点",
    players: []
  }
];

// 显示通知的方法
const showNotification = (config) => {
  currentNotification.value = {
    type: config.type,
    message: config.message,
    subMessage: config.subMessage,
    players: config.players
  };
};

// 关闭通知的方法
const closeNotification = () => {
  currentNotification.value = null;
};
</script>

<style scoped>
/* 如果需要任何额外的样式可以在这里添加 */
</style>