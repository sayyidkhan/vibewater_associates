# Setup with UV - Ultra Fast! ⚡

## What is UV?

`uv` is an extremely fast Python package installer and resolver written in Rust. It's **10-100x faster** than pip!

## Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
cd backend
./setup-uv.sh
```

This script will:
1. Install `uv` if not present
2. Create a virtual environment
3. Install all dependencies (super fast!)

### Option 2: Manual Setup

```bash
# 1. Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create virtual environment
cd backend
uv venv

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Install dependencies
uv pip install -r requirements.txt
```

## Usage

### Install Dependencies
```bash
uv pip install -r requirements.txt
```

### Add New Package
```bash
uv pip install package-name
```

### Run Backend
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Start the server
uvicorn app.main:app --reload
```

### Test VectorBT
```bash
python test_vectorbt.py
```

## Speed Comparison

**Traditional pip**:
```
Installing 16 packages... ⏱️  45-60 seconds
```

**With uv**:
```
Installing 16 packages... ⚡ 3-5 seconds
```

## Troubleshooting

### "uv: command not found"

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then restart your terminal or run:
```bash
source $HOME/.cargo/env
```

### Virtual Environment Not Activated

```bash
cd backend
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

### Permission Denied on setup-uv.sh

```bash
chmod +x setup-uv.sh
./setup-uv.sh
```

## Complete Workflow

```bash
# 1. Setup (one time)
cd backend
./setup-uv.sh

# 2. Start backend
source .venv/bin/activate
uvicorn app.main:app --reload

# 3. In another terminal, start frontend
cd ../frontend
npm run dev
```

## Why UV?

- ⚡ **10-100x faster** than pip
- 🦀 **Written in Rust** for maximum performance
- 🔒 **Reliable** dependency resolution
- 🎯 **Drop-in replacement** for pip
- 💾 **Smaller disk usage** with smart caching

## Resources

- **UV Docs**: https://github.com/astral-sh/uv
- **Installation**: https://astral.sh/uv/install

---

**Ready to go!** Your backend setup with uv is complete. 🚀
