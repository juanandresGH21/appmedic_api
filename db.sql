CREATE TABLE Users (
    Id CHAR(36) NOT NULL PRIMARY KEY,
    Email VARCHAR(255) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Timezone VARCHAR(50) NOT NULL DEFAULT 'America/Bogota',
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE Medications (
    Id CHAR(36) NOT NULL PRIMARY KEY,
    Name VARCHAR(150) NOT NULL,
    Form VARCHAR(50) NOT NULL DEFAULT 'tablet'
);
CREATE TABLE Schedules (
    Id CHAR(36) NOT NULL PRIMARY KEY,
    MedicationId CHAR(36) NOT NULL,
    UserId CHAR(36) NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NULL,
    Pattern VARCHAR(255) NOT NULL,
    -- rrule/cron/simple  
    DoseAmount VARCHAR(50) NOT NULL,
    -- ej: "10 mg"  
    FOREIGN KEY (MedicationId) REFERENCES Medications(Id),
    FOREIGN KEY (UserId) REFERENCES Users(Id)
);
CREATE TABLE Intakes (
    Id CHAR(36) NOT NULL PRIMARY KEY,
    ScheduleId CHAR(36) NOT NULL,
    PlannedAt DATETIME NOT NULL,
    -- UTC  
    Status ENUM('planned', 'taken', 'missed', 'skipped') NOT NULL DEFAULT 'planned',
    TakenAt DATETIME NULL,
    FOREIGN KEY (ScheduleId) REFERENCES Schedules(Id)
);