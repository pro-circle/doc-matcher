import { useState } from "react";
import { Check, ChevronDown } from "lucide-react";
import type { MasterProfile } from "@/lib/docalign/types";

export function MasterProfilePanel({ profile }: { profile: MasterProfile }) {
  const [open, setOpen] = useState(false);

  return (
    <section className="rounded-2xl border border-border bg-card">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        className="flex w-full items-center justify-between gap-4 px-6 py-4 text-left"
      >
        <span>
          <span className="text-sm font-semibold text-foreground">Master Profile</span>
          <span className="ml-3 text-xs text-muted-foreground">{profile.file_name}</span>
        </span>
        <ChevronDown
          className={`size-4 text-muted-foreground transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>
      {open && (
        <div className="grid gap-6 border-t border-border px-6 py-6 sm:grid-cols-2 lg:grid-cols-3">
          {profile.groups.map((group) => (
            <div key={group.group}>
              <p className="text-xs font-semibold tracking-[0.16em] text-muted-foreground uppercase">
                {group.group}
              </p>
              <ul className="mt-3 space-y-1.5">
                {group.items.map((item) => (
                  <li key={item} className="flex items-start gap-2 text-sm text-foreground">
                    <Check className="mt-0.5 size-3.5 shrink-0 text-success" aria-hidden />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
