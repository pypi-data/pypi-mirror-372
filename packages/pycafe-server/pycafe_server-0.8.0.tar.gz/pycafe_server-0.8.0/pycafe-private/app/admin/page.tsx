"use client";

import { settings } from "@/src/data";
import { useUser } from "@/src/user";
import { Button, Tooltip } from "@mui/material";
import useSWR from "swr";

export type Login = {
  user_id: string;
  email: string;
  userinfo: string;
  datetime: string;
  is_admin: boolean;
  is_editor: boolean;
};

const fetcher = async (...args: any[]): Promise<Login[]> => {
  //@ts-ignore
  const res = await fetch(...args);
  if (!res.ok) {
    throw new Error("Failed to fetch logins");
  }
  const data = await res.json();
  return data["logins"] as Login[];
};

export default function Page() {
  const user = useUser();
  const { data, error, isLoading } = useSWR("/api/logins", fetcher);
  if (settings.requireAuth) {
    if (user === null) {
      return (
        <Button variant="contained" color="primary" href={`/_login?next_url=${window.location.pathname}`}>
          Sign in
        </Button>
      );
    }
    if (!user.info.is_admin) {
      return <h1>requires admin privileges</h1>;
    }
  }

  if (isLoading) return <h1>Loading...</h1>;
  if (error) return <h1>Error: {`${error}`}</h1>;
  if (!data) return <h1>No data</h1>;

  return (
    <div>
      <h1>Admin</h1>
      <h2>Info</h2>
      Instance ID: {settings.instanceId}
      <h2>Logins</h2>
      <>Last login, per user, per day:</>
      <table>
        <thead>
          <tr>
            <th>user_id</th>
            <th>email</th>
            {/* <th>userinfo</th> */}
            <th>datetime</th>
            <th>is_admin</th>
            <th>is_editor</th>
          </tr>
        </thead>
        <tbody>
          {data.map((login) => {
            const userInfo = JSON.stringify(login.userinfo);

            return (
              <tr key={login.user_id}>
                <td>{login.user_id}</td>
                <td>{login.email}</td>
                {/* <td style={{ maxWidth: "200px", maxHeight: "30px", overflow: "hidden" }}>
                  <Tooltip title={userInfo}>
                    <p>{userInfo}</p>
                  </Tooltip>
                </td> */}
                <td>{`${login.datetime}`}</td>
                <td>{login.is_admin.toString()}</td>
                <td>{login.is_editor.toString()}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
