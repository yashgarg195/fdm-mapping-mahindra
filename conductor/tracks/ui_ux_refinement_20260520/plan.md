# Implementation Plan - UI/UX Refinement and Analytics Updates

## Phase 1: Tab Removals and Basic UI Cleanup
- [ ] Task: Remove Product Penetration section
    - [ ] Write Tests: Ensure navigation and routing tests do not expect the Product Penetration tab.
    - [ ] Implement Feature: Remove the Product Penetration tab integration and any corresponding routing links.
- [ ] Task: Clean up Overview Tab graphs
    - [ ] Write Tests: Update tests to verify FY and monthly trend graphs are not rendered.
    - [ ] Implement Feature: Remove "FY training trend" and "monthly training" graphs from the Overview tab.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Tab Removals and Basic UI Cleanup' (Protocol in workflow.md)

## Phase 2: Pending & Nominations Enhancements
- [ ] Task: Add Eligibility Timeframe filter
    - [ ] Write Tests: Add tests to verify filtering logic based on timeframe thresholds (>= 1 year, >= 6 months, etc.).
    - [ ] Implement Feature: Update the Pending & Nominations tab and corresponding analytics logic to include and process the new timeframe filter.
- [ ] Task: Implement Excel download for filtered data
    - [ ] Write Tests: Test the generation of the Excel file for filtered data using the export functionality.
    - [ ] Implement Feature: Add a download button in the Pending & Nominations tab that triggers the Excel export function with the currently filtered dataset.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Pending & Nominations Enhancements' (Protocol in workflow.md)

## Phase 3: Skill Analytics Refinement
- [ ] Task: Update Skill Score calculation logic
    - [ ] Write Tests: Add tests to ensure only trained individuals are included in the denominator for skill calculations.
    - [ ] Implement Feature: Modify logic in the skill analytics module to exclude untrained individuals from the skill score.
- [ ] Task: Refine Skill Analytics UI
    - [ ] Write Tests: Verify the UI renders the explanations and does not render the old graphs.
    - [ ] Implement Feature: Remove graphs from the Skill Analytics tab and add the 0-5 scale explanation and scoring formula text.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Skill Analytics Refinement' (Protocol in workflow.md)

## Phase 4: Unique Manpower and Audit UI Updates
- [ ] Task: Add filters to Unique Manpower
    - [ ] Write Tests: Create tests for Location, Role, and Training Status filters.
    - [ ] Implement Feature: Update the Unique Manpower tab to include the new filters while preserving the Zone distribution chart.
- [ ] Task: Rename and explain 'Fuzzy Match' in Audit
    - [ ] Write Tests: Ensure the UI components in the Audit tab render the new labels and tooltips correctly.
    - [ ] Implement Feature: Update the Audit tab to rename "Fuzzy" to "Possible Match" and add explanatory tooltips or text.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Unique Manpower and Audit UI Updates' (Protocol in workflow.md)