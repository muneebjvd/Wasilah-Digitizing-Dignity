USE WasilahDB;
GO

-- 1. WORK OFFERS TABLE
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Work_Offers')
BEGIN
    CREATE TABLE Work_Offers (
        OfferID INT IDENTITY(1,1) PRIMARY KEY,
        DonorID INT NOT NULL, BeneficiaryID INT NOT NULL,
        ProjectTitle NVARCHAR(100) NOT NULL, OfferAmount DECIMAL(18,2) NOT NULL,
        Status NVARCHAR(20) DEFAULT 'Pending', OfferDate DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (DonorID) REFERENCES Users(UserID), FOREIGN KEY (BeneficiaryID) REFERENCES Users(UserID)
    );
END
GO

-- 2. TALENT VIEW
CREATE OR ALTER VIEW View_Available_Talent AS
SELECT US.UserSkillID, U.UserID AS BeneficiaryID, UP.AliasName, UP.BioSummary, S.SkillName, US.ExperienceLevel, US.Description AS SkillDetails
FROM User_Skills US JOIN Users U ON US.UserID = U.UserID JOIN User_Public_Profiles UP ON U.UserID = UP.UserID JOIN Ref_Skills S ON US.SkillID = S.SkillID
WHERE U.UserRole = 'Beneficiary' AND U.IsActive = 1;
GO

-- 3. MAKE OFFER
CREATE OR ALTER PROCEDURE sp_Skill_MakeOffer @DonorID INT, @BenID INT, @Title NVARCHAR(100), @Amount DECIMAL(18,2) AS
BEGIN
    INSERT INTO Work_Offers (DonorID, BeneficiaryID, ProjectTitle, OfferAmount, Status) VALUES (@DonorID, @BenID, @Title, @Amount, 'Pending');
    SELECT 'SUCCESS: Offer Sent!' AS Result;
END
GO

-- 4. RESPOND OFFER
CREATE OR ALTER PROCEDURE sp_Skill_RespondOffer @OfferID INT, @BenID INT, @NewStatus NVARCHAR(20) AS
BEGIN
    IF EXISTS (SELECT 1 FROM Work_Offers WHERE OfferID = @OfferID AND BeneficiaryID = @BenID)
    BEGIN
        UPDATE Work_Offers SET Status = @NewStatus WHERE OfferID = @OfferID;
        SELECT 'SUCCESS: Offer ' + @NewStatus AS Result;
    END
    ELSE SELECT 'ERROR: Unauthorized' AS Result;
END
GO