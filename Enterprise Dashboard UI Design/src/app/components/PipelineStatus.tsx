import { useState, useEffect } from "react";
import {
  FileText,
  GitMerge,
  ShieldCheck,
  AlertOctagon,
  FileOutput,
  CheckCircle2,
  Loader2,
  Clock,
  ChevronRight,
  Activity,
  Cpu,
} from "lucide-react";

interface PipelineStep {
  id: string;
  label: string;
  description: string;
  status: "completed" | "running" | "pending" | "error";
  duration?: string;
  details: string[];
  icon: React.ReactNode;
}

interface PipelineStatusProps {
  running: boolean;
  onComplete: () => void;
}

const initialSteps: PipelineStep[] = [
  {
    id: "parse",
    label: "File Parsing",
    description: "Reading and validating Excel data structures",
    status: "pending",
    details: ["Manpower_Roster_Apr26.xlsx", "Training_Data_FY26.xlsx", "Dealer_Master_Q1.xlsx"],
    icon: <FileText size={16} />,
  },
  {
    id: "match",
    label: "Employee Matching",
    description: "Cross-referencing STAR IDs across datasets",
    status: "pending",
    details: ["Matching by STAR ID", "Fallback to Name + DOJ", "3,847 records queued"],
    icon: <GitMerge size={16} />,
  },
  {
    id: "validate",
    label: "Data Validation",
    description: "Enforcing business rules and data integrity",
    status: "pending",
    details: ["DOJ future date check", "Duplicate ID detection", "Designation validation"],
    icon: <ShieldCheck size={16} />,
  },
  {
    id: "exceptions",
    label: "Exception Handling",
    description: "Flagging unresolved and conflicting records",
    status: "pending",
    details: ["218 unresolved records", "47 duplicate STAR IDs", "12 future DOJ alerts"],
    icon: <AlertOctagon size={16} />,
  },
  {
    id: "report",
    label: "Report Generation",
    description: "Compiling audit-ready Excel and summary outputs",
    status: "pending",
    details: ["Master report", "Nominations list", "Audit log export"],
    icon: <FileOutput size={16} />,
  },
];

const processingLog = [
  "[09:42:01] Pipeline initiated by Rajesh Kumar",
  "[09:42:02] Loading Manpower_Roster_Apr26.xlsx (3,847 rows)...",
  "[09:42:04] Loading Training_Data_FY26.xlsx (12,640 rows)...",
  "[09:42:05] Loading Dealer_Master_Q1.xlsx (892 rows)...",
  "[09:42:07] File parsing complete. 3 files validated.",
  "[09:42:08] Starting STAR ID matching engine...",
  "[09:42:12] Matched 3,412 records (88.7%) via primary STAR ID",
  "[09:42:14] Fallback matching: 217 records via Name+DOJ",
  "[09:42:15] Unresolved: 218 records flagged for review",
  "[09:42:16] Running validation rules...",
  "[09:42:19] DOJ check: 12 future dates detected",
  "[09:42:20] Duplicate STAR IDs: 47 pairs identified",
  "[09:42:22] Exceptions logged: 218 records",
  "[09:42:24] Generating master report...",
  "[09:42:28] ✓ Pipeline completed successfully",
];

function StatusIcon({ status }: { status: PipelineStep["status"] }) {
  if (status === "completed") return <CheckCircle2 size={18} color="#2E7D32" />;
  if (status === "running") return <Loader2 size={18} color="#D2232A" style={{ animation: "spin 1s linear infinite" }} />;
  if (status === "error") return <AlertOctagon size={18} color="#C62828" />;
  return <div style={{ width: "18px", height: "18px", borderRadius: "50%", border: "2px solid #D0D0E0" }} />;
}

