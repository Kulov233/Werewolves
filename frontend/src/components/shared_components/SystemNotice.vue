<template>
  <div v-if="visible" class="modal-overlay" @click.self="handleClose"
       :class="{ 'modal-leaving': leaving }">
    <!-- 主内容卡片 -->
    <div :class="[
      'modal-card',
      `card-${type}`,
      getBgColor(),
      { 'card-leaving': leaving },
    ]">
      <!-- 主题装饰元素 -->
      <div :class="['theme-effects', `effects-${type}`]"></div>

      <!-- 图标部分 -->
      <div class="icon-wrapper">
        <div :class="[
          'icon-background',
          getIconBgGradient(),
          `icon-effect-${type}`
        ]">
          <div :class="['icon-ring', `ring-${type}`]"></div>
          <component
            :is="getIcon()"
            :class="['icon', getIconColor(), `icon-animate-${type}`]"
          />
        </div>
      </div>

      <!-- 文本内容 -->
      <div :class="['content-wrapper', `content-${type}`]">
        <h3 :class="['title', getTextColor()]">{{ message }}</h3>
        <p v-if="subMessage" :class="['sub-message', `message-${type}`]">
          {{ subMessage }}
        </p>
      </div>

      <!-- 玩家列表 -->
      <div v-if="players.length" class="players-wrapper">
        <div
          v-for="(player, index) in players"
          :key="index"
          :class="['player-item', `player-${type}`]"
          :style="`animation-delay: ${index * 0.1}s`"
        >
          <div :class="['avatar-wrapper', `avatar-${type}`]">
            <div :class="['avatar-ring', `ring-${type}`]"></div>
            <img :src="player.avatar" :alt="player.name" class="avatar-image" />
          </div>
          <span :class="['player-name', getTextColor()]">{{ player.name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { Moon, Sun, Skull, AlertCircle, UserCheck, MessageCircle, Info, Vote } from 'lucide-vue-next';

export default {
  props: {
    type: { type: String, default: 'info' },
    message: { type: String, default: '' },
    subMessage: { type: String, default: '' },
    players: { type: Array, default: () => [] },
  },

  emits: ['close'],

  setup(props, { emit }) {
    const visible = ref(false);
    let timer = null;

    const handleClose = () => {
      visible.value = false;
      clearTimeout(timer);
      emit('close');
    };

    onMounted(() => {
      visible.value = true;
      // 3秒后自动关闭
      timer = setTimeout(handleClose, 3000);
    });

    onBeforeUnmount(() => {
      clearTimeout(timer);
    });

    const getIcon = () => ({
      night: Moon,
      day: Sun,
      death: Skull,
      role: UserCheck,
      action: AlertCircle,
      speak: MessageCircle,
      info: Info,
      vote: Vote,
    }[props.type] || Info);

    const getIconColor = () => ({
      night: 'text-indigo-100',
      day: 'text-yellow-100',
      death: 'text-red-100',
      role: 'text-purple-100',
      action: 'text-blue-100',
      speak: 'text-green-100',
      info: 'text-gray-100',
      vote: 'text-orange-100',
    }[props.type] || 'text-gray-100');

    const getIconBgGradient = () => ({
      night: 'bg-gradient-to-br from-indigo-500 to-indigo-700',
      day: 'bg-gradient-to-br from-yellow-400 to-yellow-600',
      death: 'bg-gradient-to-br from-red-500 to-red-700',
      role: 'bg-gradient-to-br from-purple-500 to-purple-700',
      action: 'bg-gradient-to-br from-blue-500 to-blue-700',
      speak: 'bg-gradient-to-br from-green-500 to-green-700',
      info: 'bg-gradient-to-br from-gray-500 to-gray-700',
      vote: 'bg-gradient-to-br from-orange-500 to-orange-700',
    }[props.type] || 'bg-gradient-to-br from-gray-500 to-gray-700');

    const getBgColor = () => ({
      night: 'bg-indigo-50/95',
      day: 'bg-yellow-50/95',
      death: 'bg-red-50/95',
      role: 'bg-purple-50/95',
      action: 'bg-blue-50/95',
      speak: 'bg-green-50/95',
      info: 'bg-gray-50/95',
      vote: 'bg-orange-50/95',
    }[props.type] || 'bg-gray-50/95');

    const getTextColor = () => ({
      night: 'text-indigo-900',
      day: 'text-yellow-900',
      death: 'text-red-900',
      role: 'text-purple-900',
      action: 'text-blue-900',
      speak: 'text-green-900',
      info: 'text-gray-900',
      vote: 'text-orange-900',
    }[props.type] || 'text-gray-900');

    return {
      visible,
      handleClose,
      getIcon,
      getIconColor,
      getIconBgGradient,
      getBgColor,
      getTextColor
    };
  }
};
</script>


<style scoped>
/* 基础布局样式 */
.modal-overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  pointer-events: all;
  background: rgba(0, 0, 0, 0.2);
  opacity: 0;
  animation: overlayAppear 0.3s ease forwards;
}

.modal-leaving {
  animation: overlayDisappear 0.3s ease forwards;
}

.modal-card {
  position: relative;
  width: 100%;
  padding: 2.5rem;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
  overflow: hidden;
  animation: cardAppear 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
}

/* 内容区域样式 */
.icon-wrapper {
  position: relative;
  display: flex;
  justify-content: center;
  margin: -1rem auto 1.5rem;
  max-width: 440px;
  z-index: 1;
}

.icon-background {
  position: relative;
  padding: 1.25rem;
  border-radius: 1.25rem;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.icon-background:hover {
  transform: translateY(-5px) scale(1.05);
}

.icon {
  width: 3.5rem;
  height: 3.5rem;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
}

.content-wrapper {
  position: relative;
  max-width: 440px;
  margin: 0 auto;
  text-align: center;
  z-index: 1;
  margin-bottom: 2rem;
}

.title {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  letter-spacing: -0.01em;
}

.sub-message {
  font-size: 1.1rem;
  line-height: 1.5;
  opacity: 0.8;
}

/* 玩家列表样式 */
.players-wrapper {
  position: relative;
  max-width: 440px;
  margin: 0 auto;
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  flex-wrap: wrap;
  z-index: 1;
}

.player-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  animation: playerAppear 0.5s cubic-bezier(0.2, 0.8, 0.2, 1) backwards;
}

.avatar-wrapper {
  position: relative;
  width: 4.5rem;
  height: 4.5rem;
  border-radius: 50%;
  padding: 3px;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  overflow: hidden;
}

.avatar-wrapper:hover {
  transform: translateY(-5px) scale(1.05);
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.player-name {
  font-size: 1rem;
  font-weight: 600;
}

/* 主题样式 */
/* 夜晚主题 */
/* 夜晚主题卡片样式 */
.card-night {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
}

/* 夜晚主题装饰效果 */
.effects-night::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    /* 星星效果 - 使用多层径向渐变 */
    radial-gradient(1px 1px at 20px 30px, rgba(138, 180, 255, 0.8) 0%, transparent 100%),
    radial-gradient(1.2px 1.2px at 40px 70px, rgba(255, 255, 255, 0.6) 0%, transparent 100%),
    radial-gradient(1.5px 1.5px at 50px 160px, rgba(176, 196, 222, 0.7) 0%, transparent 100%),
    radial-gradient(1.2px 1.2px at 90px 40px, rgba(255, 255, 255, 0.6) 0%, transparent 100%),
    radial-gradient(1.4px 1.4px at 130px 80px, rgba(138, 180, 255, 0.8) 0%, transparent 100%),
    radial-gradient(1.8px 1.8px at 160px 120px, rgba(176, 196, 222, 0.7) 0%, transparent 100%),
    /* 月光效果 - 使用径向渐变 */
    radial-gradient(circle at 80% 20%, rgba(176, 196, 222, 0.15) 0%, transparent 50%),
    /* 柔和的夜色渐变背景 */
    linear-gradient(180deg, rgba(230, 236, 255, 0.1) 0%, rgba(214, 226, 255, 0.15) 100%);
  animation: nightEffect 20s infinite alternate;
}

/* 白天主题 */
.card-day {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
}

.effects-day::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% -20%, rgba(255, 200, 0, 0.15) 0%, transparent 70%);
  animation: sunGlow 4s infinite;
}

