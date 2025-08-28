-- pages
-- depends: 20241224_01_xuN6n-delete-upload-set-on-last-picture-trg-statement  20250102_01_EElhA-rm-cameras

-- Custom HTML pages
CREATE TABLE pages(
	name VARCHAR(50) NOT NULL,
	lang VARCHAR(10) NOT NULL,
	content TEXT NOT NULL,
	PRIMARY KEY (name, lang)
);
