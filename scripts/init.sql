-- MySQL初始化脚本
-- 创建数据库和用户权限

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS ai_diary_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（如果不存在）
CREATE USER IF NOT EXISTS 'ai_diary_user'@'%' IDENTIFIED BY 'ai_diary_password';

-- 授予权限
GRANT ALL PRIVILEGES ON ai_diary_db.* TO 'ai_diary_user'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 使用数据库
USE ai_diary_db;

-- 创建用户表
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `email` VARCHAR(128) NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `telegram_chat_id` VARCHAR(50) NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建瞬间表
CREATE TABLE IF NOT EXISTS `moments` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `image_url` VARCHAR(1024) NULL,
  `user_text` TEXT NULL,
  `ai_description_origin` TEXT NULL COMMENT 'AI原始分析',
  `ai_description_final` TEXT NULL COMMENT '人工/规则修饰后文案',
  `image_verified` TINYINT(1) DEFAULT 0 COMMENT '图片校验/压缩标记',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `fk_moments_users_idx` (`user_id`),
  INDEX `idx_user_created` (`user_id`, `created_at`),
  CONSTRAINT `fk_moments_users`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建日记表
CREATE TABLE IF NOT EXISTS `daily_diaries` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `diary_date` DATE NOT NULL,
  `content_origin` TEXT NOT NULL,
  `content_final` TEXT NULL,
  `pushed_at` TIMESTAMP NULL DEFAULT NULL COMMENT '推送时间',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `last_updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `uk_user_date` (`user_id`, `diary_date`),
  CONSTRAINT `fk_daily_diaries_users1`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; 