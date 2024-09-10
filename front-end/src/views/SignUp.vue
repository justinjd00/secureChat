<template>
  <div class="signup-container">
    <div class="signup-box">
      <h1>Registrieren</h1>
      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label for="username">Benutzername:</label>
          <input v-model="user.username" type="text" id="username" placeholder="Enter your Username" required />
        </div>

        <div class="form-group">
          <label for="email">Email:</label>
          <input v-model="user.email" type="email" id="email" placeholder="Enter your Email" required />
        </div>

        <div class="form-group">
          <label for="password">Passwort:</label>
          <input v-model="user.password" type="password" id="password" placeholder="Enter your Password" required />
        </div>

        <div class="form-group">
          <label for="confirmPassword">Passwort bestätigen:</label>
          <input v-model="confirmPassword" type="password" id="confirmPassword" placeholder="Confirm your Password" required />
        </div>

        <button type="submit" class="signup-button">Registrieren</button>
      </form>

      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

      <div class="extra-options">
        <p>
          Bereits ein Konto? <router-link to="/" class="signin-link">Hier einloggen</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      user: {
        username: '',
        email: '',
        password: '',
      },
      confirmPassword: '',
      errorMessage: '', // Für Fehlermeldungen
    };
  },
  methods: {
    async submitForm() {
      // Check if password and confirmPassword match
      if (this.user.password !== this.confirmPassword) {
        this.errorMessage = "Passwörter stimmen nicht überein!";
        return;
      }

      const response = await fetch("/api/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(this.user),
      });

      if (response.ok) {
        // Weiterleiten zur Login-Seite nach erfolgreicher Registrierung
        this.$router.push("/mainchat");
      } else {
        // Fehlermeldung anzeigen, wenn Registrierung fehlschlägt
        this.errorMessage = "Registrierung fehlgeschlagen. Versuchen Sie es erneut.";
      }
    },
  },
};
</script>

<style scoped>
.signup-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #000;
}

.signup-box {
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

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

input[type="text"],
input[type="email"],
input[type="password"] {
  width: 100%;
  padding: 0.75rem;
  margin-bottom: 1.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

.signup-button {
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

.signup-button:hover {
  background-color: #d8a535;
}

.extra-options {
  text-align: center;
  margin-top: 1.5rem;
}

.signin-link {
  color: #f4c042;
  text-decoration: none;
}

.signin-link:hover {
  text-decoration: underline;
}

.error-message {
  color: red;
  text-align: center;
  margin-top: 1rem;
}
</style>
