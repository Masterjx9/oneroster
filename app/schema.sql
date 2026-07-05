PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS "raw_manifest";
DROP TABLE IF EXISTS "raw_academicSessions";
DROP TABLE IF EXISTS "raw_categories";
DROP TABLE IF EXISTS "raw_classResources";
DROP TABLE IF EXISTS "raw_classes";
DROP TABLE IF EXISTS "raw_courseResources";
DROP TABLE IF EXISTS "raw_courses";
DROP TABLE IF EXISTS "raw_demographics";
DROP TABLE IF EXISTS "raw_enrollments";
DROP TABLE IF EXISTS "raw_lineItemLearningObjectiveIds";
DROP TABLE IF EXISTS "raw_lineItemScoreScales";
DROP TABLE IF EXISTS "raw_lineItems";
DROP TABLE IF EXISTS "raw_orgs";
DROP TABLE IF EXISTS "raw_resources";
DROP TABLE IF EXISTS "raw_resultLearningObjectiveIds";
DROP TABLE IF EXISTS "raw_resultScoreScales";
DROP TABLE IF EXISTS "raw_results";
DROP TABLE IF EXISTS "raw_roles";
DROP TABLE IF EXISTS "raw_scoreScales";
DROP TABLE IF EXISTS "raw_userProfiles";
DROP TABLE IF EXISTS "raw_userResources";
DROP TABLE IF EXISTS "raw_users";
DROP TABLE IF EXISTS "manifest";
DROP TABLE IF EXISTS "user_profiles";
DROP TABLE IF EXISTS "roles";
DROP TABLE IF EXISTS "oauth_nonces";
DROP TABLE IF EXISTS "oauth_tokens";
DROP TABLE IF EXISTS "oauth_clients";
DROP TABLE IF EXISTS "imported_records";
DROP TABLE IF EXISTS "provider_import_runs";
DROP TABLE IF EXISTS "provider_configurations";
DROP TABLE IF EXISTS "results";
DROP TABLE IF EXISTS "line_items";
DROP TABLE IF EXISTS "resources";
DROP TABLE IF EXISTS "enrollments";
DROP TABLE IF EXISTS "demographics";
DROP TABLE IF EXISTS "users";
DROP TABLE IF EXISTS "categories";
DROP TABLE IF EXISTS "classes";
DROP TABLE IF EXISTS "courses";
DROP TABLE IF EXISTS "academic_sessions";
DROP TABLE IF EXISTS "orgs";

CREATE TABLE "orgs" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "type" TEXT NOT NULL CHECK ("type" IN ('department', 'school', 'district', 'local', 'state', 'national')),
    "identifier" TEXT,
    "parentSourcedId" TEXT,
    "sourcedId" TEXT NOT NULL UNIQUE,
    "status" TEXT NOT NULL CHECK ("status" IN ('active', 'tobedeleted')),
    "dateLastModified" DATETIME NOT NULL,
    "metadata" JSON,
    FOREIGN KEY ("parentSourcedId") REFERENCES "orgs"("sourcedId")
);

CREATE TABLE "academic_sessions" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title" TEXT NOT NULL,
    "startDate" DATE NOT NULL,
    "endDate" DATE NOT NULL,
    "type" TEXT NOT NULL CHECK ("type" IN ('gradingPeriod', 'semester', 'schoolYear', 'term')),
    "parentSourcedId" TEXT,
    "schoolYear" TEXT NOT NULL,
    "sourcedId" TEXT NOT NULL UNIQUE,
    "status" TEXT NOT NULL CHECK ("status" IN ('active', 'tobedeleted')),
    "dateLastModified" DATETIME NOT NULL,
    "metadata" JSON,
    FOREIGN KEY ("parentSourcedId") REFERENCES "academic_sessions"("sourcedId")
);

CREATE TABLE "courses" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title" TEXT NOT NULL,
    "schoolYearSourcedId" TEXT,
    "courseCode" TEXT,
    "grades" JSON,
    "subjects" JSON,
    "orgSourcedId" TEXT NOT NULL,
    "subjectCodes" JSON,
    "resourceSourcedIds" JSON,
    "sourcedId" TEXT NOT NULL UNIQUE,
    "status" TEXT NOT NULL CHECK ("status" IN ('active', 'tobedeleted')),
    "dateLastModified" DATETIME NOT NULL,
    "metadata" JSON
);

CREATE TABLE "classes" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title" TEXT NOT NULL,
    "classCode" TEXT,
    "classType" TEXT NOT NULL CHECK ("classType" IN ('homeroom', 'scheduled')),
    "location" TEXT,
    "grades" JSON,
    "subjects" JSON,
    "courseSourcedId" TEXT NOT NULL,
    "schoolSourcedId" TEXT NOT NULL,
    "termSourcedIds" JSON NOT NULL,
    "subjectCodes" JSON,
    "periods" JSON,
    "resourceSourcedIds" JSON,
    "sourcedId" TEXT NOT NULL UNIQUE,
    "status" TEXT NOT NULL CHECK ("status" IN ('active', 'tobedeleted')),
    "dateLastModified" DATETIME NOT NULL,
    "metadata" JSON
);

