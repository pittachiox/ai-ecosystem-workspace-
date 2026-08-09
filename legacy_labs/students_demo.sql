-- PostgreSQL students demo SQL commands

-- 1) สร้าง table
CREATE TABLE students (
  id SERIAL PRIMARY KEY,
  name TEXT,
  age INT,
  major TEXT
);

-- 2) เพิ่มข้อมูล
INSERT INTO students (name, age, major) VALUES
  ('Bob', 20, 'Computer Science'),
  ('Susi', 21, 'Information Technology');

-- 3) แสดงข้อมูล
SELECT * FROM students;

-- 4) แก้ไขข้อมูล
UPDATE students SET age = 22 WHERE name = 'Bob';

-- 5) ลบข้อมูล
DELETE FROM students WHERE name = 'Susi';

-- 6) ลบ table
DROP TABLE students;