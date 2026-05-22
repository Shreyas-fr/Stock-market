import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Supply Chain Intelligence Platform',
  description: 'AI-powered supply chain, financial, and government policy intelligence. Monitor risks, track policies, and analyze global supply chains in real-time.',
  keywords: 'supply chain, risk intelligence, financial analysis, government policy, stock market, AI analytics',
  authors: [{ name: 'SCI Platform' }],
  openGraph: {
    title: 'Supply Chain Intelligence Platform',
    description: 'AI-powered intelligence for global supply chains',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="animated-gradient min-h-screen">
        {children}
      </body>
    </html>
  );
}
