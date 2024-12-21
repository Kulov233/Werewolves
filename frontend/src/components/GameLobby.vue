<template>

    <div class="main-page" @click="closeALL" >
      <!-- 顶部菜单栏 -->
      <div class="top-bar">
        <button class="icon-button left" @click.stop="toggleSidebar('menu')">
          <img class="icon" src="@/assets/menu.svg" alt="Menu" />
        </button>
        <!-- 右侧按钮组 -->
        <div class="right-buttons">
          <button class="icon-button" @click.stop="toggleSidebar('invites')">
            <img class="icon" src="@/assets/wolf.svg" alt="Game Invites" />
            <span class="badge" v-if="gameInvites.length > 0">{{gameInvites.length}}</span>
          </button>
          <button class="icon-button" @click.stop="toggleSidebar('friends')">
            <img class="icon" src="@/assets/friends.svg" alt="Friends" />
            <span class="badge" v-if="friendRequests.length > 0">{{friendRequests.length}}</span>
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

      <!-- 右侧滑出菜单 Invites -->
      <transition name="slide-right">
        <div v-if="showInvitesSidebar" class="sidebar invites-sidebar" @click.stop>
          <div class="sidebar-header">
            <h3>游戏邀请</h3>
            <div class="header-actions">
              <button class="close-btn" @click="toggleSidebar('invites')">
                <img src="@/assets/close-createRoom.svg" alt="Close"/>
              </button>
            </div>
          </div>

          <div class="invites-list">
            <div v-for="invite in gameInvites"
                 :key="invite.id"
                 class="invite-item"
                 :class="{
                    'accept-exit': invite.status === 'accept',
                    'reject-exit': invite.status === 'reject'
                  }">
              <img :src="invite.avatar" alt="Avatar" class="invite-avatar"/>
              <div class="invite-info">
                <span class="invite-name">{{invite.name}}</span>
              </div>
              <div class="invite-actions">
                <button class="accept-btn"
                        @click="handleGameInvite(invite.room_id, 'accept')"
                        :disabled="invite.status">接受</button>
                <button class="reject-btn"
                        @click="handleGameInvite(invite.room_id, 'reject')"
                        :disabled="invite.status">拒绝</button>
              </div>
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
              <button class="icon-btn" @click="refreshOnline" title="刷新好友相关信息">
                <img src="@/assets/refresh.svg" alt="refresh online"/>
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
                   :id="'request-' + request.id"
                   class="request-item"
                   :class="{
                      'accept-exit': request.status === 'accept',
                      'reject-exit': request.status === 'reject'
                    }">
                <img :src="request.avatar" alt="Avatar" class="request-avatar"/>
                <div class="request-info">
                  <span class="request-name">{{request.name}}</span>
                </div>
                <div class="request-actions">
                  <button class="accept-btn"
                          @click="handleFriendRequest(request.id, 'accept')"
                          :disabled="request.status">接受</button>
                  <button class="reject-btn"
                          @click="handleFriendRequest(request.id, 'reject')"
                          :disabled="request.status">拒绝</button>
                </div>
              </div>
            </div>
          </div>

          <!-- 添加好友面板 -->
          <div v-if="showAddFriend" class="add-friend-panel">
              <UserSearch
                :onSearch="handleSearch"
                :sendFriendRequest="sendFriendRequest"
                @search-complete="handleSearchComplete"
                @friend-request-sent="handleFriendRequestSent"
              />
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
                  <img :src="friend.avatar" alt="Avatar" class="friend-avatar" @click.stop="showProfile(friend.id)"/>
                  <div class="friend-info">
                    <span class="friend-name">{{friend.name}}</span>
                    <span class="friend-status">{{friend.status}}</span>
                  </div>
                  <div class="friend-actions">
                    <button class="action-btn delete-friend-btn" @click="deleteFriend(friend.id)">
                      <img src="@/assets/deleteFriend.svg" alt="Delete Friend"/>
                    </button>
                  </div>
                  <!-- 个人资料卡弹窗 -->
                  <transition name="profile">
                    <div v-if="selectedFriend === friend.id" class="profile-card" @click.stop>
                      <div class="profile-header">
                         <img :src="selectedProfile.avatar"
                            alt="头像"
                            class="large-avatar"/>
                        <div class="profile-info">
                          <h4>{{ selectedProfile.name || '房主昵称' }}</h4>
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
                        <button class="action-btn report-btn" @click="reportUser(selectedProfile.userId)">
                          <img src="@/assets/report.svg" alt="举报" class="action-icon"/>
                          举报
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
                  <img :src="friend.avatar" alt="Avatar" class="friend-avatar" @click.stop="showProfile(friend.id)"/>
                  <div class="friend-info">
                    <span class="friend-name">{{friend.name}}</span>
                    <span class="friend-status">{{friend.lastSeen}}</span>
                  </div>
                  <div class="friend-actions">
                    <button class="action-btn delete-friend-btn" @click="deleteFriend(friend.id)">
                      <img src="@/assets/deleteFriend.svg" alt="Delete Friend"/>
                    </button>
                  </div>
                  <!-- 个人资料卡弹窗 -->
                  <transition name="profile">
                    <div v-if="selectedFriend === friend.id" class="profile-card" @click.stop>
                      <div class="profile-header">
                         <img :src="selectedProfile.avatar"
                            alt="头像"
                            class="large-avatar"/>
                        <div class="profile-info">
                          <h4>{{ selectedProfile.name || '房主昵称' }}</h4>
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
                        <button class="action-btn report-btn" @click="reportUser(selectedProfile.userId)">
                          <img src="@/assets/report.svg" alt="举报" class="action-icon"/>
                          举报
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
              <span class="stat-number">{{userProfile.stats[0].value}}</span>
              <span class="stat-label">总场次</span>
            </div>
            <div class="stat-card">
              <span class="stat-number">{{userProfile.stats[1].value}}</span>
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
            <select v-model="timeSort" class="filter-select">
              <option value="desc">从近到远</option>
              <option value="asc">从远到近</option>
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
                <span class="game-time">{{game.date}}</span>
              </div>
              <div class="game-details">
                <div class="role-info">
                  <img :src="getRoleIcon(game.role)" alt="Role" class="role-icon"/>
                  <span class="role-name">{{$translate(game.role) }}</span>
                </div>
                <div class="game-stats">
                  <div class="stat">
                    <span class="label">场次时长</span>
                    <span class="value">{{game.duration}}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>

      <!-- 主体内容 -->
      <main class="content" :class="{ 'show-create-room': showCreateRoomPanel }">
        <!-- 房间列表部分 -->
        <section class="room-list" :class="{ 'shrink': showCreateRoomPanel }" ref="roomList">

          <div class="room-list-header">
            <h2>房间列表</h2>
            <div class="search-bar" @click.stop>
              <!-- 左侧 search.svg 组件 -->
              <div class="search-icon" v-show="showSearchIcon">
                <img src="@/assets/search.svg" alt="Search" />
              </div>

              <!-- 中间输入框 -->
              <input
                type="text"
                v-model="searchQuery"
                @focus="onFocus"
                @blur="onBlur"
                placeholder="搜索房间"
                ref="inputBox"
                @keyup.enter="searchRoom"
              />

              <!-- 删除按钮和分隔符 -->
              <div v-if="searchQuery.length > 0" class="clear-container">
                <button class="clear-button" @click="clearSearch" title="清空输入">
                  <img src="@/assets/clear.svg" alt="Clear" />
                </button>
                <div class="separator"></div>
              </div>

              <!-- 右侧搜索按钮 -->
              <button class="search-button" @click="searchRoom" title="点击搜索">
                <img src="@/assets/search.svg" alt="Search" />
              </button>

              <!-- 历史搜索（点击输入框时显示） -->
              <transition name="fade">
                <div v-show="showHistory && searchQuery.length === 0" class="history">
                  <div class="history-header">
                    <span>搜索历史</span>
                    <button @click.stop="clearAllHistory" class="clear-all-button" title="清空历史记录">
                      <img src="@/assets/clearAll.svg" alt="Clear" class="clear-icon" />
                    </button>
                  </div>
                  <ul>
                    <li v-for="item in history"
                        :key="item"
                        @click.stop="selectHistory(item)"
                        class="history-item">
                      <img src="@/assets/history.svg" alt="History" class="history-icon"/>
                      <span>{{ item }}</span>
                      <button @click.stop="removeHistoryItem(item)" class="remove-item" title="删除历史记录">
                        <img src="@/assets/clear.svg" alt="Clear" class="clear-icon" />
                      </button>
                    </li>
                  </ul>
                </div>
              </transition>
            </div>
            <div class="header-actions">
              <!-- 开关组件 -->
              <modern-toggle
                v-model="isListening"
                @change="handleListenChange"
              />
              <!-- 添加刷新按钮 -->
              <button class="refresh-button" @click="fetchRoomData" title="刷新房间列表">
                <img src="@/assets/refresh.svg" alt="Refresh" class="refresh-icon" />
              </button>

              <!-- 在搜索框右边添加一个创建房间按钮 -->
              <button class="create-Room-button" @click="toggleCreateRoom" title="创建房间">
                <img src="@/assets/createRoom.svg" alt="Create Room" />
              </button>
            </div>
          </div>
          <!-- 添加过渡动画容器 -->
          <transition-group
            name="room-card"
            tag="div"
            class="room-cards">

            <!-- 当没有搜索结果时显示提示信息 -->
            <div v-if="showNoResultsMessage" class="no-results">
              <p>没有找到匹配的房间</p>
            </div>

            <div v-for="room in filteredRooms.length > 0 ? filteredRooms : Rooms"
                :key="room?.id"
                class="room-card">
              <div class="room-card-header">
                <h3>{{ room.title }}</h3>
                <span class="room-type" :class="{ 'ai': room.allow_ai_players }">
                  {{ room.allow_ai_players ? '有AI' : '无AI' }}
                </span>
                <!-- 添加房主头像 -->
                <div class="owner-avatar" @click.stop="showProfile(room.id)">
                  <img :src="room.ownerAvatar" alt="房主头像" />
                  <!-- 个人资料卡弹窗 -->
                  <transition name="profile">
                    <div v-if="selectedRoom === room.id" class="profile-card" @click.stop>
                      <div class="profile-header">
                         <img :src="selectedProfile.avatar"
                            alt="房主头像"
                            class="large-avatar"/>
                        <div class="profile-info">
                          <h4>{{ selectedProfile.name || '房主昵称' }}</h4>
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
                </div>
              </div>


              <div class="room-description">
                <span class="description">
                    {{ room.description }}
                </span>
              </div>

              <div class="room-info">
                <div class="info-item">
                  <img src="@/assets/people.svg" alt="Users" class="info-icon" />
                  <span class="player-count">
                    {{ room.players.length + Object.keys(room.ai_players).length }}/{{ room.max_players }}
                  </span>
                </div>

                <!-- 可以根据需要添加更多房间信息 -->
                <div class="info-item">
                  <img src="@/assets/status.svg" alt="Status" class="info-icon" />
                  <span :class="{'status-full': room.players.length + Object.keys(room.ai_players).length === room.max_players }">
                    {{ room.players.length + Object.keys(room.ai_players).length === room.max_players ? '已满' : '可加入' }}
                  </span>
                </div>
              </div>

              <button
                class="join-button"
                :class="{ 'return-button': isInRoom(room?.id) }"
                @click="joinRoom(room.id)"
                :disabled="room.players.length + Object.keys(room.ai_players).length === room.max_players && !isInRoom(room.id)"
              >
                <span>{{ getJoinButtonText(room) }}</span>
              </button>
            </div>
          </transition-group>
        </section>

        <!-- 创建房间面板 -->
        <transition name="slide-create">
          <section v-if="showCreateRoomPanel" class="create-room">
            <div class="create-room-header">
              <button class="close-create-room" @click="toggleCreateRoom" title="关闭">
                <img src="@/assets/close-createRoom.svg" alt="Close" />
              </button>
              <h2>创建房间</h2>
            </div>

            <div class="create-room-content">

              <!-- 房间名称输入 -->
              <div class="form-group">
                <label for="roomName">房间名称</label>
                <input
                  type="text"
                  id="roomName"
                  v-model="newRoom.title"
                  class="text-input"
                  placeholder="输入房间名称"
                >
              </div>

              <!-- 房间简介输入 -->
              <div class="form-group">
                <label for="roomDescription">房间简介</label>
                <textarea
                  id="roomDescription"
                  v-model="newRoom.description"
                  class="text-input"
                  placeholder="输入房间简介"
                  rows="3"
                ></textarea>
              </div>
              <!-- 选择人数 -->
              <div class="form-group">
                <label for="peopleCount">选择人数</label>
                <select id="peopleCount" v-model="newRoom.maxPlayers" class="select-input">
                  <option v-for="count in peopleOptions" :key="count" :value="count">
                    {{ count }} 人
                  </option>
                </select>
              </div>

              <!-- 房间类型选择 -->
              <div class="form-group">
                <label>房间类型</label>
                <div class="radio-group">
                  <label class="radio-label">
                    <input type="radio" v-model="newRoom.allowAI" :value="true" />
                    <span class="radio-text">有AI</span>
                  </label>
                  <label class="radio-label">
                    <input type="radio" v-model="newRoom.allowAI" :value="false" />
                    <span class="radio-text">无AI</span>
                  </label>
                </div>
              </div>

              <!-- 按钮组 -->
              <div class="action-buttons">
                <button class="create-room-button" @click="createRoom">
                  创建房间
                </button>
              </div>
            </div>
          </section>
        </transition>
      </main>

      <!-- 浮动快速匹配按钮 -->
      <div
        class="quick-match-button-container"
        @mousedown="startDrag"
        @touchstart="startDrag"
        :style="{ top: buttonPosition.y + 'px', left: buttonPosition.x + 'px' }"
      >
        <button class="quick-match-button" @click.stop="toggleQuickMatchPanel" title="快速匹配">
          <img src="@/assets/quickMatch.svg" alt="快速匹配" />
        </button>
      </div>

      <!-- 快速匹配选项窗口 -->
      <transition name="fade">
        <div v-if="showQuickMatchPanel" class="quick-match-panel" @click.stop>
          <h3>快速匹配</h3>
          <div class="form-group">
            <label for="matchPeopleCount">选择人数</label>
            <select id="matchPeopleCount" v-model="matchPeopleCount" class="select-input">
              <option v-for="count in peopleOptions" :key="count" :value="count">
                {{ count }} 人
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>是否有AI</label>
            <div class="radio-group">
              <label class="radio-label">
                <input type="radio" v-model="matchAI" :value="true" />
                  <span class="radio-text">有AI</span>
                </label>
                <label class="radio-label">
                  <input type="radio" v-model="matchAI" :value="false" />
                <span class="radio-text">无AI</span>
              </label>
            </div>
          </div>
          <div class="action-buttons">
            <button class="confirm-match-button" @click="performQuickMatch">
              确认匹配
            </button>
            <button class="cancel-match-button" @click="toggleQuickMatchPanel">
              取消
            </button>
          </div>
        </div>
      </transition>

      <ProfileDialog
        :show="showProfileDialog"
        :userProfile="userProfile"
        @close="showProfileDialog = false"
        @update-avatar="handleAvatarChange"
        @update-signature="saveSignature"
        @update-password="handlePasswordUpdate"
      />

      <ConfirmDialog
        :show="showDialog"
        :title="dialogTitle"
        :message="dialogMessage"
        :showConfirm="dialogShowConfirm"
        @confirm="handleDialogConfirm"
        @cancel="handleDialogCancel"
      />
    </div>
