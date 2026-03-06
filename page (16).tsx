import type { Metadata } from 'next';
import './globals.css';
import { Providers } from '@/components/Providers';

export const metadata: Metadata = {
  title: 'ZOARIA — Veterinary Ecosystem',
  description: 'The complete digital platform for pet healthcare, consultations, nutrition, and medical tracking.',
  icons: { icon: '/favicon.ico' },
  openGraph: {
    title: 'ZOARIA',
    description: 'Complete veterinary ecosystem for pet owners and veterinarians',
    type: 'website',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
