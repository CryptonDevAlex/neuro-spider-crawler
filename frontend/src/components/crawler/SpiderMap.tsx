"use client";

import { NodeCard } from "./NodeCard";
import { useCrawlStore } from "@/store/crawl-store";

const POINTS: Array<[number, number]> = [
  [300, 90],
  [450, 150],
  [510, 300],
  [450, 450],
  [300, 510],
  [150, 450],
  [90, 300],
  [150, 150],
];

export function SpiderMap() {
  const nodes = useCrawlStore((state) => state.nodes);
  const lastNode = nodes[nodes.length - 1];

  return (
    <div className="relative h-full min-h-[320px] w-full">
      <svg
        viewBox="0 0 600 600"
        className="h-full w-full"
        role="img"
        aria-label={`Mapa del rastreo con ${nodes.length} nodos`}
      >
        <g className="spider-web">
          <circle cx="300" cy="300" r="70" />
          <circle cx="300" cy="300" r="140" />
          <circle cx="300" cy="300" r="210" />
          {POINTS.map(([x, y], index) => (
            <line key={index} x1="300" y1="300" x2={x} y2={y} />
          ))}
        </g>

        {nodes.map((node, index) => {
          const [x, y] = POINTS[index % POINTS.length];
          return (
            <g key={node.id}>
              <line x1="300" y1="300" x2={x} y2={y} className="spider-thread" />
              <circle cx={x} cy={y} r="7" className="spider-node" />
              <text x={x + 12} y={y - 10} fill="#65758b" fontSize="11">
                {index + 1}
              </text>
            </g>
          );
        })}

        <g className="spider-body">
          {POINTS.map(([x, y], index) => (
            <line
              key={index}
              x1="300"
              y1="300"
              x2={x}
              y2={y}
              className="spider-leg"
              style={{ animationDelay: `${index * 0.12}s` }}
            />
          ))}
          <ellipse cx="300" cy="320" rx="26" ry="34" className="spider-shell" />
          <circle cx="300" cy="276" r="16" className="spider-shell" />
        </g>
      </svg>

      <div className="absolute left-0 top-0 w-64 max-w-[80%]">
        {lastNode ? <NodeCard node={lastNode} /> : null}
      </div>
      <div className="absolute bottom-0 right-0 text-[10px] uppercase tracking-widest text-terminal-muted">
        {nodes.length} nodos detectados
      </div>
    </div>
  );
}