</template>

<script>
import { useWebSocket } from '@/composables/useWebSocket';
import ModernToggle  from './shared_components/ModernToggle.vue'
import ConfirmDialog from './shared_components/ConfirmDialog.vue';
import ProfileDialog from './shared_components/ProfileDialog.vue';
import UserSearch from './shared_components/UserSearch.vue';
import { onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import { ref } from 'vue';
import axios from 'axios';



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
        const response = await axios.post('http://localhost:8000/api/accounts/token/refresh/', {
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
    ModernToggle,
    ConfirmDialog,
    ProfileDialog,
    UserSearch,
  },
  data() {
    return {

      roleIcons: {
        //'Witch': require('@/assets/witch.svg'),
        'Werewolf': require('@/assets/wolf.svg'),
        'Villager': require('@/assets/villager.svg'),
        //'Prophet': require('@/assets/prophet.svg'),
        //'Idiot': require('@/assets/idiot.svg')
      },
      //friendRequests: [
      //  {
      //    id: 1,
      //    name: '张三',
      //    avatar: require('@/assets/profile-icon.png'),
      //    time: '10分钟前'
      //  },
      //  {
      //    id: 2,
      //    name: '李四',
      //    avatar: require('@/assets/profile-icon.png'),
      //    time: '1小时前'
      //  }
      //],
      showFriendRequests: false,
      showAddFriend: false,
      friendSearchQuery: '',
      //onlineFriends: [
      //  {
      //    id: 1,
      //    name: '王五',
      //    avatar: require('@/assets/profile-icon.png'),
      //    status: '游戏中'
      //  },
      //  {
      //    id: 2,
      //    name: '赵六',
      //    avatar: require('@/assets/profile-icon.png'),
      //    status: '在线'
      //  }
      //],


      // 历史记录相关
      totalGames: 128,
      winRate: 76,
      avgRating: 4.8,
      timeFilter: 'all',
      resultFilter: 'all',
      timeSort: 'desc', // 新增：默认从近到远排序

      showNoResultsMessage: false,
      filteredRooms: [],
      searchQuery: "", // 搜索输入
      showSearchIcon: false,   // 控制 search.svg 是否显示
      showHistory: false,      // 控制历史搜索的显示
      history: [], // 历史记录

      peopleOptions: [4, 6, 8, 12, 16], // 可选人数列表

      showMenuSidebar: false, // 控制侧边栏的显示与否
      showFriendsSidebar: false,
      showHistorySidebar: false,

      showCreateRoomPanel: false, // 控制创建房间面板的显示
      selectedRoom: null, // 用于控制显示哪个房间的个人资料卡

      userProfile_test: {
          userId: "user1",
          name: "云想衣裳花想容",
          signature: "点击编辑个性签名",
          avatar: require("@/assets/profile-icon.png"),
          isOnline: true,
          isFriend: false,
          stats: [
            { label: '游戏场数', value: 128 },
            { label: '胜率', value: '76%' },
            { label: '评分', value: 4.8 }
          ],
          recentGames: [
            { id: 'g1', result: 'win', date: '2024-12-04' },
            { id: 'g2', result: 'win', date: '2024-12-03' },
            { id: 'g3', result: 'lose', date: '2024-12-03' }
          ],
      },

      isHoveringAvatar: false,
      isEditingSignature: false,
      tempSignature: "",
      isEditingAvatar: false,

      //userProfile: null,

      buttonPosition: {
        x: 20, // 初始X位置（右下角）
        y: 20, // 初始Y位置
      },
      isDragging: false,
      dragOffset: { x: 0, y: 0 },
      showQuickMatchPanel: false, // 显示快速匹配窗口
      matchPeopleCount: 6, // 快速匹配人数
      matchAI: false // 快速匹配是否有AI

    };
  },
  setup() {
    // 好友相关状态
    const selectedFriendToDelete = ref(null)
    const friendRequests = ref([]);
    const onlineFriends = ref([]);
    const offlineFriends = ref([]);

    // 游戏邀请相关状态
    const gameInvites = ref([]);
    const showInvitesSidebar = ref(false);

    // 密码相关状态
    const tempPasswordData = ref(null);

    // 弹窗相关的状态
    const showProfileDialog  = ref(false);
    const showDialog = ref(false);
    const dialogTitle = ref('');
    const dialogMessage = ref('');
    const dialogShowConfirm = ref(true);
    const currentDialogAction = ref('');

    const selectedRoomForMatch = ref(null);

    const isListening = ref(true);
    const roomCreatedListenerCleanup = ref(null);
    const roomRemovedListenerCleanup = ref(null);

    const store = useStore();
    const router = useRouter();

    const currentRoomID = ref(localStorage.getItem('currentRoomID'));

    let room_created = ref({})
    const userProfile = ref({
      userId: null,
      name: "",
      signature: "",
      avatar: "",
      isOnline: true,
      isFriend: true,
      stats: [
        { label: '游戏场数', value: 0 },
        { label: '胜率', value: '0%' },
        { label: '评分', value: 0 }
      ]
    });
    const Rooms = ref([]);
    //const Rooms = ref([
    //  {
    //    id: 1,
    //    title: '新手村',
    //    description: '欢迎来到狼人杀,让我们一起愉快地玩耍吧!',
    //    owner: 'player1',
    //    ownerAvatar: require('@/assets/profile-icon.png'),
    //    players: ['player1', 'player2'],
    //    ai_players: {},
    //    max_players: 12,
    //  },
    //  {
    //    id: 2,
    //    title: '高玩房',
    //    description: '实力相当的高手对决,无限火力',
    //    owner: 'player3',
    //    ownerAvatar: require('@/assets/profile-icon.png'),
    //    players: ['player3', 'player4', 'player5'],
    //    ai_players: { 'AI_1': '简单', 'AI_2': '普通' },
    //    max_players: 8,
    //  },
    //  {
    //    id: 3,
    //    title: '欢乐休闲',
    //    description: '休闲玩家开黑,禁止语音',
    //    owner: 'player6',
    //    ownerAvatar: require('@/assets/profile-icon.png'),
    //    players: ['player6', 'player7', 'player8', 'player9'],
    //    ai_players: { 'AI_3': '简单' },
    //    max_players: 12,
    //  },
    //  {
    //    id: 4,
    //    title: '9人标准局',
    //    description: '标准9人局,争取胜利',
    //    owner: 'player10',
    //    ownerAvatar: require('@/assets/profile-icon.png'),
    //    players: ['player10', 'player11', 'player12'],
    //    ai_players: {},
    //    max_players: 9,
    //  },
    //  {
    //    id: 5,
    //    title: '大乱斗',
    //    description: '16人混战,你能活到最后吗',
    //    owner: 'player13',
    //    ownerAvatar: require('@/assets/profile-icon.png'),
    //    players: ['player13', 'player14', 'player15'],
    //    ai_players: { 'AI_4': '困难', 'AI_5': '地狱' },
    //    max_players: 16,
    //  },
    //]);
    const selectedProfile = ref({
      userId: '',
      name: '',
      signature: '',
      avatar: require('@/assets/profile-icon.png'),
      isOnline: false,
      isFriend: false,
      stats: [],
      recentGames: []
    });
    const newRoom = ref({
      title: '',
      description: "无",
      maxPlayers: 6,
      allowAI: false,
    });

    // 函数用于初始化或重新设置房间信息
    const initializeRoom = () => {
      newRoom.value.title = `${userProfile.value.name}的房间`; // 设置房间标题
      newRoom.value.description = "无";
      newRoom.value.maxPlayers = 6;
      newRoom.value.allowAI = false;
    };

    const token = localStorage.getItem('access_token');
    const { connect, disconnect, sendMessage, onType, isLobbyConnected } = useWebSocket(token);

    onMounted(() => {
      // 只在未连接时初始化连接
      if (!isLobbyConnected.value) {
        connect();
      }
      fetchRoomData();
      fetchUserInfo();
      fetchFriendsList();
      fetchFriendRequests();

      // 设置游戏邀请监听
      setupGameInviteListener();
    });

    // 保存清理函数的 ref
    const gameInviteListenerCleanup = ref(null);

    const setupGameInviteListener = () => {

      // 监听游戏邀请
      gameInviteListenerCleanup.value = onType('game_invite', async (data) => {
        try {
          // 获取邀请者信息
          const inviterInfo = await fetchInviterInfo(data.source);

          // 添加新邀请到列表
          gameInvites.value.unshift({
            id: Date.now(),
            room_id: data.room_id,
            source: data.source,
            name: inviterInfo.name,
            avatar: inviterInfo.avatar,
            status: null
          });

          // 创建一个新的数组以存储无重复的邀请
          const uniqueInvites = [];
          const seenCombinations = new Set();

          gameInvites.value.forEach(invite => {
            const combinationKey = `${invite.room_id}-${invite.source}`;
            if (!seenCombinations.has(combinationKey)) {
              uniqueInvites.push(invite);
              seenCombinations.add(combinationKey);
            }
          });

          // 更新gameInvites为无重复的邀请数组
          gameInvites.value = uniqueInvites;
        } catch (error) {
          console.error('处理游戏邀请失败:', error);
        }
      });
    };

    // 获取游戏邀请者信息
    const fetchInviterInfo = async (userId) => {
      try {
        const [userResponse, avatarResponse] = await Promise.all([
          api.get(`/api/accounts/public_info/${userId}/`),
          api.get(`/api/accounts/avatar/${userId}/`)
        ]);

        return {
          name: userResponse.data.username,
          avatar: avatarResponse.status === 200
            ? avatarResponse.data.avatar_url
            : require('@/assets/profile-icon.png')
        };
      } catch (error) {
        console.error('获取邀请者信息失败:', error);
        return {
          name: '未知用户',
          avatar: require('@/assets/profile-icon.png')
        };
      }
    };

    // 处理游戏邀请
    const handleGameInvite = async (roomId, action) => {
      // 更新邀请状态以触发动画
      gameInvites.value = gameInvites.value.map(invite => {
        if (invite.room_id === roomId) {
          return {
            ...invite,
            status: action
          };
        }
        return invite;
      });

      if (action === 'accept') {
        // 接受邀请，加入房间
        await joinRoom(roomId);
      }

      // 延时移除邀请
      setTimeout(() => {
        gameInvites.value = gameInvites.value.filter(invite => invite.room_id !== roomId);
      }, 500);
    };

     // 显示对话框
    const showConfirmDialog = (title, message, showConfirm = false, action = '') => {
      dialogTitle.value = title;
      dialogMessage.value = message;
      dialogShowConfirm.value = showConfirm;
      currentDialogAction.value = action;
      showDialog.value = true;
    };

    function refreshOnline(){
      // 刷新在线状态
      // 发个消息
      fetchFriendsList();
      fetchFriendRequests();
    }

    const handleOnlineFriends = (message) => {
      // 刷新在线还有
      const onlineList = message.friends;
      const allFriendsList = [...onlineFriends.value, ...offlineFriends.value];
      onlineFriends.value = [];
      offlineFriends.value = [];
      for (const friend of allFriendsList){
        if (onlineList.indexOf(friend.id) !== -1){
          // 如果在线
          friend.lastSeen = "在线";
          onlineFriends.value.push(friend);
        }
        else {
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

    // 获取好友请求列表
    const fetchFriendRequests = async () => {
      try {
        const response = await api.get('/api/accounts/friends/requests/');
        const requestIds = response.data.friend_requests;

        // 获取每个请求者的详细信息
        const requestsDetails = await Promise.all(
          requestIds.map(async (requestId) => {
            try {
              const userResponse = await api.get(`/api/accounts/public_info/${requestId}/`);
              const avatarResponse = await api.get(`/api/accounts/avatar/${requestId}/`);

              return {
                id: requestId,
                name: userResponse.data.username,
                avatar: avatarResponse.status === 200
                      ? avatarResponse.data.avatar_url
                      : require('@/assets/profile-icon.png'),
              };
            } catch (error) {
              console.error('获取请求者信息失败:', error);
              return null;
            }
          })
        );

        // 过滤掉获取失败的请求信息
        friendRequests.value = requestsDetails.filter(request => request !== null);
      } catch (error) {
        console.error('获取好友请求列表失败:', error);
      }
    };

    // 发送好友请求
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

    const checkIsFriend = (userId) => {
      // 首先检查是否是自己
      if (userId === userProfile.value.userId) {
        return true;  // 如果是自己，返回true表示"已是好友"状态
      }
      // 其他情况检查是否在好友列表中
      return onlineFriends.value.some(friend => friend.id === userId) ||
             offlineFriends.value.some(friend => friend.id === userId);
    };

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

    const deleteFriend = async (friendId) => {
      showConfirmDialog(
        '确认删除',
        '确定要删除这个好友吗？',
        true,
        'deleteFriend'
      );
      selectedFriendToDelete.value = friendId;
    };

    const handlePasswordUpdate = async ({ oldPassword, newPassword }) => {
      // 使用 showConfirmDialog 显示确认对话框
      showConfirmDialog(
        '确认修改',
        '确定要修改密码吗？',
        true,
        'changePassword'
      );

      // 存储密码信息以供确认后使用
      tempPasswordData.value = {
        oldPassword,
        newPassword
      };
    };


    const handleDialogConfirm = async () => {
      showDialog.value = false;
      if (currentDialogAction.value === 'deleteFriend') {
        // 处理删除好友的逻辑
        try {
            const response = await api.post('/api/accounts/friends/delete/',
                {
                  player: userProfile.value.userId,
                  target: selectedFriendToDelete.value
                },
                {
                  headers: {
                    'Content-Type': 'application/json'
                  }
                }
            );

          if (response.data.status === 'success') {
            // Remove friend from the lists
            onlineFriends.value = onlineFriends.value.filter(
              friend => friend.id !== selectedFriendToDelete.value
            );

            // Show success message using showConfirmDialog
            showConfirmDialog('成功', '已删除好友');
          } else {
            // Show error message using showConfirmDialog
            showConfirmDialog('错误', response.data.message || '删除好友失败');
          }

          fetchFriendsList();
        } catch (error) {
          showConfirmDialog('错误', '删除好友失败，请重试');
        }

      }
      else if (currentDialogAction.value === 'acceptFriend') {
        // 处理接受好友请求的逻辑
        console.log('接受好友请求');
      }
      else if (currentDialogAction.value === 'rejectFriend') {
        // 处理拒绝好友请求的逻辑
        console.log('拒绝好友请求');
      }
      else if (currentDialogAction.value === 'reportUser') {
        // 处理举报用户的逻辑
        console.log('举报用户');
      }
      else if (currentDialogAction.value === 'changePassword') {
        try {
          const response = await api.post('/api/accounts/password/change/',
              {
                old_password: tempPasswordData.value.oldPassword,
                new_password: tempPasswordData.value.newPassword
              },
              {
                headers: {
                  'Content-Type': 'application/json'
                }
              }
              );

          if (response.status === 200) {
            // 显示成功消息并提示重新登录
            showConfirmDialog(
              '密码修改成功',
              '请重新登录',
                true,
                'reLogin',
            );

          }
        }
        catch (error) {
            // 处理不同的错误情况
            if (error.response?.status === 400) {
              const errorData = error.response.data;
              let errorMessage = '';

              // 直接检查错误消息
              if (errorData.old_password) {
                // 如果是数组，获取第一个错误消息
                if (Array.isArray(errorData.old_password)) {
                  errorMessage += errorData.old_password[0] + '<br>';
                } else {
                  errorMessage += errorData.old_password + '<br>';
                }
              }
              if (errorData.new_password) {
                if (Array.isArray(errorData.new_password)) {
                  errorMessage += errorData.new_password[0];
                } else {
                  errorMessage += errorData.new_password;
                }
              }
              showConfirmDialog(
                '错误',
                errorMessage.trim(),
                false
              );
            } else {
              showConfirmDialog(
                '错误',
                '修改密码失败，请重试',
                false
              );
            }
          }
      }
      else if (currentDialogAction.value === 'reLogin') {
        // 断连websocket
        disconnect();
        // 清空 localStorage
        localStorage.clear();
        // 回到登录界面
        router.push('/login');
      }
      else if(currentDialogAction.value === 'quickMatchSuccess'){
        // 处理快速匹配成功的逻辑
        joinRoom(selectedRoomForMatch.value.id);
      }
      else if (currentDialogAction.value === 'logout') {
        try {
          // 断连websocket
          disconnect();

          // 清空 localStorage
          localStorage.clear();
          localStorage.removeItem('isLoggedIn');
          localStorage.removeItem('lastPath');

          // 回到登录界面
          router.push('/login');
        } catch (error) {
          console.error('Logout failed:', error);
          alert('退出登录失败，请重试');
        }
      }

    };

    // 处理对话框取消
    const handleDialogCancel = () => {
      showDialog.value = false;
      if (currentDialogAction.value === 'reLogin') {
        // 断连websocket
        disconnect();
        // 清空 localStorage
        localStorage.clear();
        // 回到登录界面
        router.push('/login');
      }
      currentDialogAction.value = '';
    };

    // 不在组件卸载时断开连接
    onUnmounted(() => {
      // 确保组件卸载时移除监听器
      if (gameInviteListenerCleanup.value) {
        gameInviteListenerCleanup.value();
        gameInviteListenerCleanup.value = null;
      }
      if (roomCreatedListenerCleanup.value) {
        roomCreatedListenerCleanup.value();
      }
      if (roomRemovedListenerCleanup.value) {
        roomRemovedListenerCleanup.value();
      }
    });
    const joinRoom = async (roomId) => {

      try {

        // 如果已经在房间中，直接跳转到房间页面
        if (isInRoom(roomId)) {
          // 获取当前房间数据
          const currentRoom = Rooms.value.find(r => r.id === roomId);
          if (currentRoom) {
            // 更新当前房间ID
            currentRoomID.value = roomId;
            localStorage.setItem('currentRoomID', roomId);

            // 存储房间数据和用户信息到 Vuex
            await store.dispatch('saveRoomData', currentRoom);
            await store.dispatch('saveUserProfile', userProfile.value);
            await store.dispatch('saveOnlineFriends', onlineFriends.value);
            await store.dispatch('saveOfflineFriends', offlineFriends.value);
            router.push({
              name: 'GameRoom',
              params: {id: roomId}
            });
            return;
          }
        }

        // 发送加入房间的 websocket 消息
        sendMessage({
          action: 'join_room',
          room_id: roomId
        });

        // 监听加入房间响应
        const cleanup = onType('player_joined', async (data) => {

          // 更新当前房间ID
          currentRoomID.value = roomId;
          localStorage.setItem('currentRoomID', roomId);

          // 存储房间数据和用户信息到 Vuex
          await store.dispatch('saveRoomData', data.room);
          await store.dispatch('saveUserProfile', userProfile.value);
          await store.dispatch('saveOnlineFriends', onlineFriends.value);
          await store.dispatch('saveOfflineFriends', offlineFriends.value);

          // 跳转到房间页面
          router.push({
            name: 'GameRoom',
            params: { id: roomId }
          });

          // 清理监听器
          cleanup();
        });

      } catch (error) {
        console.error('加入房间失败:', error);
        alert('加入房间失败，请重试');
      }
    };
    const fetchRoomData = () => {
      sendMessage({
        action: 'get_rooms'
      });

      onType('room_list', async (data) => {
        // 获取并处理每个房间的数据
        const processedRooms = await Promise.all(data.rooms.map(async (room) => {
          try {
            // 获取房主头像
            const avatarResponse = await api.get(`/api/accounts/avatar/${room.owner}/`);

            // 返回处理后的房间数据，包含所有原始数据并添加头像
            return {
              ...room, // 保持原有的所有数据
              ownerAvatar: avatarResponse.status === 200
                ? avatarResponse.data.avatar_url
                : require('@/assets/profile-icon.png')
            };
          } catch (error) {
            console.error(`获取房间 ${room.id} 的房主头像失败:`, error);
            // 出错时使用默认头像，但保留其他数据
            return {
              ...room,
              ownerAvatar: require('@/assets/profile-icon.png')
            };
          }
        }));

        // 更新 Rooms 状态
        Rooms.value = processedRooms;
      });
    };

    const handleRoomCreated = async (data) => {
      const newRoomData = data.room;
      const avatarResponse = await api.get(`/api/accounts/avatar/${newRoomData.owner}/`);
      Rooms.value.push({
        ...newRoomData,
        ownerAvatar: avatarResponse.status === 200
          ? avatarResponse.data.avatar_url
          : require('@/assets/profile-icon.png')
      });

      // 删除 Rooms 中 ID 相同的房间
      Rooms.value = Rooms.value.filter((room, index, self) =>
        index === self.findIndex(m => m.id === room.id)
      );
    };

    const handleRoomRemoved = (data) => {
      const removedRoomId = data.room.id;
      Rooms.value = Rooms.value.filter(room => room.id !== removedRoomId);
    };




    // 处理好友状态改变

    // 处理监听状态改变
    const handleListenChange = (newValue) => {
      if (newValue) {
        fetchRoomData();
        // 添加监听器
        roomCreatedListenerCleanup.value = onType('room_created', handleRoomCreated);
        roomRemovedListenerCleanup.value = onType('room_removed', handleRoomRemoved);


      } else {
        // 移除监听器
        if (roomCreatedListenerCleanup.value) {
          roomCreatedListenerCleanup.value()
          roomCreatedListenerCleanup.value = null
        }
        if (roomRemovedListenerCleanup.value) {
          roomRemovedListenerCleanup.value()
          roomRemovedListenerCleanup.value = null
        }
      }
    };

    // 处理房间删除的监听器


    // 创建房间的方法
    const createRoom = async () => {
      try {
        // 发送消息创建房间
        sendMessage({
          action: 'create_room',
          title: newRoom.value.title,
          description: newRoom.value.description,
          max_players: newRoom.value.maxPlayers,
          allow_ai_players: newRoom.value.allowAI,
        });

        onType('room_created', async (data) => {
          if(data.room.owner !== userProfile.value.userId){
            return;
          }
          room_created.value = data.room;

          // 存储房间数据和用户信息到 Vuex
          await store.dispatch('saveRoomData', room_created.value);
          await store.dispatch('saveUserProfile', userProfile.value);
          await store.dispatch('saveOnlineFriends', onlineFriends.value);
          await store.dispatch('saveOfflineFriends', offlineFriends.value);

          // 使用 router 进行导航
          router.push({
            name: 'GameRoom',
            params: { id: room_created.value.id }
          });
        });

        initializeRoom(); // 重置表单
        fetchRoomData(); // 刷新房间列表

      } catch (error) {
        console.error('Error creating room:', error);
      }
    };

    // 获取用户信息
    const fetchUserInfo = async () => {
      try {
        const response = await api.get('/api/accounts/info/');
        const data = response.data;

        // 处理对战记录
        const gameHistory = data.profile.games.map((game, index) => ({
          id: index, // 使用索引作为虚拟id
          result: game.won ? 'win' : 'lose',
          date: new Date(game.date).toLocaleString(), // 格式化日期
          timestamp: new Date(game.date).getTime(), // 添加时间戳用于排序
          role: game.role,
          duration: `${game.duration}分钟`,
        }));

        userProfile.value = {
          userId: data.id,
          name: data.username,
          signature: data.profile.bio || "点击编辑个性签名",
          avatar: `http://localhost:8000${data.profile.avatar}`,
          isOnline: true,
          isFriend: true,
          games:gameHistory,
          stats: [
            { label: '游戏场数', value: data.profile.games.length },
            { label: '胜率', value: calculateWinRate(data.profile.games) },
            // { label: '评分', value: calculateRating(data.profile.games) }
          ]
        };
      } catch (error) {
        console.error('获取用户信息失败:', error);
        // 处理错误，可能需要重定向到登录页面
      }
    };

    // 更新头像
    const updateAvatar = async (file) => {
      try {
        const formData = new FormData();
        formData.append('avatar', file);

        const response = await api.post('/api/accounts/avatar/upload/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }

        });

        if (response.status === 200) {
          // 更新头像URL
          userProfile.value.avatar = `http://localhost:8000${response.data.avatar}`;
          return true;
        }
        return false;
      } catch (error) {
        console.error('上传头像失败:', error);
        return false;
      }
    };

    // 更新个性签名
    const updateSignature = async (newSignature) => {
      try {
        const response = await api.put('/api/accounts/bio/update/', {
          bio: newSignature
        });

        if (response.status === 200) {
          userProfile.value.signature = response.data.bio;
          return true;
        }
        return false;
      } catch (error) {
        console.error('更新个性签名失败:', error);
        return false;
      }
    };


    // 获取用户头像
    const fetchSelectedAvatar = async (userId) => {
      try {
        const response = await api.get(`/api/accounts/avatar/${userId}/`);
        if (response.status === 200) {
          return response.data.avatar_url;
        } else {
          return require('@/assets/profile-icon.png'); // 默认头像
        }
      } catch (error) {
        console.error('获取头像失败:', error);
        return require('@/assets/profile-icon.png'); // 出错时返回默认头像
      }
    };

    // 获取选中的人信息
    const fetchSelectedProfile = async (userId) => {
      try {
        const response = await api.get(`/api/accounts/public_info/${userId}/`);
        const data = response.data;
        return {
          userId: data.id,
          name: data.username,
          signature: data.profile.bio,
          avatar: `http://localhost:8000${data.profile.avatar}`,
          isOnline: true,
          isFriend: checkIsFriend(userId),
          stats: [
            { label: '游戏场数', value: data.profile.wins + data.profile.loses },
            { label: '胜率', value: `${calculateWinRate(data.profile.games)}` },
            { label: '评分', value: data.profile.rating || 0 }
          ],
          recentGames: (data.profile.recent_games || []).map((game, index) => ({
            id: index.toString(),
            result: game.won ? 'win' : 'lose',
            date: new Date(game.date).toLocaleDateString()
          }))
        };
      } catch (error) {
        console.error('获取用户信息失败:', error);
        return null;
      }
    };

    // 辅助函数：计算胜率
    const calculateWinRate = (games) => {
      if (!games || games.length === 0) return '0%';
      const wins = games.filter(game => game.result === 'win').length;
      return `${Math.round((wins / games.length) * 100)}%`;
    };

    // 辅助函数：计算平均评分
    // const calculateRating = (games) => {
    //   if (!games || games.length === 0) return 0;
    //   const totalRating = games.reduce((sum, game) => sum + (game.rating || 0), 0);
    //   return (totalRating / games.length).toFixed(1);
    // };

    // 是当前房间
    const isInRoom = (roomId) => {
      const room = Rooms.value.find(r => r.id === roomId);
      if (!room) return false;

      // 检查玩家是否在普通玩家列表中
      if (room.players.includes(userProfile.value.userId)) {
        return true;
      }

      return false;
    };

    return {
      gameInvites,
      showInvitesSidebar,
      handleGameInvite,
      handlePasswordUpdate,
      tempPasswordData,
      deleteFriend,
      handleSearch,
      friendRequests,
      onlineFriends,
      offlineFriends,
      refreshOnline,
      fetchFriendsList,
      fetchFriendRequests,
      sendFriendRequest,
      isInRoom,
      showProfileDialog,
      joinRoom,
      currentRoomID,
      handleDialogConfirm,
      handleDialogCancel,
      showDialog,
      dialogTitle,
      dialogMessage,
      dialogShowConfirm,
      currentDialogAction,
      selectedRoomForMatch,
      isListening,
      handleListenChange,
      newRoom,
      sendMessage,
      Rooms,
      selectedProfile,
      fetchRoomData,
      userProfile,
      fetchUserInfo,
      updateAvatar,
      fetchSelectedProfile,
      updateSignature,
      fetchSelectedAvatar,
      initializeRoom,
      createRoom,
      disconnect
      // 其他属性和方法
    };
    // 其他组件属性和方法
  },
  computed: {
    displayedRooms() {
      const query = this.searchQuery.toLowerCase().trim();

      // 如果没有搜索关键词，返回所有房间
      if (!query) {
        return this.Rooms;
      }

      // 根据房间名称或ID进行过滤
      return this.Rooms.filter(room => {
        const titleMatch = room.title.toLowerCase().includes(query);
        const idMatch = room.id.toString().includes(query);
        return titleMatch || idMatch;
      });
    },
      filteredGameHistory() {
      let filtered = this.userProfile?.games || this.gameHistory;

      // 按时间筛选
      if (this.timeFilter !== 'all') {
        const now = new Date();
        const days = this.timeFilter === 'week' ? 7 : 30;
        const timeLimit = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);

        filtered = filtered.filter(game => {
          const gameTime = new Date(game.date);
          return gameTime >= timeLimit;
        });
      }

      // 按结果筛选
      if (this.resultFilter !== 'all') {
        filtered = filtered.filter(game => game.result === this.resultFilter);
      }

      // 按时间排序
      filtered.sort((a, b) => {
        const timeA = new Date(a.time).getTime();
        const timeB = new Date(b.time).getTime();
        return this.timeSort === 'desc' ? timeB - timeA : timeA - timeB;
      });

      return filtered;
    }

  },

  mounted() {
    // 设置按钮初始位置为右下角

    // 获取当前roomID
    try {
      this.currentRoomId = localStorage.getItem('currentRoomId');
    } catch (error) {
      console.error('获取当前房间ID失败:', error);
    }

    this.$nextTick(() => {
      const roomList = this.$refs.roomList;
      if (roomList) {
        const rect = roomList.getBoundingClientRect();
        this.buttonPosition.x = rect.width - 70; // 根据容器宽度设置X位置
        this.buttonPosition.y = rect.height - 70; // 根据容器高度设置Y位置
      }
    });

    // 添加全局的鼠标事件监听器
    window.addEventListener("mousemove", this.onDragging);
    window.addEventListener("mouseup", this.stopDrag);
    window.addEventListener("touchmove", this.onDragging);
    window.addEventListener("touchend", this.stopDrag);

  },
  beforeUnmount() {
    // 移除事件监听器
    window.removeEventListener("mousemove", this.onDragging);
    window.removeEventListener("mouseup", this.stopDrag);
    window.removeEventListener("touchmove", this.onDragging);
    window.removeEventListener("touchend", this.stopDrag);
  },




  methods: {
    // 需要复制
    handleSearchComplete() {
    },

    handleFriendRequestSent() {
    },
    async handleLogout() {
      // Show confirmation dialog
      this.dialogTitle = '退出确认';
      this.dialogMessage = '确定要退出登录吗？';
      this.dialogShowConfirm = true;
      this.currentDialogAction = 'logout';
      this.showDialog = true;
    },

    getRoleIcon(roleName) {
      return this.roleIcons[roleName] || require('@/assets/wolf.svg'); // Provide a default icon
    },

    goToHistory() {
      this.showHistorySidebar = true;
      this.showMenuSidebar = false;
    },

    goToFriends() {
      this.showFriendsSidebar = true;
      this.showMenuSidebar = false;
    },

    goToProfile() {
      this.showProfileDialog = true;
    },



  // 修改加入房间按钮的渲染逻辑
  getJoinButtonText(room) {
    if (this.isInRoom(room.id)) {
      return '返回房间';
    }
    if (room.players.length + Object.keys(room.ai_players).length === room.max_players) {
      return '房间已满';
    }
    return '加入房间';
  },

     // 好友系统相关方法
  toggleFriendRequests() {
    this.showFriendRequests = !this.showFriendRequests;
    this.showAddFriend = false;
  },

  toggleAddFriend() {
    this.showAddFriend = !this.showAddFriend;
    this.showFriendRequests = false;
  },

  async handleFriendRequest(requestId, action) {
    try {
      // 先更新 UI 显示状态以触发动画
      this.friendRequests = this.friendRequests.map(request => {
        if (request.id === requestId) {
          return {
            ...request,
            status: action
          };
        }
        return request;
      });

      // 调用 API 处理好友请求
      const response = await api.post('/api/accounts/friends/requests/', {
        player: this.userProfile.userId,
        friend_request: requestId,
        type: action === 'accept' ? 'accept' : 'deny'
      });

      if (response.data.status === 'success') {
        // 设置延时以等待动画完成
        setTimeout(async () => {
          // 从请求列表中移除
          this.friendRequests = this.friendRequests.filter(req => req.id !== requestId);

          if (action === 'accept') {
            try {
              // 获取新好友的详细信息
              const [userResponse, avatarResponse] = await Promise.all([
                api.get(`/api/accounts/public_info/${requestId}/`),
                api.get(`/api/accounts/avatar/${requestId}/`)
              ]);

              // 添加到在线好友列表
              const newFriend = {
                id: requestId,
                name: userResponse.data.username,
                avatar: avatarResponse.data.avatar_url || 'profile-icon.png',
                status: '在线',
                lastSeen: '在线'
              };

              this.onlineFriends.push(newFriend);
            } catch (error) {
              console.error('获取新好友信息失败:', error);
              this.dialogTitle = '提示';
              this.dialogMessage = '已添加好友，但获取好友信息失败，请刷新页面';
              this.dialogShowConfirm = false;
              this.showDialog = true;
            }
          }
        }, 500); // 等待动画完成

        // 显示成功消息
        this.dialogTitle = '成功';
        this.dialogMessage = action === 'accept' ? '已接受好友请求' : '已拒绝好友请求';
        this.dialogShowConfirm = false;
        this.showDialog = true;
      } else {
        // API 返回错误
        this.dialogTitle = '错误';
        this.dialogMessage = response.data.message;
        this.dialogShowConfirm = false;
        this.showDialog = true;

      }
    } catch (error) {
      console.error('处理好友请求失败:', error);

      // 显示错误消息
      this.dialogTitle = '错误';
      this.dialogMessage = '处理好友请求失败，请重试';
      this.dialogShowConfirm = false;
      this.showDialog = true;
    }
  },


    showChangeAvatar() {
      this.isHoveringAvatar = true;
    },
    hideChangeAvatar() {
      this.isHoveringAvatar = false;
    },

    toggleAvatarEdit() {
      this.isEditingAvatar = !this.isEditingAvatar;
      if (this.isEditingAvatar) {
        this.$nextTick(() => {
          this.$refs.avatarInput.click();
        });
      }
    },

    async handleAvatarChange(event) {
      const file = event.target.files[0];
      if (!file) return;

      if (!file.type.startsWith('image/')) {
        alert('请选择图片文件！');
        return;
      }

      if (file.size > 5 * 1024 * 1024) {
        alert('图片大小不能超过5MB！');
        return;
      }

      const success = await this.updateAvatar(file);
      if (success) {
        alert('头像上传成功！');
      } else {
        alert('上传头像失败，请重试');
      }
    },

    async saveSignature() {
      if (!this.userProfile.tempSignature.trim()) {
        alert('个性签名不能为空！');
        return;
      }

      const success = await this.updateSignature(this.userProfile.tempSignature.trim());
      if (success) {
        this.userProfile.signature = this.userProfile.tempSignature;
        this.userProfile.isEditingSignature = false;
        alert('个性签名更新成功！');
      } else {
        alert('更新个性签名失败，请重试');
      }
    },

    startEditSignature() {
      this.userProfile.isEditingSignature = true;
      this.userProfile.tempSignature = this.userProfile.signature;
      this.$nextTick(() => {
        this.$refs.signatureInput.focus();
      });
    },



    // 更新房主头像展示方法
    async showProfile(roomId) {
      this.selectedRoom = this.selectedRoom === roomId ? null : roomId;

      if (this.selectedRoom) {
        // 获取当前房间信息
        const room = this.Rooms.find(r => r.id === roomId);
        if (!room) return;

        // 获取房主信息
        const selectedProfile = await this.fetchSelectedProfile(room.owner);
        if (selectedProfile) {
          this.selectedProfile = selectedProfile;
        }
      }
    },

    // 开始拖动
    startDrag(event) {
      this.isDragging = true;
      const touch = event.type === "touchstart" ? event.touches[0] : event;
      this.dragOffset.x = touch.clientX - this.buttonPosition.x;
      this.dragOffset.y = touch.clientY - this.buttonPosition.y;
    },
    // 拖动中
    onDragging(event) {
      if (!this.isDragging) return;
      const touch = event.type === "touchmove" ? event.touches[0] : event;
      let newX = touch.clientX - this.dragOffset.x;
      let newY = touch.clientY - this.dragOffset.y;

      // 限制在容器内
      const roomList = this.$refs.roomList;
      if (roomList) {
        const rect = roomList.getBoundingClientRect();
        const buttonSize = 50; // 按钮的大小（px）
        newX = Math.max(0, Math.min(newX, rect.width - buttonSize));
        newY = Math.max(0, Math.min(newY, rect.height - buttonSize));
      }

      this.buttonPosition.x = newX;
      this.buttonPosition.y = newY;
    },
    // 停止拖动
    stopDrag() {
      this.isDragging = false;
    },

    // 切换快速匹配窗口的显示状态
    toggleQuickMatchPanel() {
      this.showQuickMatchPanel = !this.showQuickMatchPanel;

    },

    // 执行快速匹配
    performQuickMatch() {
      // 过滤符合条件的房间
      const matchedRooms = this.Rooms.filter(room => {
        const matchesPeople = room.max_players  === this.matchPeopleCount;
        const matchesAI = room.allow_ai_players === (this.matchAI === true);
        // 检查房间是否还有空位
        const currentPeople = room.players.length + Object.keys(room.ai_players || {}).length;
        const hasSpace = currentPeople < room.max_players;

        return matchesPeople && matchesAI && hasSpace;
      });

      if (matchedRooms.length === 0) {
        this.dialogTitle = '提示';
        this.dialogMessage = '没有找到符合条件的房间！';
        this.dialogShowConfirm = false;
        this.currentDialogAction = 'quickMatchFail';
        this.showDialog = true;
        return;
      }

      // 找出当前人数最多的房间
      const maxPeople = Math.max(...matchedRooms.map(room =>
        room.players.length + Object.keys(room.ai_players || {}).length
      ));

      // 筛选出人数最多的所有房间
      const mostPopulatedRooms = matchedRooms.filter(room =>
        (room.players.length + Object.keys(room.ai_players || {}).length) === maxPeople
      );

      // 从人数最多的房间中随机选择一个
      const selectedRoom = mostPopulatedRooms[Math.floor(Math.random() * mostPopulatedRooms.length)];

      // 存储选中的房间并显示确认对话框

      this.dialogTitle = '匹配成功';
      this.dialogMessage = `已找到房间：${selectedRoom.title}<br>是否加入？`;
      this.dialogShowConfirm = true;
      this.currentDialogAction = 'quickMatchSuccess';
      this.showDialog = true;
      this.selectedRoomForMatch = selectedRoom;

      // 关闭快速匹配面板
      this.showQuickMatchPanel = false;
    },

    onFocus() {
      this.showSearchIcon = true;
      this.showHistory = true; // 显示历史记录
    },
    onBlur() {
      if (this.searchQuery.length === 0) {
        this.showSearchIcon = false;
      }
    },
    // 清空输入框内容
    clearSearch() {
      this.searchQuery = '';
      this.showHistory = true;
    },
    // 执行搜索操作
    searchRoom() {
      if (this.searchQuery.trim()) {
        // 添加到历史记录
        if (!this.history.includes(this.searchQuery)) {
          this.history.unshift(this.searchQuery);
          // 限制历史记录最多保存10条
          if (this.history.length > 10) {
            this.history.pop();
          }
        }
        this.filteredRooms = this.displayedRooms;
        this.showNoResultsMessage = this.filteredRooms.length === 0;
      } else {
        this.filteredRooms = [];
        this.showNoResultsMessage = false;
      }
      this.showHistory = false;
    },

    // 选择历史搜索项
    selectHistory(item) {
      this.searchQuery = item;
      this.showHistory = false;
    },
    removeHistoryItem(item) {
      this.history = this.history.filter(h => h !== item);
    },
    clearAllHistory() {
      this.history = [];
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

      } else if (type === 'invites') {
      this.showInvitesSidebar = !this.showInvitesSidebar;
      this.showMenuSidebar = false;
      this.showFriendsSidebar = false;
      this.showHistorySidebar = false;
    }
    },
    // 关闭侧边栏
    closeALL(){
      this.closeMenuSidebar();
      this.closeFriendsSidebar();
      this.closeHistorySidebar();
      this.closePlayerDetails();
      this.closeHistory();
      this.showInvitesSidebar = false;
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
      this.selectedPlayer = null;
      this.selectedRoom = null
    },
    closeHistory() {
      this.showHistory = false;
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
      this.initializeRoom();
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
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
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
  background-color: #ffffff;
  width: 320px;
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0;
}

/* 个人信息头部样式 */
.profile-header-menu {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px;
  background: linear-gradient(135deg, #4c6ef5, #3b5bdb);
  color: white;
  border-radius: 0 0 20px 20px;
  position: relative;
  margin-bottom: 20px;
}

.profile-avatar {
  position: relative;
  width: 80px;
  height: 80px;
  cursor: pointer;
  margin-bottom: 12px;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.profile-avatar:hover .avatar-overlay {
  opacity: 1;
}

.avatar-input {
  position: absolute;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.avatar-edit-text {
  color: white;
  font-size: 14px;
  text-align: center;
  pointer-events: none;
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.2);
  object-fit: cover;
}

.signature-container {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.signature-container:hover {
  background: rgba(255, 255, 255, 0.1);
}



.signature-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}

.edit-icon {
  width: 14px;
  height: 14px;
  opacity: 0.7;
}

.signature-container .edit-icon {
  display: none;
}

.signature-container:hover .edit-icon {
  display: block;
}

.signature-input {
  width: 100%;
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  font-size: 14px;
  outline: none;
}

.signature-input::placeholder {
  color: #999;
}



.profile-basic {
  margin-top: 12px;
}

.profile-name {
  font-size: 1.5em;
  font-weight: 600;
  margin: 0 0 4px 0;
}

.profile-status {
  font-size: 0.9em;
  opacity: 0.9;
}

/* 统计卡片样式 */
.profile-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 0 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 12px;
  text-align: center;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-value {
  display: block;
  font-size: 1.2em;
  font-weight: 600;
  color: #4c6ef5;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.8em;
  color: #868e96;
}

/* 功能区块样式 */
.menu-sections {
  flex: 1;
  padding: 0 16px;
  overflow-y: auto;
}

.menu-section {
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  font-size: 1em;
  color: #495057;
  margin-bottom: 12px;
  padding: 0 8px;
}

.section-icon {
  width: 20px;
  height: 20px;
  margin-right: 8px;
}

.section-content {
  display: grid;
  gap: 8px;
}

.menu-button {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: #495057;
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
  text-align: left;
}

.menu-button:hover {
  background: #f8f9fa;
  color: #4c6ef5;
}

.menu-button img {
  width: 20px;
  height: 20px;
  opacity: 0.7;
}

.menu-button:hover img {
  opacity: 1;
}

/* 底部操作区样式 */
.menu-footer {
  padding: 16px;
  border-top: 1px solid #e9ecef;
  margin-top: auto;
}

.logout-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px;
  background: #fee;
  border: none;
  border-radius: 8px;
  color: #e03131;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-button:hover {
  background: #fdd;
}

.logout-button img {
  width: 20px;
  height: 20px;
}

.friends-sidebar,
.history-sidebar,
.invites-sidebar {
  width: 360px;
  background: #ffffff;
  right: 0;
}

/* 侧边栏头部 */
.sidebar-header {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 1.2em;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.icon-btn {
  position: relative;
  padding: 8px;
  background: transparent !important;;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
}

.icon-btn:hover {
  background: #f5f5f5;
}

.icon-btn img {
  width: 20px;
  height: 20px;
}

.badge {
  position: absolute;
  top: -2px;
  right: -2px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: #f56c6c;
  color: white;
  border-radius: 9px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
  font-weight: bold;
  animation: badgePulse 2s infinite;
}

@keyframes badgePulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}


.close-btn {
  padding: 8px;
  background: transparent !important;
  border: none;
  cursor: pointer;
  opacity: 0.7;
  transition: all 0.3s;
}

.close-btn:hover {
  opacity: 1;
}

.close-btn img {
  width: 16px;
  height: 16px;
}

.header-actions .icon-btn {
  position: relative;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: transparent;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.header-actions .icon-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(64, 158, 255, 0.1);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.3s ease, height 0.3s ease;
}

.header-actions .icon-btn:hover::before {
  width: 100%;
  height: 100%;
}

.header-actions .icon-btn img {
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
}

.header-actions .icon-btn:hover img {
  transform: scale(1.1);
}

.header-actions .icon-btn:active img {
  transform: scale(0.95);
}

/* 好友操作按钮样式增强 */
.friend-actions .action-btn {
  position: relative;
  padding: 8px;
  background: transparent;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.friend-actions .action-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(245, 108, 108, 0.1);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.3s ease, height 0.3s ease;
}

.friend-actions .action-btn:hover::before {
  width: 100%;
  height: 100%;
}

.friend-actions .action-btn img {
  position: relative;
  z-index: 1;
  transition: transform 0.3s ease, filter 0.3s ease;
}

.friend-actions .action-btn:hover img {
  transform: scale(1.1);
  filter: brightness(0) saturate(100%) invert(64%) sepia(94%) saturate(5620%) hue-rotate(335deg) brightness(101%) contrast(93%);
}

.friend-actions .action-btn:active img {
  transform: scale(0.95);
}

/* 好友请求操作按钮样式增强 */
.request-actions .accept-btn,
.request-actions .reject-btn {
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translateY(0);
}

.request-actions .accept-btn::before,
.request-actions .reject-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.3s ease, height 0.3s ease;
}

.request-actions .accept-btn::before {
  background: rgba(255, 255, 255, 0.2);
}

.request-actions .reject-btn::before {
  background: rgba(0, 0, 0, 0.1);
}

.request-actions .accept-btn:hover::before,
.request-actions .reject-btn:hover::before {
  width: 150%;
  height: 150%;
}

.request-actions .accept-btn:hover,
.request-actions .reject-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.request-actions .accept-btn:active,
.request-actions .reject-btn:active {
  transform: translateY(1px);
}

/* 好友刷新按钮样式增强 */
.icon-btn[title="刷新好友相关信息"] {
  position: relative;
  overflow: hidden;
}

.icon-btn[title="刷新好友相关信息"] img {
  transition: transform 0.3s ease;
}

.icon-btn[title="刷新好友相关信息"]:hover img {
  transform: rotate(180deg);
}

.icon-btn[title="刷新好友相关信息"]::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(64, 158, 255, 0.1);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.3s ease, height 0.3s ease;
}

.icon-btn[title="刷新好友相关信息"]:hover::before {
  width: 100%;
  height: 100%;
}

/* 添加好友按钮特殊效果 */
.icon-btn[title="添加好友"] {
  position: relative;
  overflow: hidden;
}

.icon-btn[title="添加好友"]::after {
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
  transition: left 0.3s ease;
}

.icon-btn[title="添加好友"]:hover::after {
  left: 100%;
}

/* 好友请求徽章动画增强 */
@keyframes badgePulse {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.4);
  }
  70% {
    transform: scale(1.1);
    box-shadow: 0 0 0 10px rgba(245, 108, 108, 0);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0);
  }
}