CREATE TABLE "categories" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title" TEXT NOT NULL,
    "sourcedId" TEXT NOT NULL UNIQUE,
    "status" TEXT NOT NULL CHECK ("status" IN ('active', 'tobedeleted')),
    "dateLastModified" DATETIME NOT NULL,
    "metadata" JSON
);

CREATE TABLE "users" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "username" TEXT NOT NULL,
    "userIds" JSON,
    "enabledUser" TEXT NOT NULL CHECK ("enabledUser" IN ('true', 'false')),
    "givenName" TEXT NOT NULL,
    "familyName" TEXT NOT NULL,
    "middleName" TEXT,
    "role" TEXT NOT NULL CHECK ("role" IN ('administrator', 'aide', 'guardian', 'parent', 'proctor', 'relative', 'student', 'teacher')),
    "identifier" TEXT,
    "email" TEXT,
    "sms" TEXT,
    "phone" TEXT,
    "agents" JSON,
    "orgs" JSON NOT NULL,
    "grades" JSON,
    "password" TEXT,
    "sourcedId" TEXT NOT NULL UNIQUE,
    "status" TEXT NOT NULL CHECK ("status" IN ('active', 'tobedeleted')),
    "dateLastModified" DATETIME NOT NULL,
    "metadata" JSON
);

CREATE TABLE "demographics" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "birthDate" DATE,
    "sex" TEXT CHECK ("sex" IN ('male', 'female') OR "sex" IS NULL),
    "americanIndianOrAlaskaNative" TEXT CHECK ("americanIndianOrAlaskaNative" IN ('true', 'false') OR "americanIndianOrAlaskaNative" IS NULL),
    "asian" TEXT CHECK ("asian" IN ('true', 'false') OR "asian" IS NULL),
    "blackOrAfricanAmerican" TEXT CHECK ("blackOrAfricanAmerican" IN ('true', 'false') OR "blackOrAfricanAmerican" IS NULL),
    "nativeHawaiianOrOtherPacificIslander" TEXT CHECK ("nativeHawaiianOrOtherPacificIslander" IN ('true', 'false') OR "nativeHawaiianOrOtherPacificIslander" IS NULL),
    "white" TEXT CHECK ("white" IN ('true', 'false') OR "white" IS NULL),
    "demographicRaceTwoOrMoreRaces" TEXT CHECK ("demographicRaceTwoOrMoreRaces" IN ('true', 'false') OR "demographicRaceTwoOrMoreRaces" IS NULL),
    "hispanicOrLatinoEthnicity" TEXT CHECK ("hispanicOrLatinoEthnicity" IN ('true', 'false') OR "hispanicOrLatinoEthnicity" IS NULL),
    "countryOfBirthCode" TEXT,
    "stateOfBirthAbbreviation" TEXT,
    "cityOfBirth" TEXT,
    "publicSchoolResidenceStatus" TEXT,
    "sourcedId" TEXT NOT NULL UNIQUE,
    "status" TEXT NOT NULL CHECK ("status" IN ('active', 'tobedeleted')),
    "dateLastModified" DATETIME NOT NULL,
    "metadata" JSON
);

CREATE TABLE "enrollments" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "userSourcedId" TEXT NOT NULL,
    "classSourcedId" TEXT NOT NULL,
    "schoolSourcedId" TEXT NOT NULL,
    "role" TEXT NOT NULL CHECK ("role" IN ('administrator', 'proctor', 'student', 'teacher')),
    "primary" TEXT CHECK ("primary" IN ('true', 'false') OR "primary" IS NULL),
    "beginDate" DATE,
    "endDate" DATE,
    "sourcedId" TEXT NOT NULL UNIQUE,
    "status" TEXT NOT NULL CHECK ("status" IN ('active', 'tobedeleted')),
    "dateLastModified" DATETIME NOT NULL,
    "metadata" JSON,
    CHECK ("primary" IS NULL OR "role" = 'teacher')
);

CREATE TABLE "resources" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title" TEXT,
    "roles" JSON,
    "importance" TEXT CHECK ("importance" IN ('primary', 'secondary') OR "importance" IS NULL),
    "vendorResourceId" TEXT NOT NULL,
    "vendorId" TEXT,
    "applicationId" TEXT,
    "sourcedId" TEXT NOT NULL UNIQUE,
    "status" TEXT NOT NULL CHECK ("status" IN ('active', 'tobedeleted')),
    "dateLastModified" DATETIME NOT NULL,
    "metadata" JSON
);

CREATE TABLE "line_items" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "title" TEXT NOT NULL,
    "description" TEXT,
    "assignDate" DATETIME NOT NULL,
    "dueDate" DATETIME NOT NULL,
    "classSourcedId" TEXT NOT NULL,
    "categorySourcedId" TEXT NOT NULL,
    "gradingPeriodSourcedId" TEXT NOT NULL,
    "resultValueMin" REAL NOT NULL,
    "resultValueMax" REAL NOT NULL,
    "sourcedId" TEXT NOT NULL UNIQUE,
    "status" TEXT NOT NULL CHECK ("status" IN ('active', 'tobedeleted')),
    "dateLastModified" DATETIME NOT NULL,
    "metadata" JSON
);

