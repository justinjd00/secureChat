<template>
  <div class="signup">
    <h1>Sign Up</h1>
    <form>
      <label for="email">Email:</label>
      <input type="email" id="email" name="email" required>

      <label for="password">Password:</label>
      <input type="password" id="password" name="password" required>

      <button type="submit">Sign Up</button>
    </form>
    <p>
      Already have an account? <router-link to="/">Sign in here</router-link>
    </p>
  </div>
</template>

<script>
export default {
  name: "SignUp"
}
</script>
