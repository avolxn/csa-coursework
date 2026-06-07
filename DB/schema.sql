DROP TABLE IF EXISTS result_audit;
DROP TABLE IF EXISTS test_results;
DROP TABLE IF EXISTS answers;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS tests;
DROP TABLE IF EXISTS users;

DROP FUNCTION IF EXISTS calculate_percent(integer, integer);
DROP FUNCTION IF EXISTS grade_from_percent(numeric);
DROP FUNCTION IF EXISTS is_passed(numeric);
DROP FUNCTION IF EXISTS set_updated_at();
DROP FUNCTION IF EXISTS fill_result_fields();
DROP FUNCTION IF EXISTS audit_result_changes();

DROP PROCEDURE IF EXISTS create_demo_test(text, text);
DROP PROCEDURE IF EXISTS register_test_result(integer, integer, integer, integer);
DROP PROCEDURE IF EXISTS clear_demo_data();

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    age INTEGER CHECK (age IS NULL OR age BETWEEN 6 AND 100),
    role VARCHAR(20) NOT NULL DEFAULT 'student'
        CHECK (role IN ('admin', 'teacher', 'student')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tests (
    id SERIAL PRIMARY KEY,
    title VARCHAR(180) NOT NULL,
    subject VARCHAR(120) NOT NULL,
    description TEXT,
    pass_percent NUMERIC(5, 2) NOT NULL DEFAULT 60,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    test_id INTEGER NOT NULL REFERENCES tests(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    points INTEGER NOT NULL DEFAULT 1 CHECK (points > 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE answers (
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE test_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    test_id INTEGER NOT NULL REFERENCES tests(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 0),
    max_score INTEGER NOT NULL CHECK (max_score > 0),
    percent NUMERIC(5, 2),
    grade INTEGER,
    passed BOOLEAN,
    comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE result_audit (
    id SERIAL PRIMARY KEY,
    result_id INTEGER,
    action VARCHAR(20) NOT NULL,
    old_score INTEGER,
    new_score INTEGER,
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION calculate_percent(p_score integer, p_max_score integer)
RETURNS NUMERIC(5, 2)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_max_score <= 0 THEN
        RETURN 0;
    END IF;

    RETURN ROUND((p_score::numeric / p_max_score::numeric) * 100, 2);
END;
$$;

CREATE OR REPLACE FUNCTION grade_from_percent(p_percent numeric)
RETURNS integer
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_percent >= 85 THEN
        RETURN 5;
    ELSIF p_percent >= 70 THEN
        RETURN 4;
    ELSIF p_percent >= 50 THEN
        RETURN 3;
    ELSE
        RETURN 2;
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION is_passed(p_percent numeric)
RETURNS boolean
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN p_percent >= 60;
END;
$$;

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION fill_result_fields()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_percent numeric(5, 2);
BEGIN
    v_percent = calculate_percent(NEW.score, NEW.max_score);
    NEW.percent = v_percent;
    NEW.grade = grade_from_percent(v_percent);
    NEW.passed = is_passed(v_percent);
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION audit_result_changes()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO result_audit(result_id, action, new_score)
        VALUES (NEW.id, 'INSERT', NEW.score);
    ELSIF TG_OP = 'UPDATE' AND OLD.score <> NEW.score THEN
        INSERT INTO result_audit(result_id, action, old_score, new_score)
        VALUES (NEW.id, 'UPDATE', OLD.score, NEW.score);
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO result_audit(result_id, action, old_score)
        VALUES (OLD.id, 'DELETE', OLD.score);
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$;

CREATE TRIGGER users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER tests_updated_at
BEFORE UPDATE ON tests
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER results_fill_fields
BEFORE INSERT OR UPDATE ON test_results
FOR EACH ROW EXECUTE FUNCTION fill_result_fields();

CREATE TRIGGER results_audit
AFTER INSERT OR UPDATE OR DELETE ON test_results
FOR EACH ROW EXECUTE FUNCTION audit_result_changes();

CREATE VIEW v_result_summary AS
SELECT
    tr.id,
    u.name AS student_name,
    u.email,
    t.title AS test_title,
    t.subject,
    tr.score,
    tr.max_score,
    tr.percent,
    tr.grade,
    tr.passed,
    tr.created_at
FROM test_results tr
JOIN users u ON u.id = tr.user_id
JOIN tests t ON t.id = tr.test_id;

CREATE VIEW v_test_average AS
SELECT
    t.id AS test_id,
    t.title,
    COUNT(tr.id) AS attempts_count,
    ROUND(AVG(tr.percent), 2) AS average_percent,
    ROUND(AVG(tr.grade), 2) AS average_grade
FROM tests t
LEFT JOIN test_results tr ON tr.test_id = t.id
GROUP BY t.id, t.title;

CREATE VIEW v_recent_results AS
SELECT *
FROM v_result_summary
ORDER BY created_at DESC
LIMIT 10;

CREATE OR REPLACE PROCEDURE create_demo_test(p_title text, p_subject text)
LANGUAGE plpgsql
AS $$
DECLARE
    v_test_id integer;
BEGIN
    INSERT INTO tests(title, subject, description)
    VALUES (p_title, p_subject, 'Демонстрационный тест для курсовой работы')
    RETURNING id INTO v_test_id;

    INSERT INTO questions(test_id, text, points)
    VALUES
        (v_test_id, 'Что показывает HTTP-метод GET?', 1),
        (v_test_id, 'Для чего нужен LocalStorage?', 1),
        (v_test_id, 'Что делает React-компонент?', 1);
END;
$$;

CREATE OR REPLACE PROCEDURE register_test_result(
    p_user_id integer,
    p_test_id integer,
    p_score integer,
    p_max_score integer
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO test_results(user_id, test_id, score, max_score)
    VALUES (p_user_id, p_test_id, p_score, p_max_score);
END;
$$;

CREATE OR REPLACE PROCEDURE clear_demo_data()
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM result_audit;
    DELETE FROM test_results;
    DELETE FROM answers;
    DELETE FROM questions;
    DELETE FROM tests;
    DELETE FROM users;
END;
$$;

INSERT INTO users(name, email, password_hash, age, role)
VALUES
    ('Анна Смирнова', 'anna@example.com', '$2y$12$.xobTZdpoLR5zPLDiqrM8eR6IBnEdIsNiDPvFNggjUo8ETJaDy82.', 20, 'student'),
    ('Игорь Петров', 'igor@example.com', '$2y$12$.xobTZdpoLR5zPLDiqrM8eR6IBnEdIsNiDPvFNggjUo8ETJaDy82.', 21, 'student'),
    ('Мария Иванова', 'maria.teacher@example.com', '$2y$12$.xobTZdpoLR5zPLDiqrM8eR6IBnEdIsNiDPvFNggjUo8ETJaDy82.', 35, 'teacher'),
    ('Администратор', 'admin@example.com', '$2y$12$.xobTZdpoLR5zPLDiqrM8eR6IBnEdIsNiDPvFNggjUo8ETJaDy82.', 30, 'admin');

INSERT INTO tests(title, subject, description, pass_percent, created_by)
VALUES
    ('Основы HTML и CSS', 'Веб-разработка', 'Проверка базовой разметки и стилей.', 60, 3),
    ('JavaScript и LocalStorage', 'Веб-разработка', 'Вопросы по событиям, массивам и локальному хранилищу.', 60, 3);

INSERT INTO questions(test_id, text, points)
VALUES
    (1, 'Какой тег используется для главного заголовка?', 1),
    (1, 'Где подключается внешний CSS-файл?', 1),
    (2, 'Какой метод сохраняет значение в LocalStorage?', 1),
    (2, 'Какой хук React удобно использовать для загрузки данных?', 1);

INSERT INTO answers(question_id, text, is_correct)
VALUES
    (1, 'h1', true),
    (1, 'title', false),
    (2, 'В head через link', true),
    (2, 'Только внутри body', false),
    (3, 'localStorage.setItem', true),
    (3, 'localStorage.push', false),
    (4, 'useEffect', true),
    (4, 'useClass', false);

CALL register_test_result(1, 1, 2, 2);
CALL register_test_result(2, 1, 1, 2);
CALL register_test_result(1, 2, 2, 2);
