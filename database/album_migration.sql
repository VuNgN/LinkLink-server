-- Migration: Tạo bảng albums và album_images cho chức năng album ảnh

CREATE TABLE albums (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE album_images (
    album_id INTEGER REFERENCES albums(id) ON DELETE CASCADE,
    image_id VARCHAR(255) REFERENCES images(filename) ON DELETE CASCADE,
    user_id VARCHAR(50) REFERENCES users(username),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (album_id, image_id)
); 