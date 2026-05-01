# 🚀 Multi-Domain Support Triage Agent

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Streamlit App](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://multi-domain-support-triage-agent-21.streamlit.app/)

An intelligent AI-powered system for automated classification, retrieval, and response generation for customer support tickets across **HackerRank**, **Claude**, and **Visa** domains.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Architecture](#project-architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
  - [Batch Processing](#batch-processing)
  - [Interactive UI](#interactive-ui)
- [How It Works](#how-it-works)
- [Output Format](#output-format)
- [Example Input & Output](#example-input--output)
- [Future Enhancements](#future-enhancements)
- [License](#license)
- [Author](#author)

---

## 📌 Overview

The **Multi-Domain Support Triage Agent** is an end-to-end solution for automating customer support ticket management. It leverages natural language processing and retrieval-augmented generation to classify tickets, retrieve relevant information from domain-specific corpora, and generate contextually appropriate responses—all while preventing AI hallucinations by grounding responses in actual data.

### What This Project Does

For each support ticket, the triage agent:

1. **Identifies the correct company** (HackerRank, Claude, or Visa)
2. **Classifies the request type** (bug, product issue, feature request, or invalid)
3. **Determines the product area** (routes to precise product category)
4. **Retrieves relevant information** from domain-specific corpora
5. **Generates a grounded response** based on retrieved data
6. **Makes escalation decisions** (reply vs. escalate)
7. **Outputs structured results** to CSV for further analysis

---

## 🚀 Features

- ✅ **Multi-Domain Support** — Extensible framework supporting HackerRank, Claude, and Visa
- ✅ **Intelligent Classification** — Identifies company, request type, and product area simultaneously
- ✅ **Retrieval-Augmented Generation** — All responses grounded in actual domain data; zero hallucinations
- ✅ **Smart Escalation Logic** — Automatically escalates tickets when no confident answer is found
- ✅ **Batch Processing** — Process multiple tickets efficiently via CSV
- ✅ **Interactive UI** — Streamlit-powered interface for real-time testing and demonstration
- ✅ **Safety Validation** — Prevents unsafe or unsupported responses
- ✅ **Structured Output** — Detailed CSV reports with justifications and decisions
- ✅ **Extensible Design** — Easy to add new domains, products, and response strategies

---

## 🧰 Tech Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.8+ |
| **UI Framework** | Streamlit |
| **Data Processing** | Pandas, NumPy |
| **NLP** | NLTK, scikit-learn, spaCy |
| **File Handling** | CSV (pandas), JSON |
| **Environment** | Virtual Environment (venv/conda) |

---

## 🏗️ Project Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Support Ticket Input (CSV/UI)              │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│          1. Ticket Classification Module                │
│   • Company Identification (HackerRank/Claude/Visa)    │
│   • Request Type Classification (Bug/Issue/Feature)    │
│   • Product Area Determination                          │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│          2. Retrieval Module                            │
│   • Domain-Specific Corpus Search                       │
│   • Relevant Document Ranking                           │
│   • Context Aggregation                                 │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│          3. Response Generation Module                  │
│   • Template-Based Response Composition                 │
│   • Context Integration                                 │
│   • Safety Validation                                   │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│          4. Decision Module                             │
│   • Confidence Scoring                                  │
│   • Reply vs. Escalate Decision                         │
│   • Justification Generation                            │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│       Structured Output (CSV / JSON / UI Display)       │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
multi-domain-support-triage-agent/
│
├── 📄 README.md                          # Project documentation
├── 📄 requirements.txt                   # Python dependencies
├── 📄 LICENSE                            # MIT License
├── 📄 .gitignore                         # Git ignore rules
│
├── 📁 agent/                             # Core triage agent modules
│   ├── __init__.py
│   ├── classifier.py                    # Company & request classification
│   ├── retriever.py                     # Domain corpus retrieval
│   ├── response_generator.py            # Response composition
│   └── safety_checker.py                # Validation & safety checks
│
├── 📁 data/                             # Domain-specific corpora
│   ├── __init__.py
│   ├── hackerrank/                      # HackerRank documentation
│   │   └── corpus.json
│   ├── claude/                          # Claude documentation
│   │   └── corpus.json
│   └── visa/                            # Visa documentation
│       └── corpus.json
│
├── 📁 support_issues/                   # Input & output data
│   ├── support_issues.csv              # Input tickets
│   └── output.csv                       # Processed results
│
├── 📁 utils/                            # Utility functions
│   ├── __init__.py
│   └── file_handler.py                 # CSV I/O operations
│
├── 📄 pipeline.py                       # Batch processing pipeline
├── 📄 app.py                            # Streamlit interactive UI
└── 📁 logs/                             # Application logs (auto-generated)
    └── triage_agent.log
```

---

## 💾 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/divyashree-21/multi-domain-support-triage-agent.git
cd multi-domain-support-triage-agent
```

### Step 2: Create Virtual Environment

```bash
# Using venv
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python -c "import streamlit; import pandas; print('✅ Installation successful!')"
```

---

## 🎯 Usage

### Batch Processing

Process multiple support tickets from a CSV file in one operation:

```bash
python pipeline.py
```

**Input file:** `support_issues/support_issues.csv`

**Expected columns:**
- `issue` — The support ticket description
- `subject` — Ticket subject/title
- `company` — Company name (HackerRank, Claude, or Visa)

**Output file:** `support_issues/output.csv`

### Interactive UI

Launch the Streamlit application for real-time classification and response testing:

```bash
streamlit run app.py
```

**Features:**
- Enter support tickets in real-time
- View immediate classification results
- Test different companies and request types
- Visualize decision-making process
- Download results as CSV

---

## 🧠 How It Works

### 1. **Classification Module** (`agent/classifier.py`)

Identifies three key attributes:

```python
{
    "company": "HackerRank",           # or Claude, Visa
    "request_type": "bug",             # or product_issue, feature_request, invalid
    "product_area": "Assessments"      # specific product category
}
```

**Approach:** Rule-based + keyword matching with fallback to similarity scoring

### 2. **Retriever Module** (`agent/retriever.py`)

Searches domain-specific corpus for relevant information:

```python
retrieved_docs = retriever.search(
    query=ticket_text,
    domain="hackerrank",
    top_k=3
)
```

**Approach:** TF-IDF ranking + semantic similarity

### 3. **Response Generator** (`agent/response_generator.py`)

Generates contextually appropriate responses:

```python
response = generator.generate(
    ticket=ticket_text,
    retrieved_context=docs,
    request_type="bug"
)
```

**Approach:** Template-based composition with context injection

### 4. **Safety Checker** (`agent/safety_checker.py`)

Validates response quality and determines escalation:

```python
is_safe, confidence = safety_checker.validate(
    response=generated_response,
    context=retrieved_docs
)
```

**Approach:** Confidence scoring, hallucination detection, escalation logic

---

## 📊 Output Format

All results are saved to `support_issues/output.csv` with the following schema:

| Column | Type | Description |
|--------|------|-------------|
| `ticket_id` | int | Unique ticket identifier |
| `original_issue` | string | Original support ticket text |
| `company` | string | Identified company (HackerRank/Claude/Visa) |
| `request_type` | string | Classification (bug/product_issue/feature_request/invalid) |
| `product_area` | string | Specific product category |
| `status` | string | Decision (replied/escalated) |
| `response` | string | Generated response or escalation note |
| `justification` | string | Reason for decision |
| `confidence_score` | float | Confidence (0.0-1.0) |
| `retrieved_sources` | string | Number of documents retrieved |
| `timestamp` | datetime | Processing timestamp |

---

## 🧪 Example Input & Output

### Example Input

**File:** `support_issues/support_issues.csv`

| issue | subject | company |
|-------|---------|---------|
| My code submissions are not executing properly. Getting timeout errors on simple test cases. | Code Execution Error | HackerRank |
| How do I update my API key for authentication? | Authentication Issue | Claude |
| Is there a way to customize transaction reports? | Feature Request | Visa |

### Example Output

**File:** `support_issues/output.csv`

| company | request_type | product_area | status | response | justification | confidence_score |
|---------|--------------|--------------|--------|----------|---------------|-----------------|
| HackerRank | bug | Code Execution | replied | Check your code for infinite loops or excessive memory usage. You can increase time limits in problem settings. | Retrieved from HackerRank troubleshooting docs | 0.92 |
| Claude | product_issue | API Management | replied | Visit your API dashboard → Settings → Authentication to regenerate your key. Use the new key in your application configuration. | Based on Claude API documentation | 0.88 |
| Visa | feature_request | Reporting | escalated | Thank you for your suggestion. Customizable reports are under development. Our team will contact you within 24 hours. | Feature request requires human review | 0.75 |

---

## 🌱 Future Enhancements

- [ ] **Multi-Language Support** — Handle tickets in multiple languages
- [ ] **Enhanced ML Models** — Integrate BERT/GPT for improved classification
- [ ] **Ticketing System Integration** — Direct integration with Zendesk, ServiceNow, Jira
- [ ] **Analytics Dashboard** — Real-time metrics on ticket resolution rates and response times
- [ ] **User Feedback Loop** — Learn from agent-human interactions to improve responses
- [ ] **Expanded Domain Coverage** — Add support for additional companies/domains
- [ ] **Response Template Library** — Curated templates for common issues
- [ ] **API Endpoint** — REST API for third-party integrations
- [ ] **Docker Containerization** — Simplified deployment and scaling
- [ ] **Automated Retraining** — Periodic model updates based on new data

---

## 📋 Requirements

See `requirements.txt` for complete dependencies:

```
streamlit==1.28.0
pandas==2.0.0
numpy==1.24.0
nltk==3.8.1
scikit-learn==1.3.0
spacy==3.6.0
python-dotenv==1.0.0
```

---

## 📝 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👩‍💻 Author

**Divya Shree M**  
Computer Science Engineering Student

- 🔗 [GitHub](https://github.com/divyashree-21)
- 💼 [LinkedIn](www.linkedin.com/in/divya-gowda-72b18932b)
- 📧 [Email](mailto:divyashree200621@gmail.com)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Support & Feedback

For questions, bugs, or suggestions, please open an [issue](https://github.com/divyashree-21/multi-domain-support-triage-agent/issues) on GitHub.

---

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [NLTK Documentation](https://www.nltk.org/)
- [scikit-learn Documentation](https://scikit-learn.org/)

---

**⭐ If you find this project helpful, please consider giving it a star!**

