"use client";
import { settings } from "@/src/data";
import { useUser } from "@/src/user";
import { Button } from "@mui/material";

export function CheckUser({ children }: { children: React.ReactNode }) {
  const user = useUser();
  if (settings.requireAuth && user === null) {
    return (
      <Button variant="contained" color="primary" href={`/_login?next_url=${window.location.pathname}`}>
        Sign in
      </Button>
    );
  }
  const canEdit = !user || user.info.is_editor;
  if (!canEdit) {
    return <h2>You are not an editor, and cannot create projects</h2>;
  }
  return children;
}
