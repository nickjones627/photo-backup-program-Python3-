## Photo backup and recovery program

A simple program that allows you to upload, view, and delete photos to / from a sql database.

## To use the program you will need to setup a sql database to store the data.

```sql
CREATE TABLE photos (
    user_id INT NOT NULL,
    photo_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    photo LONGBLOB NOT NULL
);
```
```sql
CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
```
once you complete this step simply create an account and upload your images using the exact file path.
