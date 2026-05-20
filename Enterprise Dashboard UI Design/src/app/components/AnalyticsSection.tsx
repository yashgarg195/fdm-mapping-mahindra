import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, RadialBarChart, RadialBar, Cell,
} from "recharts";
import { MoreHorizontal, TrendingUp, BarChart2, Map, Gauge } from "lucide-react";

const trainingTrendData = [
  { month: "Apr", trained: 312, target: 350, refresher: 88 },
  { month: "May", trained: 289, target: 350, refresher: 102 },
  { month: "Jun", trained: 401, target: 380, refresher: 76 },
  { month: "Jul", trained: 378, target: 380, refresher: 94 },
  { month: "Aug", trained: 445, target: 400, refresher: 112 },
  { month: "Sep", trained: 421, target: 400, refresher: 98 },
  { month: "Oct", trained: 387, target: 420, refresher: 85 },
  { month: "Nov", trained: 356, target: 420, refresher: 91 },
  { month: "Dec", trained: 298, target: 380, refresher: 67 },
  { month: "Jan", trained: 412, target: 400, refresher: 103 },
  { month: "Feb", trained: 389, target: 400, refresher: 88 },
  { month: "Mar", trained: 468, target: 420, refresher: 115 },
];

const zoneData = [
  { zone: "North", specialists: 342, target: 380, penetration: 78 },
  { zone: "South", specialists: 298, target: 320, penetration: 82 },
  { zone: "East", specialists: 187, target: 210, penetration: 68 },
  { zone: "West", specialists: 276, target: 290, penetration: 85 },
  { zone: "Central", specialists: 181, target: 200, penetration: 71 },
];

const certData = [
  { name: "Tractor Mechanic", value: 82, fill: "#D2232A" },
  { name: "Service Advisor", value: 68, fill: "#1565C0" },
  { name: "Workshop Head", value: 91, fill: "#2E7D32" },
  { name: "Parts Advisor", value: 59, fill: "#E65C00" },
];

const stateData = [
  { state: "Maharashtra", headcount: 487, certified: 378, backlog: 52 },
  { state: "Rajasthan", headcount: 412, certified: 298, backlog: 68 },
  { state: "UP", headcount: 623, certified: 441, backlog: 87 },
  { state: "Punjab", headcount: 289, certified: 234, backlog: 31 },
  { state: "Haryana", headcount: 267, certified: 198, backlog: 44 },
  { state: "MP", headcount: 341, certified: 244, backlog: 59 },
];

const heatmapData = [
  ["Maharashtra", "Gujarat", "Karnataka", "Tamil Nadu", "Rajasthan"],
  [87, 73, 68, 91, 62],
  [82, 78, 71, 88, 59],
];

const dealerPenetrationMatrix = [
  { dealer: "Auto Traders Pvt Ltd", north: 92, south: 78, east: 65, west: 88, central: 71 },
  { dealer: "Krishi Motors", north: 78, south: 85, east: 72, west: 81, central: 68 },
  { dealer: "Singh Enterprises", north: 85, south: 62, east: 58, west: 74, central: 80 },
  { dealer: "Agro Tech Sales", north: 68, south: 91, east: 83, west: 76, central: 75 },
  { dealer: "National Tractors", north: 74, south: 79, east: 91, west: 69, central: 82 },
];

function SectionCard({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <div style={{ background: "white", border: "1px solid #EBEBEF", borderRadius: "8px", boxShadow: "0 1px 4px rgba(0,0,0,0.04)" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "14px 16px", borderBottom: "1px solid #F0F0F5" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ color: "#D2232A" }}>{icon}</span>
          <span style={{ fontSize: "13px", fontWeight: 700, color: "#1A1A2E", letterSpacing: "0.1px" }}>{title}</span>
        </div>
        <button style={{ background: "transparent", border: "none", cursor: "pointer", color: "#8B8BA7" }}>
          <MoreHorizontal size={16} />
        </button>
      </div>
      <div style={{ padding: "16px" }}>{children}</div>
    </div>
  );
}

function getCellColor(value: number): string {
  if (value >= 85) return "#1B5E20";
  if (value >= 75) return "#388E3C";
  if (value >= 65) return "#FFA000";
  if (value >= 55) return "#E65100";
  return "#C62828";
}