CREATE TABLE "results" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "lineItemSourcedId" TEXT NOT NULL,
    "studentSourcedId" TEXT NOT NULL,
    "scoreStatus" TEXT NOT NULL CHECK ("scoreStatus" IN ('exempt', 'fully graded', 'not submitted', 'partially graded', 'submitted')),
    "score" REAL NOT NULL,
    "scoreDate" DATE NOT NULL,
    "comment" TEXT,
    "sourcedId" TEXT NOT NULL UNIQUE,
    "status" TEXT NOT NULL CHECK ("status" IN ('active', 'tobedeleted')),
    "dateLastModified" DATETIME NOT NULL,
    "metadata" JSON
);

CREATE TABLE "oauth_clients" (
    "client_id" TEXT NOT NULL PRIMARY KEY,
    "client_secret" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "is_confidential" INTEGER NOT NULL CHECK ("is_confidential" IN (0, 1)),
    "scopes" TEXT NOT NULL
);

CREATE TABLE "oauth_tokens" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "client_id" TEXT NOT NULL,
    "access_token" TEXT NOT NULL UNIQUE,
    "refresh_token" TEXT UNIQUE,
    "token_type" TEXT NOT NULL,
    "scopes" TEXT NOT NULL,
    "expires" DATETIME NOT NULL,
    FOREIGN KEY ("client_id") REFERENCES "oauth_clients"("client_id")
);

CREATE TABLE "oauth_nonces" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "client_id" TEXT NOT NULL,
    "nonce" TEXT NOT NULL,
    "timestamp" TEXT NOT NULL,
    "token_key" TEXT NOT NULL DEFAULT '',
    "created_at" DATETIME NOT NULL,
    UNIQUE ("client_id", "timestamp", "nonce", "token_key"),
    FOREIGN KEY ("client_id") REFERENCES "oauth_clients"("client_id")
);

CREATE TABLE "provider_configurations" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "base_url" TEXT NOT NULL,
    "token_url" TEXT,
    "client_id" TEXT NOT NULL,
    "client_secret" TEXT NOT NULL,
    "scopes" TEXT NOT NULL,
    "created_at" DATETIME NOT NULL,
    "updated_at" DATETIME NOT NULL
);

CREATE TABLE "provider_import_runs" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "provider_configuration_id" INTEGER NOT NULL,
    "status" TEXT NOT NULL,
    "started_at" DATETIME NOT NULL,
    "finished_at" DATETIME,
    "error_message" TEXT,
    "counts" JSON,
    FOREIGN KEY ("provider_configuration_id") REFERENCES "provider_configurations"("id")
);

CREATE TABLE "imported_records" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "provider_configuration_id" INTEGER NOT NULL,
    "import_run_id" INTEGER NOT NULL,
    "resource_type" TEXT NOT NULL,
    "sourced_id" TEXT NOT NULL,
    "payload" JSON NOT NULL,
    "imported_at" DATETIME NOT NULL,
    CONSTRAINT "uq_imported_record_per_run" UNIQUE ("import_run_id", "resource_type", "sourced_id"),
    FOREIGN KEY ("provider_configuration_id") REFERENCES "provider_configurations"("id"),
    FOREIGN KEY ("import_run_id") REFERENCES "provider_import_runs"("id")
);

INSERT INTO "orgs" ("name", "type", "identifier", "parentSourcedId", "sourcedId", "status", "dateLastModified", "metadata") VALUES
('Gotham Metro District', 'district', 'DIST-GMD-001', NULL, 'ORG_DIST_1', 'active', '2026-07-04 12:00:00.000000', NULL),
('Gotham High School', 'school', 'SCH-GHS-001', 'ORG_DIST_1', 'ORG_1', 'active', '2026-07-04 12:00:00.000000', NULL),
('Metropolis STEM Academy', 'school', 'SCH-MSA-002', 'ORG_DIST_1', 'ORG_2', 'active', '2026-07-04 12:00:00.000000', NULL),
('Star City Preparatory', 'school', 'SCH-SCP-003', 'ORG_DIST_1', 'ORG_3', 'active', '2026-07-04 12:00:00.000000', NULL);

INSERT INTO "academic_sessions" ("title", "startDate", "endDate", "type", "parentSourcedId", "schoolYear", "sourcedId", "status", "dateLastModified", "metadata") VALUES
('2024-2025 School Year', '2024-08-15', '2025-06-10', 'schoolYear', NULL, '2025', 'ACAD_SESS_1', 'active', '2026-07-04 12:00:00.000000', NULL),
('Fall Term', '2024-08-15', '2024-12-20', 'term', 'ACAD_SESS_1', '2025', 'TERM_FALL_1', 'active', '2026-07-04 12:00:00.000000', NULL),
('Spring Term', '2025-01-06', '2025-06-10', 'term', 'ACAD_SESS_1', '2025', 'TERM_SPRING_1', 'active', '2026-07-04 12:00:00.000000', NULL),
('Quarter 1', '2024-08-15', '2024-10-11', 'gradingPeriod', 'TERM_FALL_1', '2025', 'GP_Q1', 'active', '2026-07-04 12:00:00.000000', NULL),
('Quarter 2', '2024-10-14', '2024-12-20', 'gradingPeriod', 'TERM_FALL_1', '2025', 'GP_Q2', 'active', '2026-07-04 12:00:00.000000', NULL),
('Quarter 3', '2025-01-06', '2025-03-14', 'gradingPeriod', 'TERM_SPRING_1', '2025', 'GP_Q3', 'active', '2026-07-04 12:00:00.000000', NULL),
('Quarter 4', '2025-03-17', '2025-06-10', 'gradingPeriod', 'TERM_SPRING_1', '2025', 'GP_Q4', 'active', '2026-07-04 12:00:00.000000', NULL);

