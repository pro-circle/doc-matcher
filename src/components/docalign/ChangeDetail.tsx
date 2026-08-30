import { X } from "lucide-react";
import { CATEGORY_LABELS, type ChangeItem } from "@/lib/docalign/types";
import { ActionBadge } from "./ActionBadge";

function Block({ title, body }: { title: string; body: string }) {
  return (
    <div>
      <p className="text-xs font-semibold tracking-[0.16em] text-muted-foreground uppercase">
        {title}
      </p>
      <div className="mt-2 border-t border-border pt-2" />
      <p className="text-sm whitespace-pre-wrap text-foreground">{body}</p>
    </div>
  );
}

export function ChangeDetail({ change, onClose }: { change: ChangeItem; onClose: () => void }) {
  return (
    <aside className="sticky top-6 rounded-2xl border border-border bg-card p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold tracking-[0.16em] text-muted-foreground uppercase">
            {CATEGORY_LABELS[change.category]}
          </p>
          <h2 className="font-display mt-1 text-lg font-semibold text-foreground">
            {change.section}
          </h2>
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close detail"
          className="rounded-md p-1 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
        >
          <X className="size-4" />
        </button>
      </div>

      <div className="mt-6 space-y-5">
        <Block title="Master Document" body={change.master} />
        <Block title="Document to Verify" body={change.document} />

        <div>
          <p className="text-xs font-semibold tracking-[0.16em] text-muted-foreground uppercase">
            Status
          </p>
          <div className="mt-2 border-t border-border pt-2">
            <ActionBadge action={change.action} />
          </div>
        </div>

        <Block title="Recommendation" body={change.change} />
        <Block title="Reason" body={change.reason} />

        <div className="flex items-center justify-between border-t border-border pt-4 text-xs text-muted-foreground">
          <span>Severity: {change.severity}</span>
          <span>Confidence: {Math.round(change.confidence * 100)}%</span>
        </div>
      </div>
    </aside>
  );
}
