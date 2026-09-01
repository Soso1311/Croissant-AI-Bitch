# Croissant 🥐

A fully localised, autonomous AI voice assistant for macOS, inspired by a bitch.

Croissant will be your personal AI assistant that is able to run locally on Apple Silicon. The project is dependent upon a local LLM, speech recognition, text-to-speech, memory, web research, and macOS automation into a single assistant.

The actual goal of the project is to build a Claude-style localised brain system with autonomous agent capabilities, rather than a collection of hardcoded voice commands to aid you.

# Features

# Local AI Brain

* Runs a local LLM 
* Designed for natural conversation and reasoning
* Good at maintaining small conversation context

# Voice Interaction

* Wake word detection
* Speech recognition
* Voice activity as well as silence detection

# Web Research

Croissant can research topics on the web and reason over the gathered information.
Research results are passed back to the local model for analysis rather than simply being returned raw.

# macOS Control

Ho can interact with the desktop through tools such as:

* Open applications
* Close applications
* List open applications
* Open websites
* Open URLs in Safari
* Check system status

# Memory

The project includes a memory system for storing and retrieving information about the user, and it can retrieve the stored information.

# Architecture

                 ┌─────────────────┐
                 │    Microphone   │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Wake Word      │
                 │  openWakeWord   │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Speech-to-Text  │
                 │ Faster Whisper  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   JARVIS Agent  │
                 │                 │
                 │ Local AI Brain  │
                 │ Memory          │
                 │ Tool Selection  │
                 │ Reasoning       │
                 └───────┬─────────┘
                         │
            ┌────────────┼─────────────┐
            │            │             │
            ▼            ▼             ▼
       ┌────────┐   ┌──────────┐   ┌─────────┐
       │ Memory │   │ Web Tools│   │ macOS   │
       │        │   │          │   │ Tools   │
       └────────┘   └──────────┘   └─────────┘
                         │
                         ▼
                 ┌─────────────────┐
                 │    Reasoning     │
                 │    / Response    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │      TTS        │
                 │  JARVIS Voice   │
                 └─────────────────┘
                 
# Current Stack

| Component          | Technology              |
| ------------------ | ----------------------- |
| Language           | Python                  |
| AI inference       | MLX                     |
| Local LLM          | Qwen2.5-3B-Instruct     |
| Speech recognition | Faster Whisper          |
| Wake word          | openWakeWord            |
| Audio              | sounddevice             |
| Web requests       | Requests                |
| Web parsing        | BeautifulSoup           |
| TTS                | ONNX-based JARVIS voice |
| Platform           | macOS / Apple Silicon   |

# Development Reason

Croissant is based on the memory of a person who is dead to me, so instead I am intending to use the memory to build an **agent**, not a command dictionary.

The system should increasingly be capable of:

1. Understanding the user's intent
2. Breaking complex tasks into steps
3. Selecting appropriate tools
4. Executing those tools
5. Observing the results
6. Reasoning over the results
7. Continuing the task when necessary
8. Reporting progress naturally
9. Delivering a final answer

# Human-Like Progress

Long-running operations should not leave the user staring at a silent terminal. The system is being developed to provide short progress updates.

# Privacy

The project is designed with a **local-first architecture**.

The primary language model runs locally on the user's Mac using MLX.

External web requests are made only when Croissant needs information from the internet.

Future versions will aim to keep as much personal data, conversation history, and memory local as possible.

# Current Status

Croissant is an active development project.

The core voice pipeline is functional:

```
Wake Word
   ↓
Speech Recognition
   ↓
Local AI
   ↓
Tool / Research
   ↓
Reasoning
   ↓
Voice Response
```

The biggest current development focus is transforming the system from a **basic voice assistant into a genuinely capable autonomous AI agent**.

# License

All Rights Reserved.

This repository is publicly viewable for informational and educational purposes only.

No permission is granted to copy, modify, distribute, commercially use, sublicense, reproduce, or create derivative works from this project without explicit written permission from the copyright holder.
---

# Built on Apple Silicon 

Made with Python, MLX, open-source AI models, and way too much terminal fuckery.