.badge {
  animation: badgePulse 2s infinite;
}

/* 游戏邀请列表样式 */
.invites-list {
  padding: 20px;
  overflow-y: auto;
}

.invite-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  margin-bottom: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: all 0.5s ease;
  transform: translateX(0);
  opacity: 1;
  border: 1px solid #eee;
}

.invite-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  border-color: #409eff22;
}

.invite-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.invite-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.invite-name {
  font-size: 1em;
  font-weight: 500;
  color: #333;
}

.invite-actions {
  display: flex;
  gap: 8px;
}

/* 接受按钮 */
.accept-btn {
  padding: 8px 16px;
  background: #67c23a;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.3s ease;
}

.accept-btn:hover:not(:disabled) {
  background: #5daf34;
  transform: translateY(-2px);
}

/* 拒绝按钮 */
.reject-btn {
  padding: 8px 16px;
  background: #f56c6c;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reject-btn:hover:not(:disabled) {
  background: #e74c3c;
  transform: translateY(-2px);
}

/* 接受动画 */
.invite-item.accept-exit {
  transform: translateX(100%);
  opacity: 0;
  background-color: rgba(103, 194, 58, 0.1);
}

/* 拒绝动画 */
.invite-item.reject-exit {
  transform: translateX(-100%);
  opacity: 0;
  background-color: rgba(245, 108, 108, 0.1);
}

