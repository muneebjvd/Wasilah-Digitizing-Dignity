USE WasilahDB;
GO

-- 1. VIEWS
CREATE OR ALTER VIEW View_Master_Money_Log AS
SELECT 'Donation' AS Type, Amount AS Value, TransactionDate AS Date, DonorID AS UserID FROM Donations UNION
SELECT 'Request' AS Type, AmountNeeded AS Value, CreatedAt AS Date, UserID AS UserID FROM Requests;
GO

CREATE OR ALTER VIEW View_Suspicious_Guarantors AS
SELECT G.RealName, COUNT(GL.BeneficiaryID) AS Cnt FROM User_PII AS G JOIN Guarantor_Links AS GL ON G.UserID=GL.GuarantorID GROUP BY G.RealName HAVING COUNT(GL.BeneficiaryID) > 5;
GO

CREATE OR ALTER VIEW View_Skilled_Beneficiaries AS SELECT UserID FROM User_Skills INTERSECT SELECT UserID FROM Requests;
GO

CREATE OR ALTER VIEW View_Inactive_Beneficiaries AS SELECT UserID FROM Users WHERE UserRole = 'Beneficiary' EXCEPT SELECT UserID FROM Requests;
GO

-- 2. PROCEDURES
CREATE OR ALTER PROCEDURE sp_Admin_ToggleStatus @UserID INT, @NewStatus BIT, @AdminID INT AS
BEGIN UPDATE Users SET IsActive = @NewStatus WHERE UserID = @UserID; INSERT INTO System_Logs (UserID, ActionType, Description) VALUES (@AdminID, 'STATUS', 'User ' + CAST(@UserID AS VARCHAR) + ' -> ' + CAST(@NewStatus AS VARCHAR)); END
GO

CREATE OR ALTER PROCEDURE sp_Admin_UpdateUser @TID INT, @Email NVARCHAR(100), @Role NVARCHAR(20), @AdminID INT AS
BEGIN
    BEGIN TRY UPDATE Users SET Email=@Email, UserRole=@Role WHERE UserID=@TID; INSERT INTO System_Logs (UserID, ActionType, Description) VALUES (@AdminID, 'UPDATE', 'User ' + CAST(@TID AS VARCHAR)); SELECT 'SUCCESS' AS Result; END TRY
    BEGIN CATCH SELECT 'ERROR' AS Result; END CATCH
END
GO

CREATE OR ALTER PROCEDURE sp_Admin_DeleteUser @UserID INT, @AdminID INT AS
BEGIN
    BEGIN TRY DELETE FROM Users WHERE UserID=@UserID; INSERT INTO System_Logs (UserID, ActionType, Description) VALUES (@AdminID, 'DELETE', 'User ' + CAST(@UserID AS VARCHAR)); SELECT 'SUCCESS' AS Result; END TRY
    BEGIN CATCH SELECT 'ERROR: Active Records' AS Result; END CATCH
END
GO

CREATE OR ALTER PROCEDURE sp_Admin_DeleteRequest @ReqID INT, @AdminID INT AS
BEGIN DELETE FROM Requests WHERE RequestID=@ReqID; INSERT INTO System_Logs (UserID, ActionType, Description) VALUES (@AdminID, 'DEL_REQ', 'Req ' + CAST(@ReqID AS VARCHAR)); SELECT 'SUCCESS' AS Result; END
GO

CREATE OR ALTER PROCEDURE sp_Admin_AssignGuarantor @BenID INT, @GuarID INT, @AdminID INT AS
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Guarantor_Links WHERE BeneficiaryID=@BenID AND GuarantorID=@GuarID)
    BEGIN INSERT INTO Guarantor_Links (BeneficiaryID, GuarantorID, Status) VALUES (@BenID, @GuarID, 'Active'); INSERT INTO System_Logs (UserID, ActionType, Description) VALUES (@AdminID, 'LINK', 'Ben ' + CAST(@BenID AS VARCHAR) + ' - Guar ' + CAST(@GuarID AS VARCHAR)); SELECT 'SUCCESS' AS Result; END
    ELSE SELECT 'ERROR' AS Result;
END
GO

CREATE OR ALTER PROCEDURE sp_Admin_VerifyTransaction @DonID INT, @AdminID INT AS
BEGIN INSERT INTO System_Logs (UserID, ActionType, Description) VALUES (@AdminID, 'VERIFY', 'Donation ' + CAST(@DonID AS VARCHAR)); SELECT 'SUCCESS' AS Result; END
GO

CREATE OR ALTER PROCEDURE sp_GetSystemEfficiency AS
BEGIN SELECT SUM(AmountCollected) AS C, SUM(AmountNeeded) AS N, (SUM(AmountCollected)*100.0/NULLIF(SUM(AmountNeeded),0)) AS S FROM Requests; END
GO