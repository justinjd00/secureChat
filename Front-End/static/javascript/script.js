function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const messageText = messageInput.value.trim();

    if (messageText !== "") {


        //new message
        const newMessage = document.createElement('div');
        newMessage.classList.add('message', 'sent');
        newMessage.textContent = `You: ${messageText}`;

        //from input tp container
        const chatContainer = document.getElementById('chatContainer');
        chatContainer.appendChild(newMessage);

        // simple scroll the chat
        chatContainer.scrollTop = chatContainer.scrollHeight;

        //new delete after new message
        messageInput.value = "";
    }
}
