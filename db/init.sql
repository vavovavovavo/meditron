-- db/init.sql
CREATE TABLE departments (
    id SERIAL PRIMARY KEY
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    department_id INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE surveys (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    anket_type TEXT NOT NULL,
    visible BOOLEAN NOT NULL DEFAULT TRUE,
    answers JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Вставь свои 57 записей
INSERT INTO departments (id) VALUES (1), (2), (3);
INSERT INTO users (id, department_id) VALUES (1, 1), (2, 2), (3, 3);

INSERT INTO surveys (user_id, anket_type, visible, answers) VALUES
-- Отдел 1: первые 26 записей (user_id = 1)
(1, 'base', true, '{"ans": [6, 7, 8, 8, 8, 9, 6, 7, 8, 7], "sum": 74}'),
(2, 'base', true, '{"ans": [6, 7, 6, 9, 7, 7, 5, 7, 6, 6], "sum": 66}'),
(1, 'base', true, '{"ans": [5, 7, 6, 7, 7, 8, 6, 6, 7, 7], "sum": 66}'),
(5, 'base', true, '{"ans": [7, 9, 6, 6, 7, 7, 6, 6, 7, 5], "sum": 66}'),
(1, 'base', true, '{"ans": [6, 8, 5, 5, 7, 7, 7, 7, 7, 6], "sum": 65}'),
(2, 'base', true, '{"ans": [7, 8, 5, 8, 9, 7, 7, 6, 7, 6], "sum": 70}'),
(5, 'base', true, '{"ans": [6, 7, 5, 8, 6, 8, 5, 7, 8, 6], "sum": 66}'),
(1, 'base', true, '{"ans": [7, 8, 7, 8, 8, 8, 7, 7, 7, 7], "sum": 74}'),
(2, 'base', true, '{"ans": [6, 8, 7, 9, 7, 9, 7, 6, 8, 7], "sum": 74}'),
(5, 'base', true, '{"ans": [7, 5, 5, 7, 6, 5, 6, 6, 6, 5], "sum": 58}'),
(2, 'base', true, '{"ans": [5, 7, 7, 5, 8, 7, 5, 8, 8, 6], "sum": 66}'),
(5, 'base', true, '{"ans": [8, 7, 7, 9, 8, 8, 7, 8, 7, 7], "sum": 76}'),
(1, 'base', true, '{"ans": [6, 8, 7, 7, 7, 8, 7, 7, 8, 7], "sum": 72}'),
(2, 'base', true, '{"ans": [6, 8, 6, 8, 9, 8, 7, 6, 7, 6], "sum": 71}'),
(5, 'base', true, '{"ans": [6, 7, 7, 8, 7, 6, 4, 6, 7, 6], "sum": 64}'),
(1, 'base', true, '{"ans": [5, 7, 6, 10, 7, 9, 7, 7, 8, 8], "sum": 74}'),
(1, 'base', true, '{"ans": [8, 8, 8, 9, 9, 9, 9, 8, 10, 9], "sum": 87}'),
(5, 'base', true, '{"ans": [5, 7, 8, 6, 6, 8, 8, 7, 8, 8], "sum": 71}'),
(2, 'base', true, '{"ans": [7, 9, 7, 8, 8, 6, 8, 5, 6, 6], "sum": 70}'),
(1, 'base', true, '{"ans": [6, 6, 6, 6, 7, 6, 7, 5, 7, 6], "sum": 62}'),
(2, 'base', true, '{"ans": [5, 8, 5, 5, 7, 7, 7, 6, 6, 5], "sum": 61}'),
(1, 'base', true, '{"ans": [7, 7, 8, 8, 8, 8, 7, 8, 8, 7], "sum": 76}'),
(5, 'base', true, '{"ans": [7, 6, 6, 8, 8, 8, 6, 6, 7, 7], "sum": 69}'),
(1, 'base', true, '{"ans": [6, 8, 6, 8, 8, 7, 7, 6, 8, 6], "sum": 70}'),
(2, 'base', true, '{"ans": [1, 3, 3, 2, 1, 2, 3, 1, 3, 3], "sum": 19}'),

-- Отдел 2: следующие 17 записей (user_id = 2)
(3, 'base', true, '{"ans": [2, 1, 3, 2, 1, 3, 2, 2, 1, 3], "sum": 17}'),
(4, 'base', true, '{"ans": [1, 2, 4, 2, 1, 3, 3, 3, 2, 5], "sum": 25}'),
(3, 'base', true, '{"ans": [1, 2, 5, 1, 3, 2, 5, 2, 2, 4], "sum": 26}'),
(4, 'base', true, '{"ans": [2, 1, 2, 3, 1, 1, 1, 1, 1, 2], "sum": 14}'),
(6, 'base', true, '{"ans": [2, 2, 4, 2, 1, 4, 4, 4, 3, 5], "sum": 31}'),
(3, 'base', true, '{"ans": [3, 2, 2, 1, 2, 1, 3, 2, 1, 2], "sum": 18}'),
(4, 'base', true, '{"ans": [1, 2, 3, 4, 1, 2, 3, 3, 2, 3], "sum": 24}'),
(3, 'base', true, '{"ans": [1, 2, 3, 3, 1, 2, 3, 1, 1, 4], "sum": 19}'),
(6, 'base', true, '{"ans": [1, 4, 2, 3, 2, 3, 4, 2, 1, 4], "sum": 24}'),
(3, 'base', true, '{"ans": [1, 1, 3, 3, 1, 2, 3, 1, 1, 3], "sum": 18}'),
(4, 'base', true, '{"ans": [2, 1, 4, 1, 1, 2, 3, 1, 2, 4], "sum": 21}'),
(3, 'base', true, '{"ans": [2, 2, 4, 3, 3, 3, 4, 4, 2, 3], "sum": 30}'),
(6, 'base', true, '{"ans": [2, 4, 5, 2, 3, 3, 6, 2, 2, 4], "sum": 33}'),
(3, 'base', true, '{"ans": [2, 4, 2, 1, 2, 2, 3, 2, 1, 1], "sum": 19}'),
(4, 'base', true, '{"ans": [1, 2, 3, 3, 1, 3, 2, 4, 1, 4], "sum": 23}'),
(3, 'base', true, '{"ans": [1, 1, 3, 1, 1, 2, 3, 2, 1, 3], "sum": 18}'),
(6, 'base', true, '{"ans": [4, 5, 5, 2, 1, 5, 1, 2, 2, 4], "sum": 30}'),

-- Отдел 3: последние 14 записей (user_id = 3)
(7, 'base', true, '{"ans": [5, 5, 4, 3, 1, 5, 2, 2, 2, 3], "sum": 32}'),
(8, 'base', true, '{"ans": [4, 5, 6, 4, 1, 4, 1, 4, 3, 3], "sum": 35}'),
(7, 'base', true, '{"ans": [6, 7, 5, 2, 1, 7, 2, 2, 1, 4], "sum": 37}'),
(8, 'base', true, '{"ans": [5, 6, 6, 3, 1, 6, 1, 4, 2, 5], "sum": 39}'),
(7, 'base', true, '{"ans": [5, 4, 5, 2, 2, 4, 2, 3, 2, 4], "sum": 33}'),
(9, 'base', true, '{"ans": [4, 4, 5, 3, 1, 5, 1, 3, 2, 4], "sum": 32}'),
(7, 'base', true, '{"ans": [3, 4, 4, 2, 1, 4, 1, 3, 2, 3], "sum": 26}'),
(8, 'base', true, '{"ans": [4, 5, 5, 2, 1, 5, 2, 1, 2, 4], "sum": 31}'),
(7, 'base', true, '{"ans": [4, 6, 3, 1, 1, 5, 1, 2, 1, 3], "sum": 25}'),
(9, 'base', true, '{"ans": [4, 4, 7, 1, 1, 6, 1, 3, 3, 5], "sum": 32}'),
(7, 'base', true, '{"ans": [5, 6, 4, 3, 2, 7, 1, 3, 1, 4], "sum": 36}'),
(8, 'base', true, '{"ans": [5, 7, 4, 5, 2, 7, 2, 2, 1, 5], "sum": 39}'),
(7, 'base', true, '{"ans": [4, 5, 5, 2, 1, 5, 2, 2, 2, 2], "sum": 30}'),
(9, 'base', true, '{"ans": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5], "sum": 50}');
-- ...