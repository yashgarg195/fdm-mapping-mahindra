import { useState } from "react";
import {
  Download,
  FileSpreadsheet,
  FileText,
  ClipboardList,
  Users,
  CheckCircle2,
  Clock,
  Loader2,
  ChevronRight,
  Shield,
  Calendar,
  BarChart2,
} from "lucide-react";

interface ReportCard {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  iconColor: string;
  iconBg: string;
  stats: { label: string; value: string }[];
  lastGenerated: string;
  size: string;
  format: string;
}

const reports: ReportCard[] = [
  {
    id: "master",
    title: "Master Analytics Report",
    description: "Comprehensive workforce and training analytics for the selected fiscal year and filters. Includes all KPI summaries, zone-wise breakdowns, and specialist penetration data.",
    icon: <BarChart2 size={20} />,
    iconColor: "#D2232A",
    iconBg: "#FFF0F0",
    stats: [
      { label: "Records", value: "3,847" },
      { label: "Sheets", value: "12" },
      { label: "Charts", value: "8" },
    ],
    lastGenerated: "20 May 2026, 09:42 AM",
    size: "~4.2 MB",
    format: "XLSX",
  },
  {
    id: "nominations",
    title: "Training Nominations List",
    description: "Auto-generated list of employees due for refresher training, skill uplift programs, or initial certification — filtered by zone, state, and designation.",
    icon: <Users size={20} />,
    iconColor: "#1565C0",
    iconBg: "#EEF4FF",
    stats: [
      { label: "Nominees", value: "621" },
      { label: "Programs", value: "7" },
      { label: "Zones", value: "5" },
    ],
    lastGenerated: "20 May 2026, 09:42 AM",
    size: "~1.1 MB",
    format: "XLSX",
  },
  {
    id: "audit",
    title: "Audit Exception Log",
    description: "Full governance audit trail listing all exceptions, unresolved mappings, duplicate STAR IDs, future DOJ alerts, and training mismatches with resolution status.",
    icon: <Shield size={20} />,
    iconColor: "#C62828",
    iconBg: "rgba(198,40,40,0.08)",
    stats: [
      { label: "Exceptions", value: "218" },
      { label: "Critical", value: "47" },
      { label: "Resolved", value: "12" },
    ],
    lastGenerated: "20 May 2026, 09:42 AM",
    size: "~0.8 MB",
    format: "XLSX",
  },
  {
    id: "roster",
    title: "Dealer Manpower Roster",
    description: "Complete dealer-wise manpower listing with STAR IDs, designation, certification status, training history summary, and refresher backlog indicators.",
    icon: <ClipboardList size={20} />,
    iconColor: "#2E7D32",
    iconBg: "rgba(46,125,50,0.08)",
    stats: [
      { label: "Dealers", value: "892" },
      { label: "Employees", value: "3,847" },
      { label: "States", value: "18" },
    ],
    lastGenerated: "20 May 2026, 09:42 AM",
    size: "~3.6 MB",
    format: "XLSX",
  },
];

const quickExports = [
  { label: "Specialist Penetration Summary", icon: <FileSpreadsheet size={14} />, format: "XLSX" },
  { label: "Refresher Backlog by Zone", icon: <FileSpreadsheet size={14} />, format: "XLSX" },
  { label: "Unresolved Records Export", icon: <FileText size={14} />, format: "XLSX" },
  { label: "Certification Status Matrix", icon: <FileSpreadsheet size={14} />, format: "XLSX" },
  { label: "Pipeline Execution Summary", icon: <FileText size={14} />, format: "PDF" },
  { label: "State-wise Performance Report", icon: <FileSpreadsheet size={14} />, format: "XLSX" },
];