/* 禁用按钮状态 */
.accept-btn:disabled,
.reject-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 空列表提示 */
.invites-list:empty::after {
  content: "暂无游戏邀请";
  display: block;
  text-align: center;
  color: #999;
  padding: 32px 0;
}

/* 好友请求面板 */
.friend-requests-panel {
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
}

.friend-requests-panel,
.add-friend-panel {
  padding: 20px;
}

.panel-header {
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h4 {
  margin: 0;
  font-size: 0.9em;
  color: #666;
}

.request-count {
  font-size: 0.8em;
  color: #999;
}

.requests-list {
  padding: 0 20px 12px;
}

.request-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: all 0.5s ease;
  transform: translateX(0);
  opacity: 1;
}


/* 接受请求的退出动画 */
.request-item.accept-exit {
  transform: translateX(100%);
  opacity: 0;
  background-color: rgba(103, 194, 58, 0.1); /* 添加轻微的绿色背景 */
}

/* 拒绝请求的退出动画 */
.request-item.reject-exit {
  transform: translateX(-100%);
  opacity: 0;
  background-color: rgba(245, 108, 108, 0.1); /* 添加轻微的红色背景 */
}

/* 禁用状态的按钮样式 */
.accept-btn:disabled,
.reject-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.request-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.request-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.request-name {
  font-size: 0.9em;
  color: #333;
  margin-bottom: 4px;
}