export function PipelineStatus({ running, onComplete }: PipelineStatusProps) {
  const [steps, setSteps] = useState<PipelineStep[]>(initialSteps);
  const [currentStep, setCurrentStep] = useState(-1);
  const [logs, setLogs] = useState<string[]>([]);
  const [logIndex, setLogIndex] = useState(0);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    if (!running) {
      setSteps(initialSteps);
      setCurrentStep(-1);
      setLogs([]);
      setLogIndex(0);
      setCompleted(false);
      return;
    }

    let stepIdx = 0;
    const stepDurations = [2000, 3000, 2500, 2000, 2000];

    function advanceStep() {
      if (stepIdx >= initialSteps.length) {
        setCompleted(true);
        onComplete();
        return;
      }
      const s = stepIdx;
      setCurrentStep(s);
      setSteps((prev) =>
        prev.map((st, i) => ({
          ...st,
          status: i < s ? "completed" : i === s ? "running" : "pending",
        }))
      );
      setTimeout(() => {
        setSteps((prev) =>
          prev.map((st, i) => ({
            ...st,
            status: i <= s ? "completed" : "pending",
          }))
        );
        stepIdx++;
        advanceStep();
      }, stepDurations[s] || 2000);
    }
    advanceStep();
  }, [running]);

  useEffect(() => {
    if (!running && !completed) return;
    if (logIndex >= processingLog.length) return;
    const timer = setTimeout(() => {
      setLogs((prev) => [...prev, processingLog[logIndex]]);
      setLogIndex((i) => i + 1);
    }, 600);
    return () => clearTimeout(timer);
  }, [running, logIndex, completed]);

  const overallProgress = steps.filter((s) => s.status === "completed").length;
  const progressPercent = (overallProgress / steps.length) * 100;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      {/* Pipeline Header */}
      <div
        style={{
          background: "white",
          border: "1px solid #EBEBEF",
          borderRadius: "8px",
          padding: "16px 20px",
          boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: "36px",
                height: "36px",
                background: running ? "rgba(210,35,42,0.08)" : completed ? "rgba(46,125,50,0.08)" : "#F5F5F8",
                borderRadius: "8px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {running ? (
                <Cpu size={18} color="#D2232A" style={{ animation: "pulse 1s ease-in-out infinite" }} />
              ) : completed ? (
                <CheckCircle2 size={18} color="#2E7D32" />
              ) : (
                <Activity size={18} color="#8B8BA7" />
              )}
            </div>
            <div>
              <div style={{ fontSize: "14px", fontWeight: 700, color: "#1A1A2E" }}>
                Processing Pipeline
              </div>
              <div style={{ fontSize: "11px", color: "#8B8BA7" }}>
                {completed
                  ? "Pipeline completed — 20 May 2026, 09:42:28"
                  : running
                  ? `Step ${Math.min(currentStep + 1, 5)} of 5 in progress...`
                  : "Ready to execute — 3 files loaded"}
              </div>
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            {(running || completed) && (
              <div style={{ fontSize: "13px", fontWeight: 700, color: completed ? "#2E7D32" : "#D2232A" }}>
                {Math.round(progressPercent)}% Complete
              </div>
            )}
            <div
              style={{
                background: running ? "#FFF0F0" : completed ? "#F0F8F0" : "#F5F5F8",
                color: running ? "#D2232A" : completed ? "#2E7D32" : "#8B8BA7",
                border: `1px solid ${running ? "#FFCCCC" : completed ? "#BBDDBB" : "#E0E0E8"}`,
                borderRadius: "20px",
                padding: "4px 12px",
                fontSize: "11px",
                fontWeight: 600,
              }}
            >
              {running ? "● RUNNING" : completed ? "✓ COMPLETED" : "○ IDLE"}
            </div>
          </div>
        </div>

        {/* Overall Progress Bar */}
        <div style={{ height: "6px", background: "#F0F0F5", borderRadius: "3px", overflow: "hidden" }}>
          <div
            style={{
              height: "100%",
              width: `${progressPercent}%`,
              background: completed ? "#2E7D32" : "linear-gradient(90deg, #D2232A, #FF6B6B)",
              borderRadius: "3px",
              transition: "width 0.5s ease",
            }}
          />
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "3fr 2fr", gap: "16px" }}>
        {/* Step Tracker */}
        <div
          style={{
            background: "white",
            border: "1px solid #EBEBEF",
            borderRadius: "8px",
            padding: "20px",
            boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
          }}
        >
          <div style={{ fontSize: "13px", fontWeight: 700, color: "#1A1A2E", marginBottom: "20px" }}>
            Pipeline Steps
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0" }}>
            {steps.map((step, idx) => (
              <div key={step.id} style={{ display: "flex", gap: "14px" }}>
                {/* Step Line */}
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: "20px", flexShrink: 0 }}>
                  <StatusIcon status={step.status} />
                  {idx < steps.length - 1 && (
                    <div
                      style={{
                        width: "2px",
                        flex: 1,
                        minHeight: "32px",
                        background: step.status === "completed" ? "#2E7D32" : "#E0E0E8",
                        margin: "4px 0",
                        transition: "background 0.3s",
                      }}
                    />
                  )}
                </div>

                {/* Step Content */}
                <div
                  style={{
                    flex: 1,
                    paddingBottom: idx < steps.length - 1 ? "24px" : "0",
                    opacity: step.status === "pending" ? 0.5 : 1,
                    transition: "opacity 0.3s",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                    <span
                      style={{
                        color: step.status === "completed" ? "#2E7D32" : step.status === "running" ? "#D2232A" : "#8B8BA7",
                      }}
                    >
                      {step.icon}
                    </span>
                    <span style={{ fontSize: "13px", fontWeight: 700, color: "#1A1A2E" }}>{step.label}</span>
                    {step.status === "running" && (
                      <span style={{ fontSize: "10px", color: "#D2232A", fontWeight: 600, animation: "pulse 1s ease-in-out infinite" }}>
                        PROCESSING
                      </span>
                    )}
                    {step.status === "completed" && (
                      <span style={{ fontSize: "10px", color: "#2E7D32", fontWeight: 600 }}>DONE</span>
                    )}
                  </div>
                  <div style={{ fontSize: "11px", color: "#6B6B8A", marginBottom: "6px" }}>{step.description}</div>
                  {step.status !== "pending" && (
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
                      {step.details.map((d, i) => (
                        <span
                          key={i}
                          style={{
                            background: "#F5F5F8",
                            border: "1px solid #E8E8EC",
                            borderRadius: "4px",
                            padding: "2px 8px",
                            fontSize: "10px",
                            color: "#4A4A6A",
                          }}
                        >
                          {d}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Processing Log */}
        <div
          style={{
            background: "#0F0F24",
            border: "1px solid #2D2D45",
            borderRadius: "8px",
            padding: "16px",
            fontFamily: "'Courier New', monospace",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
            <div style={{ display: "flex", gap: "4px" }}>
              <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#FF5F57" }} />
              <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#FFBD2E" }} />
              <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#28CA41" }} />
            </div>
            <span style={{ fontSize: "11px", color: "#6B6B8A", fontFamily: "sans-serif" }}>Processing Log</span>
          </div>

          <div style={{ height: "340px", overflowY: "auto" }}>
            {logs.length === 0 ? (
              <div style={{ color: "#4A4A6A", fontSize: "11px" }}>
                {"> "}<span style={{ color: "#6B6B8A" }}>Awaiting pipeline execution...</span>
              </div>
            ) : (
              logs.map((log, i) => (
                <div
                  key={i}
                  style={{
                    fontSize: "11px",
                    color: log.includes("✓") ? "#4CAF50" : log.includes("flagged") || log.includes("Unresolved") ? "#FF9800" : "#8B8BA7",
                    marginBottom: "3px",
                    lineHeight: 1.5,
                  }}
                >
                  {"> "}{log}
                </div>
              ))
            )}
            {running && (
              <div style={{ fontSize: "11px", color: "#D2232A", marginTop: "4px" }}>
                {">"} <span style={{ animation: "blink 1s step-end infinite" }}>█</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Summary Cards (post-completion) */}
      {completed && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "12px" }}>
          {[
            { label: "Records Processed", value: "3,847", color: "#1565C0", bg: "#EEF4FF" },
            { label: "Successfully Matched", value: "3,629", color: "#2E7D32", bg: "#F0F8F0" },
            { label: "Exceptions Flagged", value: "218", color: "#E65C00", bg: "#FFF5E6" },
            { label: "Reports Generated", value: "3", color: "#D2232A", bg: "#FFF0F0" },
          ].map((s, i) => (
            <div
              key={i}
              style={{
                background: "white",
                border: "1px solid #EBEBEF",
                borderRadius: "8px",
                padding: "14px",
                display: "flex",
                alignItems: "center",
                gap: "12px",
                boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
              }}
            >
              <div
                style={{
                  width: "40px",
                  height: "40px",
                  background: s.bg,
                  borderRadius: "8px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "16px",
                  fontWeight: 800,
                  color: s.color,
                }}
              >
                {s.value.charAt(0)}
              </div>
              <div>
                <div style={{ fontSize: "18px", fontWeight: 800, color: "#1A1A2E", lineHeight: 1 }}>{s.value}</div>
                <div style={{ fontSize: "11px", color: "#6B6B8A", marginTop: "2px" }}>{s.label}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
      `}</style>
    </div>
  );
}
