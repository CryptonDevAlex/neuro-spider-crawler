import type { PageNode } from "@/lib/types";

export function NodeCard({ node }: { node: PageNode }) {
  return (
    <div className="rounded border border-terminal-border bg-terminal-bg/90 p-3 backdrop-blur">
      <p className="truncate text-[11px] text-terminal-accent">{node.title || node.url}</p>
      <p className="mt-1 truncate text-[10px] text-terminal-muted">{node.url}</p>
      <div className="mt-2 flex gap-3 text-[10px] uppercase tracking-wider text-terminal-muted">
        <span>prof. {node.depth}</span>
        <span>{node.links} links</span>
        <span>{node.word_count} palabras</span>
      </div>
    </div>
  );
}
