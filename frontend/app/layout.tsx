import "./globals.css";
import React from "react";

export const metadata = {
  title: "GroundTrace | Enterprise RAG & Context Engineering Platform",
  description: "Enterprise RAG platform with FastEmbed semantic vector indexing, context engineering, grounded source citations, and microservice log troubleshooting.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#0B0F19] text-gray-100 min-h-screen relative flex flex-col justify-between selection:bg-emerald-600 selection:text-white">
        <header className="border-b border-gray-800/80 bg-gray-900/60 backdrop-blur-md sticky top-0 z-40">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-emerald-500 via-teal-600 to-cyan-600 flex items-center justify-center font-bold text-white shadow-lg shadow-emerald-500/20">
                GT
              </div>
              <div>
                <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
                  GroundTrace
                </span>
                <span className="ml-2 text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  RAG & LogOps v1.0
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <a
                href="https://github.com/TejdeepKodati/groundtrace"
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-gray-800/80 hover:bg-gray-700/80 text-gray-300 hover:text-white transition-all border border-gray-700 flex items-center space-x-2"
              >
                <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                  <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
                </svg>
                <span>GitHub Repository</span>
              </a>
            </div>
          </div>
        </header>

        <main className="flex-grow">
          {children}
        </main>

        <footer className="py-4 px-6 border-t border-gray-800/80 bg-gray-950/80 backdrop-blur-sm text-xs text-gray-400 flex flex-col sm:flex-row justify-between items-center gap-3">
          <p>© 2026 GroundTrace Systems. Enterprise Grounded RAG & Telemetry Diagnostics.</p>
          <a
            href="https://github.com/TejdeepKodati/groundtrace"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 hover:border-emerald-400 transition-all font-medium text-xs shadow-sm"
          >
            <span>made with ♥ by Tejdeep</span>
          </a>
        </footer>

        {/* Floating bottom-right permanent badge */}
        <div className="fixed bottom-3 right-3 z-50">
          <a
            href="https://github.com/TejdeepKodati/groundtrace"
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-1.5 bg-gray-900/90 hover:bg-gray-800 text-emerald-400 text-xs font-semibold rounded-full border border-emerald-500/40 shadow-xl backdrop-blur-md flex items-center space-x-1.5 hover:scale-105 transition-transform"
          >
            <span>made with ♥ by Tejdeep</span>
          </a>
        </div>
      </body>
    </html>
  );
}
