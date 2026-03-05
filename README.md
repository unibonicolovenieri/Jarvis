# J.A.R.V.I.S.
**Just A Rather Very Intelligent System** — a terminal-based AI assistant
inspired by Tony Stark's JARVIS, powered by OpenAI (or any compatible local
model via Ollama).

---

## Features

- 🤖 Conversational AI persona — JARVIS speaks with refined British diction and
  addresses you as "Sir" or "Ma'am"
- 💬 Full conversation history so context is preserved across turns
- 🎨 Rich, colourful terminal UI (panels, styled prompts, timestamps)
- 🔌 Works with OpenAI cloud models **or** local models (Ollama, LM Studio, etc.)
- 🪟 Cross-platform — runs on Windows, macOS, and Linux

---

## Requirements

- Python 3.8 or newer
- An [OpenAI API key](https://platform.openai.com/api-keys) **or** a local
  [Ollama](https://ollama.com) instance

---

## Quick Start (Windows)

### 1 — Install Python (if not already installed)

Download and install Python from <https://python.org/downloads>.  
During installation, check **"Add Python to PATH"**.

### 2 — Clone the repository

```cmd
git clone https://github.com/unibonicolovenieri/Jarvis.git
cd Jarvis
```

### 3 — Install dependencies

```cmd
pip install -r requirements.txt
```

### 4 — Set your API key

Copy the example environment file and add your OpenAI API key:

```cmd
copy .env.example .env
```

Open `.env` in Notepad (or any editor) and set:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

### 5 — Run JARVIS

```cmd
python jarvis.py
```

You should see the JARVIS banner and can start chatting immediately.

---

## Usage

Type any message and press **Enter** to talk to JARVIS.

| Command     | Description                                     |
|-------------|-------------------------------------------------|
| `help`      | Show available commands                         |
| `clear`     | Clear conversation history (start fresh)        |
| `history`   | Print the current conversation transcript       |
| `exit`      | Exit JARVIS (also accepts `quit` or `bye`)      |

---

## Using a Local Model (Ollama)

No OpenAI account? Run JARVIS entirely on your machine:

1. Install [Ollama](https://ollama.com) and pull a model, e.g.:
   ```cmd
   ollama pull llama3
   ```
2. In your `.env` file set:
   ```
   OPENAI_BASE_URL=http://localhost:11434/v1
   JARVIS_MODEL=llama3
   OPENAI_API_KEY=ollama
   ```
3. Start JARVIS normally:
   ```cmd
   python jarvis.py
   ```

---

## Configuration

All settings are read from environment variables (`.env` file or system
environment).

| Variable          | Default        | Description                                     |
|-------------------|----------------|-------------------------------------------------|
| `OPENAI_API_KEY`  | *(required)*   | Your OpenAI API key                             |
| `JARVIS_MODEL`    | `gpt-4o-mini`  | Model name to use                               |
| `OPENAI_BASE_URL` | *(unset)*      | Custom API base URL (e.g. Ollama endpoint)      |

---

## Project Structure

```
Jarvis/
├── jarvis.py        # Main conversational agent
├── requirements.txt # Python dependencies
├── .env.example     # Environment variable template
└── README.md        # This file
```
