import { useState } from "react";
import {
  ChevronLeft,
  ChevronRight,
  Upload,
  FileSpreadsheet,
  CheckCircle2,
  AlertCircle,
  Clock,
  ChevronDown,
  Play,
  Filter,
  X,
} from "lucide-react";

interface UploadedFile {
  name: string;
  role: string;
  status: "success" | "warning" | "pending";
  size: string;
  rows: number;
}

const uploadedFiles: UploadedFile[] = [
  { name: "Manpower_Roster_Apr26.xlsx", role: "Manpower Roster", status: "success", size: "2.4 MB", rows: 3847 },
  { name: "Training_Data_FY26.xlsx", role: "Training Records", status: "success", size: "1.8 MB", rows: 12640 },
  { name: "Dealer_Master_Q1.xlsx", role: "Dealer Master", status: "warning", size: "0.6 MB", rows: 892 },
];

const zones = ["All Zones", "North", "South", "East", "West", "Central"];
const states = ["All States", "Maharashtra", "Rajasthan", "UP", "Punjab", "Haryana", "MP", "Gujarat", "Karnataka"];
const designations = ["All Designations", "Tractor Mechanic", "Service Advisor", "Branch Manager", "Territory Manager", "Workshop Head"];
const dealers = ["All Dealers", "Auto Traders Pvt Ltd", "Krishi Motors", "Singh Enterprises", "Agro Tech Sales", "National Tractors"];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  filters: { zone: string; state: string; designation: string; dealer: string };
  onFilterChange: (key: string, value: string) => void;
  onRunPipeline: () => void;
  pipelineRunning: boolean;
}

