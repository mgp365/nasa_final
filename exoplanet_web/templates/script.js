const chatbotToggler = document.querySelector(".chatbot-toggler");
const closeBtn = document.querySelector(".close-btn");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");

let userMessage = null;
const inputInitHeight = chatInput.scrollHeight;
const EXOPLANET_DOCS_URL = "https://exoplanetarchive.ipac.caltech.edu/docs/API_kepcandidate_columns.html"; 
// Configure your Gemini API key below
// WARNING: Exposing API keys in client-side code is insecure. For production,
// proxy requests through a backend service that keeps the key secret.
const GEMINI_API_KEY = "AIzaSyCoHZlTp2uVIxF0hBfE_R1DHou_x9Xx4JY"; // <-- Coloca tu API key aquí
// Intentaremos automáticamente variantes comunes si alguna no está disponible
const GEMINI_MODEL_CANDIDATES = [
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash",
    "gemini-1.5-pro-latest",
    "gemini-1.5-pro"
];

async function listAvailableModels() {
    const apiVersions = ["v1", "v1beta"]; // prefer v1 first
    for (const version of apiVersions) {
        try {
            const url = `https://generativelanguage.googleapis.com/${version}/models?key=${encodeURIComponent(GEMINI_API_KEY)}`;
            const res = await fetch(url);
            if (!res.ok) continue;
            const data = await res.json();
            const models = Array.isArray(data.models) ? data.models : [];
            // Keep only models that support generateContent
            const usable = models.filter(m => Array.isArray(m.supportedGenerationMethods) && m.supportedGenerationMethods.includes("generateContent"));
            if (usable.length) return { version, models: usable };
        } catch (_) {
            // ignore and try next
        }
    }
    return null;
}

const createChatLi = (message, className) => {
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", `${className}`);
    let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
    chatLi.innerHTML = chatContent;
    chatLi.querySelector("p").textContent = message;
    return chatLi;
}

const generateResponse = async (chatElement) => {
    const messageElement = chatElement.querySelector("p");
    const systemInstruction = `Eres un asistente experto en datos de exoplanetas de Kepler. 
        Tu única base de conocimiento es la documentación de la API de Kepler disponible en este enlace: ${EXOPLANET_DOCS_URL}. 
        **Prioriza y utiliza SÓLO la información de esa fuente** para responder a las preguntas del usuario. 
        Si la información solicitada no está en esa documentación, debes responder: "No encuentro esa información específica en la documentación de la API de Kepler que me proporcionaron."`;
    
    // If no API key provided, show guidance
    if (!GEMINI_API_KEY) {
        messageElement.textContent = "Configura tu API key de Gemini en script.js (GEMINI_API_KEY) para obtener respuestas.";
        chatbox.scrollTo(0, chatbox.scrollHeight);
        return;
    }

    // Try a few endpoint/model variations to avoid regional/version mismatches
    const apiVersions = ["v1", "v1beta"]; // prefer v1 first
    let lastError = null;
    const tryCall = async (version, model) => {
        const url = `https://generativelanguage.googleapis.com/${version}/models/${model}:generateContent?key=${encodeURIComponent(GEMINI_API_KEY)}`;
        const bodyPayload = {
            contents: [{ role: "user", parts: [{ text: userMessage }] }],
            config: {
                // Aquí se aplica la instrucción para priorizar la fuente
                systemInstruction: systemInstruction 
            }
        };
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ contents: [{ role: "user", parts: [{ text: userMessage }] }] })
        });
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status} (${version}/${model}): ${errorText}`);
        }
        const data = await response.json();
        return data?.candidates?.[0]?.content?.parts?.[0]?.text || "No se recibió respuesta.";
    };

    // 1) Try our candidate list first
    for (const version of apiVersions) {
        for (const model of GEMINI_MODEL_CANDIDATES) {
            try {
                const text = await tryCall(version, model);
                messageElement.textContent = text;
                chatbox.scrollTo(0, chatbox.scrollHeight);
                return;
            } catch (err) {
                lastError = err;
            }
        }
    }

    // 2) If that fails, list models and try those that support generateContent
    const listed = await listAvailableModels();
    if (listed && Array.isArray(listed.models) && listed.models.length) {
        // Prefer 1.5 family, otherwise take first few
        const preferred = listed.models
            .sort((a, b) => (String(b.name).includes("1.5") ? 1 : 0) - (String(a.name).includes("1.5") ? 1 : 0));
        for (const m of preferred.slice(0, 6)) {
            const modelName = m.name?.split("/").pop(); // models/NAME
            if (!modelName) continue;
            try {
                const text = await tryCall(listed.version, modelName);
                messageElement.textContent = text;
                chatbox.scrollTo(0, chatbox.scrollHeight);
                return;
            } catch (err) {
                lastError = err;
            }
        }
    }

    // If all attempts failed
    messageElement.classList.add("error");
    messageElement.textContent = `Error al consultar Gemini: ${lastError ? lastError.message : "Fallo desconocido"}` +
        "\nSugerencia: verifica en Google AI Studio los modelos disponibles y pega uno exacto en GEMINI_MODEL_CANDIDATES.";

    chatbox.scrollTo(0, chatbox.scrollHeight);
}

const handleChat = () => {
    userMessage = chatInput.value.trim();
    if(!userMessage) return;

    // Clear the input textarea and set its height to default
    chatInput.value = "";
    chatInput.style.height = `${inputInitHeight}px`;

    // Append the user's message to the chatbox
    chatbox.appendChild(createChatLi(userMessage, "outgoing"));
    chatbox.scrollTo(0, chatbox.scrollHeight);

    setTimeout(() => {
        // Display "Thinking..." message while waiting for the response
        const incomingChatLi = createChatLi("Thinking...", "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);
        generateResponse(incomingChatLi);
    }, 600);
}

chatInput.addEventListener("input", () => {
    // Adjust the height of the input textarea based on its content
    chatInput.style.height = `${inputInitHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
    // If Enter key is pressed without Shift key and the window
    // width is greater than 800px, handle the chat
    if(e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleChat();
    }
});

sendChatBtn.addEventListener("click", handleChat);
closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));
