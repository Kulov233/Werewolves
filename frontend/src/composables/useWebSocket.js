import { onMounted, onUnmounted } from 'vue';
import { useStore } from 'vuex';

export function useWebSocket(token) {
  const store = useStore();

  const connect = (roomId = null) => {
    store.dispatch('initializeWebSocket', { token, roomId });
  };

  const disconnect = () => {
    store.dispatch('clearWebSocket');
  };

  const sendMessage = (message) => {
    store.dispatch('sendWSMessage', message);
  };

  const onType = (type, handler) => {
    store.dispatch('addMessageHandler', { type, handler });
    
    // 返回一个清理函数
    return () => {
      store.dispatch('removeMessageHandler', { type, handler });
    };
  };

  onMounted(() => {
    if (!store.state.isConnected) {
      connect();
    }
  });

  onUnmounted(() => {
    // 不在组件卸载时断开连接，仅移除消息处理器
    // disconnect();
  });

  return {
    connect,
    disconnect,
    sendMessage,
    onType,
    isConnected: store.state.isConnected
  };
}