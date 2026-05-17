/* =========================================================================
PROJECT: WASILAH (The Medium)
DBMS - MUHAMMAD MUNEEB JAVED - MALIK ALI BIN SAJJAD - ABDUL JABBAR IJAZ
=========================================================================
*/

-- 1. Setup Database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'WasilahDB')
BEGIN
    CREATE DATABASE WasilahDB;
END
GO

USE WasilahDB;
GO

-- =============================================
-- STEP 0: CLEANUP (Drop tables in reverse order of dependency)
-- =============================================
DROP TABLE IF EXISTS System_Logs;
DROP TABLE IF EXISTS Smart_Vouchers;
DROP TABLE IF EXISTS Donations;
DROP TABLE IF EXISTS Requests;
DROP TABLE IF EXISTS Wallets;
DROP TABLE IF EXISTS Job_Applications;
DROP TABLE IF EXISTS Job_Postings;
DROP TABLE IF EXISTS User_Skills;
DROP TABLE IF EXISTS Ref_Skills;
DROP TABLE IF EXISTS Ref_Categories;
DROP TABLE IF EXISTS Guarantor_Links;
DROP TABLE IF EXISTS User_Public_Profiles;
DROP TABLE IF EXISTS Verification_Documents;
DROP TABLE IF EXISTS User_PII;
DROP TABLE IF EXISTS Work_Offers; -- Ensure this is dropped if it exists from feature_skills
DROP TABLE IF EXISTS InKind_Donations; -- Ensure this is dropped if it exists from dash_donor
DROP TABLE IF EXISTS Users;
GO

-- =============================================
-- MODULE 1: USER MANAGEMENT & PRIVACY
-- =============================================

-- Table 1: Users (Authentication)
CREATE TABLE Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    Email NVARCHAR(100) NOT NULL UNIQUE,
    PasswordHash NVARCHAR(255) NOT NULL,
    UserRole NVARCHAR(20) NOT NULL CHECK (UserRole IN ('Admin', 'Donor', 'Beneficiary', 'Guarantor', 'Vendor')),
    CreatedAt DATETIME DEFAULT GETDATE(),
    IsActive BIT DEFAULT 1
);
GO

-- Table 2: User_PII (Sensitive Data)
CREATE TABLE User_PII (
    PII_ID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT UNIQUE NOT NULL,
    RealName NVARCHAR(100) NOT NULL,
    CNIC_Number NVARCHAR(15) NOT NULL UNIQUE,
    PhoneNumber NVARCHAR(15) NOT NULL,
    AddressText NVARCHAR(MAX),
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
);
GO

-- Table 3: User_Public_Profiles (Anonymous Data)
CREATE TABLE User_Public_Profiles (
    ProfileID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT UNIQUE NOT NULL,
    AliasName NVARCHAR(50) NOT NULL, 
    BioSummary NVARCHAR(MAX), 
    VerificationStatus NVARCHAR(20) DEFAULT 'Unverified' CHECK (VerificationStatus IN ('Unverified', 'Pending', 'Verified', 'Rejected')),
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
);
GO

-- Table 4: Guarantor_Links (Verification)
CREATE TABLE Guarantor_Links (
    LinkID INT IDENTITY(1,1) PRIMARY KEY,
    GuarantorID INT NOT NULL,
    BeneficiaryID INT NOT NULL,
    VerificationDate DATETIME DEFAULT GETDATE(),
    Status NVARCHAR(20) DEFAULT 'Active',
    Remarks NVARCHAR(500), -- Added Remarks Column
    FOREIGN KEY (GuarantorID) REFERENCES Users(UserID),
    FOREIGN KEY (BeneficiaryID) REFERENCES Users(UserID)
);
GO

-- Table 5: Verification_Documents (Uploads)
CREATE TABLE Verification_Documents (
    DocID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT NOT NULL,
    DocType VARCHAR(50) NOT NULL,
    DocContent NVARCHAR(MAX) NOT NULL,
    UploadDate DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
);
GO

-- =============================================
-- MODULE 2: SKILLS & JOBS
-- =============================================

-- Table 6: Skills Library
CREATE TABLE Ref_Skills (
    SkillID INT IDENTITY(1,1) PRIMARY KEY,
    SkillName NVARCHAR(50) UNIQUE NOT NULL
);
GO

