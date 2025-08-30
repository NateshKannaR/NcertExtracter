// --- CONFIGURATION ---
// The API endpoint for your backend server.
const API_ENDPOINT = "http://127.0.0.1:8000/api/v1/query";

// --- DOM ELEMENT REFERENCES ---
// Getting references to the HTML elements we'll interact with.
const inputEl = document.getElementById("question");
const messagesEl = document.getElementById("messages");
const sendButton = document.querySelector("button");

// --- CORE FUNCTIONS ---

/**
 * Sends the user's query to the backend and displays the response.
 */
async function sendQuery() {
    const queryText = inputEl.value.trim();
    if (!queryText) return; // Don't send empty messages

    // 1. Display the user's message immediately and clear the input field.
    appendMessage(queryText, "user");
    inputEl.value = "";

    // 2. Disable the form and show a "typing" indicator for better UX.
    setFormDisabled(true);
    const typingIndicator = appendMessage("AI Tutor is typing...", "bot typing");

    try {
        // 3. Make the API call to the backend.
        const response = await fetch(API_ENDPOINT, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ q: queryText })
        });

        // Remove the "typing..." indicator now that we have a response.
        messagesEl.removeChild(typingIndicator);

        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }

        const data = await response.json();

        // 4. Format the response from the backend into a readable string.
        const formattedAnswer = formatApiResponse(data);
        appendMessage(formattedAnswer, "bot");

    } catch (err) {
        // 5. Handle any errors during the fetch.
        console.error("Fetch Error:", err);
        // Ensure the typing indicator is removed even if there's an error.
        if (messagesEl.contains(typingIndicator)) {
            messagesEl.removeChild(typingIndicator);
        }
        appendMessage(`❌ Error: Could not connect to the server. ${err.message}`, "bot");
    } finally {
        // 6. Re-enable the form so the user can send another message.
        setFormDisabled(false);
    }
}

/**
 * Appends a new message to the chat log.
 * @param {string} text - The content of the message.
 * @param {string} className - The CSS class for the message ('user' or 'bot').
 * @returns {HTMLElement} The created message element.
 */
function appendMessage(text, className) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `msg ${className}`;
    msgDiv.textContent = text;
    messagesEl.appendChild(msgDiv);
    // Auto-scroll to the bottom to show the latest message.
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return msgDiv;
}

/**
 * Formats the raw JSON response from the API into a user-friendly string.
 * @param {object} data - The JSON data from the backend.
 * @returns {string} A formatted string for display.
 */
function formatApiResponse(data) {
    if (data.answer && data.answer.evidence && data.answer.evidence.length > 0) {
        // If evidence is found, join the text of each piece of evidence.
        return data.answer.evidence
            .map(item => item.text)
            .join("\n\n---\n\n"); // Use a separator for readability
    }
    // Fallback message if no evidence is found in the response.
    return "I couldn't find a specific answer in the provided documents, but I'm here to help with other questions!";
}

/**
 * Enables or disables the input field and send button.
 * @param {boolean} isDisabled - True to disable, false to enable.
 */
function setFormDisabled(isDisabled) {
    inputEl.disabled = isDisabled;
    sendButton.disabled = isDisabled;
    inputEl.placeholder = isDisabled ? "Waiting for response..." : "Ask anything...";
    inputEl.focus(); // Keep the input field focused
}

// --- EVENT LISTENERS ---
// Set up listeners for the send button click and the 'Enter' key press.
sendButton.addEventListener("click", sendQuery);
inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault(); // Prevents default form submission behavior
        sendQuery();
    }
});

