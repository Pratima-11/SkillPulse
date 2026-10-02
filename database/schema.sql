-- =====================================================================
-- SkillPulse Database Schema (MySQL 8.x)
-- =====================================================================
-- This file is a REFERENCE copy of the schema that Flask-SQLAlchemy
-- creates automatically via db.create_all() (see backend/run.py).
-- You do NOT need to run this file manually if you let run.py create
-- the tables - it is provided so the database design can be reviewed,
-- printed, or imported directly via MySQL Workbench for the project
-- report's ER diagram section.
--
-- Run manually with:
--   mysql -u root -p skillpulse < database/schema.sql
-- =====================================================================

CREATE DATABASE IF NOT EXISTS skillpulse
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE skillpulse;

-- ---------------------------------------------------------------------
-- users
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('worker', 'contractor', 'admin') NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- worker_profiles
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS worker_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    full_name VARCHAR(120) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    latitude DOUBLE NULL,
    longitude DOUBLE NULL,
    area_text VARCHAR(200) NULL,
    expected_wage DOUBLE NOT NULL DEFAULT 0,
    experience_years DOUBLE NOT NULL DEFAULT 0,
    verification_status ENUM('pending', 'verified', 'rejected') NOT NULL DEFAULT 'pending',
    verification_document_path VARCHAR(255) NULL,
    reliability_score DOUBLE NOT NULL DEFAULT 0.5,
    jobs_completed INT NOT NULL DEFAULT 0,
    jobs_accepted INT NOT NULL DEFAULT 0,
    jobs_cancelled INT NOT NULL DEFAULT 0,
    average_rating DOUBLE NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_worker_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_worker_location (latitude, longitude),
    INDEX idx_worker_verification (verification_status)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- contractor_profiles
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS contractor_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    company_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(120) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    latitude DOUBLE NULL,
    longitude DOUBLE NULL,
    area_text VARCHAR(200) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_contractor_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- skills
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- worker_skills (many-to-many join table)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS worker_skills (
    worker_id INT NOT NULL,
    skill_id INT NOT NULL,
    PRIMARY KEY (worker_id, skill_id),
    CONSTRAINT fk_ws_worker FOREIGN KEY (worker_id) REFERENCES worker_profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_ws_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- jobs
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contractor_id INT NOT NULL,
    skill_id INT NOT NULL,
    workers_required INT NOT NULL DEFAULT 1,
    job_date DATE NOT NULL,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    area_text VARCHAR(200) NULL,
    wage DOUBLE NOT NULL,
    working_hours VARCHAR(50) NULL,
    min_experience DOUBLE NOT NULL DEFAULT 0,
    description TEXT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'POSTED',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_job_contractor FOREIGN KEY (contractor_id) REFERENCES contractor_profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_job_skill FOREIGN KEY (skill_id) REFERENCES skills(id),
    INDEX idx_job_status (status),
    INDEX idx_job_date (job_date),
    INDEX idx_job_location (latitude, longitude)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- job_applications  (worker <-> job, carries the computed match score)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS job_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    worker_id INT NOT NULL,
    match_score DOUBLE NOT NULL DEFAULT 0,
    score_breakdown JSON NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_app_job FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    CONSTRAINT fk_app_worker FOREIGN KEY (worker_id) REFERENCES worker_profiles(id) ON DELETE CASCADE,
    CONSTRAINT uq_job_worker UNIQUE (job_id, worker_id),
    INDEX idx_app_status (status)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- availability  (one row per worker per date)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS availability (
    id INT AUTO_INCREMENT PRIMARY KEY,
    worker_id INT NOT NULL,
    available_date DATE NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_avail_worker FOREIGN KEY (worker_id) REFERENCES worker_profiles(id) ON DELETE CASCADE,
    CONSTRAINT uq_worker_date UNIQUE (worker_id, available_date)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- ratings
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_application_id INT NOT NULL UNIQUE,
    rating_value INT NOT NULL,
    comment TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rating_app FOREIGN KEY (job_application_id) REFERENCES job_applications(id) ON DELETE CASCADE,
    CONSTRAINT chk_rating_range CHECK (rating_value >= 1 AND rating_value <= 5)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- notifications
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message VARCHAR(255) NOT NULL,
    notif_type VARCHAR(50) NOT NULL DEFAULT 'GENERAL',
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notif_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_notif_user_read (user_id, is_read)
) ENGINE=InnoDB;
