<template>
    <a-row justify="center" align="middle" style="height: 100vh">
      <a-col :span="8">
        <a-card title="Login" bordered>
          <a-form @submit="handleSubmit" layout="vertical">
            <a-form-item label="Username" name="username" rules="[ { required: true, message: 'Please input your username!' } ]">
              <a-input v-model="username" placeholder="Username" />
            </a-form-item>
            <a-form-item label="Password" name="password" rules="[ { required: true, message: 'Please input your password!' } ]">
              <a-input type="password" v-model="password" placeholder="Password" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" html-type="submit" block>Log in</a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>
    </a-row>
  </template>
  
  <script>
  export default {
    name: 'UserLogin',
    data() {
      return {
        username: '',
        password: '',
      };
    },
    methods: {
      handleSubmit() {
        console.log('Logging in with', this.username, this.password);
        // 添加登录逻辑
      },
    },
  };
  </script>
  
  <style scoped>
  a-row,
  a-col {
    width: 100%;
  }
  </style>