/* 死亡主题 */
.card-death {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
}

.effects-death::before {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 10px,
    rgba(255, 0, 0, 0.05) 10px,
    rgba(255, 0, 0, 0.05) 20px
  );
  animation: deathBg 3s infinite linear;
}

/* 身份主题 */
.card-role {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
}

.effects-role::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 50%, rgba(147, 112, 219, 0.1) 0%, transparent 70%);
  animation: roleGlow 3s infinite;
}

/* 动作主题 */
.card-action {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
}

.effects-action::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(45deg, transparent 45%, rgba(0, 123, 255, 0.1) 50%, transparent 55%);
  animation: actionSlide 2s infinite;
}

/* 发言主题 */
.card-speak {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
}

.effects-speak::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 50%, rgba(40, 167, 69, 0.1) 0%, transparent 70%);
  animation: speakPulse 3s infinite;
}

/* 主题特定头像样式 */
.avatar-night { border: 2px solid rgba(138, 180, 255, 0.5); }
.avatar-day { border: 2px solid rgba(255, 200, 0, 0.5); }
.avatar-death { border: 2px solid rgba(255, 0, 0, 0.3); }
.avatar-role { border: 2px solid rgba(147, 112, 219, 0.5); }
.avatar-action { border: 2px solid rgba(0, 123, 255, 0.5); }
.avatar-speak { border: 2px solid rgba(40, 167, 69, 0.5); }

