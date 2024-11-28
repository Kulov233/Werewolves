<template>
    <div class="profile-page">
      <div class="profile-header">
        <img :src="user.profile?.avatar ? `${getFullAvatarUrl(user.profile.avatar)}?t=${Date.now()}` : defaultAvatar" alt="User Avatar" class="profile-avatar" />
        <h2 class="profile-name">{{ user.username }}</h2>
        <p class="profile-email">{{ user.email }}</p>
      </div>
      <p class="profile-bio" v-if="user.profile?.bio">{{ user.profile.bio }}</p>
      <p class="profile-bio" v-else>暂无个人介绍</p>
      
      <!-- 上传头像功能 -->
      <div class="upload-avatar">
        <label for="avatar-upload" class="upload-label">
          上传头像
          <input id="avatar-upload" type="file" @change="handleFileAndUpload" accept="image/*" />
        </label>
      </div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  const accessToken = localStorage.getItem("access_token");
  const refreshToken = localStorage.getItem("refresh_token");
  
  export default {
    name: "UserProfile",
    data() {
      return {
        user: {}, // 初始化用户数据为空对象
        defaultAvatar: "path/to/default/avatar.jpg", // 默认头像路径
        uploading: false, // 控制上传状态
      };
    },
    created() {
      this.fetchUserData();
    },
    methods: {
      async fetchUserData() {
        try {
          const response = await axios.get("http://localhost:8000/api/accounts/info/", {
            headers: {
              Authorization: `Bearer ${accessToken}`, // 替换为实际的 Token 获取方式
            },
          });
          this.user = response.data; // 将返回的数据绑定到 user
        } catch (error) {
          if (error.response && error.response.status === 401) {
            console.warn("访问令牌已失效，尝试刷新令牌...");
            await this.refreshAccessToken();
            this.fetchUserData();
          } else {
            console.error("获取用户信息失败:", error);
          }
        }
      },
      async refreshAccessToken() {
        try {
          const response = await axios.post("http://localhost:8000/api/accounts/token/refresh/", {
            headers: {
              Authorization: `Bearer ${accessToken}`, // 替换为实际的 Token 获取方式
            },
            refresh: refreshToken, // 向后端发送 refresh_token
          });
          const newAccessToken = response.data.access;
          localStorage.setItem("access_token", newAccessToken); // 更新本地存储
          console.log("令牌刷新成功！");
        } catch (error) {
          console.error("刷新令牌失败:", error);
          this.logout();
        }
      },
      logout() {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        this.$router.push("/login");
      },
      async handleFileAndUpload(event) {
        const file = event.target.files[0]; // 获取选中的文件
        if (!file) return;
  
        this.uploading = true; // 设置上传状态为 true
        const formData = new FormData();
        formData.append("avatar", file); // 将文件添加到 FormData 中
  
        try {
          const response = await axios.post("http://localhost:8000/api/accounts/avatar/upload/", formData, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("access_token")}`, // 添加认证头
              "Content-Type": "multipart/form-data",
            },
          });
          alert("头像上传成功！");
          this.user.profile.avatar = response.data.avatar_url;
        } catch (error) {
          console.error("头像上传失败:", error);
          alert("上传失败，请重试！");
        } finally {
          this.uploading = false; // 恢复上传状态
        }
      },
      getFullAvatarUrl(path) {
        return path.startsWith("http") ? path : `http://localhost:8000${path}`;
      },
    },
  };
  </script>
  
  <style scoped>
  .profile-page {
    text-align: center;
    padding: 20px;
  }
  .profile-avatar {
    width: 100px;
    height: 100px;
    border-radius: 50%;
  }
  .profile-name {
    font-size: 24px;
    margin-top: 10px;
  }
  .profile-email {
    font-size: 16px;
    color: #333;
    margin-top: 5px;
  }
  .profile-bio {
    color: #666;
    font-style: italic;
  }
  
  .upload-avatar {
    margin-top: 20px;
  }
  .upload-avatar input {
    display: none; /* 隐藏文件选择框 */
  }
  .upload-label {
    display: inline-block;
    background-color: #007bff;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  .upload-label:hover {
    background-color: #0056b3;
  }
  </style>
  