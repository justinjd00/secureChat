<template>
  <div class="signin">
    <h1>Sign In</h1>
    <form>
      <label for="email">Email:</label>
      <input type="email" id="email" name="email" required>

      <label for="password">Password:</label>
      <input type="password" id="password" name="password" required>

      <button type="submit">Sign In</button>
    </form>
    <p>
      No account? <router-link to="/signup">Sign up here</router-link>
    </p>
  </div>
</template>

<script>
export default {
  name: "SignIn"
}
</script>
