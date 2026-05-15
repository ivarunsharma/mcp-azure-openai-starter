# MCP Client + Server

A beginner-friendly demo of the **Model Context Protocol (MCP)**. A local Python server exposes tools (calculator + weather), and a client connects Azure OpenAI to those tools so the LLM can decide when and how to call them.

---

## How it works

```
You (terminal)
    │
    ▼
client.py  ──── asks Azure OpenAI ──────────────────► Azure OpenAI
    │                                                       │
    │                                          (decides to call a tool)
    │                                                       │
    ▼                                                       ▼
server.py  ◄──── MCP (stdio) ──── client.py calls the tool back
    │
    ▼
Returns result → client sends result back to Azure OpenAI → final answer
```

1. **client.py** starts `server.py` as a subprocess automatically — you only run the client.
2. The client asks the server: *"what tools do you have?"*
3. The client passes your query + the tool list to Azure OpenAI.
4. If the LLM decides to use a tool, the client calls it on the server and sends the result back to get a final answer.

---

## Tools available (server.py)

| Tool | What it does |
|------|--------------|
| `add(a, b)` | Adds two numbers |
| `multiply(a, b)` | Multiplies two numbers |
| `get_weather(city)` | Gets current weather via OpenWeatherMap |

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create a `.env` file

Place this file one level up (at `lanchainProject/.env`):

```env
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o

weather_api_key=your_openweathermap_key_here
```

> Get a free weather API key at [openweathermap.org](https://openweathermap.org/api)

### 3. Run

```bash
cd MCP
python client.py
```

You do **not** need to run `server.py` manually — the client starts it automatically.

---

## Example session

```
MCP Client ready. Type your query (or 'exit' to quit).

You: What is 15 multiplied by 7?
============================================================
[MCP] Tools available: ['add', 'multiply', 'get_weather']
[User] What is 15 multiplied by 7?
[LLM] Calling tool 'multiply' with args {'a': 15, 'b': 7}
[MCP] Tool result: 105.0

[Assistant] 15 multiplied by 7 is 105.

You: What's the weather in Tokyo?
============================================================
[LLM] Calling tool 'get_weather' with args {'city': 'Tokyo'}
[MCP] Tool result: Tokyo: 22°C, clear sky, humidity 55%

[Assistant] The current weather in Tokyo is 22°C with clear skies and 55% humidity.

You: exit
Goodbye!
```

---

## File structure

```
MCP/
├── client.py        # Connects to Azure OpenAI + MCP server, handles the chat loop
├── server.py        # Defines the tools the LLM can call
├── requirements.txt
└── README.md
```
