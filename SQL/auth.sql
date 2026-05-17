USE WasilahDB;
GO

-- 1. EMAIL CONSTRAINT
IF NOT EXISTS (SELECT * FROM sys.check_constraints WHERE name = 'CHK_EmailFormat')
    ALTER TABLE Users ADD CONSTRAINT CHK_EmailFormat CHECK (Email LIKE '%_@_%._%');
GO

-- 2. REGISTER PROCEDURE
CREATE OR ALTER PROCEDURE sp_RegisterUser @Email NVARCHAR(100), @Password NVARCHAR(255), @Role NVARCHAR(20), @Result NVARCHAR(100) OUTPUT AS
BEGIN
    IF EXISTS (SELECT 1 FROM Users WHERE Email = @Email)
        SET @Result = 'ERROR: Email exists.';
    ELSE BEGIN
        INSERT INTO Users (Email, PasswordHash, UserRole) VALUES (@Email, @Password, @Role);
        SET @Result = 'SUCCESS';
    END
END
GO

-- 3. SEED DATA (Vendor & Guarantor)
IF NOT EXISTS (SELECT 1 FROM Users WHERE Email = 'vendor@mart.com')
    INSERT INTO Users (Email, PasswordHash, UserRole) VALUES ('vendor@mart.com', 'pass123', 'Vendor');

IF NOT EXISTS (SELECT 1 FROM Users WHERE Email = 'prof@university.edu')
    INSERT INTO Users (Email, PasswordHash, UserRole) VALUES ('prof@university.edu', 'pass123', 'Guarantor');
GO