USE WasilahDB;
GO

-- 1. SUCCESS STORIES VIEW
CREATE OR ALTER VIEW View_Success_Stories AS
SELECT TOP 3 R.Title, R.AmountCollected, C.CategoryName, P.AliasName, R.Description
FROM Requests R JOIN User_Public_Profiles P ON R.UserID = P.UserID JOIN Ref_Categories C ON R.CategoryID = C.CategoryID
WHERE R.Status IN ('Funded', 'Closed') ORDER BY R.AmountCollected DESC;
GO

-- 2. GLOBAL STATS VIEW
CREATE OR ALTER VIEW View_Public_Stats AS
SELECT 
    (SELECT COUNT(*) FROM Users WHERE UserRole='Beneficiary') AS Beneficiaries,
    (SELECT ISNULL(SUM(Amount), 0) FROM Donations) AS Funds,
    (SELECT COUNT(*) FROM Requests WHERE Status='Funded') AS Completed,
    (SELECT COUNT(*) FROM Users WHERE UserRole='Guarantor') AS Guarantors;
GO