/* 主题效果容器 */
.theme-effects {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

/* 动画定义 */
@keyframes cardAppear {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes playerAppear {
  from {
    opacity: 0;
    transform: scale(0.8) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes twinkle {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

@keyframes sunGlow {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 0.3; }
}

@keyframes deathBg {
  0% { background-position: 0 0; }
  100% { background-position: 40px 40px; }
}

@keyframes roleGlow {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.1); }
}

@keyframes actionSlide {
  0% { transform: translateX(-100%) rotate(-45deg); }
  100% { transform: translateX(100%) rotate(-45deg); }
}

@keyframes speakPulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

.icon-ring {
  position: absolute;
  inset: -3px;
  border-radius: inherit;
  border: 2px solid rgba(255, 255, 255, 0.4);
  opacity: 0;
  animation: ringPulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* 夜晚主题的星星闪烁动画 */
@keyframes nightEffect {
  0%, 100% {
    background-position:
      20px 30px,
      40px 70px,
      50px 160px,
      90px 40px,
      130px 80px,
      160px 120px,
      80% 20%,
      0 0;
    opacity: 0.8;
  }
  50% {
    background-position:
      25px 35px,
      45px 75px,
      55px 165px,
      95px 45px,
      135px 85px,
      165px 125px,
      80% 20%,
      0 0;
    opacity: 1;
  }
}

/* 夜晚主题的图标效果
.icon-effect-night {
  background: linear-gradient(135deg, rgba(138, 180, 255, 0.8), rgba(176, 196, 222, 0.8));
  box-shadow:
    0 0 20px rgba(138, 180, 255, 0.2),
    0 0 40px rgba(176, 196, 222, 0.1);
}*/

/* 夜晚主题的图标动画 */
.icon-animate-night {
  animation: moonGlow 4s infinite alternate;
}

@keyframes moonGlow {
  from {
    filter: drop-shadow(0 0 8px rgba(138, 180, 255, 0.4));
  }
  to {
    filter: drop-shadow(0 0 12px rgba(176, 196, 222, 0.6));
  }
}

/* 夜晚主题的头像边框效果*/
.avatar-night {
  border: 2px solid rgba(138, 180, 255, 0.4);
  box-shadow: 0 0 15px rgba(176, 196, 222, 0.2);
}

/* 夜晚主题的文字效果 */
.content-night .title {
  background: linear-gradient(to right, #3a4a6d, #526b9b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.content-night .sub-message {
  color: #526b9b;
}

@keyframes ringPulse {
  0% {
    opacity: 0.8;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(1.2);
  }
}

/* Info 主题样式 */
.card-info {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
}

.effects-info::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 50% 50%, rgba(75, 85, 99, 0.1) 0%, transparent 70%),
    linear-gradient(45deg, transparent 45%, rgba(75, 85, 99, 0.05) 50%, transparent 55%);
  animation: infoEffect 4s infinite;
}

/*
.icon-effect-info {
  background: linear-gradient(135deg, rgba(75, 85, 99, 0.8), rgba(107, 114, 128, 0.8));
  box-shadow:
    0 0 20px rgba(75, 85, 99, 0.2),
    0 0 40px rgba(107, 114, 128, 0.1);
}*/

.icon-animate-info {
  animation: infoIconPulse 2s infinite alternate;
}

.avatar-info {
  border: 2px solid rgba(75, 85, 99, 0.4);
  box-shadow: 0 0 15px rgba(107, 114, 128, 0.2);
}

/* 新增动画关键帧 */
@keyframes overlayAppear {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes overlayDisappear {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
  }
}

@keyframes cardDisappear {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-20px);
  }
}

@keyframes infoEffect {
  0%, 100% {
    opacity: 0.5;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

@keyframes infoIconPulse {
  from {
    filter: drop-shadow(0 0 8px rgba(75, 85, 99, 0.4));
  }
  to {
    filter: drop-shadow(0 0 12px rgba(107, 114, 128, 0.6));
  }
}
/* Vote 主题样式 */
.card-vote {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
}

.effects-vote::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 50% 50%, rgba(251, 146, 60, 0.1) 0%, transparent 70%),
    repeating-linear-gradient(
      45deg,
      transparent,
      transparent 10px,
      rgba(251, 146, 60, 0.05) 10px,
      rgba(251, 146, 60, 0.05) 20px
    );
  animation: voteEffect 3s infinite;
}

/*
.icon-effect-vote {
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.8), rgba(234, 88, 12, 0.8));
  box-shadow:
    0 0 20px rgba(251, 146, 60, 0.2),
    0 0 40px rgba(234, 88, 12, 0.1);
}*/

.icon-animate-vote {
  animation: voteIconPulse 1.5s infinite alternate;
}

.avatar-vote {
  border: 2px solid rgba(251, 146, 60, 0.4);
  box-shadow: 0 0 15px rgba(234, 88, 12, 0.2);
}

@keyframes voteEffect {
  0% {
    background-position: 0% 50%, 0 0;
    opacity: 0.5;
  }
  50% {
    background-position: 100% 50%, 20px 20px;
    opacity: 0.8;
  }
  100% {
    background-position: 0% 50%, 0 0;
    opacity: 0.5;
  }
}

@keyframes voteIconPulse {
  from {
    transform: scale(1);
    filter: drop-shadow(0 0 8px rgba(251, 146, 60, 0.4));
  }
  to {
    transform: scale(1.1);
    filter: drop-shadow(0 0 12px rgba(234, 88, 12, 0.6));
  }
}

</style>