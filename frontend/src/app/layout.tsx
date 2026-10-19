import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Relation Project — Encuentra a la persona indicada",
  description:
    "Describe tu necesidad y encuentra a las personas más indicadas para ayudarte.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
