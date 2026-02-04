# Bus Route Analytics Dashboard

An advanced, interactive Next.js dashboard for analyzing and visualizing Baku's public bus transport network.

## Features

- **Interactive Map Visualization**: Advanced Leaflet-based map showing all bus routes with color-coded performance indicators
- **Real-time Filtering**: Filter routes by carrier, region, speed, length, and more
- **Performance Analytics**: Comprehensive KPIs including speed, coverage, efficiency metrics
- **Strategic Insights**: Business intelligence charts for carrier performance, route distribution, and network optimization
- **Responsive Design**: Fully responsive interface that works on desktop, tablet, and mobile
- **Route Details**: Detailed view of individual routes with stops, coordinates, and performance data

## Tech Stack

- **Framework**: Next.js 15+ with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Maps**: React Leaflet
- **Charts**: Recharts
- **State Management**: Zustand
- **Icons**: Lucide React
- **Deployment**: Vercel

## Getting Started

### Prerequisites

- Node.js 18.x or higher
- npm or yarn

### Installation

1. Install dependencies:
\`\`\`bash
npm install
\`\`\`

2. Run the development server:
\`\`\`bash
npm run dev
\`\`\`

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Deployment to Vercel

### Method 1: Using Vercel CLI

1. Install Vercel CLI:
\`\`\`bash
npm i -g vercel
\`\`\`

2. Login to Vercel:
\`\`\`bash
vercel login
\`\`\`

3. Deploy:
\`\`\`bash
vercel
\`\`\`

For production deployment:
\`\`\`bash
vercel --prod
\`\`\`

### Method 2: Using Vercel Dashboard

1. Push your code to GitHub/GitLab/Bitbucket
2. Visit [vercel.com](https://vercel.com)
3. Click "Add New Project"
4. Import your repository
5. Configure project settings (Vercel will auto-detect Next.js)
6. Click "Deploy"

## Data Structure

The dashboard processes the following bus route data:
- 208 bus routes
- 11,786 stops
- 7,745 km total network coverage
- Route coordinates, speeds, carriers, and performance metrics

## Key Features

### Interactive Map
- Click on any route to see detailed information
- Routes color-coded by speed (green = fast, yellow = medium, red = slow)
- View stops and transport hubs
- Zoom and pan to explore the network

### Filtering System
- Filter by carrier (top 10 carriers available)
- Filter by region
- Filter by speed range
- Filter by route length
- Combine multiple filters for precise analysis

### Analytics Charts
- Speed Distribution
- Route Length Distribution
- Top Carriers Performance

---

**Built with** Next.js, React, TypeScript, Tailwind CSS, Leaflet, and Recharts
