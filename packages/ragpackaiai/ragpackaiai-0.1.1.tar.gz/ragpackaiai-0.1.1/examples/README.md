# ragpackai Examples

This directory contains comprehensive examples demonstrating how to use ragpackai for various real-world applications.

## 📓 Jupyter Notebooks

### [01_getting_started.ipynb](01_getting_started.ipynb)
**Perfect for beginners!** Learn the fundamentals of ragpackai:
- Creating your first RAG pack from documents
- Saving and loading packs
- Basic querying and question answering
- Provider overrides and configuration

**What you'll build:** A company knowledge base with HR policies, API docs, and FAQs

### [02_advanced_features.ipynb](02_advanced_features.ipynb)
**For power users.** Explore advanced ragpackai capabilities:
- Working with different AI providers (Google, Groq, Cerebras)
- Encryption and security features
- Performance optimization techniques
- Error handling and troubleshooting
- Best practices for production use

**What you'll learn:** How to optimize ragpackai for different use cases and scale

### [03_real_world_examples.ipynb](03_real_world_examples.ipynb)
**Production-ready examples.** See ragpackai in action for real applications:
- Customer support knowledge base
- Technical documentation assistant
- Personal knowledge management system
- Multi-domain knowledge integration
- Performance analytics and monitoring

**What you'll build:** Complete, deployable RAG applications

## 🐍 Python Scripts

### [basic_usage.py](basic_usage.py)
Standalone script showing core ragpackai functionality. Great for understanding the API without Jupyter.

### [provider_overrides.py](provider_overrides.py)
Demonstrates how to use different AI providers at runtime without rebuilding packs.

### [encryption_example.py](encryption_example.py)
Shows how to secure sensitive data using ragpackai's built-in encryption.

## 🖥️ Command Line Examples

### [cli_examples.sh](cli_examples.sh)
Shell script with practical CLI usage examples for automation and scripting.

## 🚀 Quick Start

1. **Install ragpackai:**
   ```bash
   pip install ragpackai
   ```

2. **Set up API keys:**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   # Optional: Add other provider keys
   export GOOGLE_API_KEY="your-google-key"
   export GROQ_API_KEY="your-groq-key"
   ```

3. **Run the notebooks:**
   ```bash
   jupyter notebook 01_getting_started.ipynb
   ```

4. **Or try the Python scripts:**
   ```bash
   python basic_usage.py
   ```

## 📋 Prerequisites

- Python 3.9 or higher
- At least one AI provider API key (OpenAI recommended for beginners)
- Jupyter Notebook (for .ipynb files)

## 🎯 Learning Path

1. **Start here:** `01_getting_started.ipynb` - Learn the basics
2. **Go deeper:** `02_advanced_features.ipynb` - Master advanced features  
3. **Build real apps:** `03_real_world_examples.ipynb` - See production examples
4. **Automate:** `cli_examples.sh` - Use the command line interface

## 💡 Tips for Success

- **Start small:** Begin with a few documents to understand the workflow
- **Experiment:** Try different chunk sizes and providers to see what works best
- **Use encryption:** Always encrypt packs containing sensitive data
- **Monitor performance:** Check pack statistics and query times
- **Read the docs:** Each notebook has detailed explanations and best practices

## 🆘 Need Help?

- Check the [main README](../README.md) for installation and setup
- Review the [API documentation](https://AIMLDev726.readthedocs.io/)
- Open an [issue on GitHub](https://github.com/AIMLDev726/ragpackai/issues)
- Join our [community discussions](https://github.com/AIMLDev726/ragpackai/discussions)

## 🤝 Contributing

Found a bug or have an idea for a new example? We'd love your contribution!

1. Fork the repository
2. Create your example
3. Test it thoroughly
4. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

---

**Happy RAG building!** 🚀