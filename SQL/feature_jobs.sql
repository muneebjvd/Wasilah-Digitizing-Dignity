USE WasilahDB;
GO

-- 1. OPEN JOB MARKET VIEW
CREATE OR ALTER VIEW View_Open_Jobs AS
SELECT J.JobID, J.JobTitle, J.JobDescription, J.Budget, J.PostedAt, S.SkillName AS RequiredSkill, U.Email AS DonorEmail, J.DonorID
FROM Job_Postings J JOIN Ref_Skills S ON J.RequiredSkillID = S.SkillID JOIN Users U ON J.DonorID = U.UserID
WHERE J.Status = 'Open';
GO

-- 2. APPLY FOR JOB PROCEDURE
CREATE OR ALTER PROCEDURE sp_Job_Apply @JobID INT, @BenID INT AS
BEGIN
    IF EXISTS (SELECT 1 FROM Job_Applications WHERE JobID = @JobID AND ApplicantID = @BenID)
    BEGIN SELECT 'ERROR: Already applied.' AS Result; END
    ELSE
    BEGIN
        INSERT INTO Job_Applications (JobID, ApplicantID, AppliedAt, Status) VALUES (@JobID, @BenID, GETDATE(), 'Pending');
        INSERT INTO System_Logs (UserID, ActionType, Description) VALUES (@BenID, 'JOB_APPLY', 'Applied for Job ID: ' + CAST(@JobID AS NVARCHAR));
        SELECT 'SUCCESS: Application Submitted!' AS Result;
    END
END
GO

-- 3. POST NEW JOB PROCEDURE
CREATE OR ALTER PROCEDURE sp_Job_PostNew @DonorID INT, @Title NVARCHAR(100), @Desc NVARCHAR(MAX), @SkillName NVARCHAR(50), @Budget DECIMAL(18,2) AS
BEGIN
    DECLARE @SkillID INT = (SELECT SkillID FROM Ref_Skills WHERE SkillName = @SkillName);
    IF @SkillID IS NOT NULL
    BEGIN
        INSERT INTO Job_Postings (DonorID, JobTitle, JobDescription, RequiredSkillID, Budget, Status) VALUES (@DonorID, @Title, @Desc, @SkillID, @Budget, 'Open');
        SELECT 'SUCCESS: Job Posted' AS Result;
    END
    ELSE SELECT 'ERROR: Invalid Skill' AS Result;
END
GO

-- 4. VIEW APPLICANTS
CREATE OR ALTER VIEW View_My_Job_Applicants AS
SELECT JA.ApplicationID, JA.AppliedAt, J.JobTitle, J.DonorID, UP.AliasName AS CandidateAlias, UP.BioSummary, S.SkillName AS CandidateMainSkill
FROM Job_Applications JA JOIN Job_Postings J ON JA.JobID = J.JobID JOIN User_Public_Profiles UP ON JA.ApplicantID = UP.UserID LEFT JOIN User_Skills US ON JA.ApplicantID = US.UserID LEFT JOIN Ref_Skills S ON US.SkillID = S.SkillID
WHERE JA.Status = 'Pending';
GO