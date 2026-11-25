import { ImageResponse } from "next/og";
import { companies, money, people } from "@/lib/data";

export async function GET(req: Request) {
  const id = new URL(req.url).searchParams.get("id");
  const p = people.find((x) => x.id === id);
  const ink = "#1b1a17", paper = "#f7f4ee", muted = "#6b665c";
  const body = p ? (
    <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
      <div style={{ fontSize: 64, fontWeight: 700 }}>{p.name}</div>
      <div style={{ fontSize: 30, color: muted }}>{companies[p.company].name}</div>
      <div style={{ display: "flex", gap: 60, marginTop: 30 }}>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ fontSize: 24, color: muted }}>Kept</div>
          <div style={{ fontSize: 56 }}>{`${p.share_kept_pct.toFixed(1)}%`}</div>
        </div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ fontSize: 24, color: muted }}>Held by others</div>
          <div style={{ fontSize: 56, fontWeight: 700 }}>{money(p.value_held_by_others_usd)}</div>
        </div>
      </div>
    </div>
  ) : (
    <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
      <div style={{ fontSize: 80, fontWeight: 700 }}>The Other List</div>
      <div style={{ fontSize: 36, color: muted }}>What the richest founders created for everyone else.</div>
    </div>
  );
  return new ImageResponse(
    (
      <div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", justifyContent: "space-between", padding: 72, background: paper, color: ink }}>
        {body}
        <div style={{ fontSize: 24, color: muted, display: "flex" }}>{`${p ? "The Other List · " : ""}every number sourced`}</div>
      </div>
    ),
    { width: 1200, height: 630 },
  );
}
