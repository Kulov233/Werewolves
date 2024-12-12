<template>
  <a-row 
    justify="center" 
    align="middle"
    class="main-container"
    >
    <a-col :span="8">
      <a-card title="注册" bordered class="register-card">
        <a-form :model="formState" @finish="onFinish" @finishFailed="onFinishFailed" layout="vertical" ref="register_form">
          <a-form-item
            class="register-label"
            label="用户名"
            name="username"
            :validateStatus="formStatus.username"
            :help="formErrors.username"
          >
            <a-input
              class="register-placeholder"
              v-model:value="formState.username"
              placeholder="用户名"
              show-count :maxlength="150"
              prefix-icon="ant-design:user-outlined"
              @change="resetUsernameState"
            />
          </a-form-item>
          <a-form-item
            class="register-label"
            label="电子邮箱"
            name="email"
            :validateStatus="formStatus.email"
            :help="formErrors.email"
          >
            <a-input
              class="register-placeholder"
              v-model:value="formState.email"
              placeholder="电子邮箱"
              prefix-icon="ant-design:user-outlined"
              @change="resetEmailState"
            />
          </a-form-item>
          <a-form-item
            class="register-label"
            label="密码"
            name="password"
            :validateStatus="formStatus.password"
            :help="formErrors.password"
          >
            <a-input-password
              class="register-placeholder"
              v-model:value="formState.password"
              placeholder="密码"
              @change="resetPasswordState"
              prefix-icon="ant-design:user-outlined"
              
            />
          </a-form-item>
          <a-form-item
            class="register-label"
            label="确认密码"
            name="confirmPassword"
            :validateStatus="formStatus.confirmPassword"
            :help="formErrors.confirmPassword"
          >
            <a-input-password
              class="register-placeholder"
              type="password"
              v-model:value="formState.confirmPassword"
              placeholder="确认密码"
              prefix-icon="ant-design:user-outlined"
              @change="resetConfirmPasswordState"
            />
          </a-form-item>
          <a-form-item>
            <a-button :disabled="disabled" type="primary" html-type="submit" block>注册</a-button>
          </a-form-item>
          <a-form-item style="text-align: center;">
            <a @click="goToLogin">已经有账号了？登录</a>
          </a-form-item>
        </a-form>
      </a-card>
      <!-- 切换主题按钮 -->
      <a-button
        shape="circle"
        size="large"
        class="theme-toggle-button"
        @click="toggleTheme"
        style="position: absolute; top: 15px; right: 15px; "
        >
        <img 
            src="@/assets/wolf.svg" 
            alt="wolf Icon" 
            style="width: 100%; height: 100%; filter: var(--img-filter);" 
          />
      </a-button>
    </a-col>
  </a-row>
</template>

<script setup>
import axios from "axios";
import {computed, reactive} from "vue";
import { useRouter } from 'vue-router';
const router = useRouter();

// 控制主题的状态
let isDarkMode = false; // 默认是白色主题

const toggleTheme = () => {
  isDarkMode = !isDarkMode; // 切换主题状态
  // 根据 isDarkMode 状态设置页面主题
  if (isDarkMode) {
    document.documentElement.style.setProperty('--background-color', '#333');
    document.documentElement.style.setProperty('--card-bg', '#444'); /* 设置卡片背景为深色 */
    document.documentElement.style.setProperty('--card-text', '#fff'); /* 设置卡片文本颜色为白色 */
    document.documentElement.style.setProperty('--input-bg', '#555'); /* 输入框背景色 */
    document.documentElement.style.setProperty('--input-color', '#fff'); /* 输入框文字颜色 */
    document.documentElement.style.setProperty('--label-color', '#fff'); /* 标签文字颜色为白色 */
    document.documentElement.style.setProperty('--placeholder-color', '#fff'); /* placeholder 文字颜色为浅色 */
    document.documentElement.style.setProperty('--button-bg', '#444'); 
    document.documentElement.style.setProperty('--img-filter', 'invert(1)');
    document.documentElement.style.setProperty('--svg-color', '#fff'); // SVG颜色为白色
  } else {
    document.documentElement.style.setProperty('--background-color', '#f4f7fa');
    document.documentElement.style.setProperty('--card-bg', '#fff'); /* 设置卡片背景为白色 */
    document.documentElement.style.setProperty('--card-text', '#333'); /* 设置卡片文本颜色为深色 */
    document.documentElement.style.setProperty('--input-bg', '#fff'); /* 输入框背景色 */
    document.documentElement.style.setProperty('--input-color', '#333'); /* 输入框文字颜色 */
    document.documentElement.style.setProperty('--label-color', '#333'); /* 标签文字颜色为深色 */
    document.documentElement.style.setProperty('--placeholder-color', '#aaa'); /* placeholder 文字颜色为浅色 */
    document.documentElement.style.setProperty('--button-bg', '#fff'); 
    document.documentElement.style.setProperty('--img-filter', 'invert(0)');
    document.documentElement.style.setProperty('--svg-color', '#333'); // SVG颜色为黑色
    
  }
};