-- Table 7: User_Skills (Portfolio)
CREATE TABLE User_Skills (
    UserSkillID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT NOT NULL,
    SkillID INT NOT NULL,
    ExperienceLevel NVARCHAR(20) CHECK (ExperienceLevel IN ('Beginner', 'Intermediate', 'Expert')),
    Description NVARCHAR(255), -- Added Description Column
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    FOREIGN KEY (SkillID) REFERENCES Ref_Skills(SkillID)
);
GO

-- Table 8: Job Postings
CREATE TABLE Job_Postings (
    JobID INT IDENTITY(1,1) PRIMARY KEY,
    DonorID INT NOT NULL,
    JobTitle NVARCHAR(100) NOT NULL,
    JobDescription NVARCHAR(MAX),
    RequiredSkillID INT,
    Budget DECIMAL(18,2) NOT NULL,
    Status NVARCHAR(20) DEFAULT 'Open' CHECK (Status IN ('Open', 'In Progress', 'Completed', 'Cancelled')),
    PostedAt DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (DonorID) REFERENCES Users(UserID),
    FOREIGN KEY (RequiredSkillID) REFERENCES Ref_Skills(SkillID)
);
GO

-- Table 9: Job Applications
CREATE TABLE Job_Applications (
    ApplicationID INT IDENTITY(1,1) PRIMARY KEY,
    JobID INT NOT NULL,
    ApplicantID INT NOT NULL,
    AppliedAt DATETIME DEFAULT GETDATE(),
    Status NVARCHAR(20) DEFAULT 'Pending' CHECK (Status IN ('Pending', 'Accepted', 'Rejected')),
    FOREIGN KEY (JobID) REFERENCES Job_Postings(JobID),
    FOREIGN KEY (ApplicantID) REFERENCES Users(UserID)
);
GO

-- Table 10: Work Offers (Direct Hire)
CREATE TABLE Work_Offers (
    OfferID INT IDENTITY(1,1) PRIMARY KEY,
    DonorID INT NOT NULL,
    BeneficiaryID INT NOT NULL,
    ProjectTitle NVARCHAR(100) NOT NULL, 
    OfferAmount DECIMAL(18,2) NOT NULL,
    Status NVARCHAR(20) DEFAULT 'Pending', 
    OfferDate DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (DonorID) REFERENCES Users(UserID),
    FOREIGN KEY (BeneficiaryID) REFERENCES Users(UserID)
);
GO

-- =============================================
-- MODULE 3: WELFARE & FINANCIALS
-- =============================================

-- Table 11: Categories
CREATE TABLE Ref_Categories (
    CategoryID INT IDENTITY(1,1) PRIMARY KEY,
    CategoryName NVARCHAR(50) UNIQUE NOT NULL
);
GO

-- Table 12: Wallets
CREATE TABLE Wallets (
    WalletID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT UNIQUE NOT NULL,
    Balance DECIMAL(18, 2) DEFAULT 0.00,
    LastUpdated DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);
GO

-- Table 13: Requests
CREATE TABLE Requests (
    RequestID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT NOT NULL,
    CategoryID INT NOT NULL,
    Title NVARCHAR(100) NOT NULL,
    Description NVARCHAR(MAX),
    AmountNeeded DECIMAL(18, 2) NOT NULL,
    AmountCollected DECIMAL(18, 2) DEFAULT 0.00,
    Status NVARCHAR(20) DEFAULT 'Open' CHECK (Status IN ('Open', 'Funded', 'Closed')),
    DeadlineDate DATE NULL, -- Added DeadlineDate Column
    CreatedAt DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (CategoryID) REFERENCES Ref_Categories(CategoryID)
);
GO

-- Table 14: Donations
CREATE TABLE Donations (
    DonationID INT IDENTITY(1,1) PRIMARY KEY,
    DonorID INT NOT NULL,
    RequestID INT NOT NULL,
    Amount DECIMAL(18, 2) NOT NULL,
    TransactionDate DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (DonorID) REFERENCES Users(UserID),
    FOREIGN KEY (RequestID) REFERENCES Requests(RequestID)
);
GO

