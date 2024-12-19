<template>
  <transition name="dialog-fade">
  <div v-if="show" class="profile-dialog-overlay" @click="handleClose">
    <div class="profile-dialog" @click.stop>
      <div class="profile-dialog-header">
        <h3>个人资料设置</h3>
        <button class="close-btn" @click="handleClose">
          <img src="@/assets/close-createRoom.svg" alt="Close"/>
        </button>
      </div>

      <div class="profile-dialog-content">
        <!-- 头像设置 -->
        <div class="avatar-section">
          <div class="avatar-container">
            <img :src="userProfile.avatar" alt="头像" class="current-avatar" />
            <div class="avatar-overlay">
              <input
                type="file"
                @change="handleAvatarChange"
                accept="image/*"
                id="avatar-upload"
                class="avatar-input"
                ref="fileInput"
              />
              <div class="upload-text">点击更换头像</div>
            </div>
          </div>
          <div class="avatar-tip">支持 jpg、png 格式大小 5MB 以内的图片</div>
        </div>

        <!-- 个性签名设置 -->
        <div class="form-section">
          <div class="label-container">
            <label>个性签名</label>
            <span v-if="isEditingSignature" class="char-count">{{ signatureLength }}/30</span>
          </div>
          <div class="input-container" v-if="!isEditingSignature">
            <div class="signature-display">{{ userProfile.signature }}</div>
            <button class="edit-btn" @click="startEditSignature">
              <img src="@/assets/edit.svg" alt="Edit" />
            </button>
          </div>
          <div class="input-container" v-else>
            <input
              v-model="tempSignature"
              type="text"
              placeholder="输入个性签名"
              maxlength="30"
              class="form-input"
              ref="signatureInput"
            />
            <div class="button-group">
              <button @click="cancelEditSignature" class="cancel-btn">取消</button>
              <button
                @click="saveSignature"
                class="save-btn"
                :disabled="!signatureChanged"
              >
                保存
              </button>
            </div>
          </div>
        </div>

        <!-- 密码修改区域 -->
        <div class="password-section">
          <div class="section-header">
            <h4>密码设置</h4>
            <button
              v-if="!isEditingPassword"
              @click="startEditPassword"
              class="edit-btn"
            >
              <img src="@/assets/edit.svg" alt="Edit" />
            </button>
          </div>

          <div v-if="!isEditingPassword" class="password-display">
            <div class="password-mask">••••••••</div>
            <div class="password-tip">建议定期更换密码，确保账号安全</div>
          </div>

          <div v-else class="password-form">
            <div class="form-section">
              <label>当前密码</label>
              <a-input-password
                v-model:value="currentPassword"
                placeholder="输入当前密码"
                class="form-input"
              />
            </div>

            <div class="form-section">
              <label>新密码</label>
              <a-input-password
                v-model:value="newPassword"
                placeholder="输入新密码"
                class="form-input"
              />
            </div>

            <div class="form-section">
              <label>确认新密码</label>
              <a-input-password
                v-model:value="confirmPassword"
                placeholder="再次输入新密码"
                class="form-input"
              />
              <div class="password-error" v-if="passwordError">
                {{ passwordError }}
              </div>
            </div>

            <div class="button-group">
              <button @click="cancelEditPassword" class="cancel-btn">取消</button>
              <button
                @click="handlePasswordChange"
                class="save-btn"
                :disabled="!canChangePassword"
              >
                确认修改
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  </transition>
</template>

<script>
import { ref, computed, watch } from 'vue';

export default {
  name: 'ProfileDialog',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    userProfile: {
      type: Object,
      required: true
    }
  },

  emits: ['close', 'update-avatar', 'update-signature', 'update-password'],

  setup(props, { emit }) {
    // 个性签名相关
    const isEditingSignature = ref(false);
    const tempSignature = ref(props.userProfile.signature || '');
    const signatureLength = computed(() => tempSignature.value.length);
    const signatureChanged = computed(() =>
      tempSignature.value !== props.userProfile.signature
    );

    // 密码相关
    const isEditingPassword = ref(false);
    const currentPassword = ref('');
    const newPassword = ref('');
    const confirmPassword = ref('');
    const passwordError = ref('');

    const canChangePassword = computed(() => {
      return currentPassword.value &&
             newPassword.value &&
             confirmPassword.value &&
             !passwordError.value;
    });

    // 监听密码变化
    watch([newPassword, confirmPassword], ([newVal, confirmVal]) => {
      if (newVal && confirmVal && newVal !== confirmVal) {
        passwordError.value = '两次输入的密码不一致';
      } else {
        passwordError.value = '';
      }
    });

    // 关闭弹窗
    const handleClose = () => {
      emit('close');
      resetForm();
    };

    // 处理头像变更
    const handleAvatarChange = (event) => {
      const file = event.target.files[0];
      if (!file) return;

      if (!file.type.startsWith('image/')) {
        alert('请选择图片文件！');
        return;
      }

      if (file.size > 5 * 1024 * 1024) {
        alert('图片大小不能超过5MB！');
        return;
      }

      emit('update-avatar', file);
    };

    // 个性签名编辑功能
    const startEditSignature = () => {
      isEditingSignature.value = true;
      tempSignature.value = props.userProfile.signature || '';
      // 在下一个 tick 后聚焦输入框
      setTimeout(() => {
        const input = document.querySelector('.form-input');
        if (input) input.focus();
      }, 0);
    };

    const cancelEditSignature = () => {
      isEditingSignature.value = false;
      tempSignature.value = props.userProfile.signature || '';
    };

    const saveSignature = () => {
      if (!tempSignature.value.trim()) {
        alert('个性签名不能为空！');
        return;
      }
      emit('update-signature', tempSignature.value.trim());
      isEditingSignature.value = false;
    };

    // 密码修改功能
    const startEditPassword = () => {
      isEditingPassword.value = true;
      resetPasswordForm();
    };

    const cancelEditPassword = () => {
      isEditingPassword.value = false;
      resetPasswordForm();
    };

    const handlePasswordChange = () => {
      if (newPassword.value !== confirmPassword.value) {
        passwordError.value = '两次输入的密码不一致';
        return;
      }

      emit('update-password', {
        oldPassword: currentPassword.value,
        newPassword: newPassword.value
      });

      isEditingPassword.value = false;
      resetPasswordForm();
    };

    // 重置表单
    const resetForm = () => {
      isEditingSignature.value = false;
      isEditingPassword.value = false;
      tempSignature.value = props.userProfile.signature || '';
      resetPasswordForm();
    };

    const resetPasswordForm = () => {
      currentPassword.value = '';
      newPassword.value = '';
      confirmPassword.value = '';
      passwordError.value = '';
    };

    return {
      isEditingSignature,
      isEditingPassword,
      tempSignature,
      signatureLength,
      signatureChanged,
      currentPassword,
      newPassword,
      confirmPassword,
      passwordError,
      canChangePassword,
      handleClose,
      handleAvatarChange,
      startEditSignature,
      cancelEditSignature,
      saveSignature,
      startEditPassword,
      cancelEditPassword,
      handlePasswordChange
    };
  }
};
</script>

