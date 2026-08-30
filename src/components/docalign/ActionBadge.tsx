import { ACTION_LABELS, type ChangeAction } from "@/lib/docalign/types";
import { cn } from "@/lib/utils";

const STYLES: Record<ChangeAction, string> = {
  none: "bg-success/10 text-success border-success/30",
  modify: "bg-warn/10 text-warn border-warn/30",
  add: "bg-danger/10 text-danger border-danger/30",
  move: "bg-info/10 text-info border-info/30",
  remove: "bg-plum/10 text-plum border-plum/30",
};

export function ActionBadge({ action, className }: { action: ChangeAction; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium whitespace-nowrap",
        STYLES[action],
        className,
      )}
    >
      {ACTION_LABELS[action]}
    </span>
  );
}
