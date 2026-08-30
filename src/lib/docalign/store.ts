import { useSyncExternalStore } from "react";
import type { AlignmentReport } from "./types";

let currentReport: AlignmentReport | null = null;
const listeners = new Set<() => void>();

function emit() {
  for (const listener of listeners) listener();
}

export function setReport(report: AlignmentReport | null) {
  currentReport = report;
  emit();
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function getSnapshot() {
  return currentReport;
}

export function useReport(): AlignmentReport | null {
  return useSyncExternalStore(subscribe, getSnapshot, () => null);
}
