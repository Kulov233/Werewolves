<template>
    <a-row justify="center" align="middle" style="height: 100vh">
      <a-col :span="8">
        <a-card title="Register" bordered>
          <a-form @submit="handleSubmit" layout="vertical">
            <a-form-item label="Username" name="username" rules="[ { required: true, message: 'Please input your username!' } ]">
              <a-input v-model="username" placeholder="Username" />
            </a-form-item>
            <a-form-item label="Password" name="password" rules="[ { required: true, message: 'Please input your password!' } ]">
              <a-input type="password" v-model="password" placeholder="Password" />
            </a-form-item>
            <a-form-item label="Confirm Password" name="confirmPassword" rules="[ { required: true, message: 'Please confirm your password!' } ]">
              <a-input type="password" v-model="confirmPassword" placeholder="Confirm Password" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" html-type="submit" block>Register</a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>
    </a-row>
  </template>
  
  <script>
  export default {
    name: 'UserRegister',
    data() {
      return {
        username: '',
        password: '',
        confirmPassword: '',
      };
    },
    methods: {
      handleSubmit() {
        if (this.password !== this.confirmPassword) {
          alert('Passwords do not match!');
          return;
        }
        console.log('Registering with', this.username, this.password);
        // 添加注册逻辑
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