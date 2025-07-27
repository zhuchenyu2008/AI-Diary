<template>
  <div class="login-container">
    <div class="login-box">
      <h2>AI Diary Login</h2>
      <form @submit.prevent="handleLogin">
        <input type="password" v-model="password" placeholder="Enter Your 1-4 Digit PIN" required maxlength="4" pattern="\d{1,4}" title="Please enter a 1-4 digit PIN">
        <button type="submit">Unlock</button>
      </form>
      <p v-if="error" class="error-message">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  data() {
    return {
      password: '',
      error: ''
    };
  },
  methods: {
    async handleLogin() {
      try {
        const response = await api.login(this.password);
        localStorage.setItem('token', response.data.token);
        this.$router.push('/');
      } catch (error) {
        this.error = 'Invalid PIN. Please try again.';
        console.error('Login failed:', error);
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}
.login-box {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
}
input {
  display: block;
  width: 100%;
  margin-bottom: 1rem;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}
button {
  width: 100%;
  padding: 0.75rem;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}
button:hover {
  background-color: #0056b3;
}
.error-message {
  color: red;
  margin-top: 1rem;
}
</style>
