<template>
  <v-app>
    <router-view></router-view>
  </v-app>
</template>

<script>
import ChatWindow from './components/MainChat.vue';

export default {
  components: {
    ChatWindow,
  },
};
</script>
<style lang="scss" scoped>
</style>