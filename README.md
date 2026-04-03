# Finite Monkey Engine v3.0

Security analysis pipeline for code auditing: **Planning → Reasoning → Validation**.  
Results are persisted to PostgreSQL and can be exported as reports.

## v3.0 Updates

- **Planning**: removes RAG / chunks / call graph / call tree. Keeps tree-sitter function parsing and uses Codex CLI to extract business flows (Gi/Fi). Tasks persisted as **Fi × checklist (rule_key)**.
- **Reasoning**: switches the main scan execution to **Codex CLI** (input: `business_flow_code + prompt`). Output remains the original **multi-vulnerability JSON**, then split into `project_finding` (unchanged downstream logic).
- **Validation**: Codex-based confirmation for `project_finding` and write-back to `validation_status` / `validation_record`.
- **Workspace restriction**: Codex always runs with `--cd <project_root>` derived from `src/dataset/agent-v1-c4/datasets.json[project_id].path`.
- **Design docs**: moved into `docs/`.

## 🚀 v2.0 Major Upgrades

**Finite Monkey Engine v2.0** brings significant architectural upgrades and feature enhancements:

### 🔥 Core Upgrades
- **🎯 Precision Language Support**: Focus on 4 core languages (Solidity/Rust/C++/Move) for optimal analysis experience
- **🧠 RAG Architecture Optimization**: New LanceDB merged 2-table architecture with 300% query efficiency improvement
- **📊 Intelligent Context Understanding**: Multi-dimensional embedding technology, significantly enhanced code comprehension
- **⚡ Performance Optimization**: Unified storage strategy, 50% memory reduction, improved concurrent processing
- **🔍 Deep Business Analysis**: Enhanced business flow visualization and cross-contract dependency analysis

## 🎯 Overview

Finite Monkey Engine is an advanced AI-driven code security analysis platform **focused on blockchain and system-level code security auditing**. By integrating multiple AI models and advanced static analysis techniques, it provides comprehensive, intelligent security auditing solutions for core programming language projects.

### 🌍 Multi-Language Support

Built on Tree-sitter parsing engine and function-level analysis architecture, **v2.0 focuses on 4 core languages** for optimal analysis experience:

**✅ Currently Fully Supported Languages:**
- **Solidity** (.sol) - Ethereum smart contracts with complete Tree-sitter support
- **Rust** (.rs) - Solana ecosystem, Substrate, system-level programming
- **C/C++** (.c/.cpp/.cxx/.cc/.C/.h/.hpp/.hxx) - Blockchain core, node clients
- **Move** (.move) - Aptos, Sui blockchain language
- **Go** (.go) - Blockchain infrastructure, TEE projects~~

**🔄 Planned Support (Future Versions):**
- ~~**Cairo** (.cairo) - StarkNet smart contract language~~
- ~~**Tact** (.tact) - TON blockchain smart contracts~~
- ~~**FunC** (.fc/.func) - TON blockchain native language~~
- ~~**FA** (.fr) - Functional smart contract language~~
- ~~**Python** (.py) - Web3, DeFi backend projects~~
- ~~**JavaScript/TypeScript** (.js/.ts) - Web3 frontend, Node.js projects~~
- ~~**Java** (.java) - Enterprise blockchain applications~~

> 💡 **v2.0 Design Philosophy**: Focus on core languages to provide deeply optimized analysis capabilities. Based on function-granularity code analysis architecture, theoretically extensible to any programming language. Future versions will gradually support more languages.

## 🚀 v2.0 Key Features

### 🧠 Enhanced AI-Powered Analysis
- **Multi-Model Collaboration**: Claude-4 Sonnet, GPT-4 and other AI models working intelligently together
- **RAG-Enhanced Understanding**: Multi-dimensional context-aware technology based on LanceDB
- **Deep Business Logic Analysis**: Deep understanding of DeFi protocols, governance mechanisms, and tokenomics
- **Intelligent Vulnerability Discovery**: AI-assisted complex vulnerability pattern recognition

