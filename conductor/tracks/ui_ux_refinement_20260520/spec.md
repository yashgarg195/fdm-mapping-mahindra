# Specification: UI/UX Refinement and Analytics Updates

## Overview
This track involves a series of UI/UX refinements and logic updates across multiple dashboard tabs. The goal is to reduce visual clutter, clarify terminology for non-technical users, refine skill scoring logic, and enhance filtering capabilities in the manpower and nominations views.

## Functional Requirements
1. **Overview Tab:**
   - Remove the "FY training trend" graph.
   - Remove the "monthly training" graph.
2. **Pending & Nominations (Backlog):**
   - Add an "Eligibility Timeframe" filter to display individuals eligible for training based on durations such as ">= 1 year", ">= 6 months", ">= 3 months", and ">= 1 month".
   - **Add an export function (button) to allow users to download an Excel sheet of the currently filtered backlog data.**
3. **Skill Analytics:**
   - Add a clear, visible explanation of the Skill Score directly on the dashboard.
   - Detail the 0-5 scale and explain the underlying scoring formula.
   - Update the skill calculation logic: *only* trained individuals should be considered (untrained individuals must be excluded from the skill score metrics/denominator).
   - Remove the existing graphs in this section to reduce visual clutter.
4. **Product Penetration:**
   - Completely remove the "Product Penetration" tab/section from the dashboard.
5. **Unique Manpower:**
   - Add new filters for Location/Region, Role/Dealership, and Training Status.
   - Ensure the data can be easily cross-checked.
   - Retain the existing "Zone manpower distribution" visualization.
6. **Audit / Exceptions:**
   - Rename all instances of the term "Fuzzy Match" (or "Fuzzy") to "Possible Match".
   - Add a layman's explanation (e.g., via text or tooltip) detailing what a "Possible Match" entails.

## Non-Functional Requirements
- Maintain Streamlit-native design patterns and the established "Corporate Industrial" branding.
- Adhere to the "Guidance-Heavy" UX principle by ensuring new explanations are clear and accessible.

## Acceptance Criteria
1. The Overview tab no longer displays the FY and monthly training trend graphs.
2. The Pending & Nominations view successfully filters individuals by the new Eligibility Timeframe criteria, and the filtered data can be successfully downloaded as an Excel file.
3. The Skill Analytics tab explains the 0-5 scale, correctly calculates scores using only trained individuals, and has no graphs.
4. The Product Penetration section is fully removed from the application.
5. The Unique Manpower tab features the new filters while keeping the Zone distribution intact.
6. The Audit / Exceptions tab exclusively uses the term "Possible Match" and includes a clear, helpful explanation.

## Out of Scope
- Implementing "Dynamic names" functionality (as explicitly excluded by user).