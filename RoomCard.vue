<template>
    <a-card class="room-card">
      <div class="card-header">
        <span class="room-title">房间标题</span>
        <span class="room-capacity">5 / 8</span>
      </div>
      <p>这里是房间简介</p>
      <div class="participants">
        <img v-for="n in 4" :key="n" src="@/assets/participant.png" alt="Participant" class="participant-icon" />
        <a-button shape="circle" icon="arrow-right" />
      </div>
    </a-card>
  </template>
  
  <script>
  import { Card, Button } from "ant-design-vue";
  
  export default {
    name: "RoomCard",
    components: {
      "a-card": Card,
      "a-button": Button,
    },
  };
  </script>
  
  <style scoped>
  .room-card {
    width: 250px;
    border-radius: 8px;
  }
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: bold;
  }
  .participants {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 8px;
  }
  .participant-icon {
    width: 32px;
    height: 32px;
    border-radius: 50%;
  }
  </style>
  