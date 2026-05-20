import { useState } from "react";
import {
  Search,
  Download,
  ChevronUp,
  ChevronDown,
  ChevronsUpDown,
  Filter,
  ArrowRight,
} from "lucide-react";

type SortDir = "asc" | "desc" | null;

const manpowerData = [
  { starId: "STR-04821", name: "Arvind Sharma", designation: "Tractor Mechanic", dealer: "Auto Traders Pvt Ltd", state: "Rajasthan", zone: "North", doj: "12 Mar 2019", status: "Active", certified: true },
  { starId: "STR-07234", name: "Priya Nair", designation: "Service Advisor", dealer: "Krishi Motors", state: "Kerala", zone: "South", doj: "05 Aug 2021", status: "Active", certified: true },
  { starId: "STR-03912", name: "Ranjit Singh", designation: "Workshop Head", dealer: "Singh Enterprises", state: "Punjab", zone: "North", doj: "19 Jan 2018", status: "Active", certified: true },
  { starId: "STR-09841", name: "Meena Kumari", designation: "Parts Advisor", dealer: "Agro Tech Sales", state: "Bihar", zone: "East", doj: "02 Nov 2022", status: "Active", certified: false },
  { starId: "STR-05623", name: "Deepak Patel", designation: "Tractor Mechanic", dealer: "National Tractors", state: "Gujarat", zone: "West", doj: "17 Jun 2020", status: "Active", certified: true },
  { starId: "STR-08347", name: "Sunita Reddy", designation: "Service Advisor", dealer: "Auto Traders Pvt Ltd", state: "Telangana", zone: "South", doj: "09 Apr 2021", status: "On Leave", certified: true },
  { starId: "STR-02198", name: "Vikram Tomar", designation: "Branch Manager", dealer: "Krishi Motors", state: "UP", zone: "North", doj: "23 Feb 2016", status: "Active", certified: true },
  { starId: "STR-11204", name: "Geeta Devi", designation: "Tractor Mechanic", dealer: "Singh Enterprises", state: "Haryana", zone: "North", doj: "14 Sep 2023", status: "Active", certified: false },
  { starId: "STR-06758", name: "Ajay Kumar", designation: "Workshop Head", dealer: "Agro Tech Sales", state: "MP", zone: "Central", doj: "28 Jul 2019", status: "Active", certified: true },
  { starId: "STR-13892", name: "Lakshmi Iyer", designation: "Parts Advisor", dealer: "National Tractors", state: "Tamil Nadu", zone: "South", doj: "11 Mar 2024", status: "Active", certified: false },
];

const trainingData = [
  { starId: "STR-04821", name: "Arvind Sharma", program: "Advanced Tractor Diagnostics", completedDate: "12 Mar 2026", score: 87, status: "Passed", nextDue: "12 Mar 2027", certType: "Refresher" },
  { starId: "STR-07234", name: "Priya Nair", program: "Customer Service Excellence", completedDate: "08 Jan 2026", score: 92, status: "Passed", nextDue: "08 Jan 2027", certType: "Initial" },
  { starId: "STR-03912", name: "Ranjit Singh", program: "Workshop Management", completedDate: "15 Nov 2025", score: 78, status: "Passed", nextDue: "15 Nov 2026", certType: "Advanced" },
  { starId: "STR-09841", name: "Meena Kumari", program: "Parts & Inventory Basics", completedDate: "—", score: 0, status: "Pending", nextDue: "30 Jun 2026", certType: "Initial" },
  { starId: "STR-05623", name: "Deepak Patel", program: "Engine Overhaul Specialist", completedDate: "22 Feb 2026", score: 81, status: "Passed", nextDue: "22 Feb 2027", certType: "Refresher" },
  { starId: "STR-08347", name: "Sunita Reddy", program: "Digital Service Tools", completedDate: "17 Dec 2025", score: 94, status: "Passed", nextDue: "17 Dec 2026", certType: "Advanced" },
  { starId: "STR-02198", name: "Vikram Tomar", program: "Branch Operations Mgmt", completedDate: "03 Oct 2025", score: 88, status: "Passed", nextDue: "03 Oct 2026", certType: "Advanced" },
  { starId: "STR-11204", name: "Geeta Devi", program: "Tractor Mechanic Foundation", completedDate: "—", score: 0, status: "Enrolled", nextDue: "15 Jul 2026", certType: "Initial" },
];