<style scoped>
.profile-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.profile-dialog {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.profile-dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.profile-dialog-header h3 {
  margin: 0;
  font-size: 1.5em;
  color: #2c3e50;
}

.close-btn {
  background: transparent;
  border: none;
  padding: 8px;
  cursor: pointer;
  transition: transform 0.2s;
}

.close-btn:hover {
  transform: scale(1.1);
}

.close-btn img {
  width: 20px;
  height: 20px;
}

/* 头像部分样式 */
.avatar-section {
  text-align: center;
  margin-bottom: 32px;
}

.avatar-container {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 12px;
  cursor: pointer;
}

.current-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.avatar-container:hover .avatar-overlay {
  opacity: 1;
}

.avatar-input {
  position: absolute;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.upload-text {
  color: white;
  font-size: 14px;
  pointer-events: none;
}

.avatar-tip {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

/* 表单部分样式 */
.form-section {
  margin-bottom: 24px;
}

.label-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.label-container label {
  color: #2c3e50;
  font-weight: 500;
}

.char-count {
  font-size: 12px;
  color: #999;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: center;
}

.signature-display {
  flex: 1;
  padding: 10px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  color: #606266;
  min-height: 40px;
  display: flex;
  align-items: center;
}

.edit-btn {
  padding: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.edit-btn img {
  width: 16px;
  height: 16px;
  opacity: 0.6;
}

.edit-btn:hover img {
  opacity: 1;
}

.form-input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-input:focus {
  border-color: #409eff;
  outline: none;
}

.button-group {
  display: flex;
  gap: 8px;
}

.save-btn,
.cancel-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.save-btn {
  background: #409eff;
  color: white;
}

.save-btn:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}

.save-btn:not(:disabled):hover {
  background: #66b1ff;
}

.cancel-btn {
  background: #f5f7fa;
  color: #606266;
  border: 1px solid #dcdfe6;
}

.cancel-btn:hover {
  color: #409eff;
  border-color: #c6e2ff;
  background-color: #ecf5ff;
}

/* 密码修改部分样式 */
.password-section {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #eee;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.1em;
}

.password-display {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 20px;
}

.password-mask {
  font-size: 16px;
  color: #606266;
  margin-bottom: 8px;
  letter-spacing: 2px;
}

.password-tip {
  font-size: 12px;
  color: #909399;
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  animation: slideDown 0.3s ease;
}
.password-form .form-section {
  display: grid;
  grid-template-columns: 120px 1fr; /* 标签固定宽度120px，输入框占剩余空间 */
  align-items: center;
  gap: 5px;
}

.password-form label {
  text-align: left;
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.password-form .form-input {
  width: 100%;
  height: 36px;
  padding: 0 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.password-error {
  font-size: 12px;
  color: #f56c6c;
  margin-top: 4px;
  grid-column: 2; /* 错误信息对齐输入框 */
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式样式 */
@media (max-width: 480px) {
  .profile-dialog {
    width: 95%;
    padding: 16px;
  }

  .button-group {
    flex-direction: column;
  }

  .save-btn,
  .cancel-btn {
    width: 100%;
  }
}
/* Dialog 动画相关样式 */
.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: opacity 0.3s ease;
}

.dialog-fade-enter-active .profile-dialog,
.dialog-fade-leave-active .profile-dialog {
  transition: transform 0.3s ease;
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}

.dialog-fade-enter-from .profile-dialog {
  transform: translateY(-20px);
}

.dialog-fade-leave-to .profile-dialog {
  transform: translateY(20px);
}

/* 确保遮罩层有过渡效果 */
.profile-dialog-overlay {
  transition: opacity 0.3s ease;
}

/* 确保弹窗本身也有过渡效果 */
.profile-dialog {
  transition: transform 0.3s ease;
}

/* 密码输入框样式 */
:deep(.ant-input-password) {
  background-color: var(--input-bg, #fff);
  border-radius: 6px;
}

:deep(.ant-input-password input) {
  background-color: var(--input-bg, #fff);
  color: var(--input-color, #000);
}

:deep(.ant-input-password-icon) {
  color: var(--svg-color, #333);
}

:deep(.ant-input-password:hover) {
  border-color: #409eff;
}

:deep(.ant-input-password:focus-within) {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

</style>