<template>
    <div class="profile-page">
      <div class="profile-header">
        <img :src="user.avatar" alt="User Avatar" class="profile-avatar" />
        <h2 class="profile-name">{{ user.name }}</h2>
      </div>
      <p class="profile-bio">{{ user.bio }}</p>
    </div>
  </template>
  
  <script>
  export default {
    name: "UserProfile",
    data() {
      return {
        user: {
          avatar: "path/to/avatar.jpg",
          name: "John Doe",
          bio: "Web developer and tech enthusiast."
        }
      };
    }
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
  .profile-bio {
    color: #666;
    font-style: italic;
  }
  </style>