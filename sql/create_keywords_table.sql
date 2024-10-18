-- 데이터베이스 생성 (이미 존재하면 생략 가능)
CREATE DATABASE IF NOT EXISTS your_database_name;

-- 데이터베이스 사용
USE your_database_name;

-- 테이블 생성
CREATE TABLE keywords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    등록일 DATE,
    상호명 VARCHAR(255),
    플레이스번호 VARCHAR(255),
    키워드 VARCHAR(255),
    최초순위 INT,
    최고순위 INT,
    현재순위 INT,
    담당자 VARCHAR(255),
    변동이력 VARCHAR(255),
    최신일자 DATETIME
);

-- 사용자 테이블 생성
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'manager') NOT NULL
);

-- 담당 업체 테이블 생성
CREATE TABLE businesses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    manager_id INT,
    FOREIGN KEY (manager_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 기본 쿼리
SELECT * FROM keywords;
SELECT * FROM users;
SELECT * FROM businesses;


-- 키워드 테이블에서 상호명과 담당자 쿼리
SELECT b.name AS 업체명, u.username AS 담당자
FROM businesses b
JOIN users u ON b.manager_id = u.id;


-- CSV 데이터 로드 예시
LOAD DATA INFILE 'C:/workspace/rank_program/data/keywords.csv'
INTO TABLE keywords
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
