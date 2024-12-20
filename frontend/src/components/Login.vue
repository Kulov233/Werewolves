<template>
  <a-row 
    justify="center" 
    align="middle"
    class="main-container"
  >
    <a-col :span="8">
      <!-- 登录框 -->
      <a-card 
        title="欢迎登录" 
        bordered 
        class="login-card"
      >
        <a-form :model="formState" @finish="onFinish" @finishFailed="onFinishFailed" layout="vertical" ref="login_form">
          <a-form-item
            class="login-label"
            label="用户名/邮箱"
            name="username_or_email"
            :validateStatus="formStatus.username_or_email"
            :help="formErrors.username_or_email"

          >
            <a-input
              class="login-placeholder"
              v-model:value="formState.username_or_email"
              placeholder="请输入用户名或邮箱"
              prefix-icon="ant-design:user-outlined"
              @change="resetUsernameOrEmailState"
            />
          </a-form-item>

          <a-form-item
            class="login-label"
            label="密码"
            name="password"
            :validateStatus="formStatus.password"
            :help="formErrors.password"
          >
            <a-input
              class="login-placeholder"
              type="password"
              v-model:value="formState.password"
              placeholder="请输入密码"
              prefix-icon="ant-design:lock-outlined"
              @change="resetPasswordState"
            />
          </a-form-item>

          <a-form-item 
            class="login-label"
            id="Verification"
            label="验证码"
            name="ver_code"
          >
            <div class="verification-container">
              <a-input
                class="login-placeholder"
                type="text"
                v-model="ver_code"
                placeholder="请输入验证码"
                prefix-icon="ant-design:lock-outlined"
                @input="onVerCodeInput"
              />
              <canvas
                id="canvas"
                class="canvascs"
                @click="draw()"
              ></canvas>
            </div>
          </a-form-item>

          <a-form-item>
            <a-button :disabled="disabled" type="primary" html-type="submit" block size="large">登录</a-button>
          </a-form-item>

          <a-form-item style="text-align: center;">
            <a @click="goToRegister">没有账号？注册</a>
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
      <ConfirmDialog
      :show="showDialog"
      :title="dialogTitle"
      :message="dialogMessage"
      :showConfirm="dialogShowConfirm"
      @confirm="handleDialogConfirm"
      @cancel="handleDialogCancel"
    />
  </a-row>



</template>

<script setup>

import {onMounted, ref} from "vue";
import { reactive, computed } from 'vue';
import { useRouter } from 'vue-router';

import axios from 'axios';
import ConfirmDialog from "@/components/shared_components/ConfirmDialog.vue";

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

const router = useRouter();
let yanma = ref("");
// 绑定验证码
let ver_code = ref("");
//验证码图形生成
var show_num = [];
onMounted(() => {
  draw();
});
function onVerCodeInput(event) {
  ver_code.value = event.target.value;
}

function draw() {
  // jQuery 对 canvas 对象无法获取，原生 JS 可以解决
  var canvas_width = document.getElementById("canvas").clientWidth;
  var canvas_height = document.getElementById("canvas").clientHeight;
  var canvas = document.getElementById("canvas"); // 获取到canvas的对象，画布
  var context = canvas.getContext("2d"); // 画笔
  // 画布范围
  canvas.width = canvas_width;
  canvas.height = canvas_height;
  // 字符集
  var sCode =
    "A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z,1,2,3,4,5,6,7,8,9,0,q,w,e,r,t,y,u,i,o,p,a,s,d,f,g,h,j,k,l,z,x,c,v,b,n,m";
  var aCode = sCode.split(",");
  var aLength = aCode.length; // 获取到数组的长度
  for (let i = 0; i <= 3; i++) { // 使用 let 声明 i
    // 向下取整
    var j = Math.floor(Math.random() * aLength); // 获取到随机的索引值
    var deg = (Math.random() * 30 * Math.PI) / 180; // 产生 0~30 之间的随机弧度
    var txt = aCode[j]; // 得到随机的一个字符
    show_num[i] = txt;
    var x = 10 + i * 20; // 文字在canvas上的x坐标
    var y = 20 + Math.random() * 8; // 文字在canvas上的y坐标
    // 字体样式大小
    context.font = "23px 微软雅黑";
    // 书写位置位移
    context.translate(x, y);
    // 旋转
    context.rotate(deg);
    // 填充的样式
    context.fillStyle = randomColor();
    // 填充的字符,位置
    context.fillText(txt, 0, 0);
    // 重置书写位置(上面的xy与循环中的i有关)
    context.rotate(-deg);
    context.translate(-x, -y);
  }
  // 干扰项
  for (let i = 0; i <= 5; i++) { // 使用 let 声明 i
    // 验证码上显示线条
    context.strokeStyle = randomColor();
    // 路线开始
    context.beginPath();
    // 起点
    context.moveTo(Math.random() * canvas_width, Math.random() * canvas_height);
    // 终点
    context.lineTo(Math.random() * canvas_width, Math.random() * canvas_height);
    // 关闭路线
    context.closePath();
    // 绘制
    context.stroke();
  }
  for (let i = 0; i <= 30; i++) { // 使用 let 声明 i
    // 验证码上显示小点
    context.strokeStyle = randomColor();
    context.beginPath();
    let x = Math.random() * canvas_width; // 使用 let 声明 x
    let y = Math.random() * canvas_height; // 使用 let 声明 y
    // 圆心 x,y,半径,起始,终点
    context.arc(x, y, 1, 0, 2 * Math.PI);
    context.closePath();
    context.stroke();
  }

  // 得到随机的颜色值
  function randomColor() {
    var r = Math.floor(Math.random() * 256);
    var g = Math.floor(Math.random() * 256);
    var b = Math.floor(Math.random() * 256);
    return `rgb(${r},${g},${b})`;
  }

  yanma.value = show_num.join("");
  alert(yanma.value)
  return show_num;
}


