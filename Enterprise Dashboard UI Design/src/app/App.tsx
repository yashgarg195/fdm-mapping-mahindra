import { useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { KPICards } from "./components/KPICards";
import { AnalyticsSection } from "./components/AnalyticsSection";
import { PipelineStatus } from "./components/PipelineStatus";
import { DataTables } from "./components/DataTables";
import { AuditExceptions } from "./components/AuditExceptions";
import { ExportsSection } from "./components/ExportsSection";

export default function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [filters, setFilters] = useState({
    zone: "All Zones",
    state: "All States",
    designation: "All Designations",
    dealer: "All Dealers",
  });
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [pipelineCompleted, setPipelineCompleted] = useState(false);

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleRunPipeline = () => {
    if (pipelineRunning) return;
    setPipelineRunning(true);
    setPipelineCompleted(false);
    setActiveTab("pipeline");
  };

  const handlePipelineComplete = () => {
    setPipelineRunning(false);
    setPipelineCompleted(true);
  };

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        width: "100vw",
        overflow: "hidden",
        background: "#F2F2F6",
        fontFamily: "'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif",
      }}
    >
      {/* Sidebar */}
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed((v) => !v)}
        filters={filters}
        onFilterChange={handleFilterChange}
        onRunPipeline={handleRunPipeline}
        pipelineRunning={pipelineRunning}
      />

      {/* Main Content */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0, overflow: "hidden" }}>
        {/* Header */}
        <Header
          activeTab={activeTab}
          onTabChange={setActiveTab}
          sidebarCollapsed={sidebarCollapsed}
        />

        {/* Page Content */}
        <main
          style={{
            flex: 1,
            overflowY: "auto",
            overflowX: "hidden",
            padding: "20px 24px",
          }}
        >
          {/* Overview Tab */}
          {activeTab === "overview" && (
            <div>
              {/* Page Heading */}
              <div style={{ marginBottom: "16px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                  <div style={{ width: "3px", height: "18px", background: "#D2232A", borderRadius: "2px" }} />
                  <span style={{ fontSize: "15px", fontWeight: 700, color: "#1A1A2E" }}>Workforce Overview</span>
                  <span style={{ background: "#FFF0F0", color: "#D2232A", border: "1px solid #FFCCCC", borderRadius: "10px", padding: "1px 8px", fontSize: "10px", fontWeight: 700 }}>
                    FY 2025-26
                  </span>
                </div>
                <div style={{ fontSize: "12px", color: "#8B8BA7", paddingLeft: "11px" }}>
                  All Zones · All States · Last updated: 20 May 2026, 09:42 AM
                </div>
              </div>

              {/* KPI Cards */}
              <KPICards />

              {/* Analytics Charts */}
              <AnalyticsSection />
            </div>
          )}

          {/* Analytics Tab */}
          {activeTab === "analytics" && (
            <div>
              <div style={{ marginBottom: "16px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                  <div style={{ width: "3px", height: "18px", background: "#D2232A", borderRadius: "2px" }} />
                  <span style={{ fontSize: "15px", fontWeight: 700, color: "#1A1A2E" }}>Analytics Deep Dive</span>
                </div>
                <div style={{ fontSize: "12px", color: "#8B8BA7", paddingLeft: "11px" }}>
                  Training trends, zone performance, and certification analytics
                </div>
              </div>
              <AnalyticsSection />
            </div>
          )}

          {/* Pipeline Tab */}
          {activeTab === "pipeline" && (
            <div>
              <div style={{ marginBottom: "16px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                  <div style={{ width: "3px", height: "18px", background: "#D2232A", borderRadius: "2px" }} />
                  <span style={{ fontSize: "15px", fontWeight: 700, color: "#1A1A2E" }}>Processing Pipeline</span>
                  {pipelineRunning && (
                    <span style={{ background: "#FFF0F0", color: "#D2232A", border: "1px solid #FFCCCC", borderRadius: "10px", padding: "1px 8px", fontSize: "10px", fontWeight: 700 }}>
                      ● RUNNING
                    </span>
                  )}
                  {pipelineCompleted && !pipelineRunning && (
                    <span style={{ background: "rgba(46,125,50,0.1)", color: "#2E7D32", border: "1px solid rgba(46,125,50,0.3)", borderRadius: "10px", padding: "1px 8px", fontSize: "10px", fontWeight: 700 }}>
                      ✓ COMPLETED
                    </span>
                  )}
                </div>
                <div style={{ fontSize: "12px", color: "#8B8BA7", paddingLeft: "11px" }}>
                  File parsing → Employee matching → Validation → Exception handling → Report generation
                </div>
              </div>
              <PipelineStatus running={pipelineRunning} onComplete={handlePipelineComplete} />
            </div>
          )}

          {/* Data Tables Tab */}
          {activeTab === "data" && (
            <div>
              <div style={{ marginBottom: "16px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                  <div style={{ width: "3px", height: "18px", background: "#D2232A", borderRadius: "2px" }} />
                  <span style={{ fontSize: "15px", fontWeight: 700, color: "#1A1A2E" }}>Data Tables</span>
                </div>
                <div style={{ fontSize: "12px", color: "#8B8BA7", paddingLeft: "11px" }}>
                  Search, filter, and export manpower, training, and mapping records
                </div>
              </div>
              <DataTables />
            </div>
          )}

          {/* Audit & Exceptions Tab */}
          {activeTab === "audit" && (
            <div>
              <div style={{ marginBottom: "16px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                  <div style={{ width: "3px", height: "18px", background: "#D2232A", borderRadius: "2px" }} />
                  <span style={{ fontSize: "15px", fontWeight: 700, color: "#1A1A2E" }}>Audit & Exceptions</span>
                  <span style={{ background: "rgba(198,40,40,0.1)", color: "#C62828", border: "1px solid rgba(198,40,40,0.2)", borderRadius: "10px", padding: "1px 8px", fontSize: "10px", fontWeight: 700 }}>
                    218 Open
                  </span>
                </div>
                <div style={{ fontSize: "12px", color: "#8B8BA7", paddingLeft: "11px" }}>
                  Governance queue: unresolved records, duplicate IDs, and data integrity exceptions
                </div>
              </div>
              <AuditExceptions />
            </div>
          )}

          {/* Exports Tab */}
          {activeTab === "exports" && (
            <div>
              <div style={{ marginBottom: "16px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                  <div style={{ width: "3px", height: "18px", background: "#D2232A", borderRadius: "2px" }} />
                  <span style={{ fontSize: "15px", fontWeight: 700, color: "#1A1A2E" }}>Reports & Exports</span>
                </div>
                <div style={{ fontSize: "12px", color: "#8B8BA7", paddingLeft: "11px" }}>
                  Generate audit-ready Excel reports, nominations lists, and data exports
                </div>
              </div>
              <ExportsSection />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
