"use client";
import * as React from "react";
import { Alert, Button, Snackbar, TextField } from "@mui/material";

export default function Page() {
  const [description, setDescription] = React.useState("");
  const [keys, setKeys] = React.useState<any[]>([]);
  const [successMessage, setSuccessMessage] = React.useState("");
  const [severity, setSeverity] = React.useState<"success" | "error">("success");
  const [lastKey, setLastKey] = React.useState("");

  React.useEffect(() => {
    (async () => {
      const res = await fetch("/api/api-keys");
      const lkeys = await res.json();
      setKeys(lkeys);
    })();
  }, []);

  async function deleteKey(hashedKey: any) {
    const res = await fetch("/api/api-keys", { method: "DELETE", body: JSON.stringify({ hashedKey }) });
    const lkeys = await res.json();
    setSeverity("success");
    setSuccessMessage("Key successfully deleted");
    setKeys(lkeys);
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>API Keys</h1>
      <Snackbar
        open={!!successMessage}
        autoHideDuration={5000}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
        onClose={(event, reason) => setSuccessMessage("")}
      >
        <Alert onClose={() => setSuccessMessage("")} severity={severity} variant="filled" sx={{ width: "100%" }}>
          {successMessage}
        </Alert>
      </Snackbar>
      <TextField label="Description" value={description} onChange={(e) => setDescription(e.target.value)}></TextField>
      <Button
        onClick={async () => {
          const res = await fetch("/api/api-keys", {
            method: "POST",
            body: JSON.stringify({ description }),
            headers: {
              "Content-Type": "application/json",
            },
          });
          if (res.status !== 200) {
            console.error("Failed to create key", res.status);
            setSeverity("error");
            setSuccessMessage("Failed to create key");
            return;
          }
          setSeverity("success");
          setSuccessMessage("Key created and copied to clipboard");
          setDescription("");
          const keysData = await res.json();
          await navigator.clipboard.writeText(keysData.key);
          setLastKey(keysData.key);
          setKeys(keysData.keys);
        }}
      >
        Create
      </Button>
      <p></p>
      <table>
        <thead>
          <tr>
            <th style={{ textAlign: "left" }}>Created</th>
            <th style={{ textAlign: "left" }}>Description</th>
            <th style={{ textAlign: "left" }}>Key</th>
            <th style={{ textAlign: "left" }}>Expires</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {keys.map((key) => (
            <tr>
              <td>{key.created}</td>
              <td>{key.description}</td>
              <td>{key.partialKey}...</td>
              <td>{key.expires}</td>
              <td>
                <Button onClick={() => deleteKey(key.hashedKey)}>delete</Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
