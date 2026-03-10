<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Flask-Web%20Framework-lightgrey.svg" alt="Flask">
  <img src="https://img.shields.io/badge/SQLite-Local%20DB-green.svg" alt="SQLite">
  <img src="https://img.shields.io/badge/Security-Offline%20First-red.svg" alt="Offline First">
  
  <h1>🛡️ CyberSec AI Assistant</h1>
  <p><strong>Secure, Private, Multi-Engine Cybersecurity AI Tool</strong></p>
  
  <p>
    An intelligent, locally-hosted assistant designed for <b>penetration testers</b>, <b>security researchers</b>, and <b>cybersecurity students</b>.
  </p>
</div>

<hr>

The **CyberSec AI Assistant** is a comprehensive artificial intelligence tool that combines local knowledge bases, external AI models (ChatGPT, Gemini, Ollama), and automated security scripts into one seamless, privacy-focused dashboard.

## 🌟 Key Features

### 🧠 Multi-AI Engine Support
Switch between different intelligence providers instantly from the Settings dashboard:

| Mode | Description |
| :--- | :--- |
| 📴 **Local Offline** | Query the offline knowledge base for instant answers without sending data over the internet. |
| 🌐 **ChatGPT & Gemini** | Connect API keys to query OpenAI's `gpt-4o` or Google's `gemini-1.5-pro` natively. |
| 🦙 **Local LLMs (Ollama)** | Run Llama 3 or other models entirely offline via your local Ollama instance. |
| 🔀 **Hybrid AI Router** | Let the system query all available AIs and automatically return the most detailed, high-quality response. |

### 🛠️ Integrated Security Tools
Execute tools directly from the AI chat using natural language:

*   🔌 `scan ports on <IP/Domain>` — Runs a multi-threaded TCP port scan on common ports.
*   🕵️‍♂️ `run recon on <Domain>` — Automates DNS, WHOIS, Subdomain Enumeration, and Vulnerability checking in one command.
*   🐛 `lookup cve <CVE-ID>` — Fetches real-time vulnerability data from the CIRCL database.
*   🔐 `check password <Password>` — Calculates Shannon entropy and grades password strength.
*   📝 `whois <Domain>` — Retrieves WHOIS registrar and registration data.
*   🌍 `dns lookup <Domain>` — Resolves A, MX, TXT, and NS records.

### 🔒 Privacy & Security Focus
*   **100% Local Hosting:** The Flask dashboard runs over localhost `127.0.0.1`.
*   **Encrypted Local DB:** All chat histories, tool outputs, and settings are stored locally in an encrypted SQLite database.
*   **XSS Protection:** Strict input validation and HTML sanitization (Bleach) ensure malicious payloads cannot be executed in the UI.

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gohilrajbha0312/ai-model.git
   cd ai-model
   ```

2. **Set up a Virtual Environment (Recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   ```bash
   python main.py
   ```
   > 💡 *The server will automatically start on `http://127.0.0.1:5000` or `http://0.0.0.0:5000` (depending on your network configuration).*

---

## 💻 Usage

### 🌐 Web Dashboard
Open your browser and navigate to `http://127.0.0.1:5000`. You will see three main sections:
1. **💬 Chat:** Ask questions or trigger tools naturally.
2. **🧰 Tools:** Execute specific tools (Port Scanner, Subdomain Enum, etc.) from a dedicated form interface.
3. **📋 Logs:** View an audit trail of all AI queries, tools executed, and commands blocked by the security filter.

### ⚙️ Configuration (Settings)
To use external AI models:
1. Click the **⚙️ Settings** button in the Web UI.
2. Enter your OpenAI or Google Gemini API keys.
3. Choose your preferred AI Mode (`local`, `chatgpt`, `gemini`, `ollama`, or `hybrid`).
4. Click **Save Settings**.

### ⌨️ CLI Mode
You can also run the assistant directly in your terminal for a lightweight experience:
```bash
python main.py --mode cli
```

---

## 📚 Built-In Knowledge Base
The offline AI defaults explicitly to an extensive knowledge base covering:
- ✅ OWASP Top 10 Vulnerabilities (XSS, SQLi, CSRF, etc.)
- ✅ MITRE ATT&CK Framework
- ✅ Linux & Windows Privilege Escalation / Hardening
- ✅ Networking Concepts (TCP/IP, OSI model)
- ✅ Penetration Testing Workflows

---

## ⚠️ Disclaimer
> **This tool is for educational and authorized testing purposes only.** Do not use the integrated security tools against targets, networks, or domains you do not own or have explicit permission to test. The developers are not responsible for any misuse.
