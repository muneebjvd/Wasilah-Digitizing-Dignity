USE WasilahDB;
GO

-- 1. PROCEDURE: PAY FREELANCER (When Job is Done)
CREATE OR ALTER PROCEDURE sp_Skill_CompleteAndPay
    @OfferID INT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @DonorID INT, @BenID INT, @Amount DECIMAL(18,2), @Status NVARCHAR(20);

    -- Get Offer Details
    SELECT @DonorID=DonorID, @BenID=BeneficiaryID, @Amount=OfferAmount, @Status=Status 
    FROM Work_Offers WHERE OfferID = @OfferID;

    -- Only pay if Accepted and not already paid
    IF @Status = 'Accepted'
    BEGIN
        -- Check Donor Balance
        IF EXISTS (SELECT 1 FROM Wallets WHERE UserID=@DonorID AND Balance >= @Amount)
        BEGIN
            BEGIN TRAN
                -- Move Money
                UPDATE Wallets SET Balance = Balance - @Amount WHERE UserID = @DonorID;
                UPDATE Wallets SET Balance = Balance + @Amount WHERE UserID = @BenID;
                
                -- Update Status
                UPDATE Work_Offers SET Status = 'Completed' WHERE OfferID = @OfferID;
                
                -- Log
                INSERT INTO System_Logs (UserID, ActionType, Description) 
                VALUES (@DonorID, 'JOB_PAYMENT', 'Paid ' + CAST(@Amount AS NVARCHAR) + ' for Offer #' + CAST(@OfferID AS NVARCHAR));
            COMMIT TRAN
            SELECT 'SUCCESS' AS Result;
        END
        ELSE SELECT 'ERROR: Insufficient Funds' AS Result;
    END
    ELSE SELECT 'ERROR: Job not in Accepted state' AS Result;
END
GO

-- 2. TRIGGER: DONATION AUTOMATION (Backup Safety)
-- Ensures money moves to beneficiary even if Python misses it
CREATE OR ALTER TRIGGER trg_Donation_AutoMove
ON Donations
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Amt DECIMAL(18,2), @ReqID INT, @BenID INT;
    
    SELECT @Amt=Amount, @ReqID=RequestID FROM INSERTED;
    SELECT @BenID=UserID FROM Requests WHERE RequestID=@ReqID;

    -- Add to Beneficiary Wallet
    UPDATE Wallets SET Balance = Balance + @Amt WHERE UserID = @BenID;
    
    -- Update Request
    UPDATE Requests SET AmountCollected = AmountCollected + @Amt WHERE RequestID = @ReqID;
END
GO