.request-time {
  font-size: 0.8em;
  color: #999;
}

.request-actions {
  display: flex;
  gap: 8px;
}

.accept-btn,
.reject-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 0.8em;
  cursor: pointer;
  transition: all 0.3s;
}

.accept-btn {
  background: #67c23a;
  color: white;
}

.accept-btn:hover {
  background: #5daf34;
}

.reject-btn {
  background: #f56c6c;
  color: white;
}

.reject-btn:hover {
  background: #e74c3c;
}

/* 添加好友面板 */
.add-friend-panel {
  padding: 20px;
  border-bottom: 1px solid #eee;
}


.search-friend input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9em;
}

.search-friend button {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.search-friend button:hover {
  background: #3a8ee6;
}

/* 好友列表 */
.friends-list {
  flex: 1;
  overflow-y: auto;
}

.friend-group {
  padding: 12px 0;
}

.group-header {
  padding: 8px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #666;
  font-size: 0.9em;
}

.count {
  font-size: 0.9em;
  color: #999;
}

.friend-items {
  padding: 0 20px;
}

.friend-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  transition: all 0.3s;
  cursor: pointer;
}

.friend-item:hover {
  background: #f5f7fa;
}

.friend-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.friend-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.friend-name {
  font-size: 0.9em;
  color: #333;
  margin-bottom: 4px;
}

