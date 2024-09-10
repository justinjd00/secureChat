<template>
  <div class="outer-container">
    <!-- Left sidebar for contact list -->
    <div class="left-sidebar">
      <h3>Contacts</h3>
      <input v-model="newContact" placeholder="Add a username" @keyup.enter="addContact" />
      <button @click="addContact">Add Contact</button>

      <!-- List of contacts (newly added ones) -->
      <ul>
        <li
          v-for="(contact, index) in sortedContacts"
          :key="index"
          :class="{ selected: contact === selectedContact }"
          @click="selectContact(contact)"
          @mousedown="startHold(contact)"
          @mouseup="endHold"
          @mouseleave="endHold"
        >
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
          <div v-for="(message, index) in currentMessages" :key="index" class="message">
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
      contacts: [], // List of contacts
      selectedContact: null, // Currently selected contact for chat
      messageInput: '', // Input field for new message
      messages: {}, // Object to store messages for each contact
      holdTimeout: null // Used to track long press for deleting a contact
    };
  },
  computed: {
    sortedContacts() {
      // Sort contacts alphabetically
      return [...this.contacts].sort((a, b) => a.localeCompare(b));
    },
    currentMessages() {
      // Return messages for the currently selected contact, or an empty array if no messages exist
      return this.messages[this.selectedContact] || [];
    }
  },
  methods: {
    addContact() {
      if (this.newContact) {
        this.contacts.push(this.newContact);
        if (!this.messages[this.newContact]) {
          // Initialize empty message array for the new contact
          this.messages[this.newContact] = [];
        }
        this.selectedContact = this.newContact; // Automatically select the contact
        this.newContact = ''; // Clear input field
      }
    },
    selectContact(contact) {
      this.selectedContact = contact;
    },
    sendMessage() {
      if (this.messageInput.trim() !== "") {
        // Push the message to the messages object for the selected contact
        if (!this.messages[this.selectedContact]) {
          this.messages[this.selectedContact] = [];
        }
        this.messages[this.selectedContact].push(`You: ${this.messageInput}`);

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
    startHold(contact) {
      // Start tracking hold time for deleting the contact
      this.holdTimeout = setTimeout(() => {
        if (confirm(`Do you want to delete the contact "${contact}"?`)) {
          this.deleteContact(contact);
        }
      }, 1000); // 1 second hold for triggering delete
    },
    endHold() {
      // Clear the timeout if the user releases the mouse before 1 second
      clearTimeout(this.holdTimeout);
    },
    deleteContact(contact) {
      this.contacts = this.contacts.filter(c => c !== contact);
      if (this.selectedContact === contact) {
        this.selectedContact = null; // Clear the selected contact if it's deleted
      }
      delete this.messages[contact]; // Remove the messages for the deleted contact
    }
  }
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
  transition: background-color 0.3s ease, padding-left 0.3s ease;
  color: black; /* Contact text color */
}

.left-sidebar li:hover {
  background-color: #ddd;
}

.left-sidebar li.selected {
  background-color: darkgray; /* Darker background for selected contact */
  padding-left: 10px; /* Move selected contact slightly to the right */
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
