// ===============================
//  AI Chat - Frontend
// ===============================

// Referencias a elementos del DOM
const chatWindow = document.querySelector('.chat-window');
const messagesContainer = document.getElementById('chat-messages');
const composerForm = chatWindow.querySelector('.composer');
const composerInput = composerForm.querySelector('input');

// Función para enviar mensaje al backend Flask
async function sendMessageToAI(message) {
  try {
    const response = await fetch('/ai', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`Error del servidor: ${response.status}`);
    }

    const data = await response.json();
    return data.reply || '⚠️ No se recibió respuesta.';
  } catch (error) {
    console.error('Error enviando mensaje a la IA:', error);
    return '⚠️ Ocurrió un error al conectar con la IA.';
  }
}

// Función para renderizar un mensaje en la ventana de chat
function renderMessage(text, sender = 'user') {
  const div = document.createElement('div');
  div.className = `message ${sender}`;
  div.textContent = text;
  messagesContainer.appendChild(div);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Manejador del formulario de entrada
composerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const userText = composerInput.value.trim();
  if (!userText) return;

  // Renderiza mensaje del usuario
  renderMessage(userText, 'user');
  composerInput.value = '';

  // Llama al backend y muestra respuesta de IA
  const aiReply = await sendMessageToAI(userText);
  renderMessage(aiReply, 'ai');
});

// Acciones rápidas (botones arriba del chat)
document.querySelectorAll('.chat-quick button').forEach((btn) => {
  btn.addEventListener('click', () => {
    composerInput.value = btn.textContent;
    composerForm.dispatchEvent(new Event('submit'));
  });
});

// Cierra el chat al presionar ESC
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && document.body.classList.contains('chat-open')) {
    document.body.classList.remove('chat-open');
  }
});

