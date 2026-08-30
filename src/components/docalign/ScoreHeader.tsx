import type { CategoryScore } from "@/lib/docalign/types";

function band(score: number) {
  if (score >= 90) return "text-success";
  if (score >= 75) return "text-warn";
  return "text-danger";
}

function barBand(score: number) {
  if (score >= 90) return "bg-success";
  if (score >= 75) return "bg-warn";
  return "bg-danger";
}

interface ScoreHeaderProps {
  score: number;
  verdict: string;
  categories: CategoryScore[];
}

export function ScoreHeader({ score, verdict, categories }: ScoreHeaderProps) {
  return (
    <section className="rounded-2xl border border-border bg-card p-8">
      <p className="text-xs font-semibold tracking-[0.22em] text-muted-foreground uppercase">
        Document Alignment
      </p>
      <div className="mt-4 flex flex-wrap items-end gap-4">
        <span className={`font-display text-6xl leading-none font-bold ${band(score)}`}>
          {Math.round(score)}%
        </span>
        <span className="pb-1 text-sm font-semibold tracking-[0.18em] text-muted-foreground uppercase">
          {verdict}
        </span>
      </div>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {categories.map((category) => (
          <div key={category.key}>
            <div className="flex items-baseline justify-between text-sm">
              <span className="text-foreground">{category.label}</span>
              <span className="tabular-nums text-muted-foreground">
                {Math.round(category.score)}%
              </span>
            </div>
            <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-muted">
              <div
                className={`h-full rounded-full ${barBand(category.score)}`}
                style={{ width: `${Math.max(0, Math.min(100, category.score))}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
