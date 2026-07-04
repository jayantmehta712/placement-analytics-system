-- Overall placement summary
SELECT
    COUNT(*) AS total_students,
    SUM(placed) AS placed_students,
    ROUND(100.0 * SUM(placed) / COUNT(*), 2) AS placement_rate,
    ROUND(AVG(NULLIF(package_lpa, 0)), 2) AS average_package_lpa,
    MAX(package_lpa) AS highest_package_lpa
FROM placements;

-- Placement trend by graduation year
SELECT
    graduation_year,
    COUNT(*) AS total_students,
    SUM(placed) AS placed_students,
    ROUND(100.0 * SUM(placed) / COUNT(*), 2) AS placement_rate,
    ROUND(AVG(NULLIF(package_lpa, 0)), 2) AS average_package_lpa
FROM placements
GROUP BY graduation_year
ORDER BY graduation_year;

-- Branch-wise placement performance
SELECT
    branch,
    COUNT(*) AS total_students,
    SUM(placed) AS placed_students,
    ROUND(100.0 * SUM(placed) / COUNT(*), 2) AS placement_rate,
    ROUND(AVG(cgpa), 2) AS average_cgpa,
    ROUND(AVG(NULLIF(package_lpa, 0)), 2) AS average_package_lpa
FROM placements
GROUP BY branch
ORDER BY placement_rate DESC;

-- Company-wise hiring and salary
SELECT
    company,
    COUNT(*) AS hires,
    ROUND(AVG(package_lpa), 2) AS average_package_lpa,
    MAX(package_lpa) AS highest_package_lpa
FROM placements
WHERE placed = 1
GROUP BY company
ORDER BY hires DESC, average_package_lpa DESC;

-- CGPA band placement conversion
SELECT
    CASE
        WHEN cgpa >= 9 THEN '9.0+'
        WHEN cgpa >= 8 THEN '8.0-8.9'
        WHEN cgpa >= 7 THEN '7.0-7.9'
        ELSE 'Below 7.0'
    END AS cgpa_band,
    COUNT(*) AS total_students,
    SUM(placed) AS placed_students,
    ROUND(100.0 * SUM(placed) / COUNT(*), 2) AS placement_rate
FROM placements
GROUP BY cgpa_band
ORDER BY placement_rate DESC;

-- Top salary offers
SELECT
    name,
    branch,
    graduation_year,
    company,
    role,
    package_lpa
FROM placements
WHERE placed = 1
ORDER BY package_lpa DESC
LIMIT 10;
