import { createStore } from 'vuex';

export default createStore({
  state: {
    // 大厅 WebSocket
    lobbyWebSocket: null,
    lobbyConnected: false,
    
    // 游戏房间 WebSocket
    gameWebSocket: null,
    gameConnected: false,
    
    wsHandlers: new Map(),
    currentRoom: null,
    userProfile: null,
    wsBaseUrl: 'ws://localhost:8000/ws',
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
    SET_LOBBY_WEBSOCKET(state, ws) {
      state.lobbyWebSocket = ws;
    },
    SET_GAME_WEBSOCKET(state, ws) {
      state.gameWebSocket = ws;
    },
    SET_LOBBY_CONNECTED(state, status) {
      state.lobbyConnected = status;
    },
    SET_GAME_CONNECTED(state, status) {
      state.gameConnected = status;
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
    // 初始化大厅 WebSocket
    initializeLobbyWebSocket({ commit, state }, token) {
      if (state.lobbyWebSocket && state.lobbyConnected) {
        return;
      }

      const wsUrl = `${state.wsBaseUrl}/lobby/?token=${token}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        commit('SET_LOBBY_CONNECTED', true);
        console.log('Lobby WebSocket connected');
      };

      ws.onclose = () => {
        commit('SET_LOBBY_CONNECTED', false);
        console.log('Lobby WebSocket disconnected');
        
        // 自动重连逻辑
        setTimeout(() => {
          if (!state.lobbyConnected) {
            this.dispatch('initializeLobbyWebSocket', token);
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
          console.error('Error processing Lobby WebSocket message:', error);
        }
      };

      commit('SET_LOBBY_WEBSOCKET', ws);
    },

    // 初始化游戏房间 WebSocket
    initializeGameWebSocket({ commit, state }, { token, roomId }) {
      if (!roomId) return;
      
      if (state.gameWebSocket && state.gameConnected) {
        state.gameWebSocket.close();
      }

      const wsUrl = `${state.wsBaseUrl}/game/${roomId}/?token=${token}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        commit('SET_GAME_CONNECTED', true);
        console.log('Game WebSocket connected');
      };

      ws.onclose = () => {
        commit('SET_GAME_CONNECTED', false);
        console.log('Game WebSocket disconnected');
        
        // 自动重连逻辑
        setTimeout(() => {
          if (!state.gameConnected && state.currentRoom?.id === roomId) {
            this.dispatch('initializeGameWebSocket', { token, roomId });
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
          console.error('Error processing Game WebSocket message:', error);
        }
      };

      commit('SET_GAME_WEBSOCKET', ws);
    },

    // 发送WebSocket消息
    sendWSMessage({ state }, { message, type = 'lobby' }) {
      const ws = type === 'lobby' ? state.lobbyWebSocket : state.gameWebSocket;
      const isConnected = type === 'lobby' ? state.lobbyConnected : state.gameConnected;
      
      if (ws && isConnected) {
        ws.send(JSON.stringify(message));
      }
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

    // 清理 WebSocket 连接
    clearWebSocket({ commit, state }, type = 'all') {
      switch (type) {
        case 'lobby':
          if (state.lobbyWebSocket) {
            state.lobbyWebSocket.close();
            commit('SET_LOBBY_WEBSOCKET', null);
            commit('SET_LOBBY_CONNECTED', false);
          }
          break;
        case 'game':
          if (state.gameWebSocket) {
            state.gameWebSocket.close();
            commit('SET_GAME_WEBSOCKET', null);
            commit('SET_GAME_CONNECTED', false);
          }
          break;
        case 'all':
        default:
          if (state.lobbyWebSocket) {
            state.lobbyWebSocket.close();
            commit('SET_LOBBY_WEBSOCKET', null);
            commit('SET_LOBBY_CONNECTED', false);
          }
          if (state.gameWebSocket) {
            state.gameWebSocket.close();
            commit('SET_GAME_WEBSOCKET', null);
            commit('SET_GAME_CONNECTED', false);
          }
      }
    },
  }
});