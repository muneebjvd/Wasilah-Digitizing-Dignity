USE WasilahDB;
GO

-- 1. ADD REMARKS COLUMN
IF NOT EXISTS(SELECT * FROM sys.columns WHERE Name = N'Remarks' AND Object_ID = Object_ID(N'Guarantor_Links'))
    ALTER TABLE Guarantor_Links ADD Remarks NVARCHAR(500);
GO

-- 2. PENDING VIEW
CREATE OR ALTER VIEW View_Pending_Verifications AS
SELECT U.UserID, P.RealName, P.CNIC_Number, P.PhoneNumber, P.AddressText, UP.AliasName, UP.VerificationStatus
FROM Users U JOIN User_PII P ON U.UserID = P.UserID JOIN User_Public_Profiles UP ON U.UserID = UP.UserID
WHERE UP.VerificationStatus IN ('Pending', 'Unverified') AND U.UserRole = 'Beneficiary';
GO

-- 3. VERIFY ACTION
CREATE OR ALTER PROCEDURE sp_Guarantor_VerifyAction @GuarantorID INT, @TargetUserID INT, @Decision VARCHAR(20), @Remarks NVARCHAR(500) AS
BEGIN
    IF EXISTS (SELECT 1 FROM Guarantor_Links WHERE GuarantorID=@GuarantorID AND BeneficiaryID=@TargetUserID)
        UPDATE Guarantor_Links SET Remarks = @Remarks, Status = 'Active', VerificationDate = GETDATE() WHERE GuarantorID=@GuarantorID AND BeneficiaryID=@TargetUserID;
    ELSE
        INSERT INTO Guarantor_Links (GuarantorID, BeneficiaryID, Status, Remarks) VALUES (@GuarantorID, @TargetUserID, 'Active', @Remarks);

    UPDATE User_Public_Profiles SET VerificationStatus = @Decision WHERE UserID = @TargetUserID;
    INSERT INTO System_Logs (UserID, ActionType, Description) VALUES (@GuarantorID, 'VERIFICATION', 'Status: ' + @Decision);
    SELECT 'SUCCESS' AS Result;
END
GO