const formState = reactive({
  username_or_email: '',
  password: '',
});

const formStatus = reactive({
  username_or_email: '',
  password: '',
});

const formErrors = reactive({
  username_or_email: '',
  password: '',
});


// 弹窗相关的状态
const showDialog = ref(false);
const dialogTitle = ref('');
const dialogMessage = ref('');
const dialogShowConfirm = ref(true);
const currentDialogAction = ref('');
 // 显示对话框
const showConfirmDialog = async(title, message, showConfirm = false, action = '') => {
  dialogTitle.value = title;
  dialogMessage.value = message;
  dialogShowConfirm.value = showConfirm;
  currentDialogAction.value = action;
  showDialog.value = true;
};

const handleDialogConfirm = async () => {
  showDialog.value = false;
  if (currentDialogAction.value === "confirm_login") {
    router.push("/GameLobby");
  }
  currentDialogAction.value = '';
};

// 处理对话框取消
const handleDialogCancel = async () => {
  showDialog.value = false;
  if (currentDialogAction.value === "confirm_login") {
    router.push("/GameLobby");
  }
  currentDialogAction.value = '';
};





const resetUsernameOrEmailState = () => {
  formStatus.username_or_email = '';
  formErrors.username_or_email = '';
};

const resetPasswordState = () => {
  formStatus.password = '';
  formErrors.password = '';
};

const disabled = computed(() => {
  return !(formState.username_or_email && formState.password);
});

const onFinish = async (values) => {
  // 验证码验证
  if (ver_code.value !== yanma.value) {
    await showConfirmDialog("验证码错误！", "");
    return;
  }
  try {
    const response = await axios.post("http://localhost:8000/api/accounts/login/", {
      username_or_email: values.username_or_email,
      password: values.password,
    });

    const { access, refresh } = response.data;

    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);

    await showConfirmDialog("登录成功！", "", true, "confirm_login");
  } catch (error) {
    if (error.response && error.response.status === 401) {
      const errors = error.response.data;
      for (const [field, message] of Object.entries(errors)) {
        formStatus[field] = "error";
        formErrors[field] = message;
      }
    } else {
      await showConfirmDialog("发生错误，请稍后再试。", "");
    }
  }
};

const onFinishFailed = (errorInfo) => {
  console.log("Failed:", errorInfo);
};

const goToRegister = () => {
  router.push('/register');
};
</script>

<style scoped>
/* 样式变量 */


a-row, a-col {
  width: 100%;
}

/* 页面的背景和卡片背景 */
.main-container {
  height: 100vh;
  background-color: var(--background-color);
}

.login-card {
  background-color: var(--card-bg);
  border-radius: 15px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  width: 100%;
  margin: 0 auto;
  position: relative;
}
:deep(.login-card .ant-card-head) {
  color: var(--card-text)!important;
}

/* 统一设置所有使用 login-label 的元素样式 */
.login-label {
  margin-bottom: 16px; /* 调整每个表单项的底部间距 */
  text-align: left; /* 使 label 左对齐 */
}

/* 控制 label 文字颜色 */
:deep(.login-label label) {
  color: var(--card-text) !important;
  margin-bottom: 2px; /* 调整 label 与 input 之间的间距 */
}

/* 统一设置所有使用 login-placeholder 的输入框样式 */
.login-placeholder {
  width: 100%; /* 使输入框宽度占满整个父容器 */
  border-radius: 5px; /* 输入框圆角 */
  padding: 8px 12px; /* 内边距 */
  font-size: 14px; /* 字体大小 */
  background-color: var(--input-bg);
  color: var(--input-color) ; 
}

/* 修改占位符（placeholder）文字颜色 */
.login-placeholder::placeholder {
  color: var(--placeholder-color); /* 占位符文字颜色 */
}

.theme-toggle-button {
  background-color: var(--button-bg);
  color: var(--button-color);
  border: none;
  cursor: pointer;
}

.theme-toggle-button:hover {
  background-color: #aaa;
  border-color: transparent;
  transform: scale(1.1);
}
.canvascs {
  width: 92px;
  height: 30px;
  border-radius: 5px;
  border: 1px solid #ccc;
  background-color: var(--input-bg);
}
 .verification-container {
  display: flex;
  align-items: center; /* 垂直居中对齐 */
}
#Verification  input {
  width: 22%;
  margin-right: 10px; /* 保证输入框和 canvas 之间有适当间距 */
  margin-top: 2px;
}

</style>