function getCellBg(value: number): string {
  if (value >= 85) return "rgba(27,94,32,0.12)";
  if (value >= 75) return "rgba(56,142,60,0.10)";
  if (value >= 65) return "rgba(255,160,0,0.12)";
  if (value >= 55) return "rgba(230,81,0,0.12)";
  return "rgba(198,40,40,0.10)";
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div style={{ background: "#1A1A2E", borderRadius: "6px", padding: "10px 14px", boxShadow: "0 4px 12px rgba(0,0,0,0.2)" }}>
        <div style={{ color: "#8B8BA7", fontSize: "11px", marginBottom: "6px" }}>{label}</div>
        {payload.map((p: any, i: number) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "2px" }}>
            <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: p.color }} />
            <span style={{ color: "#C8C8E0", fontSize: "12px" }}>{p.name}: <strong style={{ color: "white" }}>{p.value}</strong></span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export function AnalyticsSection() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      {/* Row 1: Training Trend + Zone Bar */}
      <div style={{ display: "grid", gridTemplateColumns: "3fr 2fr", gap: "16px" }}>
        {/* Monthly Training Trend */}
        <SectionCard title="Monthly Training Activity — FY 2025-26" icon={<TrendingUp size={15} />}>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={trainingTrendData} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F0F0F5" vertical={false} />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#8B8BA7" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: "#8B8BA7" }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }}
                iconType="circle"
                iconSize={8}
              />
              <Line
                type="monotone"
                dataKey="trained"
                stroke="#D2232A"
                strokeWidth={2}
                dot={{ r: 3, fill: "#D2232A" }}
                name="Trained"
              />
              <Line
                type="monotone"
                dataKey="target"
                stroke="#1565C0"
                strokeWidth={1.5}
                strokeDasharray="5 3"
                dot={false}
                name="Target"
              />
              <Line
                type="monotone"
                dataKey="refresher"
                stroke="#E65C00"
                strokeWidth={1.5}
                dot={{ r: 2, fill: "#E65C00" }}
                name="Refresher"
              />
            </LineChart>
          </ResponsiveContainer>
        </SectionCard>

        {/* Zone-wise Specialist Bar */}
        <SectionCard title="Zone-wise Specialist Count" icon={<BarChart2 size={15} />}>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={zoneData} margin={{ top: 4, right: 8, left: -20, bottom: 0 }} barSize={16}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F0F0F5" horizontal={true} vertical={false} />
              <XAxis dataKey="zone" tick={{ fontSize: 11, fill: "#8B8BA7" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: "#8B8BA7" }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} iconType="square" iconSize={8} />
              <Bar dataKey="specialists" fill="#D2232A" name="Specialists" radius={[3, 3, 0, 0]} />
              <Bar dataKey="target" fill="#E0E0E8" name="Target" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </SectionCard>
      </div>

      {/* Row 2: Dealer Penetration Heatmap + Cert Gauges + State Comparison */}
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 2fr", gap: "16px" }}>
        {/* Dealer Penetration Heatmap */}
        <SectionCard title="Dealer Penetration Heatmap (%)" icon={<Map size={15} />}>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "11px" }}>
              <thead>
                <tr>
                  <th style={{ textAlign: "left", padding: "6px 8px", color: "#8B8BA7", fontWeight: 600, fontSize: "10px", borderBottom: "1px solid #F0F0F5" }}>
                    Dealer
                  </th>
                  {["North", "South", "East", "West", "Central"].map((z) => (
                    <th key={z} style={{ textAlign: "center", padding: "6px 8px", color: "#8B8BA7", fontWeight: 600, fontSize: "10px", borderBottom: "1px solid #F0F0F5" }}>
                      {z}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {dealerPenetrationMatrix.map((row, i) => (
                  <tr key={i}>
                    <td style={{ padding: "6px 8px", color: "#4A4A6A", fontWeight: 500, fontSize: "10px", borderBottom: "1px solid #F8F8FA", whiteSpace: "nowrap" }}>
                      {row.dealer.length > 18 ? row.dealer.slice(0, 18) + "…" : row.dealer}
                    </td>
                    {[row.north, row.south, row.east, row.west, row.central].map((val, j) => (
                      <td
                        key={j}
                        style={{
                          padding: "5px 8px",
                          textAlign: "center",
                          borderBottom: "1px solid #F8F8FA",
                        }}
                      >
                        <span
                          style={{
                            display: "inline-block",
                            padding: "2px 8px",
                            borderRadius: "4px",
                            background: getCellBg(val),
                            color: getCellColor(val),
                            fontWeight: 700,
                            fontSize: "11px",
                            minWidth: "36px",
                          }}
                        >
                          {val}%
                        </span>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {/* Legend */}
            <div style={{ display: "flex", gap: "12px", marginTop: "10px", flexWrap: "wrap" }}>
              {[
                { label: "≥85% Excellent", color: "#1B5E20", bg: "rgba(27,94,32,0.12)" },
                { label: "≥75% Good", color: "#388E3C", bg: "rgba(56,142,60,0.10)" },
                { label: "≥65% Average", color: "#FFA000", bg: "rgba(255,160,0,0.12)" },
                { label: "<65% Critical", color: "#C62828", bg: "rgba(198,40,40,0.10)" },
              ].map((l) => (
                <div key={l.label} style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                  <div style={{ width: "10px", height: "10px", borderRadius: "2px", background: l.bg, border: `1px solid ${l.color}` }} />
                  <span style={{ fontSize: "10px", color: "#6B6B8A" }}>{l.label}</span>
                </div>
              ))}
            </div>
          </div>
        </SectionCard>

        {/* Certification Gauges */}
        <SectionCard title="Cert. Completion" icon={<Gauge size={15} />}>
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {certData.map((cert, i) => (
              <div key={i}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                  <span style={{ fontSize: "11px", color: "#4A4A6A", fontWeight: 500 }}>{cert.name}</span>
                  <span style={{ fontSize: "12px", fontWeight: 700, color: cert.fill }}>{cert.value}%</span>
                </div>
                <div style={{ height: "6px", background: "#F0F0F5", borderRadius: "3px", overflow: "hidden" }}>
                  <div
                    style={{
                      height: "100%",
                      width: `${cert.value}%`,
                      background: cert.fill,
                      borderRadius: "3px",
                      transition: "width 0.6s ease",
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        {/* State Performance */}
        <SectionCard title="State Performance Comparison" icon={<BarChart2 size={15} />}>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart
              data={stateData}
              layout="vertical"
              margin={{ top: 0, right: 8, left: 40, bottom: 0 }}
              barSize={12}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#F0F0F5" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 10, fill: "#8B8BA7" }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="state" tick={{ fontSize: 10, fill: "#4A4A6A" }} axisLine={false} tickLine={false} width={65} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: "11px" }} iconType="square" iconSize={8} />
              <Bar dataKey="certified" fill="#D2232A" name="Certified" radius={[0, 3, 3, 0]} />
              <Bar dataKey="backlog" fill="#FFAA00" name="Backlog" radius={[0, 3, 3, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </SectionCard>
      </div>
    </div>
  );
}
