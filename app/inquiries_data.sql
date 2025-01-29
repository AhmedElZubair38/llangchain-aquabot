-- DROP TABLE IF EXISTS inquiries;

-- Create table inquiries
CREATE TABLE IF NOT EXISTS inquiries (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP NULL,
    user_id VARCHAR(50),
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(50),
    inquiry_type VARCHAR(50),
    program VARCHAR(100),
    timestamp TIMESTAMP NULL
);

-- Insert data into the inquiries table
INSERT INTO inquiries (date, user_id, name, email, phone, inquiry_type, program, timestamp) VALUES
('1970-01-01 04:00:46', '862,210,677', 'ahmed', 'ahmedgmail', '9,696', 'Contact Us', NULL, NULL),
('1970-01-01 04:00:46', '862,210,677', 'ahmed', 'ahmd', '9,696', 'Book a Class', 'Adults Program', NULL),
('1970-01-01 04:00:46', '862,210,677', 'a', 's', 'd', 'Contact Us', 'Ladies-Only Aqua Fitness', NULL),
('1970-01-01 04:00:46', '862,210,677', 'ja', 'ls', 'ms', 'Book a Class', 'Kids Program', NULL),
('1970-01-01 04:00:46', '862,210,677', 'ah', 'm', 'ss', 'Book a Class', 'Adults Program', NULL),
('1970-01-01 04:00:46', '5,005,650,329', 'Abdul', 'Ahal@gaka.com', '838,382', 'Book a Class', 'Special Needs Program', NULL),
('1970-01-01 04:00:46', '862,210,677', 'Ahmed Elzubair', 'ahmed.elzubairy@gmail.com', '0507705229', 'Book a Class', 'Special Needs Program', NULL),
('1970-01-01 04:00:46', '862,210,677', 'The', 'Fig', 'Thy', 'Book a Class', 'Adults Program', NULL),
('1970-01-01 04:00:46', '862,210,677', 'ha', 'Ha', 'H', 'Contact Us', NULL, NULL),
('1970-01-01 04:00:46', '862,210,677', 'Ahmed', 'He', 'Hhh', 'Book a Class', 'Adults Program', NULL),
(NULL, '862210677', 'hftghfh', 'dgjdgj', 'fghfgh', 'Book a Class', 'Kids Program', '2025-01-27 10:52:55.946286'),
(NULL, '862210677', 'Mohammad ElZubair', 'moh1@gmail.com', '0507705228', 'Book a Class', 'Baby & Toddler Program', '2025-01-27 13:46:46.786070');


SELECT * FROM inquiries;