### 🔍 Comprehensive Security Detection System
- **Precision Vulnerability Detection**: Focus on core languages for more accurate vulnerability identification
- **Cross-Contract Deep Analysis**: Multi-contract interaction analysis and complex dependency tracking
- **Business Scenario Review**: Professional security analysis for different DeFi scenarios
- **Intelligent False Positive Filtering**: AI-assisted reduction of false positives, improving analysis accuracy

### 🛠 Precision Language Architecture
- **Core Language Focus**: Specialized framework for Solidity/Rust/C++/Move languages
- **Modular Design**: Planning, validation, context, and analysis modules
- **Tree-sitter Parsing**: Advanced parsing supporting core languages with high precision

## 📁 Project Structure

```
finite-monkey-engine/
├── src/
│   ├── planning/           # Task planning and business flow analysis
│   ├── validating/         # Vulnerability detection and validation
│   ├── context/            # Context management and RAG processing
│   ├── reasoning/          # Analysis reasoning and dialogue management
│   ├── dao/                # Data access objects and entity management
│   ├── library/            # Parsing libraries and utilities
│   ├── openai_api/        # AI API integrations
│   └── prompt_factory/     # Prompt engineering and management
├── knowledges/             # Domain knowledge base
├── scripts/                # Utility scripts
└── docs/                   # Documentation
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **PostgreSQL 13+** (required for storing analysis results)
- **AI API Keys** (supports OpenAI, Claude, DeepSeek, and other compatible services)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-org/finite-monkey-engine.git
cd finite-monkey-engine

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp env.example .env
# Edit .env file with your API keys and database configuration

# 4. Initialize database
psql -U postgres -d postgres -f project_task.sql

# 5. Configure project dataset
# Edit src/dataset/agent-v1-c4/datasets.json to add your project configuration

# 6. Run analysis
python src/main.py
```

## 📊 Usage Guide

### Database Initialization

Initialize PostgreSQL database using the provided SQL file:

```bash
# Connect to PostgreSQL database
psql -U postgres -d postgres

# Execute SQL file to create table structure
\i project_task.sql

# Or use command line directly
psql -U postgres -d postgres -f project_task.sql
```

### Project Configuration

Configure your project in `src/dataset/agent-v1-c4/datasets.json`:

```json
{
  "your_project_id": {
    "path": "your_project_folder_name",
    "files": [], //no need to set, disable in future
    "functions": [], //no need to set, disable in future
    "exclude_in_planning": "false", //no need to set to true, disable in future
    "exclude_directory": [] //no need to set, disable in future
  }
}
```

### Running Analysis

1. **Set Project ID**: Configure your project ID in `src/main.py`
```python
project_id = 'your_project_id'
```

2. **Execute Analysis**:
```bash
python src/main.py
```

3. **View Results**: 
   - Detailed analysis records in database
   - `output.xlsx` report file
   - Mermaid business flow diagrams (if enabled)

## 🔧 Configuration

### Quick Configuration

1. **Copy environment template**:
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` file** with your API keys and preferences

### Core Environment Variables

```bash
# Database Configuration (Required)
DATABASE_URL=postgresql://postgres:1234@127.0.0.1:5432/postgres

# Codex (Required for v3.0 planning/reasoning/validation)
CODEX_MODEL=gpt-5.2
CODEX_SANDBOX=read-only
CODEX_ASK_FOR_APPROVAL=never
CODEX_TIMEOUT_SEC=1800

# Legacy model config (still used by some auxiliary flows)
OPENAI_API_BASE="api.openai-proxy.org"  # LLM proxy platform
OPENAI_API_KEY="sk-xxxxxx"  # API key

# Scan Mode Configuration
SCAN_MODE=COMMON_PROJECT_FINE_GRAINED   # Recommended mode: Common project checklist fine-grained
# Available modes: PURE_SCAN (Pure scanning)
SCAN_MODE_AVA=False                     # Advanced scan mode features
COMPLEXITY_ANALYSIS_ENABLED=True        # Enable complexity analysis

