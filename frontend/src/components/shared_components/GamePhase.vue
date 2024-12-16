<template>
  <div class="phase-display" v-if="phase">
    <div class="phase-container">
      <h2 class="phase-text">当前阶段：{{ phase }}</h2>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GamePhase',
  props: {
    phase: {
      type: String,
      required: true
    }
  }
}
</script>

<style scoped>
.phase-display {
  width: 100%;
  max-width: 800px;
  margin: 0 auto 20px auto;
  padding: 10px;
  position: absolute;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1;
}

.phase-container {
  background: linear-gradient(135deg, #a8c0ff 0%, #8e9eab 100%);
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.phase-text {
  color: white;
  font-size: 32px;
  font-weight: bold;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
  .phase-text {
    font-size: 24px;
  }
}
</style>