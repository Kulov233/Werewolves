// 翻译映射表
const translations = {
  // 角色名称
  'Werewolf': '狼人',
  'Villager': '平民',
  'Witch': '女巫',
  'Prophet': '预言家',
  'Hunter': '猎人',
  'Guard': '守卫',
  'Idiot': '白痴',

  // 游戏状态
  'win': '胜利',
  'lose': '失败',

  // 房间状态
  'playing': '游戏中',
  'waiting': '等待中',
  'finished': '已结束',

  // 其他游戏相关术语
  'online': '在线',
  'offline': '离线',
  'room': '房间'
};

// 创建Vue插件
const TranslatorPlugin = {
  install(app) {
    // 添加全局方法
    app.config.globalProperties.$translate = function(text) {
      // 如果文本为空，返回空字符串
      if (!text) return '';

      // 如果存在直接翻译，返回翻译结果
      if (translations[text]) {
        return translations[text];
      }

      // 如果是复合词（用空格分隔的多个单词），尝试逐个翻译
      if (text.includes(' ')) {
        return text.split(' ')
          .map(word => translations[word] || word)
          .join(' ');
      }

      // 如果没有找到翻译，返回原文
      return text;
    };

    // 添加全局指令 v-translate
    app.directive('translate', {
      mounted(el, binding) {
        // 获取元素的原始文本
        const originalText = binding.value || el.textContent;

        // 应用翻译
        el.textContent = app.config.globalProperties.$translate(originalText);
      },
      updated(el, binding) {
        // 在值更新时重新翻译
        const originalText = binding.value || el.textContent;
        el.textContent = app.config.globalProperties.$translate(originalText);
      }
    });
  }
};

export default TranslatorPlugin;