# Performance Tuning
MAX_THREADS_OF_SCAN=10                  # Maximum threads for scanning phase
MAX_THREADS_OF_CONFIRMATION=50          # Maximum threads for confirmation phase
BUSINESS_FLOW_COUNT=4                   # Business flow repeat count (hallucination triggers)

# Advanced Feature Configuration
IGNORE_FOLDERS=node_modules,build,dist,test,tests,.git  # Folders to ignore

# Checklist Configuration
CHECKLIST_PATH=src/knowledges/checklist.xlsx  # Path to checklist file
CHECKLIST_SHEET=Sheet1                  # Checklist worksheet name

# Run control (v3.0)
CMD=detect_vul                 # detect_vul / planning_only
STOP_AFTER_PLANNING=false      # true: stop after planning (before reasoning)
```

> 📝 **Complete Configuration**: See `env.example` file for all configurable options and detailed descriptions

### AI Model Configuration Details

Based on actual configuration in `src/openai_api/model_config.json`:

**WARNING**  must set the model name based on your llm hub!
**WARNING**  must set the model name based on your llm hub!
**WARNING**  like in openrouter, sonnet 4 need to set to anthropic/sonnet-4

```json
{
  "openai_general": "gpt-4.1",
  "code_assumptions_analysis": "claude-sonnet-4-20250514",
  "vulnerability_detection": "claude-sonnet-4-20250514",
  "initial_vulnerability_validation": "deepseek-reasoner",
  "vulnerability_findings_json_extraction": "gpt-4o-mini",
  "additional_context_determination": "deepseek-reasoner",
  "comprehensive_vulnerability_analysis": "deepseek-reasoner",
  "final_vulnerability_extraction": "gpt-4o-mini",
  "structured_json_extraction": "gpt-4.1",
  "embedding_model": "text-embedding-3-large"
}
```

### 🌐 Using MiniMax as LLM Provider

[MiniMax](https://platform.minimax.io) offers an OpenAI-compatible API and works as a drop-in LLM backend for Finite Monkey Engine. All models feature a **204K context window**, making them well-suited for large smart-contract codebases.

**Supported MiniMax models:**

| Model | Context | Best for |
|---|---|---|
| `MiniMax-M2.7` | 204K | Flagship — vulnerability detection & reasoning |
| `MiniMax-M2.7-highspeed` | 204K | Fast JSON extraction & summarization |
| `MiniMax-M2.5` | 204K | Previous generation |
| `MiniMax-M2.5-highspeed` | 204K | Previous generation fast variant |

**Quick setup — two options:**

Option A: set `LLM_PROVIDER=minimax` and `MINIMAX_API_KEY`:
```bash
LLM_PROVIDER=minimax
MINIMAX_API_KEY=your-minimax-api-key
```

Option B: set only `MINIMAX_API_KEY` (auto-detected when `OPENAI_API_KEY` is absent):
```bash
MINIMAX_API_KEY=your-minimax-api-key
```

Then update `src/openai_api/model_config.json` to use MiniMax model names:
```json
{
  "openai_general": "MiniMax-M2.7",
  "code_assumptions_analysis": "MiniMax-M2.7",
  "vulnerability_detection": "MiniMax-M2.7",
  "group_results_summarization": "MiniMax-M2.7",
  "initial_vulnerability_validation": "MiniMax-M2.7",
  "vulnerability_findings_json_extraction": "MiniMax-M2.7-highspeed",
  "additional_context_determination": "MiniMax-M2.7",
  "comprehensive_vulnerability_analysis": "MiniMax-M2.7",
  "final_vulnerability_extraction": "MiniMax-M2.7-highspeed",
  "structured_json_extraction": "MiniMax-M2.7-highspeed",
  "embedding_model": "text-embedding-3-large"
}
```

> 💡 **Temperature note**: MiniMax requires temperature in the range `(0.0, 1.0]`.
> The built-in `_clamp_temperature()` helper enforces this automatically.

### Recommended Configuration Schemes

#### 🚀 Quick Start (Small projects < 50 files)
```bash
SCAN_MODE=PURE_SCAN
COMPLEXITY_ANALYSIS_ENABLED=False
MAX_THREADS_OF_SCAN=3
BUSINESS_FLOW_COUNT=2
```

#### 🏢 Enterprise (Large projects > 100 files)
```bash
SCAN_MODE=COMMON_PROJECT_FINE_GRAINED
COMPLEXITY_ANALYSIS_ENABLED=True
MAX_THREADS_OF_SCAN=8
MAX_THREADS_OF_CONFIRMATION=30
BUSINESS_FLOW_COUNT=4
```

#### 💰 Cost Optimized
```bash
SCAN_MODE=PURE_SCAN
BUSINESS_FLOW_COUNT=1
MAX_THREADS_OF_SCAN=3
MAX_THREADS_OF_CONFIRMATION=10
COMPLEXITY_ANALYSIS_ENABLED=False
```

## 🎯 Use Cases

### Blockchain & Web3 Projects
- **Smart Contract Security**: Solidity, Rust, Move contract analysis
- **DeFi Protocol Analysis**: AMM, lending, governance mechanism review
- **Cross-Chain Applications**: Bridge security, multi-chain deployment analysis
- **NFT & Gaming**: Minting logic, marketplace integration security

### Traditional Software Projects
- **Web3 Backend**: Python/Node.js API security analysis
- **Blockchain Infrastructure**: Go/C++ node and client security
- **Enterprise Applications**: Java enterprise blockchain applications
- **System-Level Code**: C/C++ core components and TEE projects

### Multi-Language Project Analysis
- **Polyglot Codebases**: Cross-language dependency analysis
- **Microservice Architecture**: Multi-service security assessment
- **Full-Stack Applications**: Frontend, backend, and contract integration security

## 📊 Analysis Reports

The platform generates comprehensive analysis reports including:

- **Security Vulnerability Report**: Detailed vulnerability findings with severity ratings
- **Business Flow Diagrams**: Visual representation of contract interactions
- **Gas Optimization Suggestions**: Performance improvement recommendations
- **Best Practice Compliance**: Adherence to security standards and guidelines

## 🧪 Testing

Run the test suite:

```bash
# Unit tests
python -m pytest tests/

