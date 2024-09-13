<template>
  <div class="outer-container">
    <button @click="logout" class="logout-button">Logout</button>
    <button @click="toggleContacts" class="contacts-button">Contacts</button>
    <button @click="showGroupModal = true" class="new-group-button">New Group</button>

    <!-- Sidebar with contact list for chat -->
    <div v-show="showContacts" class="left-sidebar">
      <h3>Contacts</h3>
      <input v-model="newContact" placeholder="Add a username" @keyup.enter="addContact" />
      <button @click="addContact">Add Contact</button>
      <ul>
        <li
          v-for="(contact, index) in sortedContacts"
          :key="index"
          :class="{ selected: contact === selectedContact }"
        >
          <div @click="selectContact(contact)">
            {{ contact.username }}
          </div>
          <!-- Delete button for each contact -->
          <button @click="deleteContact(contact)" class="delete-button">Delete</button>
        </li>
      </ul>
    </div>

    <!-- Chat container -->
    <div class="centered-container" :class="{ 'no-round': selectedContact || selectedGroup }">
      <div class="chat-window" :class="{ 'no-round': selectedContact || selectedGroup }">
        <div class="chat-container" id="chatContainer">
          <div v-if="!selectedContact && !selectedGroup" class="no-chat">No chat selected</div>
          <div v-if="selectedContact" class="chat-header">
            Chat with {{ selectedContact.username }}
          </div>
          <div v-if="selectedGroup" class="chat-header">
            Chat in Group: {{ selectedGroup.group_name }}
          </div>

          <div v-for="(message, index) in currentMessages" :key="index" class="message">
            {{ message.sender }}: {{ message.content }}
          </div>
        </div>
      </div>

      <div v-if="selectedContact || selectedGroup" class="input-container">
        <input type="text" v-model="messageInput" placeholder="Type your message" @keyup.enter="sendMessage" />
        <button @click="sendMessage" class="send-button">Send</button>
      </div>
    </div>

    <!-- Group Modal -->
    <div v-if="showGroupModal" class="modal">
      <div class="modal-content">
        <h2>Create a New Group</h2>
        <input v-model="newGroupName" placeholder="Enter group name" />

        <!-- Select contacts for the group -->
        <h4>Select Contacts:</h4>
        <ul>
          <li v-for="contact in contacts" :key="contact.id" @click="toggleGroupContactSelection(contact)">
            <span :class="{ 'selected-contact': selectedContactsForGroup.includes(contact) }">
              {{ contact.username }}
            </span>
          </li>
        </ul>

        <button @click="createGroup" class="modal-button">Create Group</button>
        <button @click="showGroupModal = false" class="modal-button cancel">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      newContact: '',
      contacts: [], // To store contacts
      groups: [], // To store created groups
      selectedContactsForGroup: [], // To store selected contacts for the group
      selectedContact: null, // To store the selected contact for chat
      selectedGroup: null, // For group selection
      messageInput: '',
      messages: {}, // Stores messages
      showContacts: false, // Controls sidebar visibility for normal chat
      showGroupModal: false, // Controls group modal visibility
      newGroupName: '', // Stores the new group name
    };
  },
  computed: {
    sortedContacts() {
      return [...this.contacts].sort((a, b) => a.username.localeCompare(b.username));
    },
    currentMessages() {
      if (this.selectedContact) {
        return this.messages[this.selectedContact.username] || [];
      } else if (this.selectedGroup) {
        return this.messages[this.selectedGroup.group_name] || [];
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
        this.fetchContacts();
      }
    },

    // Add contact
    async addContact() {
      const user_id = this.getLoggedInUserId();
      const contact_username = this.newContact;

      if (contact_username) {
        const response = await fetch('/api/add_contact', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({user_id, contact_username}),
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

    // Delete contact
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
    },

    // Select contact for chat
    selectContact(contact) {
      this.selectedContact = contact;
    },

    // Toggle contact selection for group creation
    toggleGroupContactSelection(contact) {
      if (this.selectedContactsForGroup.includes(contact)) {
        this.selectedContactsForGroup = this.selectedContactsForGroup.filter(c => c !== contact);
      } else {
        this.selectedContactsForGroup.push(contact);
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

    async createGroup() {
      if (!this.newGroupName.trim()) {
        alert("Group name is required.");
        return;
      }

      if (this.selectedContactsForGroup.length === 0) {
        alert("Please select at least one contact.");
        return;
      }

      try {
        const response = await fetch('/api/groups', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            group_name: this.newGroupName,
            member_ids: this.selectedContactsForGroup.map(contact => contact.id),
          }),
        });

        if (response.ok) {
          const result = await response.json();
          this.groups.push(result);
          this.showGroupModal = false;
          this.newGroupName = '';
          this.selectedContactsForGroup = [];
        } else {
          const errorData = await response.json();
          alert("Failed to create group: " + errorData.detail);
        }
      } catch (error) {
        console.error("Error creating group:", error);
      }
    },

    async sendMessage() {
      if (this.selectedGroup) {
        await this.sendMessageToGroup();
      } else if (this.selectedContact) {
        await this.sendMessageToContact();
      }
    },

    async sendMessageToContact() {
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
          body: JSON.stringify({sender_id, receiver_id, content}),
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

    async sendMessageToGroup() {
      const sender_id = this.getLoggedInUserId();
      const group_id = this.selectedGroup?.id;
      const content = this.messageInput;

      if (!sender_id || !group_id || !content.trim()) {
        alert("Message or group is missing.");
        return;
      }

      try {
        const response = await fetch(`/api/groups/${group_id}/messages`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({sender_id, group_id, content}),
        });

        if (response.ok) {
          const result = await response.json();
          if (!this.messages[this.selectedGroup.group_name]) {
            this.messages[this.selectedGroup.group_name] = [];
          }
          this.messages[this.selectedGroup.group_name].push({
            sender: 'You',
            content: result.data.content,
            timestamp: result.data.timestamp
          });
          this.messageInput = '';  // Clear the input field
          this.scrollChatToBottom();
        } else {
          const errorData = await response.json();
          alert("Failed to send group message: " + errorData.detail);
        }
      } catch (error) {
        console.error("Error sending group message:", error);
      }
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
.outer-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

/* Sidebar contact list */
.contacts-button,
.new-group-button {
  margin: 10px;
}

/* Chat window layout */
.selected-contact {
  font-weight: bold;
}

.contacts-button {
  background-color: lightblue;
  padding: 10px;
  border-radius: 4px;
}

.new-group-button {
  background-color: lightgreen;
  padding: 10px;
  border-radius: 4px;
}

/* Modal styling */
.modal {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.5);
  height: 100vh;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.modal-button {
  background-color: lightblue;
  padding: 10px;
  border-radius: 4px;
  margin: 10px;
  cursor: pointer;
}

.modal-button.cancel {
  background-color: lightcoral;
}

/* Contact list and chat layout */
.left-sidebar {
  position: absolute;
  top: 200px;
  left: 250px;
  width: 200px;
  background-color: #fff;
  border: 1px solid #ddd;
  padding: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

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
  color: black;
}

.left-sidebar li:hover {
  background-color: #ddd;
}

/* Delete button for each contact */
.delete-button {
  background-color: red;
  color: white;
  border: none;
  padding: 5px;
  border-radius: 4px;
  margin-left: 5px;
  cursor: pointer;
}

/* Chat window without rounded corners when a chat is selected */
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

.centered-container.no-round {
  border-radius: 0px;
}

/* Chat window */
.chat-window {
  display: flex;
  flex-direction: column;
  flex: 1;
  background-color: lightblue;
  border-radius: 30px;
  overflow: hidden;
}

.chat-window.no-round {
  border-radius: 0px;
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
  color: #000;
}

.no-chat {
  text-align: center;
  font-style: italic;
  color: grey;
}

/* Input container and styling */
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

/* Context menu */
.context-menu {
  position: absolute;
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  padding: 5px;
  z-index: 1000;
}
</style>
