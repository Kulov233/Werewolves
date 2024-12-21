<template>
  <div class="timer-wrapper">
    <div class="countdown-timer">
      <div class="time-display">
        <div class="time-label">剩余时间</div>
        <div class="time-numbers">
          <span class="time-number">{{ formattedMinutes }}</span>
          <span class="time-separator">:</span>
          <span class="time-number">{{ formattedSeconds }}</span>
        </div>
      </div>
      <div class="progress-container">
        <svg class="progress" viewBox="0 0 200 80">
          <!-- 背景渐变 -->
          <defs>
            <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#4CAF50;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#45a049;stop-opacity:1" />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          <!-- 背景装饰图案 -->
          <pattern id="pattern1" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
            <rect x="0" y="0" width="20" height="20" fill="none" />
            <path d="M0 10 L20 10 M10 0 L10 20" stroke="#2a2a2a" stroke-width="0.5" opacity="0.2"/>
          </pattern>
          <rect x="0" y="0" width="100%" height="100%" fill="url(#pattern1)"/>

          <!-- 主背景 -->
          <rect
            class="progress-rect-bg"
            x="4"
            y="4"
            width="292"
            height="72"
            fill="rgba(42, 42, 42, 0.3)"
            rx="6"
          />

          <!-- 进度条 -->
          <rect
            class="progress-rect"
            x="4"
            y="4"
            :width="progressWidth"
            height="72"
            fill="url(#progressGradient)"
            rx="6"
            filter="url(#glow)"
          />

          <!-- 装饰线条 -->
          <g class="decoration-lines">
            <line
              v-for="n in 29"
              :key="n"
              :x1="n * 10"
              y1="4"
              :x2="n * 10"
              y2="76"
              stroke="#ffffff"
              stroke-width="0.5"
              opacity="0.1"
            />
          </g>

          <!-- 边框 -->
          <rect
            class="progress-rect-border"
            x="2"
            y="2"
            width="296"
            height="76"
            fill="none"
            stroke="#4CAF50"
            stroke-width="0.5"
            rx="8"
            opacity="0.3"
          />
        </svg>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CountdownTimer',
  props: {
    seconds: {
      type: Number,
      required: true,
      default: 0,
    },
    initialSeconds: {
      type: Number,
      required: true,
      default: 1 ,
    }
  },
  computed: {
    formattedMinutes() {
      const minutes = Math.floor(Math.max(0, this.seconds) / 60);
      return String(minutes).padStart(2, '0');
    },
    formattedSeconds() {
      const remainingSeconds = Math.max(0, this.seconds) % 60;
      return String(remainingSeconds).padStart(2, '0');
    },
    progressWidth() {
      if (!this.initialSeconds) return 0;
      const progress = Math.max(0, Math.min(1, this.seconds / this.initialSeconds));
      return Math.max(0, Math.min(292, 292 * progress));
    }
  }
}
</script>

<style scoped>
.timer-wrapper {
  width: 200px;
  margin: 0 auto;
  padding: 10px;
}

.countdown-timer {
  position: relative;
  width: 200px;
  height: 80px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3),
              inset 0 2px 4px rgba(255, 255, 255, 0.05);
  overflow: hidden;
}

.time-display {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #ffffff;
  z-index: 2;
  background: rgba(0, 0, 0, 0.6);
  padding: 8px 16px;
  border-radius: 8px;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.time-label {
  font-size: 0.8rem;
  opacity: 0.8;
  margin-bottom: 2px;
  font-weight: 500;
  letter-spacing: 1px;
}

.time-numbers {
  display: flex;
  align-items: center;
}

.time-number {
  font-size: 1.8rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 1px;
  min-width: 2ch;
  text-align: center;
}

.time-separator {
  margin: 0 4px;
  color: #4CAF50;
  font-weight: 600;
  font-size: 1.8rem;
  animation: pulse 1s infinite;
  text-shadow: 0 0 8px rgba(76, 175, 80, 0.6);
}

.progress-container {
  position: absolute;
  width: 100%;
  height: 100%;
}

.progress {
  width: 100%;
  height: 100%;
}

.progress-rect {
  transition: width 0.3s ease;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    text-shadow: 0 0 10px rgba(76, 175, 80, 0.8);
  }
  50% {
    opacity: 0.5;
    text-shadow: 0 0 5px rgba(76, 175, 80, 0.4);
  }
}

.countdown-timer::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    linear-gradient(45deg, rgba(76, 175, 80, 0.1), transparent 60%),
    linear-gradient(-45deg, rgba(0, 0, 0, 0.2), transparent 60%);
  z-index: 1;
}

@media (max-width: 768px) {
  .timer-wrapper {
    width: 240px;
  }

  .countdown-timer {
    width: 240px;
    height: 64px;
  }

  .time-label {
    font-size: 0.7rem;
  }

  .time-number, .time-separator {
    font-size: 1.5rem;
  }
}
</style>