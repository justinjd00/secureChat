<template>
  <div class="outer-container">
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
/* Die äußere Container, der sicherstellt, dass alles in der Mitte steht */
.outer-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh; /* Volle Höhe des Viewports */
  background-color: #f0f0f0; /* Hintergrundfarbe der gesamten Seite */
}

.centered-container {
  width: 100%;
  max-width: 400px;
  height: 100%;
  max-height: 700px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background-color: white;
  border-radius: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.chat-window {
  display: flex;
  flex-direction: column;
  flex: 1;
  background-color: lightblue;
  border-top-left-radius: 30px;
  border-top-right-radius: 30px;
  overflow: hidden;
}

.chat-container {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  background-color: lightblue;
  border-top-left-radius: 30px;
  border-top-right-radius: 30px;
}

.input-container {
  display: flex;
  padding: 10px;
  background-color: lightgrey;
  border-bottom-left-radius: 30px;
  border-bottom-right-radius: 30px;
}

input[type="text"] {
  flex: 1;
  padding: 10px;
  border-radius: 20px;
  border: 1px solid #ddd;
  outline: none;
}

button {
  margin-left: 10px;
  padding: 10px 20px;
  background-color: olive;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: darkolivegreen;
}

.message {
  padding: 5px;
  margin-bottom: 5px;
  background-color: #e0e0e0;
  border-radius: 8px;
  word-wrap: break-word;
}
</style>