INSERT INTO "resources" ("title", "roles", "importance", "vendorResourceId", "vendorId", "applicationId", "sourcedId", "status", "dateLastModified", "metadata") VALUES
('Evidence Workbook', '["teacher","student"]', 'primary', 'FS-RES-001', '1edtech-demo', 'oneroster-spa', 'RES_001', 'active', '2026-07-04 12:00:00.000000', NULL),
('Lab Safety Manual', '["teacher","student"]', 'secondary', 'FS-RES-002', '1edtech-demo', 'oneroster-spa', 'RES_002', 'active', '2026-07-04 12:00:00.000000', NULL),
('Algebra Practice Bank', '["teacher","student"]', 'primary', 'MATH-RES-001', '1edtech-demo', 'oneroster-spa', 'RES_003', 'active', '2026-07-04 12:00:00.000000', NULL),
('Poetry Annotation Pack', '["teacher","student"]', 'primary', 'ENG-RES-001', '1edtech-demo', 'oneroster-spa', 'RES_004', 'active', '2026-07-04 12:00:00.000000', NULL),
('Civic Debate Toolkit', '["teacher","student"]', 'primary', 'CIV-RES-001', '1edtech-demo', 'oneroster-spa', 'RES_005', 'active', '2026-07-04 12:00:00.000000', NULL),
('Network Troubleshooting Guide', '["teacher","student"]', 'primary', 'TECH-RES-001', '1edtech-demo', 'oneroster-spa', 'RES_006', 'active', '2026-07-04 12:00:00.000000', NULL),
('Field Journal Template', '["teacher","student"]', 'primary', 'BIO-RES-001', '1edtech-demo', 'oneroster-spa', 'RES_007', 'active', '2026-07-04 12:00:00.000000', NULL),
('Microscopy Atlas', '["teacher","student"]', 'secondary', 'BIO-RES-002', '1edtech-demo', 'oneroster-spa', 'RES_008', 'active', '2026-07-04 12:00:00.000000', NULL);

INSERT INTO "courses" ("title", "schoolYearSourcedId", "courseCode", "grades", "subjects", "orgSourcedId", "subjectCodes", "resourceSourcedIds", "sourcedId", "status", "dateLastModified", "metadata") VALUES
('Forensic Science Foundations', 'ACAD_SESS_1', 'SCI-401', '["10"]', '["Forensic Science"]', 'ORG_1', '["SCI401"]', '["RES_001","RES_002"]', 'COURSE_001', 'active', '2026-07-04 12:00:00.000000', NULL),
('Applied Mathematics II', 'ACAD_SESS_1', 'MTH-320', '["11"]', '["Mathematics"]', 'ORG_1', '["MTH320"]', '["RES_003"]', 'COURSE_002', 'active', '2026-07-04 12:00:00.000000', NULL),
('World Literature Seminar', 'ACAD_SESS_1', 'ENG-215', '["10"]', '["English Language Arts"]', 'ORG_2', '["ENG215"]', '["RES_004"]', 'COURSE_003', 'active', '2026-07-04 12:00:00.000000', NULL),
('Civic Leadership Lab', 'ACAD_SESS_1', 'SOC-330', '["12"]', '["Social Studies"]', 'ORG_2', '["SOC330"]', '["RES_005"]', 'COURSE_004', 'active', '2026-07-04 12:00:00.000000', NULL),
('Computer Systems Studio', 'ACAD_SESS_1', 'CSE-410', '["11"]', '["Computer Science"]', 'ORG_3', '["CSE410"]', '["RES_006"]', 'COURSE_005', 'active', '2026-07-04 12:00:00.000000', NULL),
('Biology Field Research', 'ACAD_SESS_1', 'BIO-360', '["12"]', '["Biology"]', 'ORG_3', '["BIO360"]', '["RES_007","RES_008"]', 'COURSE_006', 'active', '2026-07-04 12:00:00.000000', NULL);

