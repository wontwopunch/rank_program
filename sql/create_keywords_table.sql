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

SELECT * 
FROM keywords;

SELECT * FROM keywords WHERE 플레이스번호 = '1556779893';

SELECT * FROM keywords WHERE id = 1;

SELECT * FROM keywords LIMIT 10;

DELETE FROM keywords;

TRUNCATE TABLE keywords;


LOAD DATA INFILE 'C:/workspace/rank_program/data/keywords.csv'
INTO TABLE keywords
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

SHOW VARIABLES LIKE 'secure_file_priv';

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/keywords.csv'
INTO TABLE keywords
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'C:/workspace/rank_program/data/keywords.csv'
INTO TABLE keywords
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;


ALTER TABLE keywords MODIFY id INT AUTO_INCREMENT;

SHOW GLOBAL VARIABLES LIKE 'local_infile';

SET GLOBAL local_infile = 1;


LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/keywords.csv'
INTO TABLE keywords
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(등록일, 상호명, 플레이스번호, 키워드, 최초순위, 최고순위, 현재순위, 담당자, 변동이력, @최신일자)
SET 최신일자 = STR_TO_DATE(@최신일자, '%Y-%m-%d %H:%i');

DESCRIBE keywords;

SELECT id, 최초순위, 최고순위, 현재순위 FROM keywords;


ALTER TABLE keywords ADD COLUMN 변동이력_정수 INT;


SET SESSION wait_timeout = 30000;  -- 30,000초
SET SESSION interactive_timeout = 30000;  -- 30,000초

DESCRIBE keywords;


SELECT id, 현재순위, 최고순위, 최초순위 FROM keywords WHERE 현재순위 IS NOT NULL;

-- '카테고리', '블로그리뷰', '방문자리뷰' 컬럼을 추가
ALTER TABLE keywords
ADD COLUMN 카테고리 VARCHAR(255) AFTER 키워드,
ADD COLUMN 블로그리뷰 INT DEFAULT 0 AFTER 변동이력,
ADD COLUMN 방문자리뷰 INT DEFAULT 0 AFTER 블로그리뷰;

SELECT * FROM keywords WHERE id = 1;

SELECT id, 카테고리, 블로그리뷰, 방문자리뷰 FROM keywords;

ALTER TABLE keywords MODIFY id INT AUTO_INCREMENT;

DELETE FROM keywords WHERE id = -998;

ALTER TABLE keywords AUTO_INCREMENT = 1;

UPDATE keywords SET id = 1 WHERE id = 2;

ALTER TABLE keywords AUTO_INCREMENT = 2;

SET @new_id = 0;

UPDATE keywords SET id = (@new_id := @new_id + 1);


SET @new_id = 0;
UPDATE keywords 
SET id = @new_id := @new_id + 1;


ALTER TABLE keywords MODIFY COLUMN id INT AUTO_INCREMENT;

-- 중복된 `id` 값을 가진 행이 있으면 삭제
DELETE FROM keywords WHERE id = 1;

-- 테이블에 AUTO_INCREMENT 값이 재조정되도록 설정
ALTER TABLE keywords AUTO_INCREMENT = 1;

ALTER TABLE keywords MODIFY COLUMN id INT;

SET @new_id = 0;
UPDATE keywords 
SET id = @new_id := @new_id + 1;

ALTER TABLE keywords MODIFY COLUMN id INT AUTO_INCREMENT;

ALTER TABLE keywords AUTO_INCREMENT = 1;

ALTER TABLE keywords MODIFY COLUMN id INT;


SET @new_id = 0;
UPDATE keywords 
SET id = (@new_id := @new_id + 1)
ORDER BY id;


SET @new_id = 0;
UPDATE keywords 
SET id = (@new_id := @new_id + 1)
ORDER BY id;

SELECT MAX(id) FROM keywords;

ALTER TABLE keywords AUTO_INCREMENT = 291;

SET @new_id = 0;
UPDATE keywords
SET id = (@new_id := @new_id + 1)
ORDER BY id;

