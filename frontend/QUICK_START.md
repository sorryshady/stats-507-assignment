# Frontend Quick Start Guide

## 🚀 Getting Started

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
cp .env.local.example .env.local
```

Edit `.env.local` if your backend runs on a different port.

### 3. Start Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## 📋 Prerequisites

- Backend server running on port 8000
- Ollama running with Llama 3.2 3B model
- Modern browser with camera support

## 🎯 Key Pages

- **/** - Landing page with features and hero section
- **/test** - Interactive test page with camera feed
- **/about** - Project information and tech stack
- **/roadmap** - Development phases and planned features
- **/demo** - Demo videos and getting started guide

## 🛠️ Development

### Adding Components

**shadcn/ui:**
```bash
npx shadcn@latest add [component-name]
```

**Aceternity UI:**
Copy components from https://ui.aceternity.com/components

### Project Structure

```
frontend/
├── app/              # Pages (App Router)
├── components/       # React components
│   ├── ui/          # shadcn/ui components
│   ├── aceternity/  # Aceternity UI components
│   └── test/        # Test page components
├── hooks/           # Custom React hooks
└── lib/             # Utilities and types
```

## 🐛 Troubleshooting

### Camera Permission Denied
- Check browser settings
- Use HTTPS in production (required for camera access)

### WebSocket Connection Failed
- Ensure backend is running on port 8000
- Check CORS settings in backend

### Build Errors
- Run `npm install` to ensure dependencies are installed
- Check TypeScript errors: `npm run build`

## 📦 Build for Production

```bash
npm run build
npm start
```

## 🔗 Links

- [Next.js Docs](https://nextjs.org/docs)
- [shadcn/ui](https://ui.shadcn.com)
- [Aceternity UI](https://ui.aceternity.com)

