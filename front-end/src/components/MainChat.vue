<template>
  <div class="outer-container">
    <!-- Left sidebar for contact list -->
    <div class="left-sidebar">
      <h3>Contacts</h3>
      <input v-model="newContact" placeholder="Add a username" @keyup.enter="addContact" />
      <button @click="addContact">Add Contact</button>

      <!-- List of contacts -->
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
      newContact: '',       // Input for adding a new contact
      contacts: [],         // List of contacts
      selectedContact: null, // Currently selected contact
      messageInput: '',     // Input field for the message
      messages: {},         // Store messages for each contact
      holdTimeout: null     // Used for long press to delete contact
    };
  },
  computed: {
    sortedContacts() {
      // Sort contacts alphabetically
      return [...this.contacts].sort((a, b) => a.localeCompare(b));
    },
    currentMessages() {
      // Return messages for the currently selected contact
      return this.messages[this.selectedContact] || [];
    }
  },
  methods: {
    async addContact() {
      if (this.newContact) {
        try {
          // Send a request to the backend to check if the contact exists
          const response = await fetch(`/api/check_user/${this.newContact}`);
          if (response.ok) {
            // Contact exists in the database
            this.contacts.push(this.newContact);
            if (!this.messages[this.newContact]) {
              this.messages[this.newContact] = [];  // Initialize message array
            }
            this.selectedContact = this.newContact;  // Automatically select the new contact
            this.newContact = '';  // Clear the input field
          } else {
            // User does not exist in the database
            alert("This user does not exist.");
          }
        } catch (error) {
          console.error("Error checking user:", error);
          alert("An error occurred while checking the user.");
        }
      }
    },
    selectContact(contact) {
      this.selectedContact = contact;
    },
    sendMessage() {
      if (this.messageInput.trim() !== "") {
        if (!this.messages[this.selectedContact]) {
          this.messages[this.selectedContact] = [];
        }
        // Add message to the message list
        this.messages[this.selectedContact].push(`You: ${this.messageInput}`);
        this.messageInput = "";  // Clear input field

        // Scroll to the bottom of the chat window
        this.scrollChatToBottom();
      }
    },
    scrollChatToBottom() {
      const chatContainer = this.$el.querySelector('#chatContainer');
      chatContainer.scrollTop = chatContainer.scrollHeight;
    },
    startHold(contact) {
      // Start tracking the hold time for deleting the contact
      this.holdTimeout = setTimeout(() => {
        if (confirm(`Do you want to delete the contact "${contact}"?`)) {
          this.deleteContact(contact);
        }
      }, 1000); // Hold for 1 second to trigger deletion
    },
    endHold() {
      // Cancel the delete if the hold is less than 1 second
      clearTimeout(this.holdTimeout);
    },
    deleteContact(contact) {
      this.contacts = this.contacts.filter(c => c !== contact);  // Remove contact from list
      if (this.selectedContact === contact) {
        this.selectedContact = null;  // Clear the selected contact if it's deleted
      }
      delete this.messages[contact];  // Remove messages related to the contact
    }
  },
  mounted() {
    // Fetch and store existing contacts and messages from the backend (or local storage) when the page is loaded
    this.loadContacts();
  },
  methods: {
    loadContacts() {
      // Fetch contacts from backend or local storage to persist contacts after login/logout
      const storedContacts = localStorage.getItem("contacts");
      if (storedContacts) {
        this.contacts = JSON.parse(storedContacts);
      }
    },
    saveContacts() {
      // Save contacts to local storage so they persist after login/logout
      localStorage.setItem("contacts", JSON.stringify(this.contacts));
    },
    addContact() {
      if (this.newContact) {
        // Add the contact and save to local storage
        this.contacts.push(this.newContact);
        this.saveContacts();
        this.newContact = '';
      }
    },
    deleteContact(contact) {
      this.contacts = this.contacts.filter(c => c !== contact);
      this.saveContacts();
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
