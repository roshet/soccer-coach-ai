import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Soccer Coach",
  description: "Professional biomechanical technique analysis powered by AI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-950 text-white min-h-screen`}>
        <header className="border-b border-gray-800 px-6 py-4">
          <div className="max-w-4xl mx-auto flex items-center gap-3">
            <span className="text-2xl">⚽</span>
            <h1 className="text-xl font-bold">AI Soccer Coach</h1>
            <span className="ml-auto text-sm text-gray-400">Professional Technique Analysis</span>
          </div>
        </header>
        <main className="max-w-4xl mx-auto px-6 py-10">{children}</main>
      </body>
    </html>
  );
}
