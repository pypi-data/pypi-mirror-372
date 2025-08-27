"use client";
import * as React from "react";
import { ProjectPageProps, ProjectState } from "@/src/types";
import { getIconByType } from "@/components/dashboard";
import { useTheme } from "@mui/material/styles";
import { Button, Icon, Theme, useMediaQuery } from "@mui/material";
import "material-icons/iconfont/material-icons.css";
import { frameworks, settings, tagline } from "@/src/data";
import { useUser } from "@/src/user";
import { CardButton } from "@/app/components/cardbutton";
import Header from "@/app/components/header";
import { FileDrop } from "@/components/filedrop";
import { Signature } from "@/app/view/page";
import { CheckUser } from "./snippet/[type]/[version]/wrapper";
import { ProjectAppView } from "@/components/app";
import { verifyProject } from "@/src/sign";

export const dynamic = "force-static";

function CreateProjectBanner(props: { theme: Theme; isMobile?: boolean; showDescription?: boolean }) {
  const showDescription = props.showDescription ?? false;
  const isMobile = props.isMobile ?? false;
  const darkMode = props.theme.palette.mode === "dark";
  const user = useUser();
  // either no logging in is configured (trial), or the user is an editor
  const canEdit = !user || user.info.is_editor;
  return (
    <div className="create-banner">
      <h2>{canEdit ? "Open the editor to create a new app" : "You are not an editor, and cannot create projects"}</h2>
      {!canEdit && settings.becomeEditorUrl && (
        <h2>
          Get editor access{" "}
          <a href={settings.becomeEditorUrl} target="_blank" style={{ color: "var(--header-logo-color)" }}>
            here
          </a>
        </h2>
      )}
      <div className="create-buttons">
        {canEdit &&
          settings.frameworks.map((frameworkName) => {
            const framework = frameworks[frameworkName];
            return (
              <a
                href={`/snippet/${framework.appType}/v1`}
                key={framework.appType}
                style={{ textDecoration: "none", color: "unset", display: "flex" }}
              >
                <CardButton
                  title={framework.name}
                  description={showDescription ? framework.description2 : ""}
                  isMobile={isMobile}
                  image={getIconByType(framework.appType, showDescription, darkMode)}
                  actionIcon="add"
                  disabled={!canEdit}
                />
              </a>
            );
          })}
      </div>
    </div>
  );
}

export default function Page({ params, searchParams }: ProjectPageProps, appview: boolean = false) {
  const theme = useTheme();
  const user = useUser();
  const isMobile = useMediaQuery("(max-width: 1200px)");

  const [projectState, setProjectState] = React.useState<ProjectState | null>(null);
  const [signature, setSignature] = React.useState<Signature>(null);
  const [editing, setEditing] = React.useState(false);

  React.useEffect(() => {
    console.info("listening for messages");
    window.parent.postMessage("ready", "*");
    const onMsg = async (event: MessageEvent) => {
      if (event.data.type === "loadProject") {
        const projectData = event.data.projectData;
        const signatureJwt = projectData.signatureJwt;
        if (window === window.top) {
          setEditing(true);
        }
        if (signatureJwt === null) {
          setProjectState(projectData.projectState);
          setSignature("trial");
          return;
        }
        const signatureCorrect = await verifyProject(projectData.projectState, signatureJwt);
        if (signatureCorrect) {
          setProjectState(projectData.projectState);
          setSignature("valid");
        } else {
          setSignature("invalid");
        }
      }
    };
    window.addEventListener("message", onMsg);
    return () => {
      window.removeEventListener("message", onMsg);
    };
  }, []);

  return (
    <>
      {settings.trialmode && (
        <h3
          style={{
            textAlign: "center",
            backgroundColor: "var(--color-primary)",
            padding: "1em 0",
            margin: "0",
          }}
        >
          PyCafe server is running in trial mode, please obtain a license key at{" "}
          <a href="https://py.cafe/contact" target="_blank" style={{ color: "var(--header-logo-color)" }}>
            PyCafe
          </a>
          <Icon style={{ marginLeft: "0.4em", verticalAlign: "text-bottom" }}>keyboard_double_arrow_right</Icon>
        </h3>
      )}
      {!projectState && (
        <>
          <Header noBranding={settings.noAnonBranding && user === null} subtitle={tagline} />
          {!settings.requireAuth || (user && user.info.is_editor) ? (
            <div style={{ textAlign: "right", paddingRight: "28px" }}>
              <a href="/api-keys" style={{ color: "var(--header-logo-color)" }}>
                API Keys
              </a>
            </div>
          ) : null}
          <div className="hero">
            {!settings.requireAuth || user ? <CreateProjectBanner theme={theme} showDescription={true} isMobile={isMobile} /> : null}
            {!settings.requireAuth || user ? null : (
              <Button variant="contained" color="primary" href="/_login">
                Sign in
              </Button>
            )}
          </div>
        </>
      )}
      {(!settings.requireAuth || user) && !projectState ? (
        <FileDrop
          file={undefined}
          setExternalStates={(projectState, signature, enableEditing) => {
            setProjectState(projectState);
            setSignature(signature);
            setEditing(enableEditing);
          }}
        />
      ) : null}
      {signature === "invalid" && <h1>Error: Invalid signature</h1>}
      {projectState && editing ? (
        <CheckUser>
          <ProjectAppView initialProjectState={projectState} initialAppState={{ appView: false, sidebar: false, editEnable: true }} />
        </CheckUser>
      ) : null}
    </>
  );
  // return <App type="solara" version="v1" />;
  // return <h1>hi</h1>
}
