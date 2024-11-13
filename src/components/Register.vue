<template>
  <a-row justify="center" align="middle" style="height: 100vh">
    <a-col :span="8">
      <a-card title="注册" bordered>
        <a-form :model="formState" @finish="onFinish" @finishFailed="onFinishFailed" layout="vertical" ref="register_form" :rules="rules">
          <a-form-item
            label="用户名"
            name="username"
            :rules="[{ required: true, message: '请输入用户名！' }]"
          >
            <a-input
              v-model:value="formState.username"
              placeholder="用户名"
            />
          </a-form-item>
          <a-form-item
            label="电子邮箱"
            name="email"
            :rules="[{ required: true, message: '请输入电子邮箱！' }]"
          >
            <a-input
              v-model:value="formState.email"
              placeholder="电子邮箱"
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
          <a-form-item
            label="确认密码"
            name="confirmPassword"
            :rules="[{ required: true, message: '请确认密码！' }]"
          >
            <a-input
              type="password"
              v-model:value="formState.confirmPassword"
              placeholder="确认密码"
            />
          </a-form-item>
          <a-form-item>
            <a-button type="primary" html-type="submit" block>注册</a-button>
          </a-form-item>
        </a-form>
      </a-card>
    </a-col>
  </a-row>
</template>

<script setup>
import axios from "axios";
import { reactive } from "vue";

const formState = reactive({
  username: "",
  email: "",
  password: "",
  confirmPassword: ""
});

// 表单验证规则
const rules = {
  confirmPassword: [
    { required: true, message: "请确认密码！" },
    { validator: (_, value) => value === formState.password ? Promise.resolve() : Promise.reject("密码不匹配！") }
  ]
};

const onFinish = async (values) => {
  // 检查密码是否匹配
  if (values.password !== values.confirmPassword) {
    alert("密码不匹配！");
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
  } catch (error) {
    // 注册失败的响应处理
    if (error.response && error.response.status === 400) {
      const errors = error.response.data;
      let errorMessages = "以下是存在的问题：\n";

      const translations = {
        username: "用户名",
        email: "电子邮件地址",
        password: "密码"
      };

      // 将所有的错误消息显示在一个弹窗中
      for (const [field, messages] of Object.entries(errors)) {
        errorMessages += `${translations[field]}: ${messages.join(", ")}\n`;
      }
      alert(errorMessages);
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
</style>
