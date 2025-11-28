# Wearable Glasses Architecture - Future Vision

## Overview

This document outlines potential architecture options for deploying the "Describe My Environment" system on wearable glasses hardware. The current implementation runs as a CLI tool on a laptop/Mac, with a web application (backend + frontend) in development. The future goal is deployment on wearable glasses.

## Architecture Options

### Option 1: Edge Computing (On-Device)

**Description:**

All processing occurs on the glasses themselves using an embedded processor (similar to Apple Vision Pro or Meta Quest). No external server is required. The architecture is similar to the current CLI implementation, but embedded in wearable hardware.

**Architecture:**

```
Glasses Hardware
├── Camera (built-in)
├── Processor (ARM chip, NPU)
├── Battery
└── Software Stack
    ├── YOLO (lightweight, optimized)
    ├── BLIP (optimized/quantized)
    ├── LLM (small model, 1-3B, quantized)
    └── TTS (on-device)
```

**Advantages:**

- Low latency - No network delay
- Privacy - Data never leaves device
- Works offline - No internet required
- Self-contained - Truly wearable
- Battery efficient - No constant network communication

**Disadvantages:**

- Hardware constraints - Limited compute power
- Model size limits - Requires smaller/quantized models
- Battery life - Processing is power-intensive
- Heat management - Processing generates heat

**Examples:** Apple Vision Pro, Meta Quest (run ML on-device)

---

### Option 2: Smartphone Companion App

**Description:**

Glasses connect to a smartphone via Bluetooth or WiFi. The smartphone performs all processing, while the glasses provide camera, display, and audio capabilities.

**Architecture:**

```
Glasses (Lightweight)
├── Camera
├── Display (AR overlay)
├── Audio (speakers/mic)
└── Communication (Bluetooth/WiFi)
    ↓
Smartphone (Heavy Processing)
├── Current codebase (adapted)
├── YOLO, BLIP, LLM
└── Sends results back to glasses
```

**Advantages:**

- More compute power - Phone has better processor
- Better battery life - Glasses are lightweight
- Easier updates - Update phone app, not glasses firmware
- Cost effective - Glasses hardware is simpler

**Disadvantages:**

- Requires phone - Not standalone
- Connectivity dependency - Must stay connected
- Latency - Network delay between glasses and phone

**Example:** Meta Ray-Ban Smart Glasses (connect to phone)

---

### Option 3: Hybrid (Edge + Cloud)

**Description:**

Fast processing (YOLO tracking) occurs on the glasses, while heavy processing (BLIP, LLM) occurs in the cloud. Glasses provide immediate safety warnings, while the cloud handles detailed narration.

**Architecture:**

```
Glasses (Edge)
├── YOLO tracking (30 FPS)
├── Safety warnings (immediate)
└── Communication
    ↓
Cloud Server
├── BLIP scene captioning
├── LLM narration
└── Advanced features
```

**Advantages:**

- Combines fast safety with detailed narration
- Always up-to-date - Models updated in cloud
- More powerful models - No device constraints

**Disadvantages:**

- Requires internet - Won't work offline
- Privacy concerns - Video sent to cloud
- Latency - Cloud processing adds delay
- Cost - Cloud infrastructure costs money
- Battery drain - Constant network communication

**Example:** Some AR glasses with cloud ML (less common)

---

### Option 4: Local Server (Current Web App)

**Description:**

Glasses connect to a local server (laptop/phone) that runs the current codebase. This represents the current development approach.

**Architecture:**

```
Glasses (Camera + Display)
    ↓ WiFi/Bluetooth
Laptop/Phone (Server)
├── FastAPI backend
├── ML pipeline
└── Sends results back
```

**Advantages:**

- Easy development - Current implementation
- Full compute power - No hardware constraints
- Easy to test - Can iterate quickly

**Disadvantages:**

- Not truly wearable - Requires carrying laptop/phone
- Not production-ready - More of a prototype/demo

**Use Case:** Development, testing, demos

---

## Recommended Evolution Path

### Phase 1: Current (Development)

**Architecture:** CLI tool on laptop

- Easy to develop
- Full compute power
- Good for testing

### Phase 2: Web App (Current Development)

**Architecture:** Backend + Frontend

- Demo/prototype
- Demonstrates concept
- Easy to share
- Runs locally (for submission)

### Phase 3: Smartphone App (Next Step)

**Architecture:** Glasses ↔ Smartphone

- More realistic wearable implementation
- Phone performs processing
- Glasses are lightweight
- Current codebase adapted to mobile app

### Phase 4: Standalone Glasses (Future)

**Architecture:** Edge computing on glasses

- All processing on-device
- Truly wearable
- Requires hardware optimization
- Current codebase optimized for embedded systems

---

## Code Adaptation Strategy

### Current Codebase Value

The current codebase remains valuable because:

1. Core logic remains the same - YOLO tracking, BLIP captioning, LLM narration
2. Interface adaptation - Instead of CLI, use API/embedded interface
3. Optimization timing - Get it working first, optimize for hardware later

### Implementation Changes

**Current (CLI):**

```python
# Direct function calls
tracker.track(frame)
narrator.generate_narration(...)
```

**Web App (Current):**

```python
# API endpoints
@app.post("/api/narration")
async def narration(...):
    return narrator.generate_narration(...)
```

**Smartphone App (Future):**

```python
# Mobile API (same backend, mobile frontend)
# Or embedded in mobile app
```

**Wearable Glasses (Future):**

```python
# Embedded system
# Same functions, but optimized:
# - Quantized models
# - Lower precision
# - Hardware acceleration (NPU)
```

---

## Architecture Selection Criteria

The web application currently under development is not the final architecture. It serves as:

- A demo/prototype - Demonstrates the concept
- A learning step - Understands API design
- A submission requirement - Course project needs web interface
- A foundation - Code can be adapted later

The actual wearable glasses implementation would likely use:

- **Option 1 (Edge)** - If hardware is powerful enough
- **Option 2 (Smartphone)** - If easier development is preferred
- **Option 3 (Hybrid)** - If advanced features are required

---

## Summary

**Current Implementation:**

- Web app for demonstration and testing
- Runs locally for development

**Future Vision:**

- Standalone wearable glasses with edge computing, or
- Smartphone companion app
- Core ML pipeline remains the same
- Interface adapted for embedded systems

**Architecture Evolution:**

- Phase 1: CLI (development)
- Phase 2: Web app (demo/prototype) - Current phase
- Phase 3: Mobile app (realistic wearable)
- Phase 4: Embedded glasses (final product)

The web server setup is a stepping stone, not the final architecture. The core ML pipeline logic remains consistent across implementations, with only the interface layer requiring adaptation.
