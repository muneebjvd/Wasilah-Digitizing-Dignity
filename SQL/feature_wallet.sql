USE WasilahDB;
GO

-- 1. ADD FUNDS
CREATE OR ALTER PROCEDURE sp_Wallet_AddFunds @UserID INT, @Amount DECIMAL(18,2) AS
BEGIN
    UPDATE Wallets SET Balance = Balance + @Amount WHERE UserID = @UserID;
    INSERT INTO System_Logs (UserID, ActionType, Description) VALUES (@UserID, 'DEPOSIT', 'Added: ' + CAST(@Amount AS NVARCHAR));
    SELECT 'SUCCESS' AS Status;
END
GO

-- 2. WITHDRAW FUNDS
CREATE OR ALTER PROCEDURE sp_Wallet_Withdraw @UserID INT, @Amount DECIMAL(18,2) AS
BEGIN
    IF EXISTS (SELECT 1 FROM Wallets WHERE UserID = @UserID AND Balance >= @Amount)
    BEGIN
        UPDATE Wallets SET Balance = Balance - @Amount WHERE UserID = @UserID;
        INSERT INTO System_Logs (UserID, ActionType, Description) VALUES (@UserID, 'WITHDRAWAL', 'Withdrew: ' + CAST(@Amount AS NVARCHAR));
        SELECT 'SUCCESS' AS Status;
    END
    ELSE SELECT 'INSUFFICIENT_FUNDS' AS Status;
END
GO

-- 3. GLOBAL STATS
CREATE OR ALTER VIEW View_Global_Wallet_Stats AS
SELECT U.UserRole, COUNT(W.WalletID) AS Wallets, SUM(W.Balance) AS Liquidity
FROM Wallets W JOIN Users U ON W.UserID = U.UserID GROUP BY U.UserRole;
GO