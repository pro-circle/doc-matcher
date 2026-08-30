export type ChangeAction = "none" | "modify" | "add" | "move" | "remove";
export type Severity = "none" | "low" | "medium" | "high";
export type CategoryKey =
  | "structure"
  | "typography"
  | "layout"
  | "formatting"
  | "visual"
  | "semantic";

export interface ChangeItem {
  id: string;
  category: CategoryKey;
  section: string;
  master: string;
  document: string;
  action: ChangeAction;
  change: string;
  severity: Severity;
  reason: string;
  confidence: number;
}

export interface CategoryScore {
  key: CategoryKey;
  label: string;
  score: number;
}

export interface ProfileGroup {
  group: string;
  items: string[];
}

export interface MasterProfile {
  file_name: string;
  groups: ProfileGroup[];
}

export interface AlignmentReport {
  overall_score: number;
  verdict: string;
  master_file: string;
  document_file: string;
  generated_at: string;
  categories: CategoryScore[];
  master_profile: MasterProfile;
  changes: ChangeItem[];
}

export const CATEGORY_LABELS: Record<CategoryKey, string> = {
  structure: "Structure",
  typography: "Typography",
  layout: "Layout",
  formatting: "Formatting",
  visual: "Visual",
  semantic: "Semantic",
};

export const ACTION_LABELS: Record<ChangeAction, string> = {
  none: "No change",
  modify: "Modify",
  add: "Add",
  move: "Move",
  remove: "Remove",
};