INSERT INTO "classes" ("title", "classCode", "classType", "location", "grades", "subjects", "courseSourcedId", "schoolSourcedId", "termSourcedIds", "subjectCodes", "periods", "resourceSourcedIds", "sourcedId", "status", "dateLastModified", "metadata") VALUES
('Forensic Science - Section A', 'FS-A-01', 'scheduled', 'Lab 201', '["10"]', '["Forensic Science"]', 'COURSE_001', 'ORG_1', '["TERM_FALL_1","TERM_SPRING_1"]', '["SCI401"]', '["1"]', '["RES_001","RES_002"]', 'CLASS_001', 'active', '2026-07-04 12:00:00.000000', NULL),
('Applied Math - Section B', 'AM-B-02', 'scheduled', 'Room 118', '["11"]', '["Mathematics"]', 'COURSE_002', 'ORG_1', '["TERM_FALL_1","TERM_SPRING_1"]', '["MTH320"]', '["2"]', '["RES_003"]', 'CLASS_002', 'active', '2026-07-04 12:00:00.000000', NULL),
('Literature Seminar - Block A', 'WL-A-01', 'scheduled', 'Room 304', '["10"]', '["English Language Arts"]', 'COURSE_003', 'ORG_2', '["TERM_FALL_1","TERM_SPRING_1"]', '["ENG215"]', '["1"]', '["RES_004"]', 'CLASS_003', 'active', '2026-07-04 12:00:00.000000', NULL),
('Civic Leadership - Block C', 'CL-C-03', 'scheduled', 'Room 210', '["12"]', '["Social Studies"]', 'COURSE_004', 'ORG_2', '["TERM_FALL_1","TERM_SPRING_1"]', '["SOC330"]', '["3"]', '["RES_005"]', 'CLASS_004', 'active', '2026-07-04 12:00:00.000000', NULL),
('Systems Studio - Lab 1', 'SS-L1-04', 'scheduled', 'Tech Lab 1', '["11"]', '["Computer Science"]', 'COURSE_005', 'ORG_3', '["TERM_FALL_1","TERM_SPRING_1"]', '["CSE410"]', '["4"]', '["RES_006"]', 'CLASS_005', 'active', '2026-07-04 12:00:00.000000', NULL),
('Biology Research - Lab 2', 'BR-L2-05', 'scheduled', 'Science Lab 5', '["12"]', '["Biology"]', 'COURSE_006', 'ORG_3', '["TERM_FALL_1","TERM_SPRING_1"]', '["BIO360"]', '["5"]', '["RES_007","RES_008"]', 'CLASS_006', 'active', '2026-07-04 12:00:00.000000', NULL);

INSERT INTO "categories" ("title", "sourcedId", "status", "dateLastModified", "metadata") VALUES
('Homework', 'CAT_001', 'active', '2026-07-04 12:00:00.000000', NULL),
('Lab Work', 'CAT_002', 'active', '2026-07-04 12:00:00.000000', NULL),
('Assessments', 'CAT_003', 'active', '2026-07-04 12:00:00.000000', NULL),
('Presentations', 'CAT_004', 'active', '2026-07-04 12:00:00.000000', NULL);

INSERT INTO "users" ("username", "userIds", "enabledUser", "givenName", "familyName", "middleName", "role", "identifier", "email", "sms", "phone", "agents", "orgs", "grades", "password", "sourcedId", "status", "dateLastModified", "metadata") VALUES
('adrian.cole@gothammetro.edu', '[{"type":"sis","identifier":"EMP-1000"}]', 'true', 'Adrian', 'Cole', NULL, 'teacher', 'T-1000', 'adrian.cole@gothammetro.edu', NULL, '555-0100', '[]', '["ORG_1"]', '[]', NULL, 'USER_0', 'active', '2026-07-04 12:00:00.000000', NULL),
('maya.patel@gothammetro.edu', '[{"type":"sis","identifier":"STU-2001"}]', 'true', 'Maya', 'Patel', NULL, 'student', 'S-2001', 'maya.patel@gothammetro.edu', NULL, '555-2001', '[]', '["ORG_1"]', '["10"]', NULL, 'USER_001', 'active', '2026-07-04 12:00:00.000000', NULL),
('jordan.lee@gothammetro.edu', '[{"type":"sis","identifier":"STU-2002"}]', 'true', 'Jordan', 'Lee', NULL, 'student', 'S-2002', 'jordan.lee@gothammetro.edu', NULL, '555-2002', '[]', '["ORG_1"]', '["11"]', NULL, 'USER_002', 'active', '2026-07-04 12:00:00.000000', NULL),
('sofia.ramirez@gothammetro.edu', '[{"type":"sis","identifier":"STU-2003"}]', 'true', 'Sofia', 'Ramirez', NULL, 'student', 'S-2003', 'sofia.ramirez@gothammetro.edu', NULL, '555-2003', '[]', '["ORG_2"]', '["10"]', NULL, 'USER_003', 'active', '2026-07-04 12:00:00.000000', NULL),
('ethan.brooks@gothammetro.edu', '[{"type":"sis","identifier":"STU-2004"}]', 'true', 'Ethan', 'Brooks', NULL, 'student', 'S-2004', 'ethan.brooks@gothammetro.edu', NULL, '555-2004', '[]', '["ORG_2"]', '["12"]', NULL, 'USER_004', 'active', '2026-07-04 12:00:00.000000', NULL),
('olivia.chen@gothammetro.edu', '[{"type":"sis","identifier":"STU-2005"}]', 'true', 'Olivia', 'Chen', NULL, 'student', 'S-2005', 'olivia.chen@gothammetro.edu', NULL, '555-2005', '[]', '["ORG_3"]', '["11"]', NULL, 'USER_005', 'active', '2026-07-04 12:00:00.000000', NULL),
('marcus.hill@gothammetro.edu', '[{"type":"sis","identifier":"STU-2006"}]', 'true', 'Marcus', 'Hill', NULL, 'student', 'S-2006', 'marcus.hill@gothammetro.edu', NULL, '555-2006', '[]', '["ORG_3"]', '["12"]', NULL, 'USER_006', 'active', '2026-07-04 12:00:00.000000', NULL),
('nina.foster@gothammetro.edu', '[{"type":"sis","identifier":"STU-2007"}]', 'true', 'Nina', 'Foster', NULL, 'student', 'S-2007', 'nina.foster@gothammetro.edu', NULL, '555-2007', '[]', '["ORG_1"]', '["10"]', NULL, 'USER_007', 'active', '2026-07-04 12:00:00.000000', NULL),
('liam.carter@gothammetro.edu', '[{"type":"sis","identifier":"STU-2008"}]', 'true', 'Liam', 'Carter', NULL, 'student', 'S-2008', 'liam.carter@gothammetro.edu', NULL, '555-2008', '[]', '["ORG_2"]', '["12"]', NULL, 'USER_008', 'active', '2026-07-04 12:00:00.000000', NULL),
('ava.thompson@gothammetro.edu', '[{"type":"sis","identifier":"STU-2009"}]', 'true', 'Ava', 'Thompson', NULL, 'student', 'S-2009', 'ava.thompson@gothammetro.edu', NULL, '555-2009', '[]', '["ORG_3"]', '["11"]', NULL, 'USER_009', 'active', '2026-07-04 12:00:00.000000', NULL),
('bianca.nguyen@gothammetro.edu', '[{"type":"sis","identifier":"EMP-1001"}]', 'true', 'Bianca', 'Nguyen', NULL, 'teacher', 'T-1001', 'bianca.nguyen@gothammetro.edu', NULL, '555-0101', '[]', '["ORG_2"]', '[]', NULL, 'USER_010', 'active', '2026-07-04 12:00:00.000000', NULL),
('daniel.ortiz@gothammetro.edu', '[{"type":"sis","identifier":"EMP-1002"}]', 'true', 'Daniel', 'Ortiz', NULL, 'teacher', 'T-1002', 'daniel.ortiz@gothammetro.edu', NULL, '555-0102', '[]', '["ORG_3"]', '[]', NULL, 'USER_011', 'active', '2026-07-04 12:00:00.000000', NULL);

