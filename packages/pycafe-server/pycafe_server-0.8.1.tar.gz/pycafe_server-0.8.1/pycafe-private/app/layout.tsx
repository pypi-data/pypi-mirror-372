"use client";
import "@/app/globals.css";
import { Inter } from "next/font/google";
import AutoTheme from "@/app/components/AutoTheme";
// import { Analytics } from "@vercel/analytics/react";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v13-appRouter";
import { UserAndSettingsProvider } from "@/components/user-server";
import * as React from "react";
import { settings } from "@/src/data";
import { useUser } from "@/src/user";

const inter = Inter({ subsets: ["latin"] });

// const title = `PyCafe: ${tagline}`;
// const description = "Playground for Python web frameworks. Run and edit Python code snippets for web frameworks in a web browser.";

// export const metadata = {
//   title,
//   description,
// };
function Body({ children }: { children: React.ReactNode }) {
  const user = useUser();
  const showBranding = !settings.noAnonBranding || user !== null;

  return (
    <body
      suppressHydrationWarning={true}
      className={`${inter.className}${showBranding ? " jc-branding" : ""} jc-private`}
      style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}
    >
      {children}
    </body>
  );
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <AppRouterCacheProvider>
      <AutoTheme>
        <html lang="en">
          <UserAndSettingsProvider>
            <Body>{children}</Body>
            {/* <Analytics /> */}
          </UserAndSettingsProvider>
        </html>
      </AutoTheme>
    </AppRouterCacheProvider>
  );
}
