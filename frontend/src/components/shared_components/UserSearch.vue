<template>
  <div class="user-search-container">
    <!-- 搜索头部 -->
    <div class="search-header">
      <h3>查找玩家</h3>
      <div class="search-input-wrapper">
        <input
          type="text"
          v-model="searchQuery"
          @input="handleSearch"
          placeholder="输入用户ID或昵称搜索"
          class="search-input"
        />
        <!-- 加载动画 -->
        <div class="search-icon" v-if="!isLoading">
          <img src="@/assets/search.svg" alt="Search" />
        </div>
        <div class="loading-icon" v-else>
          <img src="@/assets/isLoading.svg" alt="Loading" class="rotating" />
        </div>
      </div>
    </div>

    <!-- 搜索结果列表 -->
    <div class="search-results">
      <div
        v-for="user in searchResults"
        :key="user.id"
        class="user-item"
      >
        <!-- 用户信息 -->
        <div class="user-info">
          <div class="avatar">{{ user.username.charAt(0).toUpperCase() }}</div>
          <div class="user-details">
            <h4>{{ user.username }}</h4>
            <p>ID: {{ user.id }}</p>
          </div>
        </div>

        <!-- 添加好友按钮 -->
        <button
          class="add-friend-btn"
          :class="{
            'sent': sentRequests.includes(user.id),
            'is-friend': user.isFriend
          }"
          @click="handleAddFriend(user)"
          :disabled="sentRequests.includes(user.id) || user.isFriend"
        >
          <img
            :src="getFriendButtonIcon(user)"
            alt="Friend Status"
          />
          {{ getFriendButtonText(user) }}
        </button>
      </div>

      <!-- 空状态展示 -->
      <div v-if="searchQuery && !isLoading && searchResults.length === 0" class="empty-state">
        未找到匹配的用户
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';

export default {
  name: 'UserSearch',
  props: {
    // 搜索用户的方法
    onSearch: {
      type: Function,
      required: true
    },
    // 发送好友请求的方法
    sendFriendRequest: {
      type: Function,
      required: true
    }
  },
  emits: ['search-complete', 'friend-request-sent'],
  setup(props, { emit }) {
    const searchQuery = ref('');
    const searchResults = ref([]);
    const isLoading = ref(false);
    const sentRequests = ref([]);

    // 防抖处理
    let searchTimeout;
    const handleSearch = () => {
      clearTimeout(searchTimeout);
      if (!searchQuery.value.trim()) {
        searchResults.value = [];
        return;
      }

      isLoading.value = true;
      searchTimeout = setTimeout(async () => {
        try {
          const result = await props.onSearch(searchQuery.value);
          if (result.success) {
            searchResults.value = result.users;
            emit('search-complete', result.users);
          } else {
            searchResults.value = [];
            emit('search-complete', []);
            console.error('Search failed:', result.message);
          }
        } catch (error) {
          console.error('搜索失败:', error);
          searchResults.value = [];
          emit('search-complete', []);
        } finally {
          isLoading.value = false;
        }
      }, 300);
    };

    // 获取按钮图标
    const getFriendButtonIcon = (user) => {
      if (user.isFriend) {
        return require('@/assets/friends.svg');
      }
      if (sentRequests.value.includes(user.id)) {
        return require('@/assets/check.svg');
      }
      return require('@/assets/addFriend.svg');
    };

    // 获取按钮文本
    const getFriendButtonText = (user) => {
      if (user.isFriend) {
        return '已是好友';
      }
      if (sentRequests.value.includes(user.id)) {
        return '已发送';
      }
      return '加好友';
    };

    // 发送好友请求
    const handleAddFriend = async (user) => {
      if (user.isFriend || sentRequests.value.includes(user.id)) {
        return;
      }

      try {
        const result = await props.sendFriendRequest(user.id);
        if (result.success) {
          sentRequests.value.push(user.id);
          emit('friend-request-sent', user.id);
        }
      } catch (error) {
        console.error('发送好友请求失败:', error);
      }
    };

    return {
      searchQuery,
      searchResults,
      isLoading,
      sentRequests,
      handleSearch,
      handleAddFriend,
      getFriendButtonIcon,
      getFriendButtonText
    };
  }
};
</script>

<style scoped>
.user-search-container {
  width: 100%;
  max-width: 480px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.search-header {
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
}

.search-header h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #333;
  font-weight: 600;
}

.search-input-wrapper {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 16px;
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: all 0.3s ease;
}

.search-input:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.search-icon,
.loading-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
}

.search-icon img,
.loading-icon img {
  width: 20px;
  height: 20px;
  opacity: 0.5;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.search-results {
  max-height: 400px;
  overflow-y: auto;
}

.user-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.3s ease;
}

.user-item:hover {
  background-color: #f8f9fa;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  background: #e6f2ff;
  color: #409eff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
}

.user-details h4 {
  margin: 0;
  font-size: 15px;
  color: #333;
}

.user-details p {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: #999;
}

.add-friend-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 20px;
  background: #f0f7ff;
  color: #409eff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-friend-btn img {
  width: 16px;
  height: 16px;
}

.add-friend-btn:hover:not(:disabled) {
  background: #e6f2ff;
}

.add-friend-btn.sent {
  background: #f0f0f0;
  color: #999;
  cursor: not-allowed;
}

.add-friend-btn.is-friend {
  background: #f5f5f5;
  color: #666;
  cursor: default;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #999;
  font-size: 14px;
}
</style>