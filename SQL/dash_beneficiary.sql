USE WasilahDB;
GO

-- 1. VERIFICATION TABLE
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Verification_Documents')
    CREATE TABLE Verification_Documents (
        DocID INT IDENTITY(1,1) PRIMARY KEY, UserID INT NOT NULL,
        DocType VARCHAR(50) NOT NULL, DocContent NVARCHAR(MAX) NOT NULL,
        UploadDate DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE
    );
GO

-- 2. SCHEMA UPDATES
IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'DeadlineDate' AND Object_ID = Object_ID(N'Requests'))
    ALTER TABLE Requests ADD DeadlineDate DATE NULL;
IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'Description' AND Object_ID = Object_ID(N'User_Skills'))
    ALTER TABLE User_Skills ADD Description NVARCHAR(255);
GO

-- 3. TRIGGER: AUTO-PENDING
CREATE OR ALTER TRIGGER trg_AutoPending ON Verification_Documents AFTER INSERT AS
BEGIN
    UPDATE User_Public_Profiles SET VerificationStatus = 'Pending' 
    WHERE UserID = (SELECT UserID FROM INSERTED) AND VerificationStatus = 'Unverified';
END
GO

-- 4. PROCEDURES
CREATE OR ALTER PROCEDURE sp_AddUserSkill @UserID INT, @SkillName VARCHAR(50), @Level NVARCHAR(20), @Desc NVARCHAR(255) AS
BEGIN
    DECLARE @SkillID INT = (SELECT SkillID FROM Ref_Skills WHERE SkillName = @SkillName);
    IF @SkillID IS NOT NULL
        IF NOT EXISTS (SELECT 1 FROM User_Skills WHERE UserID=@UserID AND SkillID=@SkillID)
        BEGIN
            INSERT INTO User_Skills (UserID, SkillID, ExperienceLevel, Description) VALUES (@UserID, @SkillID, @Level, @Desc);
            SELECT 'SUCCESS' AS Result;
        END
        ELSE SELECT 'ERROR: Skill Exists' AS Result;
    ELSE SELECT 'ERROR: Skill Not Found' AS Result;
END
GO

CREATE OR ALTER PROCEDURE sp_Ben_UpdateRequest @ReqID INT, @Title NVARCHAR(100), @Desc NVARCHAR(MAX), @Amount DECIMAL(18,2), @Deadline DATE AS
BEGIN UPDATE Requests SET Title=@Title, Description=@Desc, AmountNeeded=@Amount, DeadlineDate=@Deadline WHERE RequestID=@ReqID; END
GO

CREATE OR ALTER PROCEDURE sp_Ben_DeleteRequest @ReqID INT AS
BEGIN DELETE FROM Requests WHERE RequestID=@ReqID; END
GO

CREATE OR ALTER PROCEDURE sp_Ben_UploadDoc @UserID INT, @Type NVARCHAR(50), @Content NVARCHAR(MAX) AS
BEGIN INSERT INTO Verification_Documents (UserID, DocType, DocContent) VALUES (@UserID, @Type, @Content); END
GO

CREATE OR ALTER PROCEDURE sp_Ben_DeleteDoc @DocID INT, @UserID INT AS
BEGIN
    IF EXISTS (SELECT 1 FROM Verification_Documents WHERE DocID=@DocID AND UserID=@UserID)
    BEGIN DELETE FROM Verification_Documents WHERE DocID=@DocID; SELECT 'SUCCESS' AS Result; END
    ELSE SELECT 'ERROR' AS Result;
END
GO

-- 5. VIEWS
CREATE OR ALTER VIEW View_Beneficiary_Job_Matches AS
SELECT DISTINCT J.JobID, J.JobTitle, J.Budget, RS.SkillName AS RequiredSkill, SUBSTRING(J.JobDescription, 1, 50) + '...' AS Description_Snippet
FROM Job_Postings J JOIN Ref_Skills RS ON J.RequiredSkillID = RS.SkillID;
GO

--6 POST REQUEST

CREATE OR ALTER PROCEDURE sp_Ben_PostRequest
    @UserID INT,
    @CatName NVARCHAR(50),
    @Title NVARCHAR(100),
    @Desc NVARCHAR(MAX),
    @Amount DECIMAL(18,2),
    @Deadline DATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- 1. Find the Category ID based on the Name selected in the dropdown
    DECLARE @CatID INT = (SELECT CategoryID FROM Ref_Categories WHERE CategoryName = @CatName);
    
    -- 2. Insert the Request
    INSERT INTO Requests (UserID, CategoryID, Title, Description, AmountNeeded, Status, DeadlineDate)
    VALUES (@UserID, @CatID, @Title, @Desc, @Amount, 'Open', @Deadline);
    
    SELECT 'SUCCESS' AS Result;
END
GO

PRINT '✅ Procedure sp_Ben_PostRequest created successfully!';