# app.py — Streamlit frontend: GIGGSO-branded real-time chat UI with Chatbot Mike
import streamlit as st
from pathlib import Path
import sys

# Ensure project root is on path for config and bots
sys.path.insert(0, str(Path(__file__).resolve().parent))
import config
from bots import get_bot, get_available_bots
from voice_utils import listen_and_transcribe, text_to_speech_audio

# Page config: professional title and layout
st.set_page_config(
    page_title="Chat with Mike | GIGGSO",
    page_icon="🦾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Resolve logo path (GIGGSO shield + orca); optional base64 for HTML header
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
LOGO_PATH = ASSETS_DIR / "giggso_logo.png"

def _logo_base64() -> str:
    """Return base64 data URL for logo so we can embed in HTML."""
    if not LOGO_PATH.exists():
        return ""
    import base64
    data = LOGO_PATH.read_bytes()
    return f"data:image/png;base64,{base64.b64encode(data).decode()}"

# ----- Rich HTML/CSS: real-time chatbot + GIGGSO branding -----
CUSTOM_CSS = """
<style>
  /* GIGGSO theme: blues and clean surfaces */
  :root {
    --giggso-primary: #0066cc;
    --giggso-primary-dark: #004c99;
    --giggso-accent: #3385d6;
    --giggso-bg: #f0f4f8;
    --giggso-card: #ffffff;
    --giggso-border: #e2e8f0;
    --giggso-text: #1a202c;
    --giggso-muted: #4a5568;
    --giggso-user-bubble: #0066cc;
    --giggso-mike-bubble: #e8f0fa;
    --giggso-shadow: 0 2px 8px rgba(0,102,204,0.08);
    --giggso-shadow-hover: 0 4px 16px rgba(0,102,204,0.12);
  }
  /* Reduce default Streamlit padding for full-bleed chat feel */
  .block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 900px;
    margin-left: auto;
    margin-right: auto;
  }
  /* Header strip: logo + title + tagline */
  .giggso-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 0 1.25rem 0;
    margin-bottom: 1rem;
    border-bottom: 2px solid var(--giggso-border);
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 12px;
    padding-left: 1.25rem;
    padding-right: 1.25rem;
    box-shadow: var(--giggso-shadow);
  }
  .giggso-header-logo {
    flex-shrink: 0;
  }
  .giggso-header-logo img {
    height: 52px;
    width: auto;
    object-fit: contain;
    display: block;
  }
  .giggso-header-text {
    flex: 1;
    min-width: 0;
  }
  .giggso-title {
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--giggso-primary-dark);
    margin: 0;
    letter-spacing: -0.02em;
  }
  .giggso-tagline {
    font-size: 0.8rem;
    color: var(--giggso-muted);
    margin: 0.2rem 0 0 0;
    font-weight: 500;
  }
  .giggso-mike-badge {
    background: linear-gradient(135deg, var(--giggso-primary) 0%, var(--giggso-accent) 100%);
    color: white;
    padding: 0.35rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    white-space: nowrap;
  }
  /* Tabs: upload / paste — card style */
  .stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: var(--giggso-bg);
    padding: 6px;
    border-radius: 10px;
    margin-bottom: 0.5rem;
  }
  .stTabs [data-baseweb="tab"] {
    padding: 10px 18px;
    border-radius: 8px;
    background: transparent;
    color: var(--giggso-muted);
    font-weight: 500;
    transition: all 0.2s ease;
  }
  .stTabs [data-baseweb="tab"]:hover {
    color: var(--giggso-primary);
    background: rgba(0,102,204,0.06);
  }
  .stTabs [aria-selected="true"] {
    background: var(--giggso-primary) !important;
    color: white !important;
  }
  /* Log preview: terminal-style */
  .log-preview {
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 0.78rem;
    line-height: 1.45;
    background: #1a202c;
    color: #e2e8f0;
    padding: 14px 16px;
    border-radius: 10px;
    max-height: 180px;
    overflow-y: auto;
    border-left: 4px solid var(--giggso-primary);
    box-shadow: var(--giggso-shadow);
  }
  .log-preview::-webkit-scrollbar {
    width: 8px;
  }
  .log-preview::-webkit-scrollbar-thumb {
    background: var(--giggso-primary);
    border-radius: 4px;
  }
  /* Chat message bubbles: real-time look with subtle animation */
  [data-testid="stChatMessage"] {
    padding: 10px 0;
    margin-bottom: 4px;
    animation: messageIn 0.3s ease;
  }
  @keyframes messageIn {
    from {
      opacity: 0;
      transform: translateY(8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  [data-testid="stChatMessage"] div[data-testid="stMarkdown"] {
    padding: 12px 16px;
    border-radius: 16px;
    box-shadow: var(--giggso-shadow);
    background: var(--giggso-mike-bubble);
    border: 1px solid var(--giggso-border);
  }
  /* Chat input area: modern bar */
  .stChatInput {
    padding: 1rem 0 !important;
  }
  .stChatInput input {
    border-radius: 24px !important;
    border: 2px solid var(--giggso-border) !important;
    padding: 12px 20px !important;
    font-size: 0.95rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
  }
  .stChatInput input:focus {
    border-color: var(--giggso-primary) !important;
    box-shadow: 0 0 0 3px rgba(0,102,204,0.15) !important;
  }
  /* Typing indicator (when spinner is shown) */
  .voice-hint {
    font-size: 0.82rem;
    color: var(--giggso-muted);
    margin-top: 6px;
  }
  /* Sidebar: Mike branding */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8fafc 0%, #f0f4f8 100%);
    border-right: 1px solid var(--giggso-border);
  }
  [data-testid="stSidebar"] .stMarkdown {
    color: var(--giggso-muted);
  }
  /* Hide Streamlit footer for cleaner look */
  footer { visibility: hidden; }
  /* Section divider */
  .chat-section-label {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--giggso-primary-dark);
    margin: 1rem 0 0.5rem 0;
    padding-bottom: 0.25rem;
    border-bottom: 1px solid var(--giggso-border);
  }
  /* Status pill in sidebar */
  .status-pill {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #22c55e;
    margin-right: 6px;
    animation: pulse 2s infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Session state
if "log_content" not in st.session_state:
    st.session_state.log_content = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "input_source_label" not in st.session_state:
    st.session_state.input_source_label = "None (paste or upload below)"

# ----- Header: GIGGSO logo + Chat with Mike + tagline (single strip) -----
logo_data = _logo_base64()
logo_img = f'<img src="{logo_data}" alt="GIGGSO" />' if logo_data else '<span class="giggso-title">GIGGSO</span>'
st.markdown(
    f'<div class="giggso-header">'
    f'  <div class="giggso-header-logo">{logo_img}</div>'
    f'  <div class="giggso-header-text">'
    f'    <p class="giggso-title">Chat with Mike</p>'
    f'    <p class="giggso-tagline">Govern. Secure. Orchestrate. — Incident Knowledge Assistant</p>'
    f'  </div>'
    f'  <div class="giggso-mike-badge">🦾 Mike</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ----- Context: Upload + Paste -----
st.markdown('<p class="chat-section-label">📎 Add incident context</p>', unsafe_allow_html=True)
tab_upload, tab_paste = st.tabs(["📤 Upload log file", "📋 Paste log text"])

with tab_upload:
    uploaded = st.file_uploader(
        "Upload a log file (e.g. .log, .txt)",
        type=["log", "txt", "out", "err"],
        help="Upload to set or replace the current incident context.",
    )
    if uploaded is not None:
        raw = uploaded.read()
        try:
            text = raw.decode("utf-8", errors="replace")
        except Exception:
            text = raw.decode("latin-1", errors="replace")
        st.session_state.log_content = text
        st.session_state.input_source_label = f"File: {uploaded.name}"
        st.success(f"Loaded **{uploaded.name}**. You can now chat or upload a different file.")

with tab_paste:
    pasted = st.text_area(
        "Paste log / incident description",
        height=200,
        placeholder="Paste your error log or incident text here, then click 'Use pasted text as source'.",
        key="pasted_log",
    )
    if st.button("Use pasted text as source"):
        st.session_state.log_content = pasted or ""
        st.session_state.input_source_label = "Pasted text"
        st.rerun()

# Current source and log preview
st.markdown("**Current data source:** " + st.session_state.input_source_label)
if st.session_state.log_content:
    preview = st.session_state.log_content[:2000]
    if len(st.session_state.log_content) > 2000:
        preview += "\n... (truncated)"
    st.markdown(f'<div class="log-preview">{preview}</div>', unsafe_allow_html=True)
else:
    st.info("Upload a file or paste log text above to provide context for Mike.")

# ----- Sidebar: Mike & session -----
with st.sidebar:
    st.markdown("### 🦾 Chatbot Mike")
    st.caption("Professional incident assistant powered by GIGGSO")
    st.markdown('<span class="status-pill"></span> **Online**', unsafe_allow_html=True)
    st.markdown("---")
    multi_bot = getattr(config, "MULTI_BOT_ENABLED", False)
    try:
        if multi_bot:
            available = get_available_bots()
            bot = None
            st.caption(f"**Multi-bot mode:** {len(available)} bot(s)")
            for name, _ in available:
                st.caption(f"  • {name}")
        else:
            bot = get_bot()
            st.caption(f"**Provider:** {bot.name}")
    except Exception as e:
        st.error(str(e))
        bot = None
    st.markdown("---")
    st.markdown("### Session")
    if st.button("Clear chat and log"):
        st.session_state.chat_history = []
        st.session_state.log_content = ""
        st.session_state.input_source_label = "None"
        st.rerun()
    st.markdown("---")
    st.markdown("### 🎤 Voice")
    if st.button("Voice input", help="Record from microphone (10 s)."):
        with st.spinner("Listening..."):
            text, err = listen_and_transcribe()
        if err:
            st.error(err)
        else:
            st.session_state.voice_result = text
            st.rerun()

# ----- Chat section: real-time with Mike -----
st.markdown('<p class="chat-section-label">💬 Chat with Mike</p>', unsafe_allow_html=True)

# When no bot is configured (e.g. fresh deploy), show how to enable a free backend
if not multi_bot and bot is None:
    st.info(
        "**No backend configured.** To chat with Mike, set a free LLM backend: in **Streamlit Cloud** or **Hugging Face** use Secrets; set `BOT_PROVIDER=openai_compatible`, `OPENAI_COMPATIBLE_URL` and `OPENAI_COMPATIBLE_API_KEY` (e.g. [Groq](https://console.groq.com) or [OpenRouter](https://openrouter.ai) free tier). See **DEPLOYMENT.md** in the repo for step-by-step instructions."
    )

voice_prefill = ""
if st.session_state.get("voice_result"):
    voice_prefill = st.session_state.voice_result
    if st.button("Send voice as message"):
        st.session_state.pending_user_message = voice_prefill
        st.session_state.voice_result = None
        st.rerun()

user_msg = st.session_state.pop("pending_user_message", None) or st.chat_input("Ask Mike about the incident or request fixes...")
if voice_prefill and not user_msg:
    st.info("Transcribed: **" + voice_prefill + "** — click 'Send voice as message' to send.")

# Render chat history: user vs Mike (assistant)
for msg in st.session_state.chat_history:
    if msg["role"] == "assistant":
        with st.chat_message("Mike", avatar="🦾"):
            st.markdown(msg["content"])
            if msg.get("audio_bytes"):
                st.audio(msg["audio_bytes"], format="audio/mp3")
    else:
        with st.chat_message("user"):
            st.markdown(msg["content"])
            if msg.get("audio_bytes"):
                st.audio(msg["audio_bytes"], format="audio/mp3")

# Send new message
if user_msg and ((multi_bot and len(get_available_bots()) > 0) or (not multi_bot and bot)):
    st.session_state.chat_history.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)

    if multi_bot:
        available = get_available_bots()
        with st.chat_message("Mike", avatar="🦾"):
            all_replies: list[tuple[str, str]] = []
            for name, provider in available:
                with st.spinner(f"Mike is asking {name}..."):
                    try:
                        reply = provider.chat(user_msg, context=st.session_state.log_content)
                        all_replies.append((name, reply))
                    except Exception as e:
                        all_replies.append((name, f"Error: {e}"))
            for name, reply in all_replies:
                with st.expander(f"**{name}**", expanded=True):
                    st.markdown(reply)
            first_reply = all_replies[0][1] if all_replies else ""
            audio_bytes = text_to_speech_audio(first_reply) if first_reply else None
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "\n\n---\n\n".join(f"**{n}:**\n{r}" for n, r in all_replies),
                "audio_bytes": audio_bytes,
            })
    else:
        with st.chat_message("Mike", avatar="🦾"):
            with st.spinner("Mike is typing..."):
                reply = bot.chat(user_msg, context=st.session_state.log_content)
            st.markdown(reply)
            audio_bytes = text_to_speech_audio(reply)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": reply,
                "audio_bytes": audio_bytes,
            })

st.markdown(
    '<p class="voice-hint">Tip: Use "Voice input" in the sidebar for hands-free questions.</p>',
    unsafe_allow_html=True,
)
