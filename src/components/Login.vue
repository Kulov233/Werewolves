<template>
  <a-row justify="center" align="middle" style="height: 100vh">
    <a-col :span="8">
      <a-card title="登录" bordered>
        <a-form :model="formState" @finish="onFinish" @finishFailed="onFinishFailed" layout="vertical" ref="login_form" :rules="rules">
          <a-form-item
            label="用户名/邮箱"
            name="username_or_email"
            :rules="[{ required: true, message: '请输入用户名！' }]"
          >
            <a-input
                v-model:value="formState.username_or_email"
                placeholder="用户名/邮箱"
            />
          </a-form-item>
          <a-form-item
            label="密码"
            name="password"
            :rules="[{ required: true, message: '请输入密码！' }]"
          >
            <a-input
                type="password"
                v-model:value="formState.password"
                placeholder="密码"

            />
          </a-form-item>
          <a-form-item>
            <a-button type="primary" html-type="submit" block>登录</a-button>
          </a-form-item>
        </a-form>
      </a-card>
    </a-col>
  </a-row>
</template>

<script setup>
import axios from "axios";
import {reactive} from 'vue';

const formState = reactive({
  username_or_email: "",
  password: "",
});

const onFinish = async values => {
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
    alert("登陆成功！");
    // 例如：this.$router.push("/dashboard");
  } catch (error) {
    if (error.response && error.response.status === 401) {
      // 登录失败，显示错误信息
      const errorMsg = error.response.data.username_or_email || error.response.data.password || "登陆失败。";
      alert(errorMsg);
    } else {
      console.error("An error occurred:", error);
    }
  }
}

const onFinishFailed = errorInfo => {
  console.log('Failed:', errorInfo);
};

</script>

<style scoped>
a-row,
a-col {
  width: 100%;
}
</style>