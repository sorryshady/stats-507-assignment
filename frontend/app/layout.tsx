import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navigation } from "@/components/Navigation";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: {
    default: "Describe My Environment | AI-Powered Visual Assistant",
    template: "%s | Describe My Environment",
  },
  description:
    "Real-time object detection and AI-powered narration for visually impaired users. Navigate your environment with confidence using advanced machine learning, YOLO tracking, and natural language descriptions.",
  keywords: [
    "AI vision assistant",
    "object detection",
    "computer vision",
    "accessibility technology",
    "visual impairment",
    "assistive technology",
    "real-time detection",
    "YOLO",
    "AI narration",
    "safety alerts",
    "machine learning",
    "Llama 3.2",
    "BLIP",
    "accessibility",
  ],
  authors: [{ name: "Akhil Nishad" }],
  creator: "Akhil Nishad",
  publisher: "Akhil Nishad",
  metadataBase: new URL("https://stats-507-assignment.vercel.app"),
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://stats-507-assignment.vercel.app",
    siteName: "Describe My Environment",
    title: "Describe My Environment | See Your World Through AI",
    description:
      "Real-time object detection and AI-powered narration for visually impaired users. Navigate your environment with confidence using advanced machine learning.",
    images: [
      {
        url: "/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "Describe My Environment - AI-Powered Visual Assistant",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Describe My Environment | See Your World Through AI",
    description:
      "Real-time object detection and AI-powered narration for visually impaired users. Navigate your environment with confidence.",
    images: ["/og-image.jpg"],
    creator: "@akhil_nishad_01",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  category: "Technology",
  classification: "Accessibility Technology",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <meta name="theme-color" content="#1E1B4B" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta
          name="apple-mobile-web-app-status-bar-style"
          content="black-translucent"
        />
        <meta name="apple-mobile-web-app-title" content="VisionAI" />
      </head>
      <body className={`${inter.variable} font-sans antialiased`}>
        <Navigation />
        <main className="pt-16 min-h-screen">{children}</main>
      </body>
    </html>
  );
}
