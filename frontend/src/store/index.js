import { createStore } from 'vuex';

export default createStore({
  state: {
    webSocket: null,
    wsHandlers: new Map(),
    currentRoom: null,
    userProfile: null,
    isConnected: false,
    wsBaseUrl: 'ws://localhost:8000/ws', // WebSocket 基础 URL
    wsEndpoint: 'lobby' // 默认端点
  },
  
  getters: {
    getWebSocketUrl: (state) => (token, roomId = null) => {
      if (roomId) {
        return `${state.wsBaseUrl}/game/${roomId}/?token=${token}`;
      }
      return `${state.wsBaseUrl}/${state.wsEndpoint}/?token=${token}`;
    }
  },

  mutations: {
    SET_WEBSOCKET(state, ws) {
      state.webSocket = ws;
    },
    SET_CONNECTED(state, status) {
      state.isConnected = status;
    },
    SET_CURRENT_ROOM(state, room) {
      state.currentRoom = room;
    },
    SET_USER_PROFILE(state, profile) {
      state.userProfile = profile;
    },
    ADD_WS_HANDLER(state, { type, handler }) {
      if (!state.wsHandlers.has(type)) {
        state.wsHandlers.set(type, new Set());
      }
      state.wsHandlers.get(type).add(handler);
    },
    REMOVE_WS_HANDLER(state, { type, handler }) {
      if (state.wsHandlers.has(type)) {
        state.wsHandlers.get(type).delete(handler);
      }
    },
    SET_WS_BASE_URL(state, url) {
      state.wsBaseUrl = url;
    },
    SET_WS_ENDPOINT(state, endpoint) {
      state.wsEndpoint = endpoint;
    }
  },
  
  actions: {
    initializeWebSocket({ commit, state, getters }, { token, roomId = null }) {
      if (state.webSocket && state.isConnected) {
        return; // WebSocket 已连接
      }

      const wsUrl = getters.getWebSocketUrl(token, roomId);
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        commit('SET_CONNECTED', true);
        console.log('WebSocket connected');
      };

      ws.onclose = () => {
        commit('SET_CONNECTED', false);
        console.log('WebSocket disconnected');
        
        // 自动重连逻辑
        setTimeout(() => {
          if (!state.isConnected) {
            this.dispatch('initializeWebSocket', { token, roomId });
          }
        }, 3000);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const handlers = state.wsHandlers.get(data.type);
          
          if (handlers) {
            handlers.forEach(handler => handler(data));
          }
        } catch (error) {
          console.error('Error processing WebSocket message:', error);
        }
      };

      commit('SET_WEBSOCKET', ws);
    },

    // 配置 WebSocket URL
    configureWebSocket({ commit }, { baseUrl, endpoint }) {
      if (baseUrl) {
        commit('SET_WS_BASE_URL', baseUrl);
      }
      if (endpoint) {
        commit('SET_WS_ENDPOINT', endpoint);
      }
    },

    // 发送WebSocket消息
    sendWSMessage({ state }, message) {
      if (state.webSocket && state.isConnected) {
        state.webSocket.send(JSON.stringify(message));
      }
    },

    // 添加消息处理器
    addMessageHandler({ commit }, { type, handler }) {
      commit('ADD_WS_HANDLER', { type, handler });
    },

    // 移除消息处理器
    removeMessageHandler({ commit }, { type, handler }) {
      commit('REMOVE_WS_HANDLER', { type, handler });
    },

    // 保存房间数据
    saveRoomData({ commit }, room) {
      commit('SET_CURRENT_ROOM', room);
    },

    // 保存用户信息
    saveUserProfile({ commit }, profile) {
      commit('SET_USER_PROFILE', profile);
    },

    // 清理WebSocket连接
    clearWebSocket({ commit, state }) {
      if (state.webSocket) {
        state.webSocket.close();
        commit('SET_WEBSOCKET', null);
        commit('SET_CONNECTED', false);
      }
    }
  }
});