# Wasilah: Digitizing Dignity

## 📖 Overview
Wasilah is a digital welfare ecosystem, acting as a secure mediator between donors and verified beneficiaries, rather than just a simple donation app. Traditional charity exposes beneficiaries and reduces donor trust due to fraud and a lack of transparency. Wasilah solves the "Dignity Paradox" by providing honorable charity and protecting the dignity of needy individuals who fear social shame.

## ✨ Core Features
* **Double-Blind Mechanism:** Donors view verified case details without names or photos, and beneficiaries receive aid without knowing the donor's identity, eliminating dependency mindsets.
* **Guarantor System:** Community leaders act as a "Human Firewall" to physically verify needy cases and invite them to the platform.
* **Smart Vouchers:** To prevent the misuse of donations, funds are converted into purpose-based QR-code vouchers redeemable only at registered vendors.
* **Reverse Job Market:** Beneficiaries can list skills (like teaching, design, or sewing) so donors can hire them, turning charity into dignified income.

## 👥 User Roles
* **Beneficiary (The Receiver):** Creates verified need requests, views locked vouchers in a smart wallet, and can apply for jobs in the Reverse Job Market.
* **Donor (The Giver):** Donates to anonymous cases, hires talent, lists physical items for donation, and tracks impact via a real-time dashboard.
* **Guarantor (The Verifier):** Verifies and creates accounts for the needy, validates requests offline, and maintains a dynamic Trust Score based on beneficiary conduct.
* **Vendor (The Shop Owner):** Scans and validates beneficiary QR vouchers, tracking sales history to claim real cash reimbursements from admins.
* **Super Admin (Governance):** Manages user accounts, oversees vendor payouts, controls fraud via dispute resolution, and views immutable system activity logs.

## 🛠️ Technology & Architecture
* **Database:** Built using Microsoft SQL Server with a fully normalized 3NF structure to eliminate redundancy and data anomalies.
* **Backend & UI:** Python (Streamlit) utilizing pyodbc and SQL Native Client for connectivity.
* **DBMS Implementation:** Handles complex business logic via ACID-compliant transactions, Stored Procedures, Joins, Triggers, and Views.

## 📈 Sustainability & Zero-Deduction Policy
* **Zero-Deduction:** 100% of user donations go directly to the beneficiary, with no administrative fees deducted from charity funds.
* **Revenue Streams:** Operational costs and salaries are covered by non-intrusive ethical advertising, corporate CSR banners, and a Vendor Affiliate Model that charges a minimal service fee for directing guaranteed business to shops.

## 🚀 Future Scope
* **Mobile App:** Developing a React Native app for easier Vendor QR scanning.
* **AI Integration:** Implementing Machine Learning to detect collusion patterns between corrupted Guarantors and Vendors.
* **Govt Integration:** Linking with NADRA APIs for automated identity verification.
