# Cursor Reference Documentation

This directory contains AI-generated reference documentation, setup guides, and planning documents created during development.

## Purpose

- **Local reference only** - Not committed to git (excluded via `.gitignore`)
- **Development aids** - Setup guides, verification checklists, design notes
- **Temporary docs** - Testing scripts, transfer helpers, internal notes

## Contents

Current reference docs:

**Mac Support:**
- `MAC_SETUP.md` - Complete Mac setup guide with Ollama
- `MAC_VERIFICATION_STEPS.md` - Step-by-step Mac testing checklist
- `CHANGES_FOR_MAC_SUPPORT.md` - Technical details of Mac implementation
- `package_for_transfer.sh` - Helper script for file transfer
- **Note:** `test_gpu_monitor_mac.py` is committed in project root (useful for Mac users)

**Multi-User Architecture:**
- `MULTI_USER_ANALYSIS.md` - Deep dive into single vs multi-user architecture
- `QUICK_REFERENCE_MULTI_USER.md` - Quick reference for multi-user considerations
- `ARCHITECTURE_DIAGRAMS.md` - Detailed architecture diagrams and data flow
- `MULTI_INSTANCE_DEPLOYMENT.md` - Multi-instance deployment guide (Docker, systemd, k8s)

**Project Planning:**
- `ROADMAP.md` - Detailed implementation roadmap with feature planning

## Convention

Per `.cursorrules`, all Cursor-generated reference docs should:
1. Be placed in this directory
2. Use ALL_CAPS_WITH_UNDERSCORES naming
3. Be kept locally (not committed)

## For Public Documentation

User-facing documentation should go in project root:
- `README.md` - Main project docs
- `ROADMAP.md` - Public roadmap
- Other guides intended for users

---

**Note:** This directory and its contents are excluded from git. Each developer maintains their own local reference docs.

