"use client";

import { Panel } from "@/components/ui/Panel";
import { SpiderMap } from "./SpiderMap";

export function SpiderGraph() {
  return (
    <Panel
      title="Mapa de reconocimiento"
      subtitle="Cada nodo representa una página detectada en tiempo real"
      className="min-h-[360px] flex-1"
    >
      <SpiderMap />
    </Panel>
  );
}
