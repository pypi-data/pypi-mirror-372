# Liotel v0.2b1

**English** | [فارسی](#-فارسی)

A resilient, lightweight Python client for the **Liotel API** with:

- **Automatic retries** (with exponential backoff & jitter) to handle network errors  
- **Safe timeouts** to prevent hanging requests  
- **Token-based authentication** for secure communication  
- **Simple CLI (`liotel`)** for quick tests and automation  
- **In-memory caching (optional)** for GET requests to improve performance  

---

## Installation

```bash
pip install liotel==0.2b1