export function Sidebar({ collapsed, onToggle, filters, onFilterChange, onRunPipeline, pipelineRunning }: SidebarProps) {
  const [dragOver, setDragOver] = useState(false);

  return (
    <aside
      style={{
        width: collapsed ? "64px" : "280px",
        minWidth: collapsed ? "64px" : "280px",
        backgroundColor: "#1A1A2E",
        borderRight: "1px solid #2D2D45",
        display: "flex",
        flexDirection: "column",
        transition: "width 0.2s ease, min-width 0.2s ease",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Logo Area */}
      <div
        style={{
          padding: collapsed ? "16px 0" : "0",
          borderBottom: "1px solid #2D2D45",
          background: "linear-gradient(135deg, #D2232A 0%, #8B0000 100%)",
          display: "flex",
          alignItems: "center",
          justifyContent: collapsed ? "center" : "space-between",
          minHeight: "64px",
          paddingLeft: collapsed ? "0" : "16px",
          paddingRight: collapsed ? "0" : "8px",
        }}
      >
        {!collapsed && (
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: "36px",
                height: "36px",
                background: "rgba(255,255,255,0.15)",
                borderRadius: "6px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L3 7V17L12 22L21 17V7L12 2Z" fill="white" fillOpacity="0.9" />
                <path d="M12 2L12 22M3 7L21 17M21 7L3 17" stroke="rgba(255,255,255,0.4)" strokeWidth="0.5" />
              </svg>
            </div>
            <div>
              <div style={{ color: "white", fontSize: "13px", fontWeight: 700, letterSpacing: "0.5px" }}>MAHINDRA</div>
              <div style={{ color: "rgba(255,255,255,0.75)", fontSize: "10px", letterSpacing: "1px", fontWeight: 500 }}>TRACTORS ANALYTICS</div>
            </div>
          </div>
        )}
        {collapsed && (
          <div
            style={{
              width: "36px",
              height: "36px",
              background: "rgba(255,255,255,0.15)",
              borderRadius: "6px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L3 7V17L12 22L21 17V7L12 2Z" fill="white" fillOpacity="0.9" />
            </svg>
          </div>
        )}
        <button
          onClick={onToggle}
          style={{
            background: "rgba(255,255,255,0.1)",
            border: "none",
            borderRadius: "4px",
            color: "white",
            cursor: "pointer",
            padding: "4px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* Scrollable Content */}
      <div style={{ flex: 1, overflowY: "auto", overflowX: "hidden" }}>
        {!collapsed && (
          <>
            {/* File Upload Section */}
            <div style={{ padding: "16px" }}>
              <div style={{ color: "#8B8BA7", fontSize: "10px", fontWeight: 600, letterSpacing: "1.5px", marginBottom: "10px" }}>
                FILE MANAGEMENT
              </div>

              {/* Drop Zone */}
              <div
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={(e) => { e.preventDefault(); setDragOver(false); }}
                style={{
                  border: `2px dashed ${dragOver ? "#D2232A" : "#3D3D5C"}`,
                  borderRadius: "8px",
                  padding: "16px",
                  textAlign: "center",
                  cursor: "pointer",
                  backgroundColor: dragOver ? "rgba(210,35,42,0.05)" : "rgba(255,255,255,0.02)",
                  transition: "all 0.2s",
                  marginBottom: "12px",
                }}
              >
                <Upload size={20} color={dragOver ? "#D2232A" : "#6B6B8A"} style={{ margin: "0 auto 6px" }} />
                <div style={{ color: "#8B8BA7", fontSize: "11px" }}>Drop Excel files here</div>
                <div style={{ color: "#5A5A78", fontSize: "10px", marginTop: "2px" }}>or</div>
                <button
                  style={{
                    marginTop: "6px",
                    background: "#D2232A",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    padding: "4px 12px",
                    fontSize: "11px",
                    cursor: "pointer",
                    fontWeight: 600,
                  }}
                >
                  Browse Files
                </button>
              </div>

              {/* Uploaded Files */}
              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                {uploadedFiles.map((file, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: "rgba(255,255,255,0.03)",
                      border: "1px solid #2D2D45",
                      borderRadius: "6px",
                      padding: "10px",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                      <FileSpreadsheet size={14} color="#4CAF50" />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ color: "#C8C8E0", fontSize: "11px", fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {file.name}
                        </div>
                        <div style={{ color: "#5A5A78", fontSize: "10px" }}>{file.size} · {file.rows.toLocaleString()} rows</div>
                      </div>
                      {file.status === "success" && <CheckCircle2 size={14} color="#4CAF50" />}
                      {file.status === "warning" && <AlertCircle size={14} color="#FF9800" />}
                      {file.status === "pending" && <Clock size={14} color="#8B8BA7" />}
                    </div>
                    <select
                      style={{
                        width: "100%",
                        background: "#0F0F24",
                        border: "1px solid #3D3D5C",
                        borderRadius: "4px",
                        color: "#A0A0C0",
                        fontSize: "10px",
                        padding: "3px 6px",
                        cursor: "pointer",
                      }}
                      defaultValue={file.role}
                    >
                      <option>Manpower Roster</option>
                      <option>Training Records</option>
                      <option>Dealer Master</option>
                      <option>STAR ID Reference</option>
                    </select>
                  </div>
                ))}
              </div>
            </div>

            {/* Divider */}
            <div style={{ height: "1px", background: "#2D2D45", margin: "0 16px" }} />

            {/* Filters */}
            <div style={{ padding: "16px" }}>
              <div style={{ color: "#8B8BA7", fontSize: "10px", fontWeight: 600, letterSpacing: "1.5px", marginBottom: "12px", display: "flex", alignItems: "center", gap: "6px" }}>
                <Filter size={10} /> FILTERS
              </div>

              {[
                { label: "Zone", key: "zone", options: zones },
                { label: "State", key: "state", options: states },
                { label: "Designation", key: "designation", options: designations },
                { label: "Dealer", key: "dealer", options: dealers },
              ].map(({ label, key, options }) => (
                <div key={key} style={{ marginBottom: "10px" }}>
                  <label style={{ color: "#6B6B8A", fontSize: "10px", fontWeight: 600, display: "block", marginBottom: "4px", letterSpacing: "0.5px" }}>
                    {label.toUpperCase()}
                  </label>
                  <div style={{ position: "relative" }}>
                    <select
                      value={filters[key as keyof typeof filters]}
                      onChange={(e) => onFilterChange(key, e.target.value)}
                      style={{
                        width: "100%",
                        background: "#0F0F24",
                        border: "1px solid #3D3D5C",
                        borderRadius: "4px",
                        color: "#C8C8E0",
                        fontSize: "11px",
                        padding: "6px 24px 6px 8px",
                        cursor: "pointer",
                        appearance: "none",
                      }}
                    >
                      {options.map((o) => <option key={o}>{o}</option>)}
                    </select>
                    <ChevronDown size={12} color="#6B6B8A" style={{ position: "absolute", right: "8px", top: "50%", transform: "translateY(-50%)", pointerEvents: "none" }} />
                  </div>
                </div>
              ))}

              {/* Active Filters */}
              <div style={{ display: "flex", flexWrap: "wrap", gap: "4px", marginBottom: "8px" }}>
                {filters.zone !== "All Zones" && (
                  <span style={{ background: "rgba(210,35,42,0.15)", border: "1px solid rgba(210,35,42,0.3)", borderRadius: "10px", padding: "2px 8px", fontSize: "10px", color: "#FF6B6B", display: "flex", alignItems: "center", gap: "4px" }}>
                    {filters.zone}
                    <X size={10} style={{ cursor: "pointer" }} onClick={() => onFilterChange("zone", "All Zones")} />
                  </span>
                )}
              </div>
            </div>

            {/* Divider */}
            <div style={{ height: "1px", background: "#2D2D45", margin: "0 16px" }} />

            {/* Run Pipeline CTA */}
            <div style={{ padding: "16px" }}>
              <button
                onClick={onRunPipeline}
                disabled={pipelineRunning}
                style={{
                  width: "100%",
                  background: pipelineRunning ? "#6B1A1E" : "linear-gradient(135deg, #D2232A 0%, #A01820 100%)",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  padding: "12px",
                  cursor: pipelineRunning ? "not-allowed" : "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px",
                  fontSize: "13px",
                  fontWeight: 700,
                  letterSpacing: "0.5px",
                  boxShadow: pipelineRunning ? "none" : "0 4px 12px rgba(210,35,42,0.4)",
                  transition: "all 0.2s",
                }}
              >
                <Play size={14} style={{ fill: "white" }} />
                {pipelineRunning ? "RUNNING..." : "RUN PIPELINE"}
              </button>
              <div style={{ color: "#4A4A6A", fontSize: "10px", textAlign: "center", marginTop: "6px" }}>
                {pipelineRunning ? "Processing 3 files..." : "3 files ready to process"}
              </div>
            </div>
          </>
        )}

        {collapsed && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "12px 0", gap: "16px" }}>
            <Upload size={18} color="#6B6B8A" style={{ cursor: "pointer" }} />
            <FileSpreadsheet size={18} color="#6B6B8A" style={{ cursor: "pointer" }} />
            <Filter size={18} color="#6B6B8A" style={{ cursor: "pointer" }} />
            <div style={{ height: "1px", width: "32px", background: "#2D2D45" }} />
            <button
              onClick={onRunPipeline}
              style={{ background: "#D2232A", border: "none", borderRadius: "6px", padding: "8px", cursor: "pointer" }}
            >
              <Play size={14} color="white" style={{ fill: "white" }} />
            </button>
          </div>
        )}
      </div>

      {/* Bottom Info */}
      {!collapsed && (
        <div style={{ padding: "12px 16px", borderTop: "1px solid #2D2D45", background: "#0F0F24" }}>
          <div style={{ color: "#4A4A6A", fontSize: "10px" }}>FY 2025-26 · Q1 Active</div>
          <div style={{ color: "#3A3A5A", fontSize: "10px" }}>Last sync: 20 May 2026, 09:42 AM</div>
        </div>
      )}
    </aside>
  );
}
