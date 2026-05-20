import { Users, Award, RefreshCcw, TrendingUp, Building2, AlertTriangle, ArrowUp, ArrowDown, Minus } from "lucide-react";

interface KPI {
  label: string;
  value: string;
  subValue: string;
  change: number;
  changeLabel: string;
  icon: React.ReactNode;
  color: string;
  bg: string;
  border: string;
}

const kpis: KPI[] = [
  {
    label: "Total Headcount",
    value: "3,847",
    subValue: "Active employees",
    change: 4.2,
    changeLabel: "vs last quarter",
    icon: <Users size={18} />,
    color: "#1A1A2E",
    bg: "#F0F0F8",
    border: "#D0D0E8",
  },
  {
    label: "Active Specialists",
    value: "1,284",
    subValue: "Certified & current",
    change: 8.7,
    changeLabel: "vs last quarter",
    icon: <Award size={18} />,
    color: "#D2232A",
    bg: "#FFF0F0",
    border: "#FFCCCC",
  },
  {
    label: "Refresher Backlog",
    value: "476",
    subValue: "Overdue by >90 days",
    change: -12.3,
    changeLabel: "vs last quarter",
    icon: <RefreshCcw size={18} />,
    color: "#E65C00",
    bg: "#FFF5E6",
    border: "#FFD9B3",
  },
  {
    label: "Skill Uplift Candidates",
    value: "621",
    subValue: "Nominated for training",
    change: 15.4,
    changeLabel: "vs last quarter",
    icon: <TrendingUp size={18} />,
    color: "#2E7D32",
    bg: "#F0F8F0",
    border: "#BBDDBB",
  },
  {
    label: "Dealer Penetration",
    value: "73.8%",
    subValue: "of 892 active dealers",
    change: 2.1,
    changeLabel: "vs last quarter",
    icon: <Building2 size={18} />,
    color: "#1565C0",
    bg: "#EEF4FF",
    border: "#BBCCEE",
  },
  {
    label: "Unresolved Records",
    value: "218",
    subValue: "Require action",
    change: -5.8,
    changeLabel: "vs last quarter",
    icon: <AlertTriangle size={18} />,
    color: "#C62828",
    bg: "#FFF0F0",
    border: "#FFBBBB",
  },
];

function ChangeIndicator({ change, label }: { change: number; label: string }) {
  const isPositive = change > 0;
  const isNeutral = change === 0;
  const color = isNeutral ? "#8B8BA7" : isPositive ? "#2E7D32" : "#C62828";
  const Icon = isNeutral ? Minus : isPositive ? ArrowUp : ArrowDown;

  return (
    <div style={{ display: "flex", alignItems: "center", gap: "3px", marginTop: "4px" }}>
      <Icon size={11} color={color} />
      <span style={{ color, fontSize: "11px", fontWeight: 600 }}>
        {Math.abs(change)}%
      </span>
      <span style={{ color: "#8B8BA7", fontSize: "10px" }}>{label}</span>
    </div>
  );
}

export function KPICards() {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(6, 1fr)",
        gap: "12px",
        marginBottom: "20px",
      }}
    >
      {kpis.map((kpi, idx) => (
        <div
          key={idx}
          style={{
            background: "white",
            border: "1px solid #EBEBEF",
            borderRadius: "8px",
            padding: "14px",
            position: "relative",
            boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
            overflow: "hidden",
          }}
        >
          {/* Top border accent */}
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              height: "3px",
              background: kpi.color,
            }}
          />

          {/* Icon */}
          <div
            style={{
              width: "36px",
              height: "36px",
              background: kpi.bg,
              border: `1px solid ${kpi.border}`,
              borderRadius: "6px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: kpi.color,
              marginBottom: "10px",
            }}
          >
            {kpi.icon}
          </div>

          {/* Value */}
          <div
            style={{
              fontSize: "22px",
              fontWeight: 800,
              color: "#1A1A2E",
              letterSpacing: "-0.5px",
              lineHeight: 1.1,
            }}
          >
            {kpi.value}
          </div>

          {/* Label */}
          <div
            style={{
              fontSize: "11px",
              color: "#4A4A6A",
              fontWeight: 600,
              marginTop: "2px",
              letterSpacing: "0.2px",
            }}
          >
            {kpi.label}
          </div>

          {/* Sub Value */}
          <div style={{ fontSize: "10px", color: "#8B8BA7", marginTop: "1px" }}>
            {kpi.subValue}
          </div>

          {/* Change */}
          <ChangeIndicator change={kpi.change} label={kpi.changeLabel} />
        </div>
      ))}
    </div>
  );
}
