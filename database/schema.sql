DROP TABLE IF EXISTS placements;

CREATE TABLE placements (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    gender TEXT NOT NULL,
    branch TEXT NOT NULL,
    graduation_year INTEGER NOT NULL,
    cgpa REAL NOT NULL,
    tenth_percent REAL NOT NULL,
    twelfth_percent REAL NOT NULL,
    internships INTEGER NOT NULL,
    projects INTEGER NOT NULL,
    certifications INTEGER NOT NULL,
    technical_skills TEXT NOT NULL,
    aptitude_score REAL NOT NULL,
    communication_score REAL NOT NULL,
    placed INTEGER NOT NULL,
    company TEXT,
    role TEXT,
    package_lpa REAL NOT NULL,
    placement_date TEXT,
    offer_type TEXT NOT NULL
);

CREATE INDEX idx_placements_year ON placements (graduation_year);
CREATE INDEX idx_placements_branch ON placements (branch);
CREATE INDEX idx_placements_company ON placements (company);
CREATE INDEX idx_placements_placed ON placements (placed);
