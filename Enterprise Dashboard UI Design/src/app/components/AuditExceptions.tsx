import { useState } from "react";
import {
  AlertTriangle,
  AlertOctagon,
  Calendar,
  Hash,
  BookX,
  CheckCircle2,
  X,
  Search,
  Download,
  ChevronRight,
  Eye,
  RefreshCcw,
} from "lucide-react";

interface AuditItem {
  id: string;
  type: string;
  starId: string;
  name: string;
  detail: string;
  zone: string;
  severity: "Critical" | "High" | "Medium" | "Low";
  detected: string;
  status: "Open" | "In Review" | "Resolved";
}

const auditData: AuditItem[] = [
  { id: "EXC-001", type: "Missing STAR ID", starId: "—", name: "Ramesh Kumar", detail: "No STAR ID found in any master reference", zone: "North", severity: "Critical", detected: "20 May 2026", status: "Open" },
  { id: "EXC-002", type: "Duplicate STAR ID", starId: "STR-07234", name: "Priya Nair / P. Narayanan", detail: "Same STAR ID assigned to 2 employees", zone: "South", severity: "Critical", detected: "20 May 2026", status: "Open" },
  { id: "EXC-003", type: "Future DOJ Alert", starId: "STR-14892", name: "Santosh Verma", detail: "DOJ set as 15 Nov 2026 — future date", zone: "East", severity: "High", detected: "20 May 2026", status: "In Review" },
  { id: "EXC-004", type: "Missing STAR ID", starId: "—", name: "Pradeep Yadav", detail: "Employee exists in manpower but not in STAR system", zone: "Central", severity: "Critical", detected: "19 May 2026", status: "Open" },
  { id: "EXC-005", type: "Training Mismatch", starId: "STR-09241", name: "Rekha Singh", detail: "Training date (Jan 2021) precedes DOJ (Mar 2022)", zone: "South", severity: "High", detected: "19 May 2026", status: "Open" },
  { id: "EXC-006", type: "Duplicate STAR ID", starId: "STR-03912", name: "Ranjit Singh / R. Singh Jr.", detail: "Possible duplicate — same name pattern", zone: "North", severity: "Medium", detected: "18 May 2026", status: "In Review" },
  { id: "EXC-007", type: "Missing STAR ID", starId: "—", name: "Mohan Lal", detail: "New hire record missing from STAR master", zone: "West", severity: "Critical", detected: "18 May 2026", status: "Open" },
  { id: "EXC-008", type: "Training Mismatch", starId: "STR-08347", name: "Sunita Reddy", detail: "Certification level mismatch: file says Level 2, system shows Level 1", zone: "South", severity: "Medium", detected: "17 May 2026", status: "Open" },
  { id: "EXC-009", type: "Future DOJ Alert", starId: "STR-15203", name: "Anil Mishra", detail: "DOJ entered as 01 Jun 2026 — not yet joined", zone: "North", severity: "Low", detected: "17 May 2026", status: "Resolved" },
  { id: "EXC-010", type: "Duplicate STAR ID", starId: "STR-05623", name: "Deepak Patel / D.K. Patel", detail: "Same ID, different dealer codes — needs deduplication", zone: "West", severity: "High", detected: "16 May 2026", status: "Open" },
];

const exceptionTypes = [
  { id: "all", label: "All Exceptions", count: 218, icon: <AlertOctagon size={14} />, color: "#D2232A" },
  { id: "missing", label: "Missing STAR IDs", count: 87, icon: <Hash size={14} />, color: "#C62828" },
  { id: "duplicate", label: "Duplicate IDs", count: 47, icon: <RefreshCcw size={14} />, color: "#E65C00" },
  { id: "future", label: "Future DOJ Alerts", count: 12, icon: <Calendar size={14} />, color: "#1565C0" },
  { id: "mismatch", label: "Training Mismatches", count: 72, icon: <BookX size={14} />, color: "#7B1FA2" },
];