INSERT INTO "demographics" ("birthDate", "sex", "americanIndianOrAlaskaNative", "asian", "blackOrAfricanAmerican", "nativeHawaiianOrOtherPacificIslander", "white", "demographicRaceTwoOrMoreRaces", "hispanicOrLatinoEthnicity", "countryOfBirthCode", "stateOfBirthAbbreviation", "cityOfBirth", "publicSchoolResidenceStatus", "sourcedId", "status", "dateLastModified", "metadata") VALUES
('2008-09-14', 'female', 'false', 'true', 'false', 'false', 'false', 'false', 'false', 'US', 'NJ', 'Jersey City', 'Resident of the state', 'USER_001', 'active', '2026-07-04 12:00:00.000000', NULL),
('2007-11-03', 'male', 'false', 'true', 'false', 'false', 'false', 'false', 'false', 'US', 'NY', 'Queens', 'Resident of the state', 'USER_002', 'active', '2026-07-04 12:00:00.000000', NULL),
('2008-05-26', 'female', 'false', 'false', 'false', 'false', 'false', 'false', 'true', 'US', 'CA', 'Los Angeles', 'Resident of the state', 'USER_003', 'active', '2026-07-04 12:00:00.000000', NULL),
('2006-12-18', 'male', 'false', 'false', 'true', 'false', 'false', 'false', 'false', 'US', 'GA', 'Atlanta', 'Resident of the state', 'USER_004', 'active', '2026-07-04 12:00:00.000000', NULL),
('2007-04-09', 'female', 'false', 'true', 'false', 'false', 'false', 'false', 'false', 'US', 'WA', 'Seattle', 'Resident of the state', 'USER_005', 'active', '2026-07-04 12:00:00.000000', NULL),
('2006-10-01', 'male', 'false', 'false', 'true', 'false', 'false', 'true', 'false', 'US', 'IL', 'Chicago', 'Resident of the state', 'USER_006', 'active', '2026-07-04 12:00:00.000000', NULL),
('2008-02-21', 'female', 'false', 'false', 'false', 'false', 'true', 'false', 'false', 'US', 'OR', 'Portland', 'Resident of the state', 'USER_007', 'active', '2026-07-04 12:00:00.000000', NULL),
('2006-08-30', 'male', 'false', 'false', 'false', 'false', 'true', 'false', 'false', 'US', 'CO', 'Denver', 'Resident of the state', 'USER_008', 'active', '2026-07-04 12:00:00.000000', NULL),
('2007-06-17', 'female', 'false', 'false', 'false', 'false', 'true', 'false', 'false', 'US', 'AZ', 'Phoenix', 'Resident of the state', 'USER_009', 'active', '2026-07-04 12:00:00.000000', NULL);