SELECT id, COUNT(*) 
FROM keywords
GROUP BY id
HAVING COUNT(*) > 1;


ALTER TABLE keywords MODIFY COLUMN id INT NOT NULL AUTO_INCREMENT;

SELECT MAX(id) FROM keywords;

ALTER TABLE keywords AUTO_INCREMENT = 291;

SELECT id, COUNT(*)
FROM keywords
GROUP BY id
HAVING COUNT(*) > 1;

DELETE FROM keywords WHERE id = 중복된_id;

ALTER TABLE keywords MODIFY COLUMN id INT AUTO_INCREMENT;

SET @new_id = 0;
UPDATE keywords 
SET id = @new_id := @new_id + 1;


-- 임시로 AUTO_INCREMENT 해제
ALTER TABLE keywords MODIFY id INT;

-- 중복되지 않도록 id 값을 1씩 증가시킴
SET @new_id = 0;
UPDATE keywords SET id = (@new_id := @new_id + 1);

-- AUTO_INCREMENT 다시 설정
ALTER TABLE keywords MODIFY id INT AUTO_INCREMENT;

-- AUTO_INCREMENT 값 조정
SELECT MAX(id) FROM keywords;

ALTER TABLE keywords AUTO_INCREMENT = 292;

SET @new_id = 0;
UPDATE keywords 
SET id = (@new_id := @new_id + 1)
ORDER BY id ASC;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'manager') NOT NULL
);

INSERT INTO users (username, password, role) VALUES ('root', 'hashed_password_here', 'admin');

SELECT * FROM users;


SELECT * FROM users;

SELECT * FROM users WHERE username = 'root';

SELECT * FROM users WHERE role = 'admin';

SELECT * FROM users WHERE username = '서지원';

UPDATE users SET role = 'manager' WHERE username = '서지원';

DELETE FROM users;

CREATE TABLE businesses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    manager_id INT,
    FOREIGN KEY (manager_id) REFERENCES users(id) ON DELETE SET NULL
);


DESCRIBE users;

ALTER TABLE users ADD COLUMN 담당자 VARCHAR(255);

DESCRIBE keywords;

SELECT * FROM users WHERE username = '이아름';

SELECT * FROM users;

DELETE FROM keywords;

TRUNCATE TABLE keywords;

DESCRIBE keywords;


ALTER TABLE keywords 
DROP COLUMN 변동이력_기호,
DROP COLUMN 변동이력_정수;

SHOW VARIABLES LIKE 'secure_file_priv';

SET @@global.sql_mode = '';
SET @@session.sql_mode = '';

LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\keywords.csv'
INTO TABLE keywords
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 LINES
(등록일, 상호명, 플레이스번호, 키워드, 최초순위, 최고순위, 현재순위, 담당자, 변동이력, 블로그리뷰, 방문자리뷰, @최신일자)
SET 최신일자 = STR_TO_DATE(@최신일자, '%Y-%m-%d %H:%i');

DELETE FROM users WHERE username = '서지원';

SELECT username, password FROM users WHERE username = '오경주';

SELECT * FROM users WHERE username = '오경주';

UPDATE users SET password = '$2b$12$correct_hashed_password' WHERE username = '오경주';

SELECT password FROM users WHERE username = '오경주';

UPDATE users SET password = '$2b$12$j4T9y2kxZ5Wr/A/wHgVWEOiPzT50Y5M9bPP7rFXvU/Xyi8mr485oy' WHERE username = '오경주';

SELECT username, password FROM users WHERE username = '오경주';

SELECT * FROM users WHERE username = '오경주';

SELECT * FROM businesses WHERE manager_id = 6;

DESCRIBE businesses;

SELECT b.name, u.username
FROM businesses b
JOIN users u ON b.manager_id = u.id
WHERE u.username = '오경주';

SELECT b.name AS 업체명, u.username AS 담당자
FROM businesses b
JOIN users u ON b.manager_id = u.id
WHERE u.username = '오경주';

SELECT id FROM users WHERE username = '오경주';

