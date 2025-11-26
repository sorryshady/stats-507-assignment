# Day 4: Frontend Setup & Test Page - Step-by-Step Guide

**Goal:** Create Next.js 16 frontend with shadcn/ui and Aceternity UI components

---

## 🎯 What We're Building Today

1. **Next.js 16 Project** - Modern React framework with App Router
2. **shadcn/ui Components** - Beautiful, accessible UI components
3. **Aceternity UI** - Cool animated components for flair
4. **Interactive Test Page** - Camera feed + WebSocket integration
5. **SaaS Website Design** - Professional, modern look

---

## 📚 Concepts to Understand

### Next.js 16 (App Router)
- File-based routing (`app/` directory)
- Server Components (default) vs Client Components (`'use client'`)
- Layouts and nested routes
- API routes (we won't need these - backend handles it)

### shadcn/ui
- Not a component library - copies components into your project
- Built on Radix UI primitives
- Fully customizable
- Uses Tailwind CSS

### Aceternity UI
- Pre-built animated components
- Copy-paste components
- Adds visual flair (animations, effects)

### WebSocket in React
- Use `useEffect` to manage WebSocket connection
- `useState` for connection state and data
- Cleanup on unmount

---

## 🏗️ Step 1: Initialize Next.js 16 Project

### Create Next.js App

```bash
cd "/Users/shady/Desktop/data science projects/final"
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"
```

**Options:**
- `--typescript` - TypeScript support
- `--tailwind` - Tailwind CSS
- `--app` - App Router (Next.js 13+)
- `--no-src-dir` - Files in root (simpler)
- `--import-alias "@/*"` - Import alias

**Your task:** Run this command and answer prompts:
- Use TypeScript? Yes
- Use ESLint? Yes
- Use Tailwind CSS? Yes (already included)
- Use `src/` directory? No
- Use App Router? Yes
- Customize import alias? @/*

---

## 🎨 Step 2: Install shadcn/ui

### Initialize shadcn/ui

```bash
cd frontend
npx shadcn@latest init
```

**Configuration:**
- Style: Default
- Base color: Slate
- CSS variables: Yes

**Your task:** Run init and accept defaults (or customize colors).

### Install Components We'll Need

```bash
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add badge
npx shadcn@latest add alert
npx shadcn@latest add skeleton
npx shadcn@latest add separator
```

**Your task:** Install these components one by one.

---

## ✨ Step 3: Set Up Aceternity UI

### Install Dependencies

```bash
cd frontend
npm install framer-motion clsx tailwind-merge
```

**Why:**
- `framer-motion` - Animations (Aceternity uses this)
- `clsx` - Conditional class names
- `tailwind-merge` - Merge Tailwind classes

### Create Utility Functions

**Create `frontend/lib/utils.ts`:**
```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

**Your task:** Create this file (shadcn might create it automatically).

---

## 🎭 Step 4: Add Aceternity UI Components

### Components We'll Use

1. **Animated Background** - Cool gradient effects
2. **Text Reveal** - Animated text
3. **3D Card** - 3D hover effects
4. **Spotlight** - Spotlight effect

**Your task:** We'll add these components as we build pages.

**Source:** https://ui.aceternity.com/components

---

## 🏠 Step 5: Create Layout & Navigation

### Root Layout (`app/layout.tsx`)

**Concept:** Root layout wraps all pages. Add:
- Metadata
- Fonts (Inter, etc.)
- Global styles
- Navigation component

**Your task:** Modify the default layout to include:
- Navigation bar
- Footer
- Beta badge

### Navigation Component (`components/Navigation.tsx`)

**Features:**
- Logo/brand name
- Links: Home, About, Roadmap, Demo, Test
- Beta badge
- Responsive (mobile menu)

**Your task:** Create navigation with shadcn components.

---

## 🎯 Step 6: Landing Page (`app/page.tsx`)

### Sections

1. **Hero Section**
   - Large headline
   - Subtitle
   - CTA button ("Try It Now")
   - Animated background (Aceternity)

2. **Features Section**
   - 3-4 feature cards
   - Icons
   - Descriptions

3. **Demo Video Section**
   - Embedded video or preview
   - Call to action

4. **Footer**
   - Links
   - Copyright

**Your task:** Build each section using shadcn components + Aceternity effects.

---

## 🧪 Step 7: Test Page (`app/test/page.tsx`)

**This is the main interactive page!**

### Components Needed

1. **CameraFeed Component**
   - WebRTC camera access
   - Video element
   - Start/Stop buttons

2. **TrackingOverlay Component**
   - Canvas overlay
   - Draw bounding boxes
   - Show detections

3. **NarrationPanel Component**
   - Show narration text
   - Loading state
   - Error handling

4. **HazardAlert Component**
   - Alert banner
   - Show when hazards detected
   - Auto-dismiss

5. **StatusPanel Component**
   - System status
   - Detection count
   - Connection status

**Your task:** We'll build these step by step.

---

## 🔌 Step 8: WebSocket Client

### Create WebSocket Hook (`hooks/useWebSocket.ts`)

**Concept:** Custom React hook for WebSocket connection.

**Features:**
- Connect/disconnect
- Send messages
- Receive messages
- Connection state
- Error handling
- Auto-reconnect

**Your task:** Create hook that:
- Connects to `ws://localhost:8000/api/ws/camera`
- Sends frames
- Receives results
- Updates state

---

## 📷 Step 9: Camera Access

### WebRTC Camera Hook (`hooks/useCamera.ts`)

**Concept:** Access user's camera via WebRTC.

**Features:**
- Request permission
- Start/stop camera
- Capture frames
- Convert to base64

**Your task:** Create hook that:
- Uses `navigator.mediaDevices.getUserMedia()`
- Captures video stream
- Converts frames to base64
- Sends to WebSocket

---

## 🎨 Step 10: Styling & Polish

### Tailwind Configuration

**Customize:**
- Colors (brand colors)
- Fonts
- Spacing
- Animations

### Aceternity Effects

**Add:**
- Animated backgrounds
- Text reveals
- Hover effects
- Transitions

**Your task:** Make it look professional and modern.

---

## 📝 Step-by-Step Implementation Order

1. **Setup** (Steps 1-3)
   - Next.js project
   - shadcn/ui
   - Aceternity dependencies

2. **Layout** (Step 5)
   - Navigation
   - Footer
   - Root layout

3. **Landing Page** (Step 6)
   - Hero section
   - Features
   - Demo section

4. **Test Page Foundation** (Step 7)
   - Page structure
   - Basic layout

5. **WebSocket Integration** (Step 8)
   - Custom hook
   - Connection logic

6. **Camera Integration** (Step 9)
   - Camera hook
   - Frame capture

7. **Components** (Step 7 continued)
   - Tracking overlay
   - Narration panel
   - Hazard alerts

8. **Polish** (Step 10)
   - Styling
   - Animations
   - Responsive design

---

## 🎓 Learning Checkpoints

After each step, verify:

1. **Next.js Setup:**
   - ✅ Project created
   - ✅ Dev server runs (`npm run dev`)
   - ✅ Can see default page

2. **shadcn/ui:**
   - ✅ Components installed
   - ✅ Can import and use Button, Card, etc.

3. **Layout:**
   - ✅ Navigation works
   - ✅ Links navigate correctly
   - ✅ Responsive on mobile

4. **WebSocket:**
   - ✅ Connects to backend
   - ✅ Sends/receives messages
   - ✅ Handles disconnections

5. **Camera:**
   - ✅ Requests permission
   - ✅ Shows video feed
   - ✅ Captures frames

---

## 🐛 Common Issues

### Issue: WebSocket Connection Refused
**Solution:** Make sure backend is running on port 8000

### Issue: Camera Permission Denied
**Solution:** Check browser permissions, use HTTPS in production

### Issue: CORS Errors
**Solution:** Backend CORS is configured, but check browser console

### Issue: Import Errors
**Solution:** Check import paths, use `@/` alias for components

---

## 📦 Dependencies Needed

```json
{
  "dependencies": {
    "next": "^16.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "framer-motion": "^11.0.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

---

## 🚀 Getting Started

**Ready to begin?** Start with Step 1: Initialize Next.js project!

**Command:**
```bash
cd "/Users/shady/Desktop/data science projects/final"
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"
```

---

**Good luck!** 🎉

