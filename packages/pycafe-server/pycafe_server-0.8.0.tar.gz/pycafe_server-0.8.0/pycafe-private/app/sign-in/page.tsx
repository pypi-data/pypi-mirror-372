"use client";
import React from "react";

export default function Page() {
  React.useEffect(() => {
    if (window.opener) {
      window.opener.postMessage({ type: "sign-in:loaded" }, "*");
      // we can close ourselves, because we let the parent know we are loaded
      window.close();
    }
  }, []);
  return <>Checking your credentials...</>;
}