export function ExportsSection() {
  const [generatingId, setGeneratingId] = useState<string | null>(null);
  const [downloadedIds, setDownloadedIds] = useState<string[]>([]);

  const handleGenerate = (id: string) => {
    setGeneratingId(id);
    setTimeout(() => {
      setGeneratingId(null);
      setDownloadedIds((prev) => [...prev, id]);
    }, 2500);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* Header Banner */}
      <div
        style={{
          background: "linear-gradient(135deg, #1A1A2E 0%, #2D2D4E 100%)",
          borderRadius: "10px",
          padding: "20px 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div>
          <div style={{ color: "white", fontSize: "16px", fontWeight: 700, marginBottom: "4px" }}>
            Report Generation Center
          </div>
          <div style={{ color: "rgba(255,255,255,0.6)", fontSize: "12px" }}>
            Generate audit-ready Excel reports and export data for FY 2025-26 · All filters applied
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div style={{ textAlign: "right" }}>
            <div style={{ color: "rgba(255,255,255,0.5)", fontSize: "10px", marginBottom: "2px" }}>Last Pipeline Run</div>
            <div style={{ color: "white", fontSize: "12px", fontWeight: 600, display: "flex", alignItems: "center", gap: "4px" }}>
              <CheckCircle2 size={12} color="#4CAF50" /> 20 May 2026, 09:42 AM
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ color: "rgba(255,255,255,0.5)", fontSize: "10px", marginBottom: "2px" }}>Data Coverage</div>
            <div style={{ color: "white", fontSize: "12px", fontWeight: 600 }}>FY 2025-26 · All Zones</div>
          </div>
        </div>
      </div>

      {/* Main Report Cards */}
      <div>
        <div style={{ fontSize: "13px", fontWeight: 700, color: "#1A1A2E", marginBottom: "12px", letterSpacing: "0.1px" }}>
          Standard Reports
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "14px" }}>
          {reports.map((report) => {
            const isGenerating = generatingId === report.id;
            const isDownloaded = downloadedIds.includes(report.id);

            return (
              <div
                key={report.id}
                style={{
                  background: "white",
                  border: "1px solid #EBEBEF",
                  borderRadius: "10px",
                  padding: "18px",
                  boxShadow: "0 1px 6px rgba(0,0,0,0.05)",
                  display: "flex",
                  flexDirection: "column",
                  gap: "12px",
                }}
              >
                {/* Top */}
                <div style={{ display: "flex", alignItems: "flex-start", gap: "12px" }}>
                  <div
                    style={{
                      width: "44px",
                      height: "44px",
                      background: report.iconBg,
                      borderRadius: "8px",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: report.iconColor,
                      flexShrink: 0,
                    }}
                  >
                    {report.icon}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: "13px", fontWeight: 700, color: "#1A1A2E", marginBottom: "3px" }}>
                      {report.title}
                    </div>
                    <div style={{ fontSize: "11px", color: "#6B6B8A", lineHeight: 1.5 }}>
                      {report.description}
                    </div>
                  </div>
                </div>

                {/* Stats */}
                <div style={{ display: "flex", gap: "8px" }}>
                  {report.stats.map((stat) => (
                    <div
                      key={stat.label}
                      style={{
                        flex: 1,
                        background: "#F8F8FB",
                        borderRadius: "6px",
                        padding: "6px 8px",
                        textAlign: "center",
                      }}
                    >
                      <div style={{ fontSize: "14px", fontWeight: 800, color: "#1A1A2E" }}>{stat.value}</div>
                      <div style={{ fontSize: "9px", color: "#8B8BA7", fontWeight: 600, letterSpacing: "0.3px" }}>{stat.label.toUpperCase()}</div>
                    </div>
                  ))}
                </div>

                {/* Meta */}
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <div style={{ display: "flex", gap: "12px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "10px", color: "#8B8BA7" }}>
                      <Clock size={10} />
                      {report.lastGenerated}
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "10px", color: "#8B8BA7" }}>
                      <FileSpreadsheet size={10} />
                      {report.format} · {report.size}
                    </div>
                  </div>
                </div>

                {/* Action */}
                <div style={{ display: "flex", gap: "8px" }}>
                  <button
                    onClick={() => handleGenerate(report.id)}
                    disabled={isGenerating}
                    style={{
                      flex: 1,
                      background: isDownloaded ? "#2E7D32" : report.iconColor,
                      color: "white",
                      border: "none",
                      borderRadius: "6px",
                      padding: "10px",
                      cursor: isGenerating ? "not-allowed" : "pointer",
                      fontSize: "12px",
                      fontWeight: 700,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: "6px",
                      opacity: isGenerating ? 0.8 : 1,
                      transition: "all 0.2s",
                    }}
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 size={14} style={{ animation: "spin 1s linear infinite" }} />
                        Generating...
                      </>
                    ) : isDownloaded ? (
                      <>
                        <CheckCircle2 size={14} />
                        Downloaded
                      </>
                    ) : (
                      <>
                        <Download size={14} />
                        Generate & Download
                      </>
                    )}
                  </button>
                  {isDownloaded && (
                    <button
                      onClick={() => handleGenerate(report.id)}
                      style={{
                        background: "#F5F5F8",
                        border: "1px solid #E0E0E8",
                        borderRadius: "6px",
                        padding: "10px 12px",
                        cursor: "pointer",
                        color: "#4A4A6A",
                        fontSize: "12px",
                        fontWeight: 500,
                      }}
                    >
                      Regenerate
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Quick Exports */}
      <div>
        <div style={{ fontSize: "13px", fontWeight: 700, color: "#1A1A2E", marginBottom: "12px" }}>
          Quick Exports
        </div>
        <div style={{ background: "white", border: "1px solid #EBEBEF", borderRadius: "10px", overflow: "hidden", boxShadow: "0 1px 4px rgba(0,0,0,0.04)" }}>
          {quickExports.map((exp, i) => (
            <div
              key={exp.label}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "12px 16px",
                borderBottom: i < quickExports.length - 1 ? "1px solid #F0F0F5" : "none",
                cursor: "pointer",
                transition: "background 0.1s",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "#FAFAFA")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "white")}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <span style={{ color: "#D2232A" }}>{exp.icon}</span>
                <span style={{ fontSize: "12px", color: "#2A2A4A", fontWeight: 500 }}>{exp.label}</span>
                <span style={{ background: "#F0F0F8", border: "1px solid #D8D8E8", borderRadius: "4px", padding: "1px 6px", fontSize: "10px", color: "#6B6B8A" }}>
                  {exp.format}
                </span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#D2232A" }}>
                <span style={{ fontSize: "11px", fontWeight: 600 }}>Download</span>
                <ChevronRight size={14} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Export History */}
      <div>
        <div style={{ fontSize: "13px", fontWeight: 700, color: "#1A1A2E", marginBottom: "12px" }}>
          Recent Export History
        </div>
        <div style={{ background: "white", border: "1px solid #EBEBEF", borderRadius: "10px", overflow: "hidden", boxShadow: "0 1px 4px rgba(0,0,0,0.04)" }}>
          {[
            { file: "Master_Analytics_FY26_Apr.xlsx", user: "Rajesh Kumar", date: "19 May 2026, 03:22 PM", size: "4.1 MB" },
            { file: "Nominations_Q1_FY26.xlsx", user: "Anita Sharma", date: "18 May 2026, 11:45 AM", size: "1.0 MB" },
            { file: "Audit_Log_Week20.xlsx", user: "Rajesh Kumar", date: "17 May 2026, 09:30 AM", size: "0.7 MB" },
            { file: "Dealer_Manpower_Roster_May26.xlsx", user: "Vikram Tomar", date: "15 May 2026, 04:12 PM", size: "3.5 MB" },
          ].map((item, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "10px 16px",
                borderBottom: i < 3 ? "1px solid #F0F0F5" : "none",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <FileSpreadsheet size={16} color="#4CAF50" />
                <div>
                  <div style={{ fontSize: "12px", fontWeight: 600, color: "#2A2A4A" }}>{item.file}</div>
                  <div style={{ fontSize: "10px", color: "#8B8BA7" }}>by {item.user} · {item.size}</div>
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "11px", color: "#8B8BA7" }}>
                  <Calendar size={11} />
                  {item.date}
                </div>
                <button style={{ background: "transparent", border: "1px solid #E0E0E8", borderRadius: "4px", padding: "4px 8px", cursor: "pointer", color: "#4A4A6A", fontSize: "11px", display: "flex", alignItems: "center", gap: "4px" }}>
                  <Download size={11} /> Re-download
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
