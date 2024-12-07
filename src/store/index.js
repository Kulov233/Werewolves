import { createStore } from 'vuex';

export default createStore({
  state: {
    currentRoom: null,
    userProfile: null,
    webSocket: null,
    isAuthenticated: false
  },
  
  getters: {
    getCurrentRoom: state => state.currentRoom,
    getUserProfile: state => state.userProfile,
    getWebSocket: state => state.webSocket,
    isAuthenticated: state => state.isAuthenticated
  },
  
  mutations: {
    SET_CURRENT_ROOM(state, room) {
      state.currentRoom = room;
    },
    SET_USER_PROFILE(state, profile) {
      state.userProfile = profile;
    },
    SET_WEBSOCKET(state, ws) {
      state.webSocket = ws;
    },
    SET_AUTH_STATUS(state, status) {
      state.isAuthenticated = status;
    }
  },
  
  actions: {
    saveRoomData({ commit }, room) {
      commit('SET_CURRENT_ROOM', room);
    },
    saveUserProfile({ commit }, profile) {
      commit('SET_USER_PROFILE', profile);
    },
    saveWebSocket({ commit }, ws) {
      commit('SET_WEBSOCKET', ws);
    },
    updateAuthStatus({ commit }, status) {
      commit('SET_AUTH_STATUS', status);
    }
  }
});