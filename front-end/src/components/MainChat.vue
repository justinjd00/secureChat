<template>
  <div class="outer-container">
    <button @click="logout" class="logout-button">Logout</button>
    <button @click="toggleContacts" class="contacts-button">Contacts</button>
    <button @click="toggleGroups" class="groups-button">Groups</button>

    <!-- Sidebar with contact list for chat -->
    <div v-show="showContacts" class="contact-sidebar">
      <h3>Contacts</h3>
      <input v-model="newContact" placeholder="Add a username" @keyup.enter="addContact" />
      <button @click="addContact">Add Contact</button>
      <ul class="contacts-list">
        <li
          v-for="(contact, index) in sortedContacts"
          :key="index"
          :class="{ selected: contact === selectedContact }"
        >
          <div class="contact-item" @click="selectContact(contact)">
            {{ contact.username }}
            <button @click.stop="deleteContact(contact)" class="delete-button">✕</button>
          </div>
        </li>
      </ul>
    </div>

    <!-- Sidebar for groups -->
    <div v-show="showGroups" class="group-sidebar">
      <h3>Groups</h3>
      <button @click="showGroupModal = true">New Group</button>
      <ul class="groups-list">
        <li v-for="(group, index) in groups" :key="index" @click="selectGroup(group)">
          {{ group.group_name }}
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
    <h4>Select Contacts:</h4>
    <ul class="contacts-list">
      <li v-for="contact in contacts" :key="contact.id" @click="toggleGroupContactSelection(contact)">
        <span :class="{ 'selected-group-contact': selectedContactsForGroup.includes(contact) }">
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
import {id} from "vuetify/locale";

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
      showContacts: false, // Controls sidebar visibility for contacts
      showGroups: false, // Controls sidebar visibility for groups
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

    toggleGroups() {
      this.showGroups = !this.showGroups;
      if (this.showGroups) {
        this.fetchGroups();
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
      this.fetchMessagesForContact(contact);
    },

    // Select group for chat
    selectGroup(group) {
      this.selectedGroup = group;
    },

    // Toggle contact selection for group creation
    toggleGroupContactSelection(contact) {
  if (this.selectedContactsForGroup.includes(contact)) {
    this.selectedContactsForGroup = this.selectedContactsForGroup.filter(c => c !== contact);
  } else {
    this.selectedContactsForGroup.push(contact);
  }
}
,

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

    async fetchGroups() {
      const user_id = this.getLoggedInUserId();
      try {
        const response = await fetch(`/api/get_groups/${user_id}`);
        if (response.ok) {
          const data = await response.json();
          this.groups = data;
        } else {
          alert("Failed to fetch groups.");
        }
      } catch (error) {
        console.error("Error fetching groups:", error);
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
    // Neue Methode zum Abrufen der Nachrichten
async fetchMessagesForContact(contact) {
  const user_id = this.getLoggedInUserId();
  const contact_id = contact?.id;

  if (!user_id || !contact_id) {
    console.error("User ID or Contact ID is missing.");
    return; // Beende die Funktion, wenn eine der IDs fehlt
  }

  try {
    const response = await fetch(`/api/get_messages/${user_id}/${contact_id}`);
    if (response.ok) {
      const result = await response.json();
      this.messages[contact.username] = result.messages;
      this.scrollChatToBottom();
    } else {
      console.error("Failed to fetch messages:", response.statusText);
    }
  } catch (error) {
    console.error("Error fetching messages:", error);
  }
}
,



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
          body: JSON.stringify({ sender_id, group_id, content }),
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
    this.fetchMessagesForContact(id);
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

/* Sidebar contact list
.contacts-button,
.groups-button {
  margin: 100px;
}
*/
.contact-sidebar {
  position: absolute;
  top: 550px;
  left: 50px;
  width: 150px;
  height: 400px;
  background-color: #fff;
  border: 1px solid #ddd;
  padding: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  overflow-y: auto; /* Added scroll function */
}


.contacts-list {
  list-style: none;
  padding: 0;
}

.contact-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logout-button {
  background-color: lightcoral;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  border: none;
  font-size: 14px;
  position: absolute;  /* Positionierung */
  top: 20px;           /* Abstand vom oberen Rand */
  left: 20px;          /* Abstand vom linken Rand */
}

.contact-sidebar li {
  padding: 8px;
  background-color: #f0f0f0;
  margin-bottom: 8px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s ease;
  color: black;
}

.contact-sidebar li:hover {
  background-color: #ddd;
}
.contact-sidebar input {
  color: black; /* Set the input text color to black */
}
/* Right Sidebar for Groups */
.group-sidebar {
  position: absolute;
  top: 550px;
  left: 250px; /* Position it on the right side */
  width: 150px;
  height: 400px;
  background-color: #fff;
  border: 1px solid #ddd;
  padding: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  overflow-y: auto; /* Added scroll function */
}

.groups-list {
  list-style: none;
  padding: 0;
}

.group-sidebar li {
  padding: 8px;
  background-color: #f0f0f0;
  margin-bottom: 8px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s ease;
  color: black;
}

.group-sidebar li:hover {
  background-color: #ddd;
}

.group-sidebar button {
  background-color: lightgreen;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 5px;
  cursor: pointer;
}


/* Delete button for each contact */
.delete-button {
  background-color: red;
  color: white;
  border: none;
  padding: 2px 5px;
  border-radius: 4px;
  cursor: pointer;
}

.selected-contact {
  background-color: darkgrey; /* Ausgewählter Kontakt in dunklem Grau */
  color: white; /* Schriftfarbe für ausgewählte Kontakte auf Weiß */
}

/* Kontakt-Selektionsstil in der Gruppenansicht */
.selected-group-contact {
  background-color: darkgrey; /* Ausgewählter Kontakt in der Gruppenansicht */
  color: white; /* Schriftfarbe für ausgewählte Kontakte in der Gruppenansicht */
}

.contacts-button {
  background-color: lightblue;
  padding: 10px;
  border-radius: 4px;
  position: absolute;
  top: 500px; /* Abstand vom oberen Rand */
  left: 100px; /* Abstand vom linken Rand */
  cursor: pointer;
}

.groups-button {
  background-color: lightblue;
  padding: 10px;
  border-radius: 2px;
  position: absolute;
  top: 500px; /* Abstand vom oberen Rand */
  left: 300px; /* Abstand vom linken Rand, gleiche Linie wie Contacts-Button */
  cursor: pointer;
}

.contact-sidebar, .group-sidebar, .modal-content {
  color: black; /* Textfarbe in den Kästen auf Schwarz setzen */
}

.contacts-list li, .groups-list li {
  cursor: pointer;
  padding: 8px;
  background-color: lightgrey; /* Hellgrau für nicht ausgewählte Kontakte */
  margin-bottom: 8px;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

/* Hover-Effekt für Kontakte und Gruppen */
.contacts-list li:hover, .groups-list li:hover {
  background-color: darkgrey; /* Dunkleres Grau, wenn der Mauszeiger darüber ist */
}


.modal {
  position: fixed;
  top: 400px;
  right: -100px;
  transform: translate(-50%, -50%);
  background-color: white;
  border-radius: 10px;
  z-index: 1000;
  width: 300px; /* Gesamte Breite des Modals */
  height: auto; /* Höhe passt sich automatisch dem Inhalt an */
  padding: 10px; /* Kleinere Innenabstände */
}
.modal-content {
  padding: 10px; /* Verringert den inneren Abstand (padding) des gesamten Modals */
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  width: 300px; /* Breite des Modals */
  height: auto; /* Höhe automatisch, damit sie sich dem Inhalt anpasst */
}

.modal input {
  margin-top: 5px;
  background-color: black;/* Verkleinerung des oberen Abstands zum Eingabefeld */
  padding: 5px; /* Kleinere Polsterung des Eingabefelds */
  width: 100%; /* Breite des Eingabefelds */
}

.modal-button {
  background-color: lightblue;
  padding: 8px 12px;
  border-radius: 4px;
  margin: 10px;
  cursor: pointer;
}

.modal-button.cancel {
  background-color: lightcoral;
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
</style>