.friend-status {
  font-size: 0.8em;
  color: #67c23a;
}

.friend-item.offline .friend-status {
  color: #999;
}

.friend-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.3s;
}

.friend-item:hover .friend-actions {
  opacity: 1;
}

.action-btn {
  padding: 6px;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn:hover {
  background: #eee;
}

.action-btn img {
  width: 16px;
  height: 16px;
  opacity: 0.7;
}

.delete-friend-btn {
  background-color: transparent;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.delete-friend-btn:hover {
  background-color: #fef0f0;
}

.delete-friend-btn img {
  width: 16px;
  height: 16px;
  opacity: 0.7;
  transition: filter 0.3s ease;
}

/* 历史记录侧边栏 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 20px;
  background: #f8f9fa;
}

.stat-card {
  padding: 16px;
  background: white;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.stat-number {
  display: block;
  font-size: 1.5em;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.8em;
  color: #666;
}

.history-filters {
  padding: 12px 20px;
  display: flex;
  gap: 12px;
  border-bottom: 1px solid #eee;
}

.filter-select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9em;
  color: #666;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1; /* 让选择器平均分配空间 */
}

.filter-select:hover {
  border-color: #409eff;
}

.filter-select:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64,158,255,0.2);
}

.game-history-list {
  padding: 20px;
  overflow-y: auto;
}