SELECT * FROM businesses WHERE manager_id = 6;

UPDATE businesses
SET manager_id = 6
WHERE name = '포근네일';

SELECT * FROM businesses WHERE manager_id = 6;

SELECT * FROM businesses;

TRUNCATE TABLE businesses;


UPDATE businesses b
JOIN users u ON b.manager_id = u.id
JOIN keywords k ON k.담당자 = u.username
SET b.manager_id = u.id;

SELECT * FROM businesses;

SELECT b.name AS 업체명, u.username AS 담당자
FROM businesses b
JOIN users u ON b.manager_id = u.id;

SELECT * FROM businesses WHERE manager_id = 6;

SELECT b.id AS 업체ID, b.name AS 상호명, k.등록일, k.플레이스번호, k.키워드, k.카테고리, 
       k.최초순위, k.최고순위, k.현재순위, k.담당자, k.변동이력, k.블로그리뷰, 
       k.방문자리뷰, k.최신일자
FROM businesses b
LEFT JOIN keywords k ON b.id = k.플레이스번호
WHERE b.manager_id = 6;

SELECT b.id AS 업체ID, b.name AS 상호명, k.플레이스번호
FROM businesses b
LEFT JOIN keywords k ON b.id = k.플레이스번호;

UPDATE keywords 
SET 플레이스번호 = (SELECT id FROM businesses WHERE name = '포근네일')
WHERE 상호명 = '포근네일';

SELECT b.id AS 업체ID, b.name AS 상호명, k.등록일, k.플레이스번호, k.키워드, k.카테고리, 
       k.최초순위, k.최고순위, k.현재순위, k.담당자, k.변동이력, k.블로그리뷰, 
       k.방문자리뷰, k.최신일자
FROM businesses b
LEFT JOIN keywords k ON b.id = k.플레이스번호
WHERE b.manager_id = 6;

SELECT b.id, b.name, k.플레이스번호
FROM businesses b
LEFT JOIN keywords k ON b.id = k.플레이스번호;

SELECT b.id, b.name, k.플레이스번호
FROM businesses b
LEFT JOIN keywords k ON b.id = k.플레이스번호
WHERE b.manager_id = 6;

SELECT * FROM keywords WHERE 플레이스번호 = 1;

UPDATE keywords
SET 플레이스번호 = 1645705642
WHERE 상호명 = '포근네일';


SELECT *
FROM keywords
WHERE 상호명 = '포근네일';


SELECT b.id AS 업체ID, b.name AS 상호명, k.플레이스번호, k.키워드
FROM businesses b
LEFT JOIN keywords k ON b.id = k.플레이스번호
WHERE b.manager_id = 6;


UPDATE businesses b
JOIN keywords k ON b.name = k.상호명
SET b.플레이스번호 = k.플레이스번호;

SELECT b.id AS 업체ID, b.name AS 상호명, k.등록일, b.플레이스번호, k.키워드, k.카테고리, 
       k.최초순위, k.최고순위, k.현재순위, k.담당자, k.변동이력, k.블로그리뷰, 
       k.방문자리뷰, k.최신일자
FROM businesses b
LEFT JOIN keywords k ON b.플레이스번호 = k.플레이스번호
WHERE b.manager_id = 6;

SELECT b.id AS 업체ID, b.name AS 상호명, k.플레이스번호 AS 키워드_플레이스번호, b.플레이스번호 AS 비즈니스_플레이스번호
FROM businesses b
LEFT JOIN keywords k ON b.플레이스번호 = k.플레이스번호;


SELECT b.id AS 업체ID, b.name AS 상호명, k.등록일, b.플레이스번호, k.키워드, k.카테고리, 
       k.최초순위, k.최고순위, k.현재순위, k.담당자, k.변동이력, k.블로그리뷰, 
       k.방문자리뷰, k.최신일자
FROM businesses b
INNER JOIN keywords k ON b.플레이스번호 = k.플레이스번호
WHERE b.manager_id = 6;

ALTER TABLE keywords ADD COLUMN manager_id INT;

