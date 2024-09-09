<template>
  <div class="centered-container">
    <div class="chat-window">
      <div class="chat-container" id="chatContainer">
        <!-- Chat container Display für chat  -->
        <div v-for="(message, index) in messages" :key="index" class="message">
          {{ message }}
        </div>
      </div>
    </div>
    <div class="input-container">
      <input type="text" v-model="messageInput" placeholder="Type something to send" @keyup.enter="sendMessage" />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script>
import { io } from 'socket.io-client';

export default {
  data() {
    return {
      socket: null,
      messageInput: '',
      messages: [],
    };
  },
  mounted() {
    // Connect to the Socket.io server
    this.socket = io('http://' + document.domain + ':' + location.port);

    this.socket.on('connect', () => {
      this.socket.send('User has connected!');
    });

    this.socket.on('message', (msg) => {
      this.messages.push(msg);
      this.scrollChatToBottom();
    });
  },
  methods: {
    sendMessage() {
      const messageText = this.messageInput.trim();

      if (messageText !== "") {
        // Emit message via socket
        this.socket.send(`You: ${messageText}`);

        // Add the message to the messages array
        this.messages.push(`You: ${messageText}`);

        // Clear the input field
        this.messageInput = "";

        // Scroll the chat to the bottom
        this.scrollChatToBottom();
      }
    },
    scrollChatToBottom() {
      const chatContainer = this.$el.querySelector('#chatContainer');
      chatContainer.scrollTop = chatContainer.scrollHeight;
    },
  },
};
</script>

<style scoped>
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f0f0;
}

.centered-container {
  width: 300px;
  height: 600px;
  border: 5px solid black;
  display: flex;
  flex-direction: column;
  background-color: white;
}

.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: lightblue;
}

.chat-container {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  background-color: lightblue;
}

.input-container {
  display: flex;
  padding: 10px;
  border-top: 1px solid #ddd;
  background-color: lightgrey;
}

input[type="text"] {
  flex: 1;
  padding: 10px;
  border-radius: 20px;
  border: 1px solid #ddd;
}

button {
  margin-left: 10px;
  padding: 10px 20px;
  background-color: olive;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}
</style>
