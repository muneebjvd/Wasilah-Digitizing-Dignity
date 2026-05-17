USE WasilahDB;
GO

-- 1. SCHEMA MOD
ALTER TABLE Smart_Vouchers ALTER COLUMN RequestID INT NULL;
GO

-- 2. GENERATE VOUCHER
CREATE OR ALTER PROCEDURE sp_Voucher_Generate @UserID INT, @Amount DECIMAL(18,2) AS
BEGIN
    IF EXISTS (SELECT 1 FROM Wallets WHERE UserID = @UserID AND Balance >= @Amount)
    BEGIN
        BEGIN TRY
            UPDATE Wallets SET Balance = Balance - @Amount WHERE UserID = @UserID;
            DECLARE @Code NVARCHAR(50) = 'V-' + CAST(ABS(CHECKSUM(NEWID())) % 90000 + 10000 AS NVARCHAR);
            INSERT INTO Smart_Vouchers (VoucherCode, AmountValue, ExpiryDate, IsRedeemed) VALUES (@Code, @Amount, DATEADD(day, 30, GETDATE()), 0);
            INSERT INTO System_Logs (UserID, ActionType, Description) VALUES (@UserID, 'VOUCHER_GEN', 'Created: ' + @Code);
            SELECT 'SUCCESS' AS Status, @Code AS VoucherCode;
        END TRY
        BEGIN CATCH SELECT 'ERROR' AS Status, ERROR_MESSAGE() AS VoucherCode; END CATCH
    END
    ELSE SELECT 'ERROR' AS Status, 'Insufficient Funds' AS VoucherCode;
END
GO

-- 3. VIEW VOUCHERS
CREATE OR ALTER VIEW View_My_Vouchers AS
SELECT SL.UserID, SV.VoucherCode, SV.AmountValue, SV.ExpiryDate, SV.IsRedeemed
FROM Smart_Vouchers SV JOIN System_Logs SL ON SL.Description LIKE '%' + SV.VoucherCode + '%'
WHERE SL.ActionType = 'VOUCHER_GEN';
GO