-- Table 15: Smart Vouchers
CREATE TABLE Smart_Vouchers (
    VoucherID INT IDENTITY(1,1) PRIMARY KEY,
    RequestID INT NULL, -- Made Nullable
    VoucherCode NVARCHAR(50) UNIQUE NOT NULL,
    AmountValue DECIMAL(18, 2) NOT NULL,
    ExpiryDate DATETIME NOT NULL,
    IsRedeemed BIT DEFAULT 0,
    RedeemedBy_VendorID INT NULL,
    RedeemedAt DATETIME NULL,
    FOREIGN KEY (RequestID) REFERENCES Requests(RequestID),
    FOREIGN KEY (RedeemedBy_VendorID) REFERENCES Users(UserID)
);
GO

-- Table 16: In-Kind Donations
CREATE TABLE InKind_Donations (
    ItemDonationID INT IDENTITY(1,1) PRIMARY KEY,
    DonorID INT NOT NULL,
    ItemCategory VARCHAR(50) NOT NULL, 
    ItemName VARCHAR(100) NOT NULL,
    Quantity INT DEFAULT 1,
    Status VARCHAR(20) DEFAULT 'Pending',
    DonationDate DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (DonorID) REFERENCES Users(UserID)
);
GO

-- =============================================
-- MODULE 4: AUDITS
-- =============================================

-- Table 17: System Logs
CREATE TABLE System_Logs (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT NULL,
    ActionType NVARCHAR(50) NOT NULL,
    Description NVARCHAR(255),
    IP_Address NVARCHAR(50),
    LogDate DATETIME DEFAULT GETDATE()
);
GO

-- =============================================
-- SEED DATA (Base Data)
-- =============================================

-- 1. Insert Categories
INSERT INTO Ref_Categories (CategoryName) VALUES 
('University Fees'), ('Healthcare'), ('Groceries'), ('Utility Bills'), ('Remote Work Equipment');

-- 2. Insert Skills
INSERT INTO Ref_Skills (SkillName) VALUES 
('Python Programming'), ('Graphic Design'), ('Data Entry'), ('Accounting'), ('Content Writing'), ('Teaching');

-- 3. Insert Base Users
INSERT INTO Users (Email, PasswordHash, UserRole) VALUES 
('admin@wasilah.com', 'hashed_pass_123', 'Admin'),
('donor@gmail.com', 'pass123', 'Donor'),
('needy@yahoo.com', 'pass123', 'Beneficiary'),
('imam@mosque.com', 'pass123', 'Guarantor'),
('vendor@mart.com', 'pass123', 'Vendor');

-- 4. Create Wallets for Base Users
INSERT INTO Wallets (UserID, Balance) VALUES 
((SELECT UserID FROM Users WHERE Email='admin@wasilah.com'), 0.00),
((SELECT UserID FROM Users WHERE Email='donor@gmail.com'), 50000.00),
((SELECT UserID FROM Users WHERE Email='needy@yahoo.com'), 0.00),
((SELECT UserID FROM Users WHERE Email='imam@mosque.com'), 0.00),
((SELECT UserID FROM Users WHERE Email='vendor@mart.com'), 0.00);

-- 5. Set up Beneficiary Profile
DECLARE @BenID INT = (SELECT UserID FROM Users WHERE Email='needy@yahoo.com');

INSERT INTO User_PII (UserID, RealName, CNIC_Number, PhoneNumber, AddressText) VALUES 
(@BenID, 'Ahmed Ali', '35202-1234567-1', '0300-1234567', 'House 123, Lahore');

INSERT INTO User_Public_Profiles (UserID, AliasName, BioSummary, VerificationStatus) VALUES 
(@BenID, 'Candidate #101', 'BS CS Student needing help with semester fee.', 'Verified');

INSERT INTO User_Skills (UserID, SkillID, ExperienceLevel, Description) VALUES 
(@BenID, (SELECT SkillID FROM Ref_Skills WHERE SkillName='Python Programming'), 'Intermediate', 'Built a few flask apps');

-- 6. Set up Vendor Profile (Optional but good for testing)
DECLARE @VenID INT = (SELECT UserID FROM Users WHERE Email='vendor@mart.com');

INSERT INTO User_PII (UserID, RealName, CNIC_Number, PhoneNumber, AddressText) VALUES 
(@VenID, 'Al-Fatah Store', '35202-1111111-1', '0321-1111111', 'Main Market');

INSERT INTO User_Public_Profiles (UserID, AliasName, BioSummary, VerificationStatus) VALUES 
(@VenID, 'Trusted Vendor', 'Authorized Grocery Partner', 'Verified');

PRINT '✅ Database Rebuilt & Seeded Successfully!';


