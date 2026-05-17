USE WasilahDB;
GO

-- 1. CHECK VOUCHER (Peek)
CREATE OR ALTER PROCEDURE sp_Vendor_CheckVoucher
    @Code NVARCHAR(50)
AS
BEGIN
    -- Simple Logic: If it exists and isn't used, show it.
    IF EXISTS (SELECT 1 FROM Smart_Vouchers WHERE VoucherCode = @Code AND IsRedeemed = 0)
    BEGIN
        SELECT 
            'VALID' AS Status,
            V.AmountValue,
            V.ExpiryDate,
            R.Title,
            RIGHT(PII.RealName, 5) AS MaskName,
            RIGHT(PII.CNIC_Number, 5) AS MaskCNIC
        FROM Smart_Vouchers V
        JOIN Requests R ON V.RequestID = R.RequestID
        JOIN User_PII PII ON R.UserID = PII.UserID
        WHERE V.VoucherCode = @Code;
    END
    ELSE
    BEGIN
        SELECT 'INVALID' AS Status;
    END
END
GO

-- 2. REDEEM VOUCHER (The Action)
CREATE OR ALTER PROCEDURE sp_Vendor_RedeemVoucher
    @Code NVARCHAR(50),
    @VendorID INT
AS
BEGIN
    -- Step 1: Mark Voucher as Used
    UPDATE Smart_Vouchers 
    SET IsRedeemed = 1, RedeemedBy_VendorID = @VendorID, RedeemedAt = GETDATE()
    WHERE VoucherCode = @Code;

    -- Step 2: Get the Amount
    DECLARE @Amount DECIMAL(18,2) = (SELECT AmountValue FROM Smart_Vouchers WHERE VoucherCode = @Code);

    -- Step 3: Add Money to Vendor
    UPDATE Wallets SET Balance = Balance + @Amount WHERE UserID = @VendorID;

    -- Step 4: Log it
    INSERT INTO System_Logs (UserID, ActionType, Description) 
    VALUES (@VendorID, 'REDEEM', 'Voucher: ' + @Code);

    SELECT 'SUCCESS' AS Result;
END
GO