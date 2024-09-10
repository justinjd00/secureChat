<template>
  <div class="signin-container">
    <div class="signin-box">
      <h1>Anmeldung</h1>
      <form @submit.prevent="submitForm">
        <label for="username">Benutzername:</label>
        <input v-model="username" type="text" id="username" name="username" placeholder="Enter your Username" required />

        <label for="password">Passwort:</label>
        <input v-model="password" type="password" id="password" name="password" placeholder="Enter your Password" required />

        <div class="remember-me">
          <input type="checkbox" id="remember" />
          <label for="remember">Remember me</label>
        </div>

        <button type="submit" class="signin-button">Anmeldung</button>
      </form>

      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <div class="extra-options">
        <a href="#" class="forgot-password">Passwort vergessen?</a>
        <p>
          Sie haben kein Konto? <router-link to="/signup" class="signup-link">Hier anmelden</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "SignIn",
  data() {
    return {
      username: '',
      password: '',
      errorMessage: ''
    };
  },
  methods: {
    async submitForm() {
      try {
        const response = await fetch("/api/signin", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            username: this.username,
            password: this.password
          }),
        });

        if (response.ok) {
          const data = await response.json();
          // Speichere das Token und leite den Benutzer weiter
          localStorage.setItem("token", data.token);
          this.$router.push("/mainchat");  // Leitet den Benutzer zum Hauptchat weiter
        } else {
          const errorData = await response.json();
          this.errorMessage = errorData.detail || "Anmeldung fehlgeschlagen";
        }
      } catch (error) {
        this.errorMessage = "Es gab ein Problem bei der Anmeldung.";
      }
    }
  }
}
</script>

<style scoped>
.signin-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: url('your-background-image-path.jpg') no-repeat center center;
  background-size: cover;
}

.signin-box {
  background-color: rgba(255, 255, 255, 0.9);
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  max-width: 400px;
  width: 100%;
}

h1 {
  text-align: center;
  margin-bottom: 2rem;
  font-size: 1.8rem;
  color: #333;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

input[type="text"],
input[type="password"] {
  width: 100%;
  padding: 0.75rem;
  margin-bottom: 1.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

.remember-me {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
}

.remember-me input {
  margin-right: 0.5rem;
}

.signin-button {
  width: 100%;
  padding: 0.75rem;
  background-color: #f4c042;
  border: none;
  color: #fff;
  font-size: 1.1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.signin-button:hover {
  background-color: #d8a535;
}

.extra-options {
  text-align: center;
  margin-top: 1.5rem;
}

.extra-options a {
  color: #999;
  text-decoration: none;
  font-size: 0.9rem;
}

.signup-link {
  color: #f4c042;
  text-decoration: none;
}

.signup-link:hover {
  text-decoration: underline;
}

.error-message {
  color: red;
  text-align: center;
  margin-top: 1rem;
}
</style>
