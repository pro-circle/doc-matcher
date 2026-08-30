import type { ChangeItem } from "@/lib/docalign/types";
import { CATEGORY_LABELS } from "@/lib/docalign/types";
import { ActionBadge } from "./ActionBadge";

interface ChangeTableProps {
  changes: ChangeItem[];
  onSelect: (change: ChangeItem) => void;
  selectedId?: string | null;
}

export function ChangeTable({ changes, onSelect, selectedId }: ChangeTableProps) {
  if (changes.length === 0) {
    return (
      <div className="rounded-2xl border border-border bg-card p-10 text-center text-sm text-muted-foreground">
        No items match the current filters.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-border bg-card">
      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b border-border bg-muted/50">
            <th className="px-5 py-3 text-xs font-semibold tracking-[0.14em] text-muted-foreground uppercase">
              Section
            </th>
            <th className="hidden px-5 py-3 text-xs font-semibold tracking-[0.14em] text-muted-foreground uppercase md:table-cell">
              Master
            </th>
            <th className="hidden px-5 py-3 text-xs font-semibold tracking-[0.14em] text-muted-foreground uppercase md:table-cell">
              Document
            </th>
            <th className="px-5 py-3 text-xs font-semibold tracking-[0.14em] text-muted-foreground uppercase">
              Change required
            </th>
          </tr>
        </thead>
        <tbody>
          {changes.map((change) => (
            <tr
              key={change.id}
              onClick={() => onSelect(change)}
              className={`cursor-pointer border-b border-border/70 align-top transition-colors last:border-0 hover:bg-muted/40 ${
                selectedId === change.id ? "bg-accent/5" : ""
              }`}
            >
              <td className="px-5 py-4">
                <p className="font-medium text-foreground">{change.section}</p>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  {CATEGORY_LABELS[change.category]}
                </p>
              </td>
              <td className="hidden max-w-[16rem] px-5 py-4 text-muted-foreground md:table-cell">
                <span className="line-clamp-3">{change.master}</span>
              </td>
              <td className="hidden max-w-[16rem] px-5 py-4 text-muted-foreground md:table-cell">
                <span className="line-clamp-3">{change.document}</span>
              </td>
              <td className="px-5 py-4">
                <ActionBadge action={change.action} />
                <p className="mt-2 text-foreground">{change.change}</p>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
