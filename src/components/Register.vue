<template>
  <a-row justify="center" align="middle" style="height: 100vh">
    <a-col :span="8">
      <a-card title="注册" bordered>
        <a-form :model="formState" @finish="onFinish" @finishFailed="onFinishFailed" layout="vertical" ref="register_form">
          <a-form-item
            has-feedback
            label="用户名"
            name="username"
            :validateStatus="formStatus.username"
            :help="formErrors.username"
            :rules="[{ required: true, message: '请输入用户名！' }]"
          >
            <a-input
              v-model:value="formState.username"
              placeholder="用户名"
              show-count :maxlength="150"
              @change="resetUsernameState"
            />
          </a-form-item>
          <a-form-item
            has-feedback
            label="电子邮箱"
            name="email"
            :validateStatus="formStatus.email"
            :help="formErrors.email"
            :rules="[{ required: true, message: '请输入电子邮箱！' }]"
          >
            <a-input
              v-model:value="formState.email"
              placeholder="电子邮箱"
              @change="resetEmailState"
            />
          </a-form-item>
          <a-form-item
            has-feedback
            label="密码"
            name="password"
            :validateStatus="formStatus.password"
            :help="formErrors.password"
            :rules="[{ required: true, message: '请输入密码！' }]"
          >
            <a-input-password
              v-model:value="formState.password"
              placeholder="密码"
              @change="resetPasswordState"
            />
          </a-form-item>
          <a-form-item
            has-feedback
            label="确认密码"
            name="confirmPassword"
            :validateStatus="formStatus.confirmPassword"
            :help="formErrors.confirmPassword"
            :rules="[{ required: true, message: '请确认密码！' }]"
          >
            <a-input-password
              type="password"
              v-model:value="formState.confirmPassword"
              placeholder="确认密码"
              @change="resetConfirmPasswordState"
            />
          </a-form-item>
          <a-form-item>
            <a-button :disabled="disabled" type="primary" html-type="submit" block>注册</a-button>
          </a-form-item>
        </a-form>
      </a-card>
    </a-col>
  </a-row>
</template>

<script setup>
import axios from "axios";
import {computed, reactive} from "vue";

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
</style>