const unresolvedData = [
  { id: "URE-001", starId: "STR-????", name: "Ramesh Kumar", issue: "No STAR ID found in master", source: "Manpower Roster", zone: "North", severity: "High" },
  { id: "URE-002", starId: "STR-14892", name: "Santosh Verma", issue: "Name mismatch across files", source: "Training Records", zone: "East", severity: "Medium" },
  { id: "URE-003", starId: "STR-????", name: "Pradeep Yadav", issue: "Dealer code invalid", source: "Dealer Master", zone: "Central", severity: "High" },
  { id: "URE-004", starId: "STR-09241", name: "Rekha Singh", issue: "Training date precedes DOJ", source: "Training Records", zone: "South", severity: "Low" },
  { id: "URE-005", starId: "STR-????", name: "Mohan Lal", issue: "No STAR ID found in master", source: "Manpower Roster", zone: "West", severity: "High" },
];

interface TableTab {
  id: string;
  label: string;
  count: number;
}

const tableTabs: TableTab[] = [
  { id: "manpower", label: "Manpower Roster", count: 3847 },
  { id: "training", label: "Training History", count: 12640 },
  { id: "unresolved", label: "Unresolved Mappings", count: 218 },
];

function SortIcon({ dir }: { dir: SortDir }) {
  if (dir === "asc") return <ChevronUp size={12} color="#D2232A" />;
  if (dir === "desc") return <ChevronDown size={12} color="#D2232A" />;
  return <ChevronsUpDown size={12} color="#C0C0D0" />;
}

function SeverityBadge({ level }: { level: string }) {
  const map: Record<string, { bg: string; color: string }> = {
    High: { bg: "rgba(198,40,40,0.1)", color: "#C62828" },
    Medium: { bg: "rgba(230,92,0,0.1)", color: "#E65C00" },
    Low: { bg: "rgba(46,125,50,0.1)", color: "#2E7D32" },
  };
  const style = map[level] || { bg: "#F5F5F8", color: "#6B6B8A" };
  return (
    <span style={{ background: style.bg, color: style.color, borderRadius: "4px", padding: "2px 8px", fontSize: "10px", fontWeight: 700 }}>
      {level}
    </span>
  );
}

