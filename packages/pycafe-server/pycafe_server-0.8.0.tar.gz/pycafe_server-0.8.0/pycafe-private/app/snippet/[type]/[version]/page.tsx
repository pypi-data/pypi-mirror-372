import * as React from "react";
import { Metadata, ResolvingMetadata } from "next";
import { App } from "@/components/app";
import { fetchProjectById } from "@/src/database";
import { makeProjectMetadata } from "@/src/utils";
import { CheckUser } from "./wrapper";

export const dynamic = "force-static";

type Props = {
  params: { type: string; version: string };
  searchParams: { [key: string]: string | string[] | undefined };
};

const types = ["solara", "dash", "vizro", "streamlit", "shiny", "panel"];
export async function generateStaticParams() {
  return types.map((type) => {
    return { type, version: "v1" };
  });
}

export async function generateMetadata({ params, searchParams }: Props, parent: ResolvingMetadata): Promise<Metadata> {
  const id = params.type;
  const projectId = searchParams.projectId;

  if (typeof projectId == "string") {
    const project = await fetchProjectById({ projectId });
    return makeProjectMetadata(project);
  }

  return {
    title: "PyCafe",
    openGraph: {
      images: ["https://py.cafe/coffeecup.gif"],
    },
  };
}

export default function Page({ params, searchParams }: Props) {
  return (
    <CheckUser>
      <App searchParams={searchParams} type={params.type} version={params.version} />
    </CheckUser>
  );
}