INSERT INTO "enrollments" ("userSourcedId", "classSourcedId", "schoolSourcedId", "role", "primary", "beginDate", "endDate", "sourcedId", "status", "dateLastModified", "metadata") VALUES
('USER_0', 'CLASS_001', 'ORG_1', 'teacher', 'true', '2024-08-15', '2025-06-10', 'ENROLL_001', 'active', '2026-07-04 12:00:00.000000', NULL),
('USER_0', 'CLASS_002', 'ORG_1', 'teacher', 'true', '2024-08-15', '2025-06-10', 'ENROLL_002', 'active', '2026-07-04 12:00:00.000000', NULL),
('USER_010', 'CLASS_003', 'ORG_2', 'teacher', 'true', '2024-08-15', '2025-06-10', 'ENROLL_003', 'active', '2026-07-04 12:00:00.000000', NULL),
('USER_010', 'CLASS_004', 'ORG_2', 'teacher', 'true', '2024-08-15', '2025-06-10', 'ENROLL_004', 'active', '2026-07-04 12:00:00.000000', NULL),
('USER_011', 'CLASS_005', 'ORG_3', 'teacher', 'true', '2024-08-15', '2025-06-10', 'ENROLL_005', 'active', '2026-07-04 12:00:00.000000', NULL),
('USER_011', 'CLASS_006', 'ORG_3', 'teacher', 'true', '2024-08-15', '2025-06-10', 'ENROLL_006', 'active', '2026-07-04 12:00:00.000000', NULL),
('USER_001', 'CLASS_001', 'ORG_1', 'student', NULL, '2024-08-15', '2025-06-10', 'ENROLL_101', 'active', '2026-07-04 12:00:00.000000', NULL),
('USER_007', 'CLASS_001', 'ORG_1', 'student', NULL, '2024-08-15', '2025-06-10', 'ENROLL_102', 'active', '2026-07-04 12:00:00.000000', NULL),
('USER_001', 'CLASS_002', 'ORG_1', 'student', NULL, '2024-08-15', '2025-06-10', 'ENROLL_103', 'active', '2026-07-04 12:00:00.000000', NULL),
('USER_002', 'CLASS_002', 'ORG_1', 'student', NULL, '2024-08-15', '2025-06-10', 'ENROLL_104', 'active', '2026-07-04 12:00:00.000000', NULL),
('USER_003', 'CLASS_003', 'ORG_2', 'student', NULL, '2024-08-15', '2025-06-10', 'ENROLL_105', 'active', '2026-07-04 12:00:00.000000', NULL),
('USER_008', 'CLASS_003', 'ORG_2', 'student', NULL, '2024-08-15', '2025-06-10', 'ENROLL_106', 'active', '2026-07-04 12:00:00.000000', NULL),
('USER_004', 'CLASS_004', 'ORG_2', 'student', NULL, '2024-08-15', '2025-06-10', 'ENROLL_107', 'active', '2026-07-04 12:00:00.000000', NULL),
('USER_008', 'CLASS_004', 'ORG_2', 'student', NULL, '2024-08-15', '2025-06-10', 'ENROLL_108', 'active', '2026-07-04 12:00:00.000000', NULL),
('USER_005', 'CLASS_005', 'ORG_3', 'student', NULL, '2024-08-15', '2025-06-10', 'ENROLL_109', 'active', '2026-07-04 12:00:00.000000', NULL),
('USER_009', 'CLASS_005', 'ORG_3', 'student', NULL, '2024-08-15', '2025-06-10', 'ENROLL_110', 'active', '2026-07-04 12:00:00.000000', NULL),
('USER_006', 'CLASS_006', 'ORG_3', 'student', NULL, '2024-08-15', '2025-06-10', 'ENROLL_111', 'active', '2026-07-04 12:00:00.000000', NULL),
('USER_009', 'CLASS_006', 'ORG_3', 'student', NULL, '2024-08-15', '2025-06-10', 'ENROLL_112', 'active', '2026-07-04 12:00:00.000000', NULL);

INSERT INTO "line_items" ("title", "description", "assignDate", "dueDate", "classSourcedId", "categorySourcedId", "gradingPeriodSourcedId", "resultValueMin", "resultValueMax", "sourcedId", "status", "dateLastModified", "metadata") VALUES
('Case File Analysis', 'Analyze a starter evidence packet and summarize findings.', '2024-09-01 08:00:00.000000', '2024-09-15 23:59:00.000000', 'CLASS_001', 'CAT_002', 'GP_Q1', 0.0, 100.0, 'LINEITEM_001', 'active', '2026-07-04 12:00:00.000000', NULL),
('Fingerprint Lab', 'Complete the fingerprint comparison lab report.', '2024-10-01 08:00:00.000000', '2024-10-11 23:59:00.000000', 'CLASS_001', 'CAT_002', 'GP_Q2', 0.0, 100.0, 'LINEITEM_002', 'active', '2026-07-04 12:00:00.000000', NULL),
('Reflection Journal', 'Write a reflection on investigative methods used this term.', '2025-01-15 08:00:00.000000', '2025-01-22 23:59:00.000000', 'CLASS_001', 'CAT_001', 'GP_Q3', 0.0, 100.0, 'LINEITEM_003', 'active', '2026-07-04 12:00:00.000000', NULL),
('Polynomial Checkpoint', 'Short quiz covering polynomial operations.', '2024-09-10 08:00:00.000000', '2024-09-10 15:00:00.000000', 'CLASS_002', 'CAT_003', 'GP_Q1', 0.0, 100.0, 'LINEITEM_004', 'active', '2026-07-04 12:00:00.000000', NULL),
('Close Reading Essay', 'Submit a comparative literature essay.', '2024-11-04 08:00:00.000000', '2024-11-18 23:59:00.000000', 'CLASS_003', 'CAT_003', 'GP_Q2', 0.0, 100.0, 'LINEITEM_005', 'active', '2026-07-04 12:00:00.000000', NULL),
('Town Hall Speech', 'Deliver a civic proposal speech to the class.', '2024-11-12 08:00:00.000000', '2024-11-22 23:59:00.000000', 'CLASS_004', 'CAT_004', 'GP_Q2', 0.0, 100.0, 'LINEITEM_006', 'active', '2026-07-04 12:00:00.000000', NULL),
('Router Configuration Lab', 'Configure and validate a multi-router lab network.', '2025-02-10 08:00:00.000000', '2025-02-21 23:59:00.000000', 'CLASS_005', 'CAT_002', 'GP_Q3', 0.0, 100.0, 'LINEITEM_007', 'active', '2026-07-04 12:00:00.000000', NULL),
('Field Study Report', 'Compile biological observations from field sampling.', '2025-04-07 08:00:00.000000', '2025-04-21 23:59:00.000000', 'CLASS_006', 'CAT_002', 'GP_Q4', 0.0, 100.0, 'LINEITEM_008', 'active', '2026-07-04 12:00:00.000000', NULL);

