document.addEventListener('DOMContentLoaded', function () {
    const chatBox = document.getElementById('chatBox');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const typingIndicator = document.getElementById('typingIndicator');
    const documentUpload = document.getElementById('documentUpload');
    const fileInfo = document.getElementById('fileInfo');
    let file_text = "";
    let file_name = "";
    let file_type = "";

    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function addMessage(text, isUser, isDocument = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : isDocument ? 'document-message' : 'bot-message'}`;

        let safeText = escapeHtml(text);
        safeText = safeText.replace(/(```(\w*)([\s\S]*?)```|`([^`]*)`)/g,
            (match, p1, p2, p3, p4) => {
                if (p3) {
                    return `<pre class="bg-dark text-light p-2 rounded"><code>${p3}</code></pre>`;
                } else if (p4) {
                    return `<code class="bg-light text-dark p-1 rounded">${p4}</code>`;
                }
                return match;
            });

        safeText += `<span class="message-time">${getCurrentTime()}</span>`;
        messageDiv.innerHTML = safeText;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        addMessage(message, true);
        userInput.value = '';
        resetTextareaHeight();
        typingIndicator.style.display = 'flex';

        try {
            const response = await fetch('http://192.168.9.102:8000/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: message,
                    file_text: file_text,
                    file_name: file_name,
                    file_type: file_type
                }),
                credentials: 'include'
            });
            file_text = "";
            file_name = "";
            file_type = "";
            if (!response.ok) throw new Error('Error en la respuesta');

            const data = await response.json();
            addMessage(data.response, false);

            if (data.sources?.length > 0) {
                addMessage("Fuentes consultadas: " + data.sources.join(", "), false);
            }

        } catch (error) {
            console.error('Error:', error);
            addMessage('Lo siento, hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo.', false);
        } finally {
            typingIndicator.style.display = 'none';
            userInput.focus();
        }
    }

    function resetTextareaHeight() {
        userInput.style.height = 'auto';
    }

    document.getElementById("documentUpload").addEventListener("change", async function(event) {
        let fileInput = event.target.files[0];

        if (!fileInput) {
            fileInfo.innerHTML = '<i class="bi bi-file-earmark file-icon"></i><span>Ningún archivo seleccionado</span>';
            return;
        }

        let formData = new FormData();
        formData.append("file", fileInput);

        fileInfo.innerHTML = `<i class="bi bi-arrow-up-circle file-icon"></i><span>Subiendo: ${fileInput.name}...</span>`;

        try {
            let response = await fetch("http://192.168.9.102:8000/upload_file", {
                method: "POST",
                body: formData
            });

            let result = await response.json();
           
            file_text = result.file_text;
            file_name = result.file_name;
            file_type = result.file_type;

            if (response.ok) {
                fileInfo.innerHTML = `<i class="bi bi-check-circle-fill text-success"></i><span>${fileInput.name} (listo)</span>`;
                addMessage("📄 Archivo cargado correctamente: " + fileInput.name, false, true);
            } else {
                fileInfo.innerHTML = '<i class="bi bi-exclamation-circle-fill text-danger"></i><span>Error al subir</span>';
                addMessage("❌ Error al procesar el archivo: " + result.detail, false);
            }
            
        } catch (error) {
            console.error("Error al subir el archivo:", error);
            fileInfo.innerHTML = '<i class="bi bi-exclamation-circle-fill text-danger"></i><span>Error al subir</span>';
            addMessage("❌ Error de conexión al subir el archivo", false);
        }
    });

    sendButton.addEventListener('click', sendMessage);
    
    userInput.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            sendMessage();
        }
        else if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        
        const maxHeight = parseInt(getComputedStyle(this).lineHeight) * 5;
        if (this.scrollHeight > maxHeight) {
            this.style.overflowY = 'auto';
        } else {
            this.style.overflowY = 'hidden';
        }
    });

    userInput.addEventListener('focus', function() {
        document.querySelector('.input-group').style.boxShadow = '0 0 0 2px rgba(96, 165, 250, 0.5)';
    });

    userInput.addEventListener('blur', function() {
        document.querySelector('.input-group').style.boxShadow = 'var(--shadow-md)';
    });

    userInput.focus();
});