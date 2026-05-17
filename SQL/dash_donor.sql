USE WasilahDB;
GO

-- 1. IN-KIND DONATIONS
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'InKind_Donations')
BEGIN
    CREATE TABLE InKind_Donations (
        ItemDonationID INT IDENTITY(1,1) PRIMARY KEY, DonorID INT NOT NULL,
        ItemCategory VARCHAR(50) NOT NULL, ItemName VARCHAR(100) NOT NULL, Quantity INT DEFAULT 1,
        Status VARCHAR(20) DEFAULT 'Pending', DonationDate DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (DonorID) REFERENCES Users(UserID)
    );
END
GO

-- 2. SAFE INFO VIEW
CREATE OR ALTER VIEW View_Safe_Beneficiary_Info AS
SELECT R.RequestID, R.Title, R.Description, R.AmountNeeded, R.AmountCollected, R.DeadlineDate, C.CategoryName, P.AliasName, P.BioSummary
FROM Requests R JOIN User_Public_Profiles P ON R.UserID=P.UserID JOIN Ref_Categories C ON R.CategoryID=C.CategoryID WHERE R.Status='Open';
GO

-- 3. JOB PROCS
CREATE OR ALTER PROCEDURE sp_Donor_PostJob @DonorID INT, @Title NVARCHAR(100), @Desc NVARCHAR(MAX), @SkillName NVARCHAR(50), @Budget DECIMAL(18,2) AS
BEGIN
    DECLARE @SkillID INT = (SELECT SkillID FROM Ref_Skills WHERE SkillName = @SkillName);
    INSERT INTO Job_Postings (DonorID, JobTitle, JobDescription, RequiredSkillID, Budget, Status) VALUES (@DonorID, @Title, @Desc, @SkillID, @Budget, 'Open');
END
GO
CREATE OR ALTER PROCEDURE sp_Donor_UpdateJob @JobID INT, @Title NVARCHAR(100), @Desc NVARCHAR(MAX), @Budget DECIMAL(18,2) AS
BEGIN UPDATE Job_Postings SET JobTitle=@Title, JobDescription=@Desc, Budget=@Budget WHERE JobID=@JobID; END
GO
CREATE OR ALTER PROCEDURE sp_Donor_DeleteJob @JobID INT AS
BEGIN DELETE FROM Job_Postings WHERE JobID=@JobID; END
GO

-- 4. DONATE PROCS
CREATE OR ALTER PROCEDURE sp_Donor_DonateItem @DonorID INT, @Cat VARCHAR(50), @Name VARCHAR(100), @Qty INT AS
BEGIN INSERT INTO InKind_Donations (DonorID, ItemCategory, ItemName, Quantity) VALUES (@DonorID, @Cat, @Name, @Qty); END
GO
CREATE OR ALTER PROCEDURE sp_Donor_GeneralDonation @DonorID INT, @Amt DECIMAL(18,2) AS
BEGIN
    UPDATE Wallets SET Balance = Balance - @Amt WHERE UserID = @DonorID;
    UPDATE Wallets SET Balance = Balance + @Amt WHERE UserID = (SELECT TOP 1 UserID FROM Users WHERE UserRole='Admin');
    INSERT INTO System_Logs (UserID, ActionType, Description) VALUES (@DonorID, 'GEN_DONATION', 'Fund: ' + CAST(@Amt AS NVARCHAR));
END
GO