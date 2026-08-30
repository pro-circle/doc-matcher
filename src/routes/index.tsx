import { useState } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { ArrowDown, Loader2 } from "lucide-react";
import { DropZone } from "@/components/docalign/DropZone";
import { analyzeDocuments } from "@/lib/docalign/api";
import { demoReport } from "@/lib/docalign/demo";
import { setReport } from "@/lib/docalign/store";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "DocAlign — AI Document Alignment Checker" },
      {
        name: "description",
        content:
          "Upload a master document and a document to verify. DocAlign checks structure, typography, layout, formatting, visuals and meaning, then lists the exact changes to make.",
      },
      { property: "og:title", content: "DocAlign — AI Document Alignment Checker" },
      {
        property: "og:description",
        content:
          "Check whether a document follows your master document's structure, style and meaning — and get actionable changes.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: UploadPage,
});

const STAGES = [
  "Analyzing master…",
  "Analyzing document…",
  "Comparing against master profile…",
  "Building report…",
];

function UploadPage() {
  const navigate = useNavigate();
  const [master, setMaster] = useState<File | null>(null);
  const [child, setChild] = useState<File | null>(null);
  const [stage, setStage] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const running = stage !== null;

  async function runAnalysis() {
    if (!master || !child) return;
    setError(null);
    setStage(0);
    const timers = [
      setTimeout(() => setStage(1), 1200),
      setTimeout(() => setStage(2), 3000),
      setTimeout(() => setStage(3), 5200),
    ];
    try {
      const report = await analyzeDocuments(master, child);
      setReport(report);
      navigate({ to: "/results" });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Analysis failed.");
    } finally {
      timers.forEach(clearTimeout);
      setStage(null);
    }
  }

  function openDemo() {
    setReport(demoReport);
    navigate({ to: "/results" });
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-2xl flex-col items-center px-6 py-20">
      <header className="text-center">
        <h1 className="font-display text-4xl font-bold tracking-tight text-foreground">DocAlign</h1>
        <p className="mt-2 text-sm tracking-[0.16em] text-muted-foreground uppercase">
          AI Document Alignment Checker
        </p>
      </header>

      <div className="mt-14 w-full space-y-6">
        <DropZone
          label="Master Document"
          hint="Drop PDF / DOCX here"
          accept={[".pdf", ".docx"]}
          file={master}
          onFile={setMaster}
        />

        <div className="flex justify-center">
          <ArrowDown className="size-5 text-muted-foreground" aria-hidden />
        </div>

        <DropZone
          label="Document to Verify"
          hint="Drop DOCX here"
          accept={[".docx"]}
          file={child}
          onFile={setChild}
        />
      </div>

      <button
        type="button"
        onClick={runAnalysis}
        disabled={!master || !child || running}
        className="mt-10 inline-flex h-11 w-48 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {running ? <Loader2 className="size-4 animate-spin" aria-hidden /> : "Analyze"}
      </button>

      {running && (
        <p className="mt-4 text-sm text-muted-foreground" aria-live="polite">
          {STAGES[stage]}
        </p>
      )}

      {error && (
        <div className="mt-6 w-full rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
          {error}
        </div>
      )}

      <button
        type="button"
        onClick={openDemo}
        className="mt-8 text-xs text-muted-foreground underline underline-offset-4 transition-colors hover:text-foreground"
      >
        View a sample report
      </button>
    </main>
  );
}
