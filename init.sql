CREATE DATABASE Bank

ALTER DATABASE bank
SET READ_COMMITTED_SNAPSHOT ON WITH ROLLBACK IMMEDIATE;

ALTER DATABASE bank
SET ALLOW_SNAPSHOT_ISOLATION ON;