<template>
  <Transition
    enter-active-class="transition-all duration-500 ease-in-out"
    leave-active-class="transition-all duration-500 ease-in-out"
    enter-from-class="opacity-0 translate-x-[-100%]"
    enter-to-class="opacity-100 translate-x-0"
    leave-from-class="opacity-100 translate-x-0"
    leave-to-class="opacity-0 translate-x-[100%]"
  >
    <div v-if="visible" class="fixed left-0 right-0 top-1/2 -translate-y-1/2 z-50 flex justify-center pointer-events-none">
      <div :class="[getBgColor(), 'max-w-lg w-full mx-4 rounded-xl shadow-2xl p-6']">
        <!-- 图标 -->
        <div class="flex justify-center mb-4">
          <component :is="getIcon()" class="w-12 h-12" :class="getIconColor()" />
        </div>
        
        <!-- 消息内容 -->
        <div class="text-center space-y-2">
          <h3 class="text-xl font-bold text-gray-800">{{ message }}</h3>
          <p v-if="subMessage" class="text-sm text-gray-600">{{ subMessage }}</p>
        </div>
        
        <!-- 玩家列表 -->
        <div v-if="players.length > 0" class="mt-4 flex justify-center gap-4">
          <div v-for="(player, index) in players" :key="index" class="flex flex-col items-center">
            <div class="w-12 h-12 rounded-full overflow-hidden mb-2 border-2 border-white shadow-lg">
              <img :src="player.avatar" :alt="player.name" class="w-full h-full object-cover" />
            </div>
            <span class="text-sm font-medium text-gray-700">{{ player.name }}</span>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script>
import { ref, onMounted } from 'vue';
import { Moon, Sun, Skull, AlertCircle, UserCheck, MessageCircle } from 'lucide-vue-next';

export default {
  props: {
    type: {
      type: String,
      default: 'info'
    },
    message: {
      type: String,
      default: ''
    },
    subMessage: {
      type: String,
      default: ''
    },
    players: {
      type: Array,
      default: () => []
    }
  },

  emits: ['close'],

  setup(props, { emit }) {
    const visible = ref(false);

    onMounted(() => {
      visible.value = true;
      setTimeout(() => {
        visible.value = false;
        setTimeout(() => {
          emit('close');
        }, 500);
      }, 3000);
    });

    const getIcon = () => {
      switch (props.type) {
        case 'night':
          return Moon;
        case 'day':
          return Sun;
        case 'death':
          return Skull;
        case 'role':
          return UserCheck;
        case 'action':
          return AlertCircle;
        case 'speak':
          return MessageCircle;
        default:
          return AlertCircle;
      }
    };

    const getIconColor = () => {
      switch (props.type) {
        case 'night':
          return 'text-indigo-600';
        case 'day':
          return 'text-yellow-500';
        case 'death':
          return 'text-red-600';
        case 'role':
          return 'text-purple-600';
        case 'action':
          return 'text-blue-600';
        case 'speak':
          return 'text-green-600';
        default:
          return 'text-gray-600';
      }
    };

    const getBgColor = () => {
      switch (props.type) {
        case 'night':
          return 'bg-indigo-50';
        case 'day':
          return 'bg-yellow-50';
        case 'death':
          return 'bg-red-50';
        case 'role':
          return 'bg-purple-50';
        case 'action':
          return 'bg-blue-50';
        case 'speak':
          return 'bg-green-50';
        default:
          return 'bg-gray-50';
      }
    };

    return {
      visible,
      getIcon,
      getIconColor,
      getBgColor
    }
  }
}
</script>