import { useCallback, useRef, useState } from "react";
import { FileText, Upload, X } from "lucide-react";
import { cn } from "@/lib/utils";

const MAX_BYTES = 20 * 1024 * 1024;

interface DropZoneProps {
  label: string;
  hint: string;
  accept: string[];
  file: File | null;
  onFile: (file: File | null) => void;
}

export function DropZone({ label, hint, accept, file, onFile }: DropZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const accepted = useCallback(
    (candidate: File) => {
      const ext = "." + (candidate.name.split(".").pop() ?? "").toLowerCase();
      if (!accept.includes(ext)) return `Only ${accept.join(" or ")} files are accepted here.`;
      if (candidate.size > MAX_BYTES) return "File is larger than 20 MB.";
      return null;
    },
    [accept],
  );

  const handle = useCallback(
    (candidate: File | undefined) => {
      if (!candidate) return;
      const message = accepted(candidate);
      if (message) {
        setError(message);
        return;
      }
      setError(null);
      onFile(candidate);
    },
    [accepted, onFile],
  );

  return (
    <div className="w-full">
      <p className="mb-2 text-xs font-semibold tracking-[0.18em] text-muted-foreground uppercase">
        {label}
      </p>
      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") inputRef.current?.click();
        }}
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDragging(false);
          handle(event.dataTransfer.files[0]);
        }}
        className={cn(
          "flex min-h-36 w-full cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed px-6 py-8 text-center transition-colors",
          dragging ? "border-accent bg-accent/10" : "border-border bg-card hover:border-accent/60",
          file && "border-solid border-accent/50 bg-accent/5",
        )}
      >
        {file ? (
          <div className="flex items-center gap-3">
            <FileText className="size-5 text-accent" aria-hidden />
            <div className="text-left">
              <p className="text-sm font-medium text-foreground">{file.name}</p>
              <p className="text-xs text-muted-foreground">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <button
              type="button"
              aria-label={`Remove ${file.name}`}
              onClick={(event) => {
                event.stopPropagation();
                onFile(null);
                if (inputRef.current) inputRef.current.value = "";
              }}
              className="ml-2 rounded-md p-1 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            >
              <X className="size-4" />
            </button>
          </div>
        ) : (
          <>
            <Upload className="mb-3 size-5 text-muted-foreground" aria-hidden />
            <p className="text-sm font-medium text-foreground">{hint}</p>
            <p className="mt-1 text-xs text-muted-foreground">Drag and drop, or click to browse</p>
          </>
        )}
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept={accept.join(",")}
          onChange={(event) => handle(event.target.files?.[0])}
        />
      </div>
      {error && <p className="mt-2 text-xs text-destructive">{error}</p>}
    </div>
  );
}
