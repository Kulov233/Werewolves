import { ref, onMounted, onUnmounted } from 'vue';
import { useStore } from 'vuex';

export const useWebSocket = (token) => {
  const store = useStore();
  const isLobbyConnected = ref(false);
  const isGameConnected = ref(false);


  // 连接 WebSocket
  const connect = () => {
    store.dispatch('initializeLobbyWebSocket', token);
  };

  // 连接游戏房间
  const connectToGame = (roomId) => {
    store.dispatch('initializeGameWebSocket', { token, roomId });
  };

  // 断开连接
  const disconnect = (type = 'all') => {
    store.dispatch('clearWebSocket', type);
  };

  // 发送消息
  const sendMessage = (message, type = 'lobby') => {
    store.dispatch('sendWSMessage', { message, type });
  };

  // 监听消息类型
  const onType = (type, handler) => {
    store.dispatch('addMessageHandler', { type, handler });
    return () => store.dispatch('removeMessageHandler', { type, handler });
  };

  onMounted(() => {

  });

  onUnmounted(() => {
    // 不在组件卸载时断开连接，仅移除消息处理器
    // disconnect();
  });

  return {
    connect,
    connectToGame,
    disconnect,
    sendMessage,
    onType,
    isLobbyConnected,
    isGameConnected,
  };
}