# Integration tests
python -m pytest tests/integration/

# Coverage report
python -m pytest --cov=src tests/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ANTLR4**: For Solidity parsing capabilities
- **Claude AI**: For advanced code understanding
- **Mermaid**: For business flow visualization
- **OpenAI**: For AI-powered analysis capabilities
- **MiniMax**: For OpenAI-compatible LLM API with large context windows

## 📞 Contact

- **Email**: nerbonic@gmail.com
- **Twitter**: [@xy9301](https://x.com/xy9301)
- **Telegram**: [https://t.me/+4-s4jDfy-ig1M2Y1](https://t.me/+4-s4jDfy-ig1M2Y1)

---

## 🆕 v2.0 Release Notes

### Major Upgrades
- **Core Language Specialization**: Focus on Solidity/Rust/C++/Move for optimal analysis experience
- **RAG Architecture Revolution**: LanceDB merged 2-table architecture with 300% performance improvement
- **Intelligent Embedding**: Multi-dimensional code understanding with significantly enhanced analysis precision
- **Architecture Optimization**: 50% memory reduction, supporting larger-scale projects

### Migration Guide
- v2.0 is fully backward compatible, no configuration changes required
- Unsupported language files will be automatically skipped without affecting system operation
- Recommended to update configuration files for optimal performance experience

---

**🎉 Finite Monkey Engine v2.0 - Making Code Security Analysis More Intelligent, Professional, and Efficient!** 