export function DataTables() {
  const [activeTable, setActiveTable] = useState("manpower");
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<SortDir>(null);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : d === "desc" ? null : "asc"));
      if (sortDir === "desc") setSortKey(null);
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  const thStyle = (key: string): React.CSSProperties => ({
    padding: "10px 12px",
    textAlign: "left",
    fontSize: "11px",
    fontWeight: 600,
    color: "#6B6B8A",
    letterSpacing: "0.5px",
    background: "#F8F8FB",
    borderBottom: "1px solid #EBEBEF",
    cursor: "pointer",
    userSelect: "none",
    whiteSpace: "nowrap",
    position: "sticky",
    top: 0,
    zIndex: 1,
  });

  const tdStyle: React.CSSProperties = {
    padding: "9px 12px",
    fontSize: "12px",
    color: "#2A2A4A",
    borderBottom: "1px solid #F0F0F5",
    whiteSpace: "nowrap",
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      {/* Sub-tabs */}
      <div
        style={{
          background: "white",
          border: "1px solid #EBEBEF",
          borderRadius: "8px",
          boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
          overflow: "hidden",
        }}
      >
        {/* Table Tabs */}
        <div style={{ display: "flex", borderBottom: "1px solid #EBEBEF", background: "#FAFAFA" }}>
          {tableTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => { setActiveTable(tab.id); setSearch(""); }}
              style={{
                background: "transparent",
                border: "none",
                borderBottom: activeTable === tab.id ? "2px solid #D2232A" : "2px solid transparent",
                color: activeTable === tab.id ? "#D2232A" : "#6B6B8A",
                padding: "10px 16px",
                cursor: "pointer",
                fontSize: "12px",
                fontWeight: activeTable === tab.id ? 700 : 500,
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              {tab.label}
              <span
                style={{
                  background: activeTable === tab.id ? "rgba(210,35,42,0.1)" : "#EBEBEF",
                  color: activeTable === tab.id ? "#D2232A" : "#8B8BA7",
                  borderRadius: "10px",
                  padding: "1px 7px",
                  fontSize: "10px",
                  fontWeight: 700,
                }}
              >
                {tab.count.toLocaleString()}
              </span>
            </button>
          ))}
        </div>

        {/* Toolbar */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "12px 16px",
            borderBottom: "1px solid #F0F0F5",
          }}
        >
          <div style={{ position: "relative", width: "280px" }}>
            <Search size={14} color="#8B8BA7" style={{ position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)" }} />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by name, STAR ID, dealer..."
              style={{
                width: "100%",
                padding: "7px 10px 7px 32px",
                border: "1px solid #E0E0E8",
                borderRadius: "6px",
                fontSize: "12px",
                color: "#2A2A4A",
                outline: "none",
                background: "#FAFAFA",
              }}
            />
          </div>

          <div style={{ display: "flex", gap: "8px" }}>
            <button
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                background: "transparent",
                border: "1px solid #E0E0E8",
                borderRadius: "6px",
                padding: "6px 12px",
                cursor: "pointer",
                fontSize: "12px",
                color: "#4A4A6A",
                fontWeight: 500,
              }}
            >
              <Filter size={13} color="#8B8BA7" />
              Filters
            </button>
            <button
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                background: "#1A1A2E",
                border: "none",
                borderRadius: "6px",
                padding: "6px 12px",
                cursor: "pointer",
                fontSize: "12px",
                color: "white",
                fontWeight: 600,
              }}
            >
              <Download size={13} />
              Export
            </button>
          </div>
        </div>

        {/* Table */}
        <div style={{ overflowX: "auto", maxHeight: "420px", overflowY: "auto" }}>
          {activeTable === "manpower" && (
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {[
                    { key: "starId", label: "STAR ID" },
                    { key: "name", label: "Name" },
                    { key: "designation", label: "Designation" },
                    { key: "dealer", label: "Dealer" },
                    { key: "state", label: "State" },
                    { key: "zone", label: "Zone" },
                    { key: "doj", label: "DOJ" },
                    { key: "status", label: "Status" },
                    { key: "certified", label: "Certified" },
                  ].map(({ key, label }) => (
                    <th key={key} style={thStyle(key)} onClick={() => handleSort(key)}>
                      <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                        {label}
                        <SortIcon dir={sortKey === key ? sortDir : null} />
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {manpowerData
                  .filter((r) =>
                    !search ||
                    r.name.toLowerCase().includes(search.toLowerCase()) ||
                    r.starId.toLowerCase().includes(search.toLowerCase()) ||
                    r.dealer.toLowerCase().includes(search.toLowerCase())
                  )
                  .map((row, i) => (
                    <tr key={i} style={{ background: i % 2 === 0 ? "white" : "#FDFCFF" }}>
                      <td style={{ ...tdStyle, fontFamily: "monospace", color: "#D2232A", fontWeight: 600, fontSize: "11px" }}>{row.starId}</td>
                      <td style={{ ...tdStyle, fontWeight: 600 }}>{row.name}</td>
                      <td style={tdStyle}>{row.designation}</td>
                      <td style={{ ...tdStyle, color: "#4A4A6A" }}>{row.dealer}</td>
                      <td style={tdStyle}>{row.state}</td>
                      <td style={tdStyle}>
                        <span style={{ background: "#F0F0F8", border: "1px solid #D8D8E8", borderRadius: "4px", padding: "1px 6px", fontSize: "10px", color: "#4A4A6A" }}>
                          {row.zone}
                        </span>
                      </td>
                      <td style={{ ...tdStyle, color: "#8B8BA7" }}>{row.doj}</td>
                      <td style={tdStyle}>
                        <span style={{
                          background: row.status === "Active" ? "rgba(46,125,50,0.1)" : "rgba(230,92,0,0.1)",
                          color: row.status === "Active" ? "#2E7D32" : "#E65C00",
                          borderRadius: "4px",
                          padding: "2px 8px",
                          fontSize: "10px",
                          fontWeight: 600,
                        }}>
                          {row.status}
                        </span>
                      </td>
                      <td style={tdStyle}>
                        {row.certified
                          ? <span style={{ color: "#2E7D32", fontSize: "12px" }}>✓ Yes</span>
                          : <span style={{ color: "#E65C00", fontSize: "12px" }}>✗ No</span>
                        }
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          )}

          {activeTable === "training" && (
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {["STAR ID", "Name", "Program", "Completed", "Score", "Status", "Next Due", "Type"].map((h) => (
                    <th key={h} style={thStyle(h)}>
                      <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>{h} <SortIcon dir={null} /></div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {trainingData
                  .filter((r) =>
                    !search ||
                    r.name.toLowerCase().includes(search.toLowerCase()) ||
                    r.starId.toLowerCase().includes(search.toLowerCase()) ||
                    r.program.toLowerCase().includes(search.toLowerCase())
                  )
                  .map((row, i) => (
                    <tr key={i} style={{ background: i % 2 === 0 ? "white" : "#FDFCFF" }}>
                      <td style={{ ...tdStyle, fontFamily: "monospace", color: "#D2232A", fontWeight: 600, fontSize: "11px" }}>{row.starId}</td>
                      <td style={{ ...tdStyle, fontWeight: 600 }}>{row.name}</td>
                      <td style={tdStyle}>{row.program}</td>
                      <td style={{ ...tdStyle, color: "#8B8BA7" }}>{row.completedDate}</td>
                      <td style={tdStyle}>
                        {row.score > 0 ? (
                          <span style={{ fontWeight: 700, color: row.score >= 80 ? "#2E7D32" : row.score >= 60 ? "#E65C00" : "#C62828" }}>
                            {row.score}%
                          </span>
                        ) : "—"}
                      </td>
                      <td style={tdStyle}>
                        <span style={{
                          background: row.status === "Passed" ? "rgba(46,125,50,0.1)" : row.status === "Enrolled" ? "rgba(21,101,192,0.1)" : "rgba(230,92,0,0.1)",
                          color: row.status === "Passed" ? "#2E7D32" : row.status === "Enrolled" ? "#1565C0" : "#E65C00",
                          borderRadius: "4px",
                          padding: "2px 8px",
                          fontSize: "10px",
                          fontWeight: 600,
                        }}>
                          {row.status}
                        </span>
                      </td>
                      <td style={{ ...tdStyle, color: "#8B8BA7" }}>{row.nextDue}</td>
                      <td style={tdStyle}>
                        <span style={{ background: "#F0F0F8", border: "1px solid #D8D8E8", borderRadius: "4px", padding: "1px 6px", fontSize: "10px", color: "#4A4A6A" }}>
                          {row.certType}
                        </span>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          )}

          {activeTable === "unresolved" && (
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  {["ID", "STAR ID", "Name", "Issue", "Source", "Zone", "Severity", "Action"].map((h) => (
                    <th key={h} style={thStyle(h)}>
                      <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>{h} <SortIcon dir={null} /></div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {unresolvedData
                  .filter((r) =>
                    !search ||
                    r.name.toLowerCase().includes(search.toLowerCase()) ||
                    r.issue.toLowerCase().includes(search.toLowerCase())
                  )
                  .map((row, i) => (
                    <tr key={i} style={{ background: i % 2 === 0 ? "white" : "#FDFCFF" }}>
                      <td style={{ ...tdStyle, fontFamily: "monospace", fontSize: "11px", color: "#8B8BA7" }}>{row.id}</td>
                      <td style={{ ...tdStyle, fontFamily: "monospace", color: row.starId.includes("?") ? "#C62828" : "#D2232A", fontWeight: 600, fontSize: "11px" }}>{row.starId}</td>
                      <td style={{ ...tdStyle, fontWeight: 600 }}>{row.name}</td>
                      <td style={{ ...tdStyle, color: "#C62828" }}>{row.issue}</td>
                      <td style={tdStyle}>{row.source}</td>
                      <td style={tdStyle}>
                        <span style={{ background: "#F0F0F8", border: "1px solid #D8D8E8", borderRadius: "4px", padding: "1px 6px", fontSize: "10px", color: "#4A4A6A" }}>
                          {row.zone}
                        </span>
                      </td>
                      <td style={tdStyle}><SeverityBadge level={row.severity} /></td>
                      <td style={tdStyle}>
                        <button style={{ background: "transparent", border: "1px solid #D2232A", color: "#D2232A", borderRadius: "4px", padding: "3px 8px", fontSize: "10px", fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: "3px" }}>
                          Resolve <ArrowRight size={10} />
                        </button>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "10px 16px",
            borderTop: "1px solid #F0F0F5",
            background: "#FAFAFA",
          }}
        >
          <span style={{ fontSize: "11px", color: "#8B8BA7" }}>
            Showing {activeTable === "manpower" ? "10 of 3,847" : activeTable === "training" ? "8 of 12,640" : "5 of 218"} records
          </span>
          <div style={{ display: "flex", gap: "4px" }}>
            {["Prev", "1", "2", "3", "...", "385", "Next"].map((p) => (
              <button
                key={p}
                style={{
                  background: p === "1" ? "#D2232A" : "transparent",
                  border: "1px solid " + (p === "1" ? "#D2232A" : "#E0E0E8"),
                  color: p === "1" ? "white" : "#4A4A6A",
                  borderRadius: "4px",
                  padding: "4px 8px",
                  fontSize: "11px",
                  cursor: "pointer",
                  fontWeight: p === "1" ? 700 : 400,
                  minWidth: "30px",
                }}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
