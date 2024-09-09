<template>
  <div class="form-container">
    <h1>Sign Up</h1>
    <form @submit.prevent="submitForm" class="form">
      <label for="username">Username:</label>
      <input type="text" v-model="username" id="username" required>

      <label for="email">Email:</label>
      <input type="email" v-model="email" id="email" required>

      <label for="password">Password:</label>
      <input type="password" v-model="password" id="password" required>

      <label for="confirmPassword">Confirm Password:</label>
      <input type="password" v-model="confirmPassword" id="confirmPassword" required>

      <button type="submit">Sign Up</button>

      <p>Already have an account? <router-link to="/">Sign in here</router-link></p>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
    };
  },
  methods: {
    async submitForm() {
      if (this.password !== this.confirmPassword) {
        alert("Passwords do not match");
        return;
      }
      try {
        const response = await fetch('/api/signup', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: this.username,
            email: this.email,
            password: this.password,
            confirm_password: this.confirmPassword,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message);
        }

        alert('Sign-up successful!');
      } catch (error) {
        alert(`Error: ${error.message}`);
      }
    },
  },
};
</script>

<style scoped>
/* Container für das gesamte Formular */
.form-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  max-width: 400px;
  margin: 0 auto;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Stil für das Formular */
.form {
  display: flex;
  flex-direction: column;
  width: 100%;
}

/* Stil für die Labels */
.form label {
  margin-top: 15px;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

/* Stil für die Input-Felder */
.form input {
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
  border: 1px solid #ccc;
  font-size: 16px;
}

/* Stil für den Button */
.form button {
  padding: 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 15px;
}

/* Hover-Effekt für den Button */
.form button:hover {
  background-color: #0056b3;
}

/* Link zur Anmeldung */
.form p {
  margin-top: 15px;
  font-size: 14px;
}

.form p a {
  color: #007bff;
  text-decoration: none;
}

.form p a:hover {
  text-decoration: underline;
}
</style>
