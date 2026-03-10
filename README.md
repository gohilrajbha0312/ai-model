<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/Flask-Web%20Framework-black.svg?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/SQLite-Local%20DB-003B57.svg?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Security-Offline%20First-red.svg?style=for-the-badge" alt="Offline First">
  
  <br><br>
  
  <h1>🛡️ CyberSec AI Assistant</h1>
  <p><strong>The Ultimate Secure, Private, Multi-Engine Cybersecurity AI Companion.</strong></p>
  
  <p>
    Designed exclusively for <b>Penetration Testers</b>, <b>Security Researchers</b>, and <b>Cybersecurity Students</b>. Run security tools and analyze vulnerabilities directly through a natural language interface.
  </p>
</div>

<hr>

## 📖 Table of Contents
- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [Installation](#-installation)
- [Usage Guide](#-usage-guide)
- [Built-In Tools](#-built-in-tools)
- [Knowledge Base](#-built-in-knowledge-base)
- [Security & Privacy](#-security--privacy)
- [Disclaimer](#-disclaimer)

---

## 🎯 About the Project

The **CyberSec AI Assistant** is a self-hosted, offline-capable AI dashboard. Instead of relying purely on a single cloud provider, this tool gives you the power to choose your AI engine dynamically. Whether you need the unparalleled reasoning of ChatGPT, the speed of Google Gemini, or the total privacy of a local Llama 3 model via Ollama—you control the intelligence.

Coupled with an integrated toolkit, this assistant doesn't just answer questions; it executes reconnaissance, port scans, and vulnerability lookups directly from the chat interface.

---

## 🌟 Key Features

### 🧠 Dynamic AI Routing
Switch seamlessly between different intelligence engines from the unified Settings dashboard:

| Mode | Privacy Level | Description |
| :--- | :---: | :--- |
| 📴 **Local KB** | 🟢 **Max** | Queries the local JSON knowledge base for instant, completely offline answers. |
| 🦙 **Ollama** | 🟢 **Max** | Runs fully local LLMs (like Llama 3) via your dedicated Ollama instance. |
| 🌐 **ChatGPT** | 🟡 Medium | Connects to OpenAI's `gpt-4o` API for deep reasoning and code generation. |
| 🌐 **Gemini** | 🟡 Medium | Connects to Google's `gemini-1.5-pro` API for rapid threat intelligence analysis. |
| 🔀 **Hybrid** | 🟡 Medium | Aggregates answers from all available models to give you the ultimate response. |

### 🛠️ Hands-on Security Automation
Why alt-tab to a terminal when your AI can run the tools for you? Our `ToolExecutor` understands natural language commands:
*   `run recon on <domain>`
*   `lookup cve <CVE-ID>`
*   `scan ports on <IP/Domain>`
*   `check password <password>`

---

## 🚀 Installation

Setting up the CyberSec AI Assistant is fast and straightforward.

### Prerequisites
- Python 3.10 or higher
- Git
- *(Optional)* Ollama installed locally for offline LLM support

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gohilrajbha0312/ai-model.git
   cd ai-model
   ```

2. **Create a Virtual Environment (Recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Server:**
   ```bash
   python main.py
   ```
   > 💡 *The Flask server will start. Open your browser and navigate to `http://127.0.0.1:5000`.*

---

## 💻 Usage Guide

### 🌐 The Web Dashboard
Navigate to `http://127.0.0.1:5000` to access the application.
- **💬 Chat Panel:** Ask technical questions, request exploit explanations, or trigger tools.
- **🧰 Tools Panel:** A dedicated UI for running specific modules like Port Scanning or Subdomain Enumeration without using chat commands.
- **📋 Activity Logs:** Every query, tool execution, and blocked malicious prompt is recorded in the local SQLite database for auditing.

### ⚙️ Configuring AI Models
To unleash the full power of the assistant:
1. Click the **⚙️ Settings** icon in the top navigation bar.
2. Enter your **OpenAI API Key** or **Google Gemini API Key**.
3. Select your active `AI Mode` from the dropdown.
4. Click **Save Settings**. The AI Router will immediately reload without requiring a server restart.

### ⌨️ CLI Interface
Prefer the terminal? Run the assistant directly from your command line:
```bash
python main.py --mode cli
```
Type `/help` to see available commands, or `/mode hybrid` to switch engines on the fly.

---

## 🧰 Built-In Tools Reference

| Command Pattern | Action | Engine |
| :--- | :--- | :--- |
| `run recon on [Target]` | Full OSINT Pipeline (DNS, WHOIS, Vulns) | `ReconEngine` |
| `scan ports on [Target]` | Multi-threaded TCP Top Ports Scan | `PortScanner` |
| `lookup cve [CVE-ID]` | Fetches NIST/CIRCL Vulnerability Data | `CVELookup` |
| `dns lookup [Target]` | Resolves A, MX, TXT, NS records | `DNSLookup` |
| `whois [Target]` | Retrieves domain registration details | `WhoisLookup` |
| `check password [Secret]` | Calculates Shannon entropy & strength | `PasswordChecker` |

---

## 📚 Built-In Knowledge Base
If you run without API keys, the AI defaults to our strictly-curated offline knowledge base covering critical cybersecurity domains:
- 🛡️ **OWASP Top 10** (XSS, SQLi, CSRF, IDOR, etc.)
- 🎯 **MITRE ATT&CK Framework**
- 🐧 **Linux & Windows Privilege Escalation**
- 🌐 **Advanced Networking Concepts** (TCP/IP, OSI model)
- 🧪 **Penetration Testing Methodology**

---

## 🔒 Security & Privacy
We believe security tools should be secure by design:
*   **Encrypted Storage:** Settings, histories, and API keys are stored locally in `data/assistant.db`.
*   **XSS Protection:** Strict input validation and sanitization using Python `bleach` guarantee that malicious payloads in chat history never execute in the browser.
*   **Query Filtering:** Built-in safeguards reject inherently illegal prompts (e.g., "how do I write a ransomware virus?").

---

## ⚠️ Disclaimer
> **This tool is built strictly for educational, research, and authorized testing purposes only.** 
> You must only use the integrated security tools (Port Scanner, Recon, etc.) against systems, networks, or domains that you own or have explicit, documented permission to test. The developers hold absolutely no responsibility for any misuse, damage, or illegal actions caused by utilizing this software.

---
<div align="center">
  <i>Built with ❤️ for the Cybersecurity Community.</i>
</div>
