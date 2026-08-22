import './globals.css';
import type { Metadata } from 'react';

export const metadata: Metadata = {
  title: 'Misinformation Radar',
  description: 'Detect structural anomalies and emotional bait instantly.',
};

export default function RootLayout({
  children,
}, {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}
