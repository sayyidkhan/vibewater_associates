# Vibe Water Associates - Frontend

Next.js 14 frontend for the algorithmic trading platform.

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS v3
- **UI Components**: Custom components with Lucide icons
- **Charts**: Recharts
- **Flow Editor**: ReactFlow
- **HTTP Client**: Axios

## Getting Started

### Install Dependencies

```bash
npm install
```

### Configure Environment

```bash
cp env.example .env.local
# Edit .env.local with your API URL
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Dashboard (chat interface)
│   ├── builder/           # Visual strategy builder
│   ├── strategies/        # Strategy list and details
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── Header.tsx
│   ├── StrategyBuilder.tsx
│   └── ui/               # UI primitives
├── lib/                  # Utilities
│   ├── api.ts           # API client
│   └── utils.ts         # Helper functions
├── types/               # TypeScript types
└── public/              # Static assets
```

## Pages

- `/` - Dashboard with chat interface
- `/builder` - Visual strategy builder
- `/strategies` - Strategy library
- `/strategies/[id]` - Strategy analytics

## Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
