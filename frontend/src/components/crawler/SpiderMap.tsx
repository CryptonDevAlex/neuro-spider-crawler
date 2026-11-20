"use client";

import { useEffect, useRef, useState } from "react";

import { NodeCard } from "./NodeCard";
import { useScanStore } from "@/store/scan-store";

type Point = { x: number; y: number };

const CENTER: Point = { x: 300, y: 300 };
const POINTS: Point[] = [
  { x: 300, y: 90 },
  { x: 450, y: 150 },
  { x: 510, y: 300 },
  { x: 450, y: 450 },
  { x: 300, y: 510 },
  { x: 150, y: 450 },
  { x: 90, y: 300 },
  { x: 150, y: 150 },
];
const LEG_ANGLES = [-155, -120, -60, -25, 25, 60, 120, 155];
const SEGMENT_MS = 850;

function legPoints(index: number, heading: number, phase: number, walking: boolean): string {
  const angle = heading + (LEG_ANGLES[index] * Math.PI) / 180;
  const swing = walking ? Math.sin(phase + (index % 2) * Math.PI) * 9 : 0;
  const perpX = -Math.sin(angle);
  const perpY = Math.cos(angle);
  const kneeX = Math.cos(angle) * 24 + perpX * swing * 0.4;
  const kneeY = Math.sin(angle) * 24 + perpY * swing * 0.4;
  const footX = Math.cos(angle) * (42 + swing) + perpX * swing;
  const footY = Math.sin(angle) * (42 + swing) + perpY * swing;
  return `0,0 ${kneeX.toFixed(1)},${kneeY.toFixed(1)} ${footX.toFixed(1)},${footY.toFixed(1)}`;
}

export function SpiderMap() {
  const nodes = useScanStore((state) => state.nodes);
  const done = useScanStore((state) => state.done);
  const nodeCount = nodes.length;
  const lastNode = nodes[nodeCount - 1];
  const positionRef = useRef<Point>(CENTER);
  const [position, setPosition] = useState<Point>(CENTER);
  const [heading, setHeading] = useState(-Math.PI / 2);
  const [phase, setPhase] = useState(0);
  const [walking, setWalking] = useState(false);

  useEffect(() => {
    const route = Array.from({ length: nodeCount }, (_, index) => POINTS[index % POINTS.length]);
    if (done && nodeCount > 0) {
      route.push(CENTER);
    }

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reducedMotion || route.length === 0) {
      const finalPoint = route[route.length - 1] ?? CENTER;
      const frame = requestAnimationFrame(() => {
        positionRef.current = finalPoint;
        setPosition(finalPoint);
        setWalking(false);
      });
      return () => cancelAnimationFrame(frame);
    }

    let cancelled = false;
    let frame = 0;
    let segment = 0;
    let initialized = false;
    let from = positionRef.current;
    let to = route[0];
    let startedAt = 0;

    const animate = (now: number) => {
      if (cancelled) {
        return;
      }

      if (!initialized) {
        initialized = true;
        startedAt = now;
        setHeading(Math.atan2(to.y - from.y, to.x - from.x));
        setWalking(true);
      }

      const progress = Math.min((now - startedAt) / SEGMENT_MS, 1);
      const eased = progress * progress * (3 - 2 * progress);
      const current = {
        x: from.x + (to.x - from.x) * eased,
        y: from.y + (to.y - from.y) * eased,
      };

      positionRef.current = current;
      setPosition(current);
      setPhase(now / 100);

      if (progress < 1) {
        frame = requestAnimationFrame(animate);
        return;
      }

      segment += 1;
      if (segment >= route.length) {
        setWalking(false);
        return;
      }

      from = current;
      to = route[segment];
      startedAt = now;
      setHeading(Math.atan2(to.y - from.y, to.x - from.x));
      frame = requestAnimationFrame(animate);
    };

    frame = requestAnimationFrame(animate);
    return () => {
      cancelled = true;
      cancelAnimationFrame(frame);
    };
  }, [nodeCount, done]);

  return (
    <div className="relative h-full min-h-[320px] w-full">
      <svg
        viewBox="0 0 600 600"
        className="h-full w-full"
        role="img"
        aria-label={`Mapa del reconocimiento con ${nodeCount} nodos`}
      >
        <g className="spider-web">
          <circle cx="300" cy="300" r="70" />
          <circle cx="300" cy="300" r="140" />
          <circle cx="300" cy="300" r="210" />
          {POINTS.map((point, index) => (
            <line key={index} x1="300" y1="300" x2={point.x} y2={point.y} />
          ))}
        </g>

        {nodes.map((node, index) => {
          const point = POINTS[index % POINTS.length];
          return (
            <g key={node.id}>
              <line x1="300" y1="300" x2={point.x} y2={point.y} className="spider-thread" />
              <circle cx={point.x} cy={point.y} r="7" className="spider-node" />
              <text x={point.x + 12} y={point.y - 10} fill="#65758b" fontSize="11">
                {index + 1}
              </text>
            </g>
          );
        })}

        <g
          className="spider-fire"
          transform={`translate(${position.x.toFixed(1)} ${position.y.toFixed(1)})`}
        >
          {LEG_ANGLES.map((_, index) => (
            <polyline
              key={index}
              points={legPoints(index, heading, phase, walking)}
              className="spider-leg"
              style={{ animationDelay: `${index * 0.08}s` }}
            />
          ))}
          <ellipse cx="0" cy="8" rx="25" ry="32" className="spider-shell" />
          <circle cx="0" cy="-18" r="15" className="spider-shell" />
          <circle cx="-6" cy="-21" r="2.5" className="spider-eye" />
          <circle cx="6" cy="-21" r="2.5" className="spider-eye" />
        </g>
      </svg>

      <div className="absolute left-0 top-0 w-64 max-w-[80%]">
        {lastNode ? <NodeCard node={lastNode} /> : null}
      </div>
      <div className="absolute bottom-0 right-0 text-[10px] uppercase tracking-widest text-terminal-muted">
        {nodeCount} páginas detectadas
      </div>
    </div>
  );
}
