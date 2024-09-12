<template>
  <div class="outer-container">
    <!-- Logout Button at the top right corner -->
    <button @click="logout" class="logout-button">Logout</button>

    <!-- Contacts Button -->
    <button @click="toggleContacts" class="contacts-button">Contacts</button>

    <!-- Sidebar with contact list under the Contacts button -->
    <div v-show="showContacts" class="left-sidebar">
      <h3>Contacts</h3>
      <div class="contact-input">
        <input v-model="newContact" placeholder="Add a username" @keyup.enter="addContact" />
        <!-- Small button for adding contact -->
        <button @click="addContact" class="small-add-button">+</button>
      </div>
      <ul>
        <!-- Displaying the list of contacts -->
        <li
          v-for="(contact, index) in sortedContacts"
          :key="index"
          :class="{ selected: contact === selectedContact }"
          @click="selectContact(contact)"
          @contextmenu.prevent="showDeleteMenu(contact, $event)"
          @mousedown="startPress(contact)"
          @mouseup="clearPress"
        >
          {{ contact.username }}
        </li>
      </ul>
    </div>

    <!-- Chat container without rounded corners when a chat is active -->
    <div class="centered-container" :class="{ 'no-round': selectedContact }">
      <div class="chat-window" :class="{ 'no-round': selectedContact }">
        <div class="chat-container" id="chatContainer">
          <div v-if="!selectedContact" class="no-chat">No chat selected</div>
          <div v-if="selectedContact" class="chat-header">
            Chat with {{ selectedContact.username }}
          </div>

          <div v-for="(message, index) in currentMessages" :key="index" class="message">
            {{ message.sender }}: {{ message.content }}
          </div>
        </div>
      </div>

      <div v-if="selectedContact" class="input-container">
        <input type="text" v-model="messageInput" placeholder="Type your message" @keyup.enter="sendMessage" />
        <button @click="sendMessage" class="send-button">Send</button>
      </div>
    </div>

    <!-- Right-click context menu for delete -->
    <div v-if="showMenu" :style="{ top: menuY + 'px', left: menuX + 'px' }" class="context-menu">
      <button @click="deleteContact(menuContact)">Delete Contact</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      newContact: '',
      contacts: [],
      selectedContact: null,
      messageInput: '',
      messages: {},
      showMenu: false,
      menuX: 0,
      menuY: 0,
      menuContact: null,
      pressTimer: null,
      showContacts: false, // Controls the visibility of the sidebar
    };
  },
  computed: {
    sortedContacts() {
      return [...this.contacts].sort((a, b) => a.username.localeCompare(b.username));
    },
    currentMessages() {
      if (this.selectedContact) {
        return this.messages[this.selectedContact.username] || [];
      }
      return [];
    }
  },
  methods: {
    async logout() {
      localStorage.removeItem('user_id');
      this.$router.push('/');
    },

    toggleContacts() {
      this.showContacts = !this.showContacts;
      if (this.showContacts) {
        this.fetchContacts(); // Fetch contacts when the sidebar is shown
      }
    },

    async deleteContact(contact) {
      const user_id = this.getLoggedInUserId();
      if (!user_id) {
        alert("No user ID found. Please log in again.");
        return;
      }

      try {
        const response = await fetch(`/api/delete_contact/${user_id}/${contact.id}`, {
          method: 'DELETE',
        });

        if (response.ok) {
          alert("Contact deleted successfully");
          this.fetchContacts(); // Refresh the contact list after deletion
        } else {
          alert("Failed to delete contact");
        }
      } catch (error) {
        console.error("Error deleting contact:", error);
      }

      // Hide the context menu after deleting the contact
      this.showMenu = false;
    },

    showDeleteMenu(contact, event) {
      this.menuX = event.clientX;
      this.menuY = event.clientY;
      this.menuContact = contact;
      this.showMenu = true;
    },

    startPress(contact) {
      this.pressTimer = setTimeout(() => {
        this.menuContact = contact;
        this.showMenu = true;
      }, 1000); // Long press time of 1 second
    },

    clearPress() {
      clearTimeout(this.pressTimer); // Cancel the long press if the user lifts the mouse before 1 second
    },

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
          this.fetchContacts();  // Fetch contacts again after adding new one
          this.newContact = '';  // Clear the input field
        } else {
          const errorData = await response.json();
          alert("Failed to add contact: " + errorData.detail);
        }
      }
    },

    async fetchContacts() {
      const user_id = this.getLoggedInUserId();

      try {
        const response = await fetch(`/api/get_contacts/${user_id}`);
        if (response.ok) {
          const data = await response.json();
          this.contacts = data.map(contact => ({
            username: contact.username,
            id: contact.id || "undefined"
          }));
        } else {
          alert("Failed to fetch contacts.");
        }
      } catch (error) {
        console.error("Error fetching contacts:", error);
      }
    },

    async selectContact(contact) {
      if (!contact.id || !contact.username) {
        alert("Invalid contact selected. Contact must have a username and id.");
        return;
      }

      this.selectedContact = contact;

      const user_id = this.getLoggedInUserId();
      try {
        const response = await fetch(`/api/get_messages/${user_id}/${contact.id}`);
        if (response.ok) {
          const data = await response.json();
          this.messages[this.selectedContact.username] = data.messages;
        } else {
          const errorData = await response.json();
          console.error("Error fetching messages:", errorData.detail);
        }
      } catch (error) {
        console.error("Error fetching messages:", error);
      }
    },

    async sendMessage() {
      const sender_id = this.getLoggedInUserId();
      const receiver_id = this.selectedContact?.id;
      const content = this.messageInput;

      if (!sender_id || !receiver_id || !content.trim()) {
        alert("Message or contact is missing.");
        return;
      }

      try {
        const response = await fetch('/api/send_message', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ sender_id, receiver_id, content }),
        });

        if (response.ok) {
          const result = await response.json();
          if (!this.messages[this.selectedContact.username]) {
            this.messages[this.selectedContact.username] = [];
          }
          this.messages[this.selectedContact.username].push({
            sender: 'You',
            content: result.data.content,
            timestamp: result.data.timestamp
          });
          this.messageInput = '';  // Clear the input field
          this.scrollChatToBottom();
        } else {
          const errorData = await response.json();
          alert("Failed to send message: " + errorData.detail);
        }
      } catch (error) {
        console.error("Error sending message:", error);
      }
    },

    scrollChatToBottom() {
      const chatContainer = this.$el.querySelector('#chatContainer');
      chatContainer.scrollTop = chatContainer.scrollHeight;
    },

    getLoggedInUserId() {
      const userId = localStorage.getItem('user_id');
      if (!userId) {
        alert('User not logged in');
        this.$router.push('/');
      }
      return userId;
    }
  },

  mounted() {
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
  position: relative;
}

