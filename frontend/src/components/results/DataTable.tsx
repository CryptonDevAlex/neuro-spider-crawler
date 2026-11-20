"use client";

import { useCrawlStore } from "@/store/crawl-store";

export function DataTable() {
  const tables = useCrawlStore((state) => state.tables);

  if (tables.length === 0) {
    return (
      <div className="rounded border border-dashed border-terminal-border p-4 text-xs text-terminal-muted">
        No se detectaron tablas en las páginas rastreadas.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {tables.map((table, index) => (
        <div key={`${table.node_id}-${index}`} className="overflow-x-auto rounded border border-terminal-border">
          <p className="border-b border-terminal-border bg-terminal-bg/60 px-3 py-2 text-[10px] uppercase tracking-widest text-terminal-muted">
            tabla {index + 1} · {table.node_id}
          </p>
          <table className="w-full text-left text-xs">
            <thead>
              <tr>
                {table.headers.map((header, headerIndex) => (
                  <th
                    key={headerIndex}
                    className="border-b border-terminal-border px-3 py-2 font-semibold text-terminal-accent"
                  >
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {table.rows.map((row, rowIndex) => (
                <tr key={rowIndex} className="border-b border-terminal-border/60 last:border-0">
                  {row.map((cell, cellIndex) => (
                    <td key={cellIndex} className="px-3 py-2 text-terminal-text">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}