UPDATE keywords k
JOIN businesses b ON k.플레이스번호 = b.플레이스번호
SET k.manager_id = b.manager_id;

SELECT * 
FROM keywords
WHERE manager_id = 6;

-- 담당 상호명 등록
INSERT INTO businesses (name, manager_id)
VALUES ('프로클리어',14);

-- 플레이스번호 연동
UPDATE businesses b
JOIN keywords k ON b.name = k.상호명
SET b.플레이스번호 = k.플레이스번호;


TRUNCATE TABLE businesses;

ALTER TABLE businesses AUTO_INCREMENT = 1;



ALTER TABLE businesses
ADD CONSTRAINT fk_manager
FOREIGN KEY (manager_id) REFERENCES users(id)
ON DELETE CASCADE;

SELECT b.*
FROM businesses b
JOIN users u ON u.id = b.manager_id
WHERE u.id = 7;

SELECT * FROM businesses;

ALTER TABLE businesses ADD COLUMN 담당자 VARCHAR(255);
ALTER TABLE businesses DROP COLUMN 담당자;


SELECT * FROM users WHERE username = '한시은';


SHOW TRIGGERS FROM your_database_name LIKE 'businesses';

DROP TRIGGER IF EXISTS set_cnt_id;


SELECT * FROM businesses;

ALTER TABLE businesses ADD COLUMN 담당자 VARCHAR(255);

SELECT * FROM keywords WHERE 담당자 = '한시은';

SELECT * FROM keywords WHERE 담당자 = '오경주';


SELECT DISTINCT b.id AS ID, k.등록일, k.상호명, k.플레이스번호, k.키워드, 
       k.카테고리, k.최초순위, k.최고순위, k.현재순위, k.담당자, k.변동이력, 
       k.블로그리뷰, k.방문자리뷰, k.최신일자
FROM businesses b
JOIN keywords k ON b.플레이스번호 = k.플레이스번호
WHERE k.담당자 = '오경주';


SELECT DISTINCT b.id AS ID, k.등록일, k.상호명, k.플레이스번호, k.키워드, 
       k.카테고리, k.최초순위, k.최고순위, k.현재순위, k.담당자, k.변동이력, 
       k.블로그리뷰, k.방문자리뷰, k.최신일자
FROM businesses b
JOIN keywords k ON b.플레이스번호 = k.플레이스번호
WHERE b.manager_id = 6;


SELECT * FROM businesses;

INSERT INTO businesses (name, 플레이스번호, 담당자)
SELECT DISTINCT 상호명, 플레이스번호, 담당자
FROM keywords
WHERE 플레이스번호 IS NOT NULL;


SELECT DISTINCT b.id AS ID, k.등록일, k.상호명, k.플레이스번호, k.키워드, 
       k.카테고리, k.최초순위, k.최고순위, k.현재순위, k.담당자, k.변동이력, 
       k.블로그리뷰, k.방문자리뷰, k.최신일자
FROM businesses b
JOIN keywords k ON b.플레이스번호 = k.플레이스번호
WHERE k.담당자 = '오경주';

SELECT * FROM users WHERE username = '김주성';
DELETE FROM users WHERE username = '서지우';


SELECT * FROM keywords WHERE 플레이스번호 = 1345060254;

SELECT DISTINCT b.id AS ID, k.등록일, k.상호명, k.플레이스번호, k.키워드, 
       k.카테고리, k.최초순위, k.최고순위, k.현재순위, k.담당자, 
       k.변동이력, k.블로그리뷰, k.방문자리뷰, k.최신일자
FROM businesses b
JOIN keywords k ON b.플레이스번호 = k.플레이스번호
WHERE b.manager_id = 6;

SELECT * FROM businesses;
SELECT * FROM keywords;

DESCRIBE businesses;
DESCRIBE keywords;

ALTER TABLE businesses MODIFY 플레이스번호 VARCHAR(255);



SELECT * FROM businesses;

ALTER TABLE businesses
ADD COLUMN 플레이스번호 VARCHAR(255);








