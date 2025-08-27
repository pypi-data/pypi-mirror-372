# Riddles Solver

🧩 A Python library for solving riddles using repixify.com API

[![PyPI version](https://badge.fury.io/py/riddles-solver.svg)](https://badge.fury.io/py/riddles-solver)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🔄 **Synchronous and asynchronous API**
- 🔑 **Automatic key extraction**
- 🎭 **Random User-Agent support**
- 🚀 **Easy to use**

## 📦 Installation

```bash
pip install riddles-solver

# Install all dependencies
playwright install
```

### Optional dependencies

```bash
# For asynchronous client
pip install riddles-solver[async]

# For User-Agent generation
pip install riddles-solver[user-agent]

# For development
pip install riddles-solver[dev]
```

## 🚀 Quick Start

### 1. Getting a key

```python
import riddles_solver

# Automatic key extraction
key = riddles_solver.get_key()
print(f"Your key: {key}")
```

### 2. Solving riddles (synchronous)

```python
import riddles_solver

# Create client
client = riddles_solver.Client(key="a1b2c3d4e5f6789012345678901234567890abcdef")

# Solve riddles
answer = client.solve("2+2")
print(answer)  # 4

answer = client.solve("What has keys but no locks?")
print(answer)  # Piano
```

### 3. Asynchronous riddle solving

```python
import asyncio
import riddles_solver

async def main():
    # Create asynchronous client
    async with riddles_solver.AsyncClient(key="a1b2c3d4e5f6789012345678901234567890abcdef") as client:
        # Solve one riddle
        answer = await client.solve("2+2")
        print(answer)
        
        # Solve multiple riddles in parallel
        riddles = ["2+2", "2+2*2", "What is the capital of France?"]
        answers = await client.solve_batch(riddles)
        
        for riddle, answer in zip(riddles, answers):
            print(f"{riddle} = {answer}")

asyncio.run(main())
```

## 📖 Documentation

### Synchronous client

```python
# Basic usage
client = riddles_solver.Client(key="your_key")

# With custom User-Agent
client = riddles_solver.Client(
    key="your_key",
    user_agent="Custom User Agent"
)

# Solve riddle
answer = client.solve("your riddle")
```

### Asynchronous client

```python
# Create client
async_client = riddles_solver.AsyncClient(key="your_key")

# Solve one riddle
answer = await async_client.solve("riddle")

# Batch solving
riddles = ["riddle1", "riddle2", "riddle3"]
answers = await async_client.solve_batch(riddles)

# Don't forget to close the session
await async_client.close()

# Or use context manager
async with riddles_solver.AsyncClient(key="your_key") as client:
    answer = await client.solve("riddle")
```

### Getting keys

```python
# Programmatically
key = riddles_solver.get_key()

# Via CLI
# riddles-get-key
```

## 🛠️ CLI

After installation, a command-line utility is available:

```bash
# Get a new key
riddles-get-key

# Or
python -m riddles_solver.cli
```

## 📋 Complete example

```python
import asyncio
import riddles_solver

async def demo():
    print("🔑 Getting key...")
    key = riddles_solver.get_key()
    
    if not key:
        print("❌ Failed to get key")
        return
    
    print(f"✅ Key obtained: {key}")
    
    # Synchronous client
    print("\n🔄 Synchronous solving:")
    sync_client = riddles_solver.Client(key=key)
    answer = sync_client.solve("2+2")
    print(f"2+2 = {answer}")
    
    # Asynchronous client
    print("\n⚡ Asynchronous solving:")
    async with riddles_solver.AsyncClient(key=key) as async_client:
        riddles = ["2+2*2", "What is the capital of Russia?", "10-5"]
        answers = await async_client.solve_batch(riddles)
        
        for riddle, answer in zip(riddles, answers):
            print(f"{riddle} = {answer}")

if __name__ == "__main__":
    asyncio.run(demo())
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=riddles_solver
```

## 🤝 Development

```bash
# Clone repository
git clone https://github.com/Towux/riddles_solver.git
cd riddles_solver

# Install in development mode
pip install -e .[dev]

# Code formatting
black riddles_solver/

# Type checking
mypy riddles_solver/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

If you have questions or issues:

1. Check [Issues](https://github.com/Towux/riddles_solver/issues)
2. Create a new Issue if you don't find a solution
3. Describe the problem in as much detail as possible
