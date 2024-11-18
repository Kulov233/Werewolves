<template>
  <a-row justify="center" style="height: 100vh">
    <a-col :span="8">
      <a-card title="登录" bordered>
        <a-form :model="formState" @finish="onFinish" @finishFailed="onFinishFailed" layout="vertical" ref="login_form">
          <a-form-item
            label="用户名/邮箱"
            name="username_or_email"
            :validateStatus="formStatus.username_or_email"
            :help="formErrors.username_or_email"
          >
            <a-input
              v-model:value="formState.username_or_email"
              placeholder="用户名/邮箱"
              @change="resetUsernameOrEmailState"
            />
          </a-form-item>
          <a-form-item
            label="密码"
            name="password"
            :validateStatus="formStatus.password"
            :help="formErrors.password"
          >
            <a-input
              type="password"
              v-model:value="formState.password"
              placeholder="密码"
              @change="resetPasswordState"
            />
          </a-form-item>
          <a-form-item>
            <a-button :disabled="disabled" type="primary" html-type="submit" block>登录</a-button>
          </a-form-item>
        </a-form>
      </a-card>
    </a-col>
  </a-row>
</template>

<script setup>
import axios from "axios";
import {computed, reactive} from "vue";

import { useRouter } from "vue-router"; // 引入 Vue Router

const router = useRouter(); // 获取 router 实例

const formState = reactive({
  username_or_email: "",
  password: "",
});

const formStatus = reactive({
  username_or_email: '',
  password: ''
});

const formErrors = reactive({
  username_or_email: '',
  password: ''
});

// 重置表单项状态和错误提示
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
  try {
    const response = await axios.post("http://localhost:8000/api/accounts/login/", {
      username_or_email: values.username_or_email,
      password: values.password,
    });

    // 获取并存储 access 和 refresh token
    const { access, refresh, message } = response.data;
    console.log(message);

    // 存储 tokens（例如，可以存储在 localStorage 中）
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);

    // 成功登录后重定向或执行其他逻辑
    alert("登录成功！");
    // 例如：this.$router.push("/dashboard");
	router.push("/Home");
  } catch (error) {
    if (error.response && error.response.status === 401) {
      // 登录失败时处理错误响应
      const errors = error.response.data;

      // 遍历返回的错误消息，设置表单状态和错误提示
      for (const [field, message] of Object.entries(errors)) {
        formStatus[field] = "error";
        formErrors[field] = message;  // 使用字符串格式的错误消息
      }
    } else {
      console.error("An error occurred:", error);
      alert("发生错误，请稍后再试。");
    }
  }
}

const onFinishFailed = (errorInfo) => {
  console.log("Failed:", errorInfo);
};
</script>

<style scoped>
a-row,
a-col {
  width: 100%;
}
</style>