function SeverityBadge({ level }: { level: string }) {
  const map: Record<string, { bg: string; color: string; border: string }> = {
    Critical: { bg: "rgba(198,40,40,0.08)", color: "#C62828", border: "rgba(198,40,40,0.25)" },
    High: { bg: "rgba(230,92,0,0.08)", color: "#E65C00", border: "rgba(230,92,0,0.25)" },
    Medium: { bg: "rgba(255,160,0,0.08)", color: "#FF8F00", border: "rgba(255,160,0,0.25)" },
    Low: { bg: "rgba(46,125,50,0.08)", color: "#2E7D32", border: "rgba(46,125,50,0.25)" },
  };
  const s = map[level] || map.Medium;
  return (
    <span style={{ background: s.bg, color: s.color, border: `1px solid ${s.border}`, borderRadius: "4px", padding: "2px 8px", fontSize: "10px", fontWeight: 700 }}>
      {level}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { bg: string; color: string }> = {
    Open: { bg: "rgba(198,40,40,0.08)", color: "#C62828" },
    "In Review": { bg: "rgba(21,101,192,0.08)", color: "#1565C0" },
    Resolved: { bg: "rgba(46,125,50,0.08)", color: "#2E7D32" },
  };
  const s = map[status] || map.Open;
  return (
    <span style={{ background: s.bg, color: s.color, borderRadius: "4px", padding: "2px 8px", fontSize: "10px", fontWeight: 600 }}>
      {status}
    </span>
  );
}

function TypeBadge({ type }: { type: string }) {
  const map: Record<string, { bg: string; color: string; icon: React.ReactNode }> = {
    "Missing STAR ID": { bg: "#FFF0F0", color: "#C62828", icon: <Hash size={10} /> },
    "Duplicate STAR ID": { bg: "#FFF5E6", color: "#E65C00", icon: <RefreshCcw size={10} /> },
    "Future DOJ Alert": { bg: "#EEF4FF", color: "#1565C0", icon: <Calendar size={10} /> },
    "Training Mismatch": { bg: "#F5EEF8", color: "#7B1FA2", icon: <BookX size={10} /> },
  };
  const s = map[type] || { bg: "#F5F5F8", color: "#6B6B8A", icon: <AlertTriangle size={10} /> };
  return (
    <span style={{ background: s.bg, color: s.color, borderRadius: "4px", padding: "3px 8px", fontSize: "10px", fontWeight: 600, display: "inline-flex", alignItems: "center", gap: "4px" }}>
      {s.icon} {type}
    </span>
  );
}

export function AuditExceptions() {
  const [activeFilter, setActiveFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [selectedItem, setSelectedItem] = useState<AuditItem | null>(null);

  const filteredData = auditData.filter((item) => {
    const matchesFilter =
      activeFilter === "all" ||
      (activeFilter === "missing" && item.type === "Missing STAR ID") ||
      (activeFilter === "duplicate" && item.type === "Duplicate STAR ID") ||
      (activeFilter === "future" && item.type === "Future DOJ Alert") ||
      (activeFilter === "mismatch" && item.type === "Training Mismatch");

    const matchesSearch =
      !search ||
      item.name.toLowerCase().includes(search.toLowerCase()) ||
      item.id.toLowerCase().includes(search.toLowerCase()) ||
      item.starId.toLowerCase().includes(search.toLowerCase());

    return matchesFilter && matchesSearch;
  });

  const criticalCount = auditData.filter((d) => d.severity === "Critical" && d.status === "Open").length;
  const openCount = auditData.filter((d) => d.status === "Open").length;
  const resolvedCount = auditData.filter((d) => d.status === "Resolved").length;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      {/* Alert Banner */}
      <div
        style={{
          background: "linear-gradient(135deg, #C62828 0%, #8B0000 100%)",
          borderRadius: "8px",
          padding: "14px 20px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          boxShadow: "0 4px 12px rgba(198,40,40,0.25)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <AlertOctagon size={22} color="white" />
          <div>
            <div style={{ color: "white", fontWeight: 700, fontSize: "14px" }}>
              {criticalCount} Critical Exceptions Require Immediate Attention
            </div>
            <div style={{ color: "rgba(255,255,255,0.75)", fontSize: "12px" }}>
              {openCount} open exceptions · Last audit run: 20 May 2026, 09:42 AM
            </div>
          </div>
        </div>
        <button
          style={{
            background: "rgba(255,255,255,0.15)",
            border: "1px solid rgba(255,255,255,0.3)",
            color: "white",
            borderRadius: "6px",
            padding: "6px 14px",
            cursor: "pointer",
            fontSize: "12px",
            fontWeight: 600,
          }}
        >
          Assign to Team
        </button>
      </div>

      {/* Exception Type Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "10px" }}>
        {exceptionTypes.map((type) => (
          <button
            key={type.id}
            onClick={() => setActiveFilter(type.id)}
            style={{
              background: activeFilter === type.id ? "#FFF0F0" : "white",
              border: `1px solid ${activeFilter === type.id ? "#FFCCCC" : "#EBEBEF"}`,
              borderRadius: "8px",
              padding: "12px",
              cursor: "pointer",
              textAlign: "left",
              boxShadow: activeFilter === type.id ? "0 2px 8px rgba(210,35,42,0.1)" : "0 1px 4px rgba(0,0,0,0.04)",
              outline: activeFilter === type.id ? "2px solid #D2232A" : "none",
              outlineOffset: "-1px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "6px", color: activeFilter === type.id ? "#D2232A" : type.color }}>
              {type.icon}
              <span style={{ fontSize: "11px", fontWeight: 600, color: "inherit" }}>{type.label}</span>
            </div>
            <div style={{ fontSize: "22px", fontWeight: 800, color: activeFilter === type.id ? "#D2232A" : "#1A1A2E" }}>
              {type.count}
            </div>
          </button>
        ))}
      </div>

      {/* Summary Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "10px" }}>
        {[
          { label: "Open", value: openCount, color: "#C62828", bg: "rgba(198,40,40,0.08)" },
          { label: "In Review", value: auditData.filter((d) => d.status === "In Review").length, color: "#1565C0", bg: "rgba(21,101,192,0.08)" },
          { label: "Resolved", value: resolvedCount, color: "#2E7D32", bg: "rgba(46,125,50,0.08)" },
        ].map((s) => (
          <div key={s.label} style={{ background: "white", border: "1px solid #EBEBEF", borderRadius: "8px", padding: "12px 16px", display: "flex", alignItems: "center", gap: "12px", boxShadow: "0 1px 4px rgba(0,0,0,0.04)" }}>
            <div style={{ width: "8px", height: "40px", borderRadius: "4px", background: s.color }} />
            <div>
              <div style={{ fontSize: "24px", fontWeight: 800, color: "#1A1A2E", lineHeight: 1 }}>{s.value}</div>
              <div style={{ fontSize: "12px", color: "#6B6B8A", marginTop: "2px" }}>{s.label} Exceptions</div>
            </div>
          </div>
        ))}
      </div>

      {/* Exception Table */}
      <div style={{ background: "white", border: "1px solid #EBEBEF", borderRadius: "8px", boxShadow: "0 1px 4px rgba(0,0,0,0.04)", overflow: "hidden" }}>
        {/* Toolbar */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 16px", borderBottom: "1px solid #F0F0F5" }}>
          <div style={{ fontSize: "13px", fontWeight: 700, color: "#1A1A2E" }}>
            Exception Queue
            <span style={{ marginLeft: "8px", background: "rgba(210,35,42,0.1)", color: "#D2232A", borderRadius: "10px", padding: "2px 8px", fontSize: "11px", fontWeight: 700 }}>
              {filteredData.length}
            </span>
          </div>
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <div style={{ position: "relative" }}>
              <Search size={13} color="#8B8BA7" style={{ position: "absolute", left: "8px", top: "50%", transform: "translateY(-50%)" }} />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search exceptions..."
                style={{ padding: "6px 8px 6px 28px", border: "1px solid #E0E0E8", borderRadius: "6px", fontSize: "12px", width: "220px", outline: "none", background: "#FAFAFA" }}
              />
            </div>
            <button style={{ display: "flex", alignItems: "center", gap: "6px", background: "#1A1A2E", border: "none", borderRadius: "6px", padding: "6px 12px", cursor: "pointer", fontSize: "12px", color: "white", fontWeight: 600 }}>
              <Download size={13} /> Export Audit Log
            </button>
          </div>
        </div>

        {/* Table */}
        <div style={{ overflowX: "auto", maxHeight: "380px", overflowY: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                {["Exc. ID", "Type", "STAR ID", "Employee", "Issue Detail", "Zone", "Severity", "Detected", "Status", "Actions"].map((h) => (
                  <th key={h} style={{
                    padding: "10px 12px",
                    textAlign: "left",
                    fontSize: "11px",
                    fontWeight: 600,
                    color: "#6B6B8A",
                    letterSpacing: "0.5px",
                    background: "#F8F8FB",
                    borderBottom: "1px solid #EBEBEF",
                    whiteSpace: "nowrap",
                    position: "sticky",
                    top: 0,
                    zIndex: 1,
                  }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredData.map((row, i) => (
                <tr
                  key={row.id}
                  style={{ background: i % 2 === 0 ? "white" : "#FDFCFF", cursor: "pointer" }}
                  onClick={() => setSelectedItem(row)}
                >
                  <td style={{ padding: "9px 12px", fontSize: "11px", color: "#8B8BA7", fontFamily: "monospace", borderBottom: "1px solid #F0F0F5", whiteSpace: "nowrap" }}>
                    {row.id}
                  </td>
                  <td style={{ padding: "9px 12px", borderBottom: "1px solid #F0F0F5", whiteSpace: "nowrap" }}>
                    <TypeBadge type={row.type} />
                  </td>
                  <td style={{ padding: "9px 12px", fontSize: "11px", color: row.starId === "—" ? "#C62828" : "#D2232A", fontFamily: "monospace", fontWeight: 700, borderBottom: "1px solid #F0F0F5" }}>
                    {row.starId}
                  </td>
                  <td style={{ padding: "9px 12px", fontSize: "12px", fontWeight: 600, color: "#2A2A4A", borderBottom: "1px solid #F0F0F5", whiteSpace: "nowrap" }}>
                    {row.name}
                  </td>
                  <td style={{ padding: "9px 12px", fontSize: "11px", color: "#6B6B8A", borderBottom: "1px solid #F0F0F5", maxWidth: "220px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {row.detail}
                  </td>
                  <td style={{ padding: "9px 12px", borderBottom: "1px solid #F0F0F5" }}>
                    <span style={{ background: "#F0F0F8", border: "1px solid #D8D8E8", borderRadius: "4px", padding: "1px 6px", fontSize: "10px", color: "#4A4A6A" }}>
                      {row.zone}
                    </span>
                  </td>
                  <td style={{ padding: "9px 12px", borderBottom: "1px solid #F0F0F5" }}>
                    <SeverityBadge level={row.severity} />
                  </td>
                  <td style={{ padding: "9px 12px", fontSize: "11px", color: "#8B8BA7", borderBottom: "1px solid #F0F0F5", whiteSpace: "nowrap" }}>
                    {row.detected}
                  </td>
                  <td style={{ padding: "9px 12px", borderBottom: "1px solid #F0F0F5" }}>
                    <StatusBadge status={row.status} />
                  </td>
                  <td style={{ padding: "9px 12px", borderBottom: "1px solid #F0F0F5" }}>
                    <div style={{ display: "flex", gap: "4px" }}>
                      <button style={{ background: "transparent", border: "1px solid #E0E0E8", borderRadius: "4px", padding: "3px 6px", cursor: "pointer", color: "#6B6B8A" }} onClick={(e) => { e.stopPropagation(); setSelectedItem(row); }}>
                        <Eye size={12} />
                      </button>
                      {row.status !== "Resolved" && (
                        <button style={{ background: "transparent", border: "1px solid #D2232A", borderRadius: "4px", padding: "3px 6px", cursor: "pointer", color: "#D2232A", fontSize: "10px", fontWeight: 600 }}>
                          Resolve
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail Modal */}
      {selectedItem && (
        <div
          style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center" }}
          onClick={() => setSelectedItem(null)}
        >
          <div
            style={{ background: "white", borderRadius: "12px", padding: "24px", width: "500px", maxWidth: "90vw", boxShadow: "0 20px 60px rgba(0,0,0,0.3)" }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
              <div>
                <div style={{ fontSize: "16px", fontWeight: 700, color: "#1A1A2E" }}>Exception Detail</div>
                <div style={{ fontSize: "11px", color: "#8B8BA7", fontFamily: "monospace" }}>{selectedItem.id}</div>
              </div>
              <button onClick={() => setSelectedItem(null)} style={{ background: "transparent", border: "none", cursor: "pointer", color: "#8B8BA7" }}>
                <X size={18} />
              </button>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              {[
                { label: "Employee", value: selectedItem.name },
                { label: "STAR ID", value: selectedItem.starId },
                { label: "Exception Type", value: selectedItem.type },
                { label: "Severity", value: selectedItem.severity },
                { label: "Zone", value: selectedItem.zone },
                { label: "Detected", value: selectedItem.detected },
                { label: "Status", value: selectedItem.status },
              ].map(({ label, value }) => (
                <div key={label} style={{ background: "#F8F8FB", borderRadius: "6px", padding: "10px" }}>
                  <div style={{ fontSize: "10px", color: "#8B8BA7", fontWeight: 600, letterSpacing: "0.5px", marginBottom: "3px" }}>{label.toUpperCase()}</div>
                  <div style={{ fontSize: "13px", color: "#1A1A2E", fontWeight: 600 }}>{value}</div>
                </div>
              ))}
              <div style={{ gridColumn: "1/-1", background: "#FFF8E1", border: "1px solid #FFE082", borderRadius: "6px", padding: "10px" }}>
                <div style={{ fontSize: "10px", color: "#8B8BA7", fontWeight: 600, marginBottom: "3px" }}>ISSUE DETAIL</div>
                <div style={{ fontSize: "12px", color: "#4A4A6A" }}>{selectedItem.detail}</div>
              </div>
            </div>
            <div style={{ display: "flex", gap: "8px", marginTop: "16px" }}>
              {selectedItem.status !== "Resolved" && (
                <button style={{ flex: 1, background: "#D2232A", color: "white", border: "none", borderRadius: "6px", padding: "10px", cursor: "pointer", fontWeight: 600, fontSize: "13px" }}>
                  Mark as Resolved
                </button>
              )}
              <button style={{ flex: 1, background: "#F5F5F8", color: "#4A4A6A", border: "1px solid #E0E0E8", borderRadius: "6px", padding: "10px", cursor: "pointer", fontWeight: 600, fontSize: "13px" }}>
                Flag for Review
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
