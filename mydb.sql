CREATE DATABASE farm_management;
USE farm_management;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE animals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tag_number VARCHAR(50) NOT NULL UNIQUE,
    animal_type VARCHAR(50) NOT NULL,
    breed VARCHAR(100),
    birth_date DATE,
    weight DECIMAL(8,2),
    health_status VARCHAR(50) DEFAULT 'Healthy',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE feeding (
    id INT AUTO_INCREMENT PRIMARY KEY,
    animal_id INT,
    feed_type VARCHAR(100) NOT NULL,
    quantity DECIMAL(8,2) NOT NULL,
    feeding_date DATETIME NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (animal_id) REFERENCES animals(id)
);

CREATE TABLE health_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    animal_id INT,
    check_date DATE NOT NULL,
    temperature DECIMAL(4,2),
    weight DECIMAL(8,2),
    symptoms TEXT,
    treatment TEXT,
    vet_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (animal_id) REFERENCES animals(id)
);

INSERT INTO users (username, email, password) VALUES 
('admin', 'admin@farm.com', 'pbkdf2:sha256:260000$salt$hash');

INSERT INTO animals (tag_number, animal_type, breed, birth_date, weight, health_status) VALUES
('TAG001', 'Cattle', 'Friesian', '2022-05-14', 350.5, 'Healthy'),
('TAG002', 'Goat', 'Boer', '2023-01-10', 45.0, 'Sick'),
('TAG003', 'Sheep', 'Dorper', '2022-09-03', 60.2, 'Healthy'),
('TAG004', 'Pig', 'Large White', '2023-03-20', 90.8, 'Under Treatment'),
('TAG005', 'Chicken', 'Rhode Island Red', '2024-01-05', 2.3, 'Healthy');