/* Button for showing contacts */
.contacts-button {
  position: absolute;
  top: 150px;
  left: 250px; /* Move the button more to the left */
  background-color: lightblue;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

/* Logout button at the top right */
.logout-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: lightblue;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

/* Sidebar with contact list directly under the Contacts button */
.left-sidebar {
  position: absolute;
  top: 200px; /* Directly under the Contacts button */
  left: 250px; /* Move the container more to the left */
  width: 200px;
  height: auto;
  background-color: #fff;
  border: 1px solid #ddd;
  padding: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  z-index: 10;
}

/* Input field and add button for contacts */
.contact-input {
  display: flex;
  align-items: center;
}

.contact-input input {
  flex: 1;
  padding: 5px;
  margin-right: 5px;
  border-radius: 4px;
  border: 1px solid #ddd;
  color: black; /* Black text for contact input */
}

.small-add-button {
  background-color: green;
  color: white;
  padding: 5px;
  border: none;
  border-radius: 50%;
  cursor: pointer;
}

/* Contact list styling */
.left-sidebar ul {
  list-style: none;
  padding: 0;
}

.left-sidebar li {
  padding: 8px;
  background-color: #f0f0f0;
  margin-bottom: 8px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s ease;
  color: black; /* Black text for contacts */
}

.left-sidebar li.selected {
  background-color: darkgray;
}

.left-sidebar li:hover {
  background-color: #ddd;
}

/* Chat container without rounded corners when a chat is selected */
.centered-container {
  width: 100%;
  max-width: 450px;
  height: 100%;
  max-height: 800px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background-color: white;
  border-radius: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid black;
}

/* Remove rounded corners when a contact is selected */
.centered-container.no-round {
  border-radius: 0px; /* Remove rounding */
}

/* Chat window styling */
.chat-window {
  display: flex;
  flex-direction: column;
  flex: 1;
  background-color: lightblue;
  border-radius: 30px;
  overflow: hidden;
}

.chat-window.no-round {
  border-radius: 0px; /* Remove rounding of chat window when a contact is selected */
}

.chat-container {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  background-color: lightblue;
}

.chat-header {
  text-align: center;
  font-weight: bold;
  margin-bottom: 10px;
  color: #000; /* Adjusted text color */
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
}

input[type="text"] {
  flex: 1;
  padding: 10px;
  border-radius: 20px;
  border: 1px solid #ddd;
  outline: none;
  color: black;
}

.send-button {
  margin-left: 10px;
  padding: 10px 20px;
  background-color: lightblue;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.send-button:hover {
  background-color: darkolivegreen;
}
</style>
