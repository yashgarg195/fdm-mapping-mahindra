import { Bell, RefreshCw, Download, ChevronDown, User, Shield, Clock } from "lucide-react";
import { useState } from "react";

const fiscalYears = ["FY 2025-26", "FY 2024-25", "FY 2023-24"];

interface HeaderProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  sidebarCollapsed: boolean;
}

const tabs = [
  { id: "overview", label: "Overview" },
  { id: "analytics", label: "Analytics" },
  { id: "pipeline", label: "Pipeline" },
  { id: "data", label: "Data Tables" },
  { id: "audit", label: "Audit & Exceptions" },
  { id: "exports", label: "Exports" },
];

export function Header({ activeTab, onTabChange, sidebarCollapsed }: HeaderProps) {
  const [selectedFY, setSelectedFY] = useState("FY 2025-26");
  const [showFYDropdown, setShowFYDropdown] = useState(false);

  return (
    <header
      style={{
        background: "white",
        borderBottom: "1px solid #E8E8EC",
        flexShrink: 0,
        zIndex: 10,
      }}
    >
      {/* Top Bar */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 24px",
          height: "56px",
          borderBottom: "1px solid #EEEEEF",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div>
            <div style={{ fontSize: "15px", fontWeight: 700, color: "#1A1A2E", letterSpacing: "-0.2px" }}>
              Training & Manpower Analytics
            </div>
            <div style={{ fontSize: "11px", color: "#8B8BA7", letterSpacing: "0.3px" }}>
              Mahindra Tractors · Workforce Intelligence Platform
            </div>
          </div>

          {/* Fiscal Year Selector */}
          <div style={{ position: "relative" }}>
            <button
              onClick={() => setShowFYDropdown(!showFYDropdown)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                background: "#F5F5F8",
                border: "1px solid #E0E0E8",
                borderRadius: "6px",
                padding: "5px 10px",
                cursor: "pointer",
                fontSize: "12px",
                color: "#1A1A2E",
                fontWeight: 600,
              }}
            >
              <Shield size={12} color="#D2232A" />
              {selectedFY}
              <ChevronDown size={12} color="#8B8BA7" />
            </button>
            {showFYDropdown && (
              <div
                style={{
                  position: "absolute",
                  top: "calc(100% + 4px)",
                  left: 0,
                  background: "white",
                  border: "1px solid #E0E0E8",
                  borderRadius: "6px",
                  boxShadow: "0 4px 16px rgba(0,0,0,0.1)",
                  zIndex: 100,
                  minWidth: "140px",
                  overflow: "hidden",
                }}
              >
                {fiscalYears.map((fy) => (
                  <button
                    key={fy}
                    onClick={() => { setSelectedFY(fy); setShowFYDropdown(false); }}
                    style={{
                      display: "block",
                      width: "100%",
                      textAlign: "left",
                      padding: "8px 12px",
                      background: selectedFY === fy ? "#FFF0F0" : "transparent",
                      color: selectedFY === fy ? "#D2232A" : "#1A1A2E",
                      border: "none",
                      cursor: "pointer",
                      fontSize: "12px",
                      fontWeight: selectedFY === fy ? 600 : 400,
                    }}
                  >
                    {fy}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Section */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          {/* Last Refresh */}
          <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#8B8BA7", fontSize: "11px" }}>
            <Clock size={12} />
            <span>Updated: 20 May 2026, 09:42 AM</span>
          </div>

          {/* Actions */}
          <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <button
              style={{
                background: "transparent",
                border: "1px solid #E0E0E8",
                borderRadius: "6px",
                padding: "6px 8px",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "6px",
                fontSize: "12px",
                color: "#4A4A6A",
                fontWeight: 500,
              }}
            >
              <RefreshCw size={13} color="#8B8BA7" />
              Refresh
            </button>

            <button
              style={{
                background: "#1A1A2E",
                border: "none",
                borderRadius: "6px",
                padding: "6px 12px",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "6px",
                fontSize: "12px",
                color: "white",
                fontWeight: 600,
              }}
            >
              <Download size={13} />
              Export
            </button>
          </div>

          {/* Notification */}
          <div style={{ position: "relative" }}>
            <button
              style={{
                background: "#F5F5F8",
                border: "1px solid #E0E0E8",
                borderRadius: "6px",
                padding: "6px",
                cursor: "pointer",
                display: "flex",
              }}
            >
              <Bell size={16} color="#4A4A6A" />
            </button>
            <span
              style={{
                position: "absolute",
                top: "-4px",
                right: "-4px",
                background: "#D2232A",
                color: "white",
                borderRadius: "50%",
                width: "16px",
                height: "16px",
                fontSize: "9px",
                fontWeight: 700,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              4
            </span>
          </div>

          {/* User Profile */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              background: "#F5F5F8",
              border: "1px solid #E0E0E8",
              borderRadius: "6px",
              padding: "5px 10px",
              cursor: "pointer",
            }}
          >
            <div
              style={{
                width: "28px",
                height: "28px",
                background: "linear-gradient(135deg, #D2232A, #8B0000)",
                borderRadius: "50%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <User size={14} color="white" />
            </div>
            <div>
              <div style={{ fontSize: "12px", fontWeight: 600, color: "#1A1A2E" }}>Rajesh Kumar</div>
              <div style={{ fontSize: "10px", color: "#8B8BA7" }}>National Training Head</div>
            </div>
            <ChevronDown size={12} color="#8B8BA7" />
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          padding: "0 24px",
          gap: "0",
          borderBottom: "none",
        }}
      >
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            style={{
              background: "transparent",
              border: "none",
              borderBottom: activeTab === tab.id ? "2px solid #D2232A" : "2px solid transparent",
              color: activeTab === tab.id ? "#D2232A" : "#6B6B8A",
              padding: "10px 16px",
              cursor: "pointer",
              fontSize: "13px",
              fontWeight: activeTab === tab.id ? 600 : 500,
              transition: "all 0.15s",
              letterSpacing: "0.2px",
              whiteSpace: "nowrap",
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </header>
  );
}
