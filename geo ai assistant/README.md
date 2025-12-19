# GeoAI Assistant Simple - Minimal Version

## 🚀 Overview

**GeoAI Assistant Simple** is a beginner-friendly QGIS plugin with core features and a simple UI, but powered by the same robust modules as the main version.

## ✨ Features

### Core Modules (7 modules)
- ✅ **LLMHandler** - Full handler (defaults to Ollama, supports all providers)
- ✅ **SQLExecutor** - Complete SQL execution
- ✅ All other modules available (not in UI, but accessible)

### Features
1. ✅ **SQL Generation** - Natural language to SQL
   - Uses full LLMHandler
   - Context-aware generation
   - Supports all providers (defaults to Ollama)

2. ✅ **SQL Execution** - Execute generated SQL
   - Full SQLExecutor
   - Results display in table
   - Error handling

3. ✅ **Context Awareness** - Automatic context extraction
   - Layer information
   - Field names
   - Database type detection

4. ✅ **Error Handling** - Comprehensive error messages
   - User-friendly feedback
   - Status indicators

### UI
- ✅ Simple single-dialog interface
- ✅ Clean, beginner-friendly
- ✅ Easy to use
- ✅ Minimal but powerful

## 🏗️ Architecture

- **2-Layer**: UI → Business Logic
- **Full Module Support**: Uses same modules as main version
- **Ollama-First**: Defaults to local Ollama (phi3)
- **Provider Support**: Can use any provider via .env

## 📁 Structure

```
GeoAI_Assistant_Simple/
├── modules/         # All 7 modules from main version
├── core/           # (legacy, can be removed)
└── ui/             # Simple dialog
```

## 🚀 Getting Started

1. Install Ollama: https://ollama.ai
2. Pull model: `ollama pull phi3`
3. Copy to QGIS plugins directory
4. Enable in Plugin Manager
5. Use!

## ✅ Status

**CORE FEATURES ARE FULLY FUNCTIONAL!**

Uses the same powerful modules as the main version, but with a simple, beginner-friendly UI.