.game-record {
  background: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transform-origin: top;
  animation: slideDown 0.3s ease forwards;
  opacity: 0;
  position: relative;
  transition: all 0.3s ease;
  cursor: pointer;
}

.game-record:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.1);
}

/* 添加光晕效果 */
.game-record::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 8px;
  background: linear-gradient(45deg, #409eff15, #67c23a15);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.game-record:hover::before {
  opacity: 1;
}

/* 胜利和失败记录的特殊悬停效果 */
.game-record .game-result.win:hover + .game-details {
  background: linear-gradient(to right, #f0f9eb22, transparent);
}

.game-record .game-result.lose:hover + .game-details {
  background: linear-gradient(to right, #fef0f022, transparent);
}

/* 游戏详情的过渡效果 */
.game-details {
  transition: all 0.3s ease;
}

.game-record:hover .game-details {
  padding-left: 8px;
}

/* 角色图标悬停效果 */
.role-icon {
  transition: transform 0.3s ease;
}

.game-record:hover .role-icon {
  transform: scale(1.1) rotate(5deg);
}

/* 统计数据悬停效果 */
.game-stats .stat {
  transition: transform 0.3s ease;
}

.game-record:hover .game-stats .stat {
  transform: translateY(-2px);
}

/* 添加交互式边框效果 */
.game-record {
  border: 1px solid transparent;
  transition: all 0.3s ease;
}

.game-record:hover {
  border-color: #409eff22;
}

/* 时间标签的悬停效果 */
.game-time {
  transition: color 0.3s ease;
}

.game-record:hover .game-time {
  color: #409eff;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 为每个记录添加延迟，创造瀑布效果 */
.game-record:nth-child(1) { animation-delay: 0.1s; }
.game-record:nth-child(2) { animation-delay: 0.2s; }
.game-record:nth-child(3) { animation-delay: 0.3s; }
.game-record:nth-child(4) { animation-delay: 0.4s; }
.game-record:nth-child(5) { animation-delay: 0.5s; }

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.game-result {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.9em;
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

.game-time {
  font-size: 0.8em;
  color: #999;
}

.game-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
}

.role-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.role-icon {
  width: 32px;
  height: 32px;
}

.role-name {
  font-size: 0.9em;
  color: #333;
}

.game-stats {
  display: flex;
  gap: 16px;
}

.stat {
  text-align: center;
}

.stat .label {
  display: block;
  font-size: 0.8em;
  color: #999;
  margin-bottom: 4px;
}

.stat .value {
  font-size: 0.9em;
  color: #333;
  font-weight: 500;
}

.game-players {
  padding-top: 12px;
}

.team {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.player {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: #f5f7fa;
  border-radius: 12px;
}

.player-avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
}

.player-name {
  font-size: 0.8em;
  color: #666;
}

.good-team .player {
  background: #f0f9eb;
}

.bad-team .player {
  background: #fef0f0;
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
  /* 顶部导航栏样式 */
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #f5f5f5;
    padding: 10px;
    border-bottom: 1px solid #ccc;
  }

  .menu-btn {
    font-size: 20px;
    border: none;
    background: none;
    cursor: pointer;
  }

.search-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;  /* 确保左右两侧元素均匀分布 */
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 25px;
  width: 40%;
  position: relative;
  background-color: #fff;
}

.search-icon img,
.search-button img {
  width: 24px;
  height: 24px;
  transition: filter 0.3s;

}

.search-icon {
  margin-right: 8px;
  transition: width 0.3s ease;
  display: flex;
  margin-top: -1px;
}


.search-bar input {
  flex-grow: 1; /* 输入框占据大部分空间 */
  height: 30px;
  padding: 8px;
  font-size: 14px;
  line-height: 20px;
  border: none;
  outline: none;
  box-sizing: border-box;
  overflow: hidden;
  resize: none;
  padding-right: 25%; /* 保证删除按钮不会遮挡文字 */
  width: 100%;  /* 确保输入框填满可用空间 */
}

.clear-container {
  top: 20%;
  display: flex;
  align-items: center;
  position: absolute;
  right: 10%; /* 右侧对齐 */

}

.clear-button img {
  width: 24px;
  height: 24px;
  transition: filter 0.3s;
}
.clear-button:hover {
  filter: brightness(0) saturate(100%) invert(41%) sepia(93%) saturate(390%) hue-rotate(188deg) brightness(98%) contrast(89%);
  /* 鼠标悬停时给图标添加颜色变化 */
}
.search-bar .clear-button, .search-bar .search-button {
  background-color: transparent;
  border: none;
  cursor: pointer;
}

.search-bar .search-button {
  position: absolute;
  right: 1%;
  top: 50%;
  transform: translateY(-50%);
  background-color: transparent;
  border-radius: 50%; /* 圆形按钮 */
  /*border: 2px solid #007bff; /* 给按钮加一个蓝色边框 */
  border: none;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.3s; /* 添加过渡效果 */
}


.search-bar .search-button:hover {
  filter: brightness(0) saturate(100%) invert(41%) sepia(93%) saturate(390%) hue-rotate(188deg) brightness(98%) contrast(89%);
  /* 鼠标悬停时给图标添加颜色变化 */
}


.separator {

  border-radius: 50%; /* 圆角效果，显得更精致 */
  width: 2px;
  height: 20px;
  background-color: #333;
  position: absolute;
  top: 12%;
  right: -8%; /* 右侧对齐 */
}

/* 淡入淡出动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.history {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  width: 100%;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 2;
  overflow: hidden;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
}

.history-header span {
  color: #666;
  font-size: 14px;
  font-weight: 500;
}


.history ul {
  margin: 0;
  padding: 8px 0;
  list-style: none;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.history-item:hover {
  background-color: #f5f5f5;
}

.history-icon {
  width: 16px;
  height: 16px;
  margin-right: 12px;
  opacity: 0.5;
}

.history-item span {
  flex: 1;
  color: #333;
  font-size: 14px;
}
.clear-all-button,
.remove-item {
  background-color: transparent !important;
  border: none;
  padding: 6px;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.clear-all-button:hover .clear-icon,
.remove-item:hover .clear-icon {
  filter: invert(31%) sepia(98%) saturate(1640%) hue-rotate(201deg) brightness(96%) contrast(107%);
}

.clear-icon {
  width: 16px;
  height: 16px;
  transition: filter 0.3s ease;
}

.remove-item {
  visibility: hidden;
  opacity: 0;
  transition: all 0.3s ease;
}

.history-item:hover .remove-item {
  visibility: visible;
  opacity: 1;
}

.history-item:hover .remove-item {
  visibility: visible;
}


  .header-actions button {
    margin-left: 10px;
    background-color: #007bff;
    color: white;
    border: none;
    padding: 5px 10px;
    cursor: pointer;
  }

/* 主内容区域样式调整 */
.content {
  display: flex;
  flex: 1;
  padding: 20px;
  gap: 20px;
  overflow-x: hidden;
  position: relative;
  transition: all 0.3s ease;
}

/* 房间列表样式 */
.room-list {
  flex: 2;
  background-color: #f4f7fc;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}
.room-list {
  transition: transform 0.3s ease, flex 0.3s ease;
}
.room-list.shrink {
  transform: translateX(-2%);
}

/* 房间列表头部布局 */
.room-list-header {
  display: flex;
  justify-content: space-between; /* 元素分布在两端和中间 */
  align-items: center;
  margin-bottom: 24px;
  padding: 0 10px;
  height: 50px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.refresh-button {
  background-color: transparent !important;
  border: none;
  cursor: pointer;
  padding: 10px;
  transition: transform 0.3s ease;
}

.refresh-button:hover {
  transform: scale(1.1);
  filter: brightness(0) saturate(100%) invert(41%) sepia(93%) saturate(390%) hue-rotate(188deg) brightness(98%) contrast(89%);
}

.refresh-icon {
  width: 24px;
  height: 24px;
  filter: var(--img-filter);
  transition: filter 0.3s ease;
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

.no-results {
  width: 100%;
  padding: 40px;
  text-align: center;
  color: #666;
  background: #f8f9fa;
  border-radius: 8px;
  margin: 20px 0;
}

.no-results p {
  margin: 0;
  font-size: 1.1em;
}

.room-list-header h2 {
  font-size: 1.5em;
  color: #2c3e50;
  margin: 0;
}

/* 房间卡片网格布局 */
.room-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  padding: 8px 4px;
}

/* 卡片动画效果 */
.room-card-enter-active,
.room-card-leave-active {
  transition: all 0.5s ease;
}

.room-card-enter-from,
.room-card-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.room-card-move {
  transition: transform 0.5s ease;
}

/* 房间卡片样式 */
.room-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  border: 1px solid #eef1f5;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.room-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.08);
  border-color: #e1e8f0;
  z-index: 15;
}

/* 卡片头部样式 */
.room-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

/* 房主头像样式 */
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.owner-avatar {
  position: relative;
  width: 32px;
  height: 32px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.owner-avatar:hover {
  transform: scale(1.1);
}

.owner-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
  background: #fff ;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 16px;
  z-index: 10;
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
  justify-content: center;
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

.action-btn img{
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

/* 添加 room-description 样式 */
.room-description {
  padding: 8px 0;
  border-top: 1px solid #f0f2f5;
  border-bottom: 1px solid #f0f2f5;
}

.room-description .description {
  color: #666;
  font-size: 0.9em;
  line-height: 1.4;
  display: block;
  /* 超出两行显示省略号 */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.room-card-header h3 {
  margin: 0;
  font-size: 1.1em;
  color: #2c3e50;
  font-weight: 600;
}

.room-type {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85em;
  background-color: #f0f2f5;
  color: #606a78;
}

.room-type.ai {
  background-color: #ecf5ff;
  color: #409eff;
}

/* 房间信息样式 */
.room-info {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606a78;
  font-size: 0.9em;
}

.info-icon {
  width: 16px;
  height: 16px;
  opacity: 0.7;
}

.player-count {
  font-family: 'Monaco', monospace;
}

.status-full {
  color: #f56c6c;
}

/* 加入按钮样式 */
.join-button {
  margin-top: auto;
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 8px;
  background-color: #409eff;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.join-button:hover:not(:disabled) {
  background-color: #3a8ee6;
  transform: translateY(-2px);
}

.join-button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
  transform: none;
}

.join-button.return-button {
  background-color: #67c23a;
}

.join-button.return-button:hover {
  background-color: #5daf34;
}

/* 创建房间面板样式 */
.create-room {
  position: relative;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
  padding: 24px;
  width: 400px;
  transition: all 0.3s ease;
  overflow-y: auto;
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

/* 创建房间头部样式 */
.create-room-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  position: relative;
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

.create-room h2 {
  flex: 1;
  text-align: center;
  margin: 0;
  color: #333;
  font-size: 1.5em;
}

/* 表单样式美化 */
.create-room-content {
  padding: 20px 0;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #666;
  font-weight: 500;
  text-align: left; /* 确保文本左对齐 */
}
.text-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  background-color: #fff;
  transition: all 0.3s ease;
  outline: none;
}

.text-input:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64,158,255,0.1);
}

textarea.text-input {
  resize: vertical;
  min-height: 80px;
}
.select-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  background-color: #fff;
  transition: border-color 0.3s ease;
}

.select-input:focus {
  border-color: #007bff;
  outline: none;
}

/* 单选按钮组样式 */
.radio-group {
  display: flex;
  gap: 20px;
}

.radio-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.radio-label input[type="radio"] {
  margin-right: 8px;
}

.radio-text {
  color: #666;
}

/* 按钮样式美化 */
.action-buttons {
  display: flex;
  gap: 16px;
  margin-top: 32px;
}

.create-room-button {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}


.create-room-button {
  background-color: #007bff;
  color: white;
}


.create-room-button:hover {
  background-color: #0056b3;
}

.create-room-button {
  flex: 1;
  padding: 10px 0;
  background-color: var(--primary-color);
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color var(--transition-speed) ease;
}

.create-room-button:hover {
  background-color: var(--button-hover);
}

/* 浮动快速匹配按钮的容器 */
.quick-match-button-container {
  position: absolute;
  cursor: grab;
  z-index: 10;
}

.quick-match-button-container:active {
  cursor: grabbing;
}

/* 浮动快速匹配按钮 */
.quick-match-button {
  width: 50px;
  height: 50px;
  background-color: #409eff;
  border: none;
  border-radius: 50%;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s ease, transform 0.3s ease;
}

.quick-match-button img {
  width: 24px;
  height: 24px;
  filter: brightness(0) invert(1);
}

.quick-match-button:hover {
  background-color: #3a8ee6;
  transform: scale(1.1);
}

/* 快速匹配选项窗口 */
.quick-match-panel {
  position: absolute;
  bottom: 70px; /* 位于按钮上方 */
  right: 0;
  width: 250px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 16px;
  z-index: 20;
  animation: slideIn 0.3s ease forwards;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

}

.quick-match-panel h3 {
  margin-top: 0;
  color: #2c3e50;
  font-size: 1.2em;
  text-align: center;
}

.quick-match-panel .form-group {
  margin-bottom: 16px;
}

.quick-match-panel .form-group label {
  display: block;
  font-size: 0.9em;
  margin-bottom: 8px;
  color: #777;
}

.quick-match-panel .select-input,
.quick-match-panel .radio-group {
  width: 100%;
}

.quick-match-panel .select-input {
  padding: 8px;
  font-size: 1em;
  border-radius: 8px;
  border: 1px solid #ccc;
}

.quick-match-panel .radio-group label {
  display: inline-block;
  margin-right: 10px;
}

.quick-match-panel .action-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quick-match-panel .action-buttons button {
  width: 45%;
  padding: 8px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.quick-match-panel .action-buttons button:hover {
  background-color: #3a8ee6;
}

  </style>
