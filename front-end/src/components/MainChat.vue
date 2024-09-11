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
          {{ contact.username }} <!-- Display contacts by username -->
        </li>
      </ul>
    </div>

    <!-- Chat window showing open chats -->
    <div class="centered-container">
      <div class="chat-window">
        <div class="chat-container" id="chatContainer">
          <div v-if="!selectedContact" class="no-chat">No chat selected</div>
          <div v-if="selectedContact" class="chat-header">
            Chat with {{ selectedContact.username }} <!-- Display chat with selected contact -->
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
      newContact: '',        // Input for adding a new contact
      contacts: [],          // List of contacts fetched from DB
      selectedContact: null,  // Currently selected contact (start as null)
      messageInput: '',      // Input field for the message
      messages: {},          // Store messages for each contact (optional)
      holdTimeout: null      // Used for long press to delete contact
    };
  },
  computed: {
    sortedContacts() {
      // Sort contacts alphabetically by username
      return [...this.contacts].sort((a, b) => a.username.localeCompare(b.username));
    },
    currentMessages() {
      // Return messages for the currently selected contact
      return this.selectedContact ? this.messages[this.selectedContact.username] || [] : [];
    }
  },
  methods: {
    async addContact() {
      const user_id = this.getLoggedInUserId();
      const contact_username = this.newContact;

      if (contact_username) {
        const response = await fetch('/api/add_contact', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ user_id, contact_username }),
        });

        if (response.ok) {
          // Successfully added contact to the database
          this.contacts.push({ username: contact_username });
          this.newContact = '';  // Clear the input field
        } else {
          const errorData = await response.json();
          alert("Failed to add contact: " + errorData.detail);
        }
      }
    },
    selectContact(contact) {
      this.selectedContact = contact; // Make sure selectedContact is the entire contact object
    },
    async fetchContacts() {
      const user_id = this.getLoggedInUserId();
      if (!user_id) {
        alert("No user ID found. Please log in again.");
        this.$router.push('/login');  // Redirect to login if no user_id
        return;
      }

      try {
        const response = await fetch(`/api/get_contacts/${user_id}`);
        if (response.ok) {
          const data = await response.json();
          this.contacts = data.message === "No contacts found" ? [] : data;  // Set contacts or empty array
        } else {
          alert("Failed to fetch contacts.");
        }
      } catch (error) {
        console.error("Error fetching contacts:", error);
      }
    },
    getLoggedInUserId() {
      // Retrieve logged-in user's ID (stored in localStorage)
      const userId = localStorage.getItem('user_id');
      if (!userId) {
        alert("User not logged in");
        this.$router.push('/login');  // Redirect to login if no user_id is found
      }
      return userId;
    }
  },
  mounted() {
    // Fetch contacts from the database when the component is mounted
    this.fetchContacts();
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
  color: black;
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
  color: black;
}

.left-sidebar li:hover {
  background-color: #ddd;
}

.left-sidebar li.selected {
  background-color: darkgray;
  padding-left: 10px;
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
  color: black;
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
