import { ref, onUnmounted } from 'vue';

export function useWebSocket(url, accessToken) {
    const socket = ref(null);
    const isConnected = ref(false);
    const listeners = {};              // 存储不同类型的消息回调
  
    function connect() {
      // 在 URL 中附加 Access Token
        const connectionUrl = `${url}?token=${accessToken}`;

        socket.value = new WebSocket(connectionUrl);

        socket.value.onopen = () => {
        console.log('WebSocket connection established');
        isConnected.value = true;
        };

        socket.value.onclose = () => {
        console.log('WebSocket connection closed');
        isConnected.value = false;
        };

        socket.value.onerror = (event) => {
        console.error('WebSocket error:', event);
        };
        socket.value.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type && listeners[data.type]) {
            listeners[data.type].forEach(callback => callback(data));
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
    }

  function disconnect() {
    if (socket.value) {
      socket.value.close();
      socket.value = null;
      isConnected.value = false;
    }
  }

  function sendMessage(message) {
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      socket.value.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  // 监听特定类型的消息
  function onType(type, callback) {
    if (!listeners[type]) {
      listeners[type] = [];
    }
    listeners[type].push(callback);
  }

  onUnmounted(() => {
    disconnect();
  });

  return {
    connect,
    disconnect,
    sendMessage,
    onType,
    isConnected
  };
}