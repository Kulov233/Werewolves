<template>
  <Transition name="fade">
    <div v-if="show" class="dialog-overlay" @click="$emit('close')">
      <Transition name="slide">
        <div class="dialog-content" @click.stop>
          <!-- Dialog Header -->
          <div class="dialog-header">
            <h3>邀请玩家</h3>
            <button class="close-btn" @click="$emit('close')">×</button>
          </div>

          <!-- Search Section -->
          <div class="search-section">
            <div class="search-input-container">
              <input
                v-model="searchQuery"
                type="text"
                class="search-input"
                placeholder="输入玩家ID或名字搜索..."
                @input="$emit('search', searchQuery)"
              />
              <button class="search-button" @click="$emit('search', searchQuery)">
                <img src="@/assets/search.svg" alt="Search" class="search-icon" />
              </button>
            </div>
          </div>

          <!-- Search Results -->
          <div class="search-results" v-if="searchResults.length > 0">
            <TransitionGroup name="list" tag="div">
              <div v-for="user in searchResults"
                   :key="user.id"
                   class="user-item"
                   :class="{ 'invited': localInvitedUsers.has(user.id) }">
                <div class="user-info">
                  <div class="avatar-container">
                    <img :src="user.avatar" :alt="user.username" class="user-avatar" />
                  </div>
                  <div class="user-details">
                    <span class="username">{{ user.username }}</span>
                    <span class="user-id">ID: {{ user.id }}</span>
                  </div>
                </div>
                <button
                  class="invite-btn"
                  @click="handleInvite(user.id)"
                  :disabled="localInvitedUsers.has(user.id)"
                  :class="{ 'success': localInvitedUsers.has(user.id) }"
                >
                  <span class="invite-text">
                    {{ localInvitedUsers.has(user.id) ? '已邀请' : '邀请' }}
                  </span>
                </button>
              </div>
            </TransitionGroup>
          </div>

          <!-- Empty State -->
          <TransitionGroup name="fade">
            <div v-if="hasSearched && !searchResults.length"
                 class="empty-state"
                 key="empty">
              <img src="@/assets/wolf.svg" alt="No Results" class="empty-icon" />
              <p>未找到相关玩家</p>
            </div>
          </TransitionGroup>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script>
import { ref, onBeforeUnmount } from 'vue';

export default {
  name: 'InvitePlayerDialog',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    searchResults: {
      type: Array,
      required: true
    },
    hasSearched: {
      type: Boolean,
      required: true
    },
    invitedUsers: {
      type: Array,
      required: true,
      default: () => []
    }
  },

  emits: ['close', 'search', 'invite'],

  setup(props, { emit }) {
    const searchQuery = ref('');
    // 使用 Set 来跟踪本地邀请状态，提高查找效率
    const localInvitedUsers = ref(new Set());
    // 存储定时器的 Map
    const timers = new Map();

    // 处理邀请逻辑
    const handleInvite = (userId) => {
      if (localInvitedUsers.value.has(userId)) return;

      // 添加到本地已邀请集合
      localInvitedUsers.value.add(userId);

      // 发出邀请事件
      emit('invite', userId);

      // 设置3秒后重置的定时器
      const timer = setTimeout(() => {
        localInvitedUsers.value.delete(userId);
        timers.delete(userId);
      }, 3000);

      // 存储定时器以便清理
      timers.set(userId, timer);
    };

    // 组件卸载前清理所有定时器
    onBeforeUnmount(() => {
      timers.forEach(timer => clearTimeout(timer));
      timers.clear();
      localInvitedUsers.value.clear();
    });

    return {
      searchQuery,
      localInvitedUsers,
      handleInvite
    };
  }
}
</script>

<style scoped>
/* Base Styles */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-content {
  width: 90%;
  max-width: 500px;
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

/* Dialog Header */
.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.dialog-header h3 {
  margin: 0;
  font-size: 20px;
  color: #2c3e50;
  font-weight: 600;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 24px;
  color: #64748b;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #f1f5f9;
  color: #1e293b;
}

/* Search Section */
.search-section {
  margin-bottom: 20px;
}

.search-input-container {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: #f8fafc;
}

.search-input:focus {
  border-color: #3b82f6;
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  background: white;
}

.search-button {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.search-button:hover {
  background: #e2e8f0;
}

.search-icon {
  width: 20px;
  height: 20px;
  opacity: 0.5;
  transition: opacity 0.2s ease;
}

/* Search Results */
.search-results {
  max-height: 400px;
  overflow-y: auto;
  margin: -4px;
  padding: 4px;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin-bottom: 8px;
  background: white;
  transition: all 0.3s ease;
}

.user-item:hover {
  transform: translateX(4px);
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-container {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
}

.user-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 500;
  color: #2c3e50;
}

.user-id {
  font-size: 12px;
  color: #64748b;
}

/* Updated Invite Button Styles */
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
  min-width: 80px;
  justify-content: center;
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

.invite-btn:disabled {
  background: linear-gradient(135deg, #93c5fd, #60a5fa);
  cursor: not-allowed;
}

.invite-text {
  font-weight: 500;
  position: relative;
}

.invite-btn.success {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  animation: successPulse 0.3s ease;
}

@keyframes successPulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #64748b;
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
  animation: bounce 2s infinite ease-in-out;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* Scrollbar Styling */
.search-results::-webkit-scrollbar {
  width: 8px;
}

.search-results::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.search-results::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.search-results::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}
</style>