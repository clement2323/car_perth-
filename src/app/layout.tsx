import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Achat Voiture Perth WA',
  description: 'Dashboard d\'aide à l\'achat de voiture d\'occasion à Perth, Australie',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  )
}
