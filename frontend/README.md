# Frontend - Describe My Environment

Next.js 16 frontend application with shadcn/ui and Aceternity UI components.

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend server running on port 8000

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.local.example .env.local

# Start development server
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Landing page
│   ├── test/              # Interactive test page
│   ├── about/             # About page
│   ├── roadmap/           # Roadmap page
│   └── demo/              # Demo page
├── components/
│   ├── ui/                # shadcn/ui components
│   ├── aceternity/        # Aceternity UI components
│   └── test/              # Test page components
├── hooks/                 # React hooks
│   ├── useCamera.ts       # Camera access hook
│   └── useWebSocket.ts    # WebSocket hook
└── lib/                   # Utilities
    ├── utils.ts           # Utility functions
    └── types/             # TypeScript types
```

## Features

- **Modern UI**: Built with Next.js 16, shadcn/ui, and Aceternity UI
- **Real-time Camera Feed**: WebRTC camera access
- **Object Tracking**: Real-time detection overlay
- **Hazard Alerts**: Visual alerts for detected hazards
- **AI Narration**: Generate scene descriptions
- **System Status**: Backend status monitoring

## Environment Variables

Create a `.env.local` file with:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/ws/camera
```

## Development

### Adding shadcn/ui Components

```bash
npx shadcn@latest add [component-name]
```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Tech Stack

- **Next.js 16** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **Aceternity UI** - Animated components
- **Framer Motion** - Animations
- **WebSocket** - Real-time communication
- **WebRTC** - Camera access
