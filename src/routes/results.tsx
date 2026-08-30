import { useMemo, useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowLeft, Copy, Printer } from "lucide-react";
import { ScoreHeader } from "@/components/docalign/ScoreHeader";
import { MasterProfilePanel } from "@/components/docalign/MasterProfilePanel";
import { ChangeTable } from "@/components/docalign/ChangeTable";
import { ChangeDetail } from "@/components/docalign/ChangeDetail";
import { useReport } from "@/lib/docalign/store";
import {
  ACTION_LABELS,
  CATEGORY_LABELS,
  type ChangeAction,
  type CategoryKey,
  type ChangeItem,
} from "@/lib/docalign/types";

export const Route = createFileRoute("/results")({
  head: () => ({
    meta: [
      { title: "Alignment Report — DocAlign" },
      {
        name: "description",
        content:
          "Alignment score by category plus a table of the exact structural, typographic and semantic changes required to match the master document.",
      },
      { property: "og:title", content: "Alignment Report — DocAlign" },
      {
        property: "og:description",
        content: "Category scores and actionable changes for your document to verify.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: ResultsPage,
});

const ACTIONS: ChangeAction[] = ["modify", "add", "move", "remove", "none"];

function ResultsPage() {
  const report = useReport();
  const [action, setAction] = useState<ChangeAction | "all">("all");
  const [category, setCategory] = useState<CategoryKey | "all">("all");
  const [hideNoChange, setHideNoChange] = useState(true);
  const [selected, setSelected] = useState<ChangeItem | null>(null);

  const changes = useMemo(() => {
    if (!report) return [];
    return report.changes.filter((item) => {
      if (hideNoChange && item.action === "none") return false;
      if (action !== "all" && item.action !== action) return false;
      if (category !== "all" && item.category !== category) return false;
      return true;
    });
  }, [report, action, category, hideNoChange]);

  if (!report) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4 px-6 text-center">
        <h1 className="font-display text-2xl font-semibold text-foreground">No report loaded</h1>
        <p className="text-sm text-muted-foreground">
          Upload a master document and a document to verify to generate a report.
        </p>
        <Link
          to="/"
          className="mt-2 inline-flex h-10 items-center justify-center rounded-full bg-primary px-6 text-sm font-semibold text-primary-foreground"
        >
          Start an analysis
        </Link>
      </main>
    );
  }

  function copyReport() {
    const lines = report!.changes.map(
      (item) =>
        `${item.section} | ${ACTION_LABELS[item.action]} | ${item.change} (${CATEGORY_LABELS[item.category]})`,
    );
    void navigator.clipboard.writeText(
      `DocAlign — ${Math.round(report!.overall_score)}% ${report!.verdict}\n\n${lines.join("\n")}`,
    );
  }

  return (
    <main className="mx-auto w-full max-w-6xl px-6 py-12">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="size-4" aria-hidden />
          New analysis
        </Link>
        <div className="flex gap-2 print:hidden">
          <button
            type="button"
            onClick={copyReport}
            className="inline-flex h-9 items-center gap-2 rounded-full border border-border px-4 text-sm text-foreground transition-colors hover:bg-muted"
          >
            <Copy className="size-3.5" aria-hidden />
            Copy report
          </button>
          <button
            type="button"
            onClick={() => window.print()}
            className="inline-flex h-9 items-center gap-2 rounded-full border border-border px-4 text-sm text-foreground transition-colors hover:bg-muted"
          >
            <Printer className="size-3.5" aria-hidden />
            Print
          </button>
        </div>
      </div>

      <div className="mt-6 space-y-6">
        <ScoreHeader
          score={report.overall_score}
          verdict={report.verdict}
          categories={report.categories}
        />

        <p className="text-xs text-muted-foreground">
          Master: <span className="text-foreground">{report.master_file}</span> · Document:{" "}
          <span className="text-foreground">{report.document_file}</span>
        </p>

        <MasterProfilePanel profile={report.master_profile} />

        <div className="flex flex-wrap items-center gap-2 print:hidden">
          <FilterChip active={action === "all"} onClick={() => setAction("all")}>
            All actions
          </FilterChip>
          {ACTIONS.map((value) => (
            <FilterChip
              key={value}
              active={action === value}
              onClick={() => setAction(action === value ? "all" : value)}
            >
              {ACTION_LABELS[value]}
            </FilterChip>
          ))}
          <span className="mx-2 h-5 w-px bg-border" />
          <FilterChip active={category === "all"} onClick={() => setCategory("all")}>
            All categories
          </FilterChip>
          {(Object.keys(CATEGORY_LABELS) as CategoryKey[]).map((value) => (
            <FilterChip
              key={value}
              active={category === value}
              onClick={() => setCategory(category === value ? "all" : value)}
            >
              {CATEGORY_LABELS[value]}
            </FilterChip>
          ))}
          <label className="ml-auto flex items-center gap-2 text-xs text-muted-foreground">
            <input
              type="checkbox"
              checked={hideNoChange}
              onChange={(event) => setHideNoChange(event.target.checked)}
              className="size-3.5 accent-[var(--accent)]"
            />
            Hide no-change rows
          </label>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_20rem]">
          <ChangeTable changes={changes} onSelect={setSelected} selectedId={selected?.id} />
          {selected && (
            <div className="print:hidden">
              <ChangeDetail change={selected} onClose={() => setSelected(null)} />
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

function FilterChip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-full border px-3 py-1 text-xs transition-colors ${
        active
          ? "border-transparent bg-primary text-primary-foreground"
          : "border-border text-muted-foreground hover:bg-muted"
      }`}
    >
      {children}
    </button>
  );
}