const goToLogin = () => {
  router.push('/login');
};

const formState = reactive({
  username: "",
  email: "",
  password: "",
  confirmPassword: ""
});

const formStatus = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
});

const formErrors = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
});

const resetUsernameState = () => {
  formStatus.username = '';
  formErrors.username = '';
};

const resetEmailState = () => {
  formStatus.email = '';
  formErrors.email = '';
};

const resetPasswordState = () => {
  formStatus.password = '';
  formErrors.password = '';
};

const resetConfirmPasswordState = () => {
  formStatus.confirmPassword = '';
  formErrors.confirmPassword = '';
};

const disabled = computed(() => {
  return !(formState.username  && formState.email && formState.password && formState.confirmPassword);
});

const onFinish = async (values) => {
  // 检查密码是否匹配
  if (values.password !== values.confirmPassword) {
    formStatus.password = "error";
    formStatus.confirmPassword = "error";
    formErrors.confirmPassword = "密码不匹配！";
    return;
  }

  // 准备请求数据
  const requestData = {
    username: values.username,
    email: values.email,
    password: values.password
  };

  try {
    // 发送注册请求
    const response = await axios.post("http://localhost:8000/api/accounts/register/", requestData);

    // 注册成功的响应
    alert(response.data.message || "注册成功！");
    // 清空表单
    Object.keys(formState).forEach(key => formState[key] = "");
    Object.keys(formStatus).forEach(key => formStatus[key] = "");
    Object.keys(formErrors).forEach(key => formErrors[key] = "");
    
    router.push("/login");

  } catch (error) {
    // 注册失败的响应处理
    if (error.response && error.response.status === 400) {
      const errors = error.response.data;

      // 将错误消息分配到每个字段的状态和帮助文本中
      for (const [field, messages] of Object.entries(errors)) {
        formStatus[field] = "error";
        formErrors[field] = messages.join(", ");
      }
    } else {
      // 其他错误，例如网络错误
      alert("发生错误，请稍后再试。");
    }
  }
};

const onFinishFailed = (errorInfo) => {
  console.log("Failed:", errorInfo);
};
</script>

<style scoped>
a-row,
a-col {
  width: 100%;
}
/* 页面的背景和卡片背景 */
.main-container {
  height: 100vh;
  background-color: var(--background-color);
}

.register-card {
  background-color: var(--card-bg);
  border-radius: 15px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  width: 100%;
  margin: 0 auto;
  position: relative;
}
:deep(.register-card .ant-card-head) {
  color: var(--card-text)!important;
}

/* 统一设置所有使用 register-label 的元素样式 */
.logiregistern-label {
  margin-bottom: 16px; /* 调整每个表单项的底部间距 */
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 控制 label 文字颜色 */
:deep(.register-label label) {
  color: var(--card-text) !important;
  margin-bottom: 2px; /* 调整 label 与 input 之间的间距 */
}

/* 统一设置所有使用 register-placeholder 的输入框样式 */
:deep(.register-placeholder)  {
  width: 100%; /* 使输入框宽度占满整个父容器 */
  border-radius: 5px; /* 输入框圆角 */
  
  padding: 8px 12px; /* 内边距 */
  font-size: 14px; /* 字体大小 */
  background-color: var(--input-bg);
  color: var(--input-color) ; 
}

/* 修改占位符（placeholder）文字颜色 */
:deep(.register-placeholder::placeholder) {
  color: var(--placeholder-color)!important; /* 占位符文字颜色 */
}

/* 修改密码框内小黑点的颜色为小白点 */
:deep(.ant-input-password) input {
  font-family: "Courier New", monospace; /* 可选，设定一个特定字体 */
  color: var(--input-color); /* 设置为白色 */
  background-color: var(--input-bg);
}

/* 如果要改变图标样式，可以调整密码显示/隐藏的按钮颜色 */
:deep(.ant-input-password input[type="password"]) {
  color: var(--input-color) !important;
  background-color: var(--input-bg);
}

/* 可通过 :after 和 content 来插入新的符号 */
:deep(.ant-input-password input[type="password"]::-webkit-outer-spin-button) {
  color: transparent; /* 防止影响密码的显示 */
}

/* 修改占位符文字颜色 */
:deep(.ant-input-password input::placeholder) {
  color: var(--placeholder-color) !important; /* 设置占位符颜色 */
}
.theme-toggle-button {
  background-color: var(--button-bg);
  color: var(--button-color);
  border: none;
  cursor: pointer;
}

:deep(.ant-input-password .ant-input-password-suffix svg) {
  fill: var(--button-color) !important;  /* 设置图标颜色 */
}

.theme-toggle-button:hover {
  background-color: #aaa;
  border-color: transparent;
  transform: scale(1.1);
}
</style>
