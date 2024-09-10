<template>
  <div class="outer-container">
    <!-- Left sidebar for contact list -->
    <div class="left-sidebar">
      <h3>Contacts</h3>
      <input v-model="newContact" placeholder="Add a username" @keyup.enter="addContact" />
      <button @click="addContact">Add Contact</button>

      <!-- List of contacts (newly added ones) -->
      <ul>
        <li v-for="(contact, index) in contacts" :key="index" @click="selectContact(contact)">
          {{ contact }}
        </li>
      </ul>
    </div>

    <!-- Chat window showing open chats (with message input allowed) -->
    <div class="centered-container">
      <div class="chat-window">
        <div class="chat-container" id="chatContainer">
          <div v-if="!selectedContact" class="no-chat">No chat selected</div>
          <div v-if="selectedContact" class="chat-header">
            Chat with {{ selectedContact }}
          </div>

          <!-- Messages sent to the selected contact -->
          <div v-for="(message, index) in messages" :key="index" class="message">
            {{ message }}
          </div>
        </div>
      </div>

      <!-- Message input only if a contact is selected -->
      <div v-if="selectedContact" class="input-container">
        <input
          type="text"
          v-model="messageInput"
          placeholder="Type your message"
          @keyup.enter="sendMessage"
        />
        <button @click="sendMessage">Send</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      newContact: '',
      contacts: [], // Initially empty contact list
      selectedContact: null, // Selected contact for chat
      messageInput: '', // Input field for new message
      messages: [], // Array of messages to be displayed in chat window
    };
  },
  methods: {
    addContact() {
      if (this.newContact) {
        this.contacts.push(this.newContact);
        this.selectedContact = this.newContact; // Automatically select the contact
        this.newContact = ''; // Clear input field
      }
    },
    selectContact(contact) {
      this.selectedContact = contact;
      this.messages = []; // Reset messages when a new contact is selected
    },
    sendMessage() {
      if (this.messageInput.trim() !== "") {
        // Push the message to the messages array
        this.messages.push(`You: ${this.messageInput}`);

        // Clear the input field
        this.messageInput = "";

        // Scroll to the bottom after sending the message
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
/* Overall container with flexbox for chat and contacts */
.outer-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f0f0;
}

/* Left sidebar for contact list */
.left-sidebar {
  width: 200px;
  height: 100%;
  background-color: #fff;
  border-right: 1px solid #ddd;
  padding: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.left-sidebar h3 {
  text-align: center;
}

.left-sidebar input {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  outline: none;
  color: black; /* Input text color */
}

.left-sidebar button {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  background-color: olive;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.left-sidebar ul {
  list-style: none;
  padding: 0;
}

.left-sidebar li {
  padding: 10px;
  background-color: #f0f0f0;
  margin-bottom: 10px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.left-sidebar li:hover {
  background-color: #ddd;
}

/* Chat window styling */
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

.chat-header {
  text-align: center;
  font-weight: bold;
  margin-bottom: 10px;
}

.no-chat {
  text-align: center;
  font-style: italic;
  color: grey;
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
  color: black; /* Input text color */
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