INSERT INTO "results" ("lineItemSourcedId", "studentSourcedId", "scoreStatus", "score", "scoreDate", "comment", "sourcedId", "status", "dateLastModified", "metadata") VALUES
('LINEITEM_001', 'USER_001', 'fully graded', 92.0, '2024-09-15', 'Strong analytical thinking.', 'RESULT_001', 'active', '2026-07-04 12:00:00.000000', NULL),
('LINEITEM_001', 'USER_007', 'not submitted', 0.0, '2024-09-15', 'Missing submission.', 'RESULT_002', 'active', '2026-07-04 12:00:00.000000', NULL),
('LINEITEM_002', 'USER_001', 'submitted', 95.0, '2024-10-11', 'Excellent lab precision.', 'RESULT_003', 'active', '2026-07-04 12:00:00.000000', NULL),
('LINEITEM_002', 'USER_007', 'partially graded', 81.0, '2024-10-11', 'Awaiting rubric moderation.', 'RESULT_004', 'active', '2026-07-04 12:00:00.000000', NULL),
('LINEITEM_003', 'USER_001', 'fully graded', 89.0, '2025-01-22', 'Clear reflection and evidence.', 'RESULT_005', 'active', '2026-07-04 12:00:00.000000', NULL),
('LINEITEM_003', 'USER_007', 'exempt', 0.0, '2025-01-22', 'Exempt due to transfer review.', 'RESULT_006', 'active', '2026-07-04 12:00:00.000000', NULL),
('LINEITEM_004', 'USER_001', 'fully graded', 88.0, '2024-09-10', 'Solid checkpoint performance.', 'RESULT_007', 'active', '2026-07-04 12:00:00.000000', NULL),
('LINEITEM_004', 'USER_002', 'fully graded', 91.0, '2024-09-10', 'Accurate and efficient work.', 'RESULT_008', 'active', '2026-07-04 12:00:00.000000', NULL),
('LINEITEM_005', 'USER_003', 'fully graded', 94.0, '2024-11-18', 'Strong thesis and citations.', 'RESULT_009', 'active', '2026-07-04 12:00:00.000000', NULL),
('LINEITEM_005', 'USER_008', 'submitted', 90.0, '2024-11-18', 'Submitted pending final annotation check.', 'RESULT_010', 'active', '2026-07-04 12:00:00.000000', NULL),
('LINEITEM_006', 'USER_004', 'fully graded', 87.0, '2024-11-22', 'Confident presentation.', 'RESULT_011', 'active', '2026-07-04 12:00:00.000000', NULL),
('LINEITEM_006', 'USER_008', 'fully graded', 93.0, '2024-11-22', 'Excellent audience engagement.', 'RESULT_012', 'active', '2026-07-04 12:00:00.000000', NULL),
('LINEITEM_007', 'USER_005', 'fully graded', 96.0, '2025-02-21', 'Outstanding configuration accuracy.', 'RESULT_013', 'active', '2026-07-04 12:00:00.000000', NULL),
('LINEITEM_007', 'USER_009', 'partially graded', 84.0, '2025-02-21', 'Waiting on lab verification step.', 'RESULT_014', 'active', '2026-07-04 12:00:00.000000', NULL),
('LINEITEM_008', 'USER_006', 'fully graded', 91.0, '2025-04-21', 'Well-documented field observations.', 'RESULT_015', 'active', '2026-07-04 12:00:00.000000', NULL),
('LINEITEM_008', 'USER_009', 'submitted', 88.0, '2025-04-21', 'Final review submitted successfully.', 'RESULT_016', 'active', '2026-07-04 12:00:00.000000', NULL);

INSERT INTO "oauth_clients" ("client_id", "client_secret", "name", "is_confidential", "scopes") VALUES
('oneroster-client', 'oneroster-secret', 'OneRoster Client', 1, 'https://purl.imsglobal.org/spec/or/v1p1/scope/roster-core.readonly https://purl.imsglobal.org/spec/or/v1p1/scope/roster.readonly https://purl.imsglobal.org/spec/or/v1p1/scope/roster-demographics.readonly https://purl.imsglobal.org/spec/or/v1p1/scope/resource.readonly https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.readonly https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.createput https://purl.imsglobal.org/spec/or/v1p1/scope/gradebook.delete');

COMMIT;
PRAGMA foreign_keys = ON;
