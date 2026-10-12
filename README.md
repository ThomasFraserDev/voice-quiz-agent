# Voice Quiz Agent

[![Python](https://img.shields.io/badge/Python-3.10--3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LiveKit Agents](https://img.shields.io/badge/LiveKit_Agents-1.8-111827?style=for-the-badge)](https://docs.livekit.io/agents/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](./LICENSE)

## Description

This project is a voice-based quiz agent built with LiveKit Agents for Python. It asks questions from a validated JSON set of questions, listens to spoken answers, checks them against accepted answers, explains the result, and can offer summaries of the user's score.

The agent uses LiveKit Inference for:

- **LLM:** Google Gemma 4 31B IT
- **Speech-to-text:** AssemblyAI Universal-3-6-Pro
- **Text-to-speech:** Fish Audio S2.1 Pro
- **Voice interaction:** LiveKit turn detection and adaptive interruption handling

Quiz state and answer checking are implemented locally in [`agent/src/quiz_engine.py`](./agent/src/quiz_engine.py), and questions are stored in [`agent/src/questions.json`](./agent/src/questions.json). Answers must currently match one of the predefined accepted answers. The plan is to improve answer evaluation so the agent can recognise correct responses even when they are worded differently, while still checking answers against the expected answer and its meaning to avoid incorrectly marking responses as correct.

Questions are currently loaded from a local JSON file when the agent starts. Future development will allow users to upload their own question sets, validate them, and start quizzes without manually editing the JSON file. Additional planned features include providing helpful feedback and explanations, tracking scores and missed questions, identifying weaker topics, and adapting future quizzes to focus on areas where the user needs more practice.

## Download and Run

### Prerequisites

- Python 3.10–3.14
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- A LiveKit Cloud project and credentials
- The LiveKit CLI if you want to run the agent with LiveKit Cloud:
  [`lk` installation instructions](https://docs.livekit.io/intro/basics/cli/)

### Download the project

```bash
git clone https://github.com/ThomasFraserDev/live-kit-test.git
cd live-kit-test/agent
```

### Configure environment variables

Copy the example environment file and add your LiveKit credentials:

```bash
cp .env.example .env.local
```

The `.env.local` file should contain the values for your LiveKit project,
including `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET`.
Do not commit this file or share its contents.

### Install dependencies

```bash
uv sync
```

### Run locally

To run the agent in the LiveKit console:

```bash
lk agent console
```

To run the development agent so a frontend or LiveKit Cloud client can connect:

```bash
lk agent dev
```

To run the Python entry point directly:

```bash
uv run src/agent.py start
```

### Check the code

```bash
uv run ruff format --check src
uv run ruff check src
uv run pytest
```

## License

This software is licensed under the MIT license.
