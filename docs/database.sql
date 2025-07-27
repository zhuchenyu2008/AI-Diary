CREATE DATABASE IF NOT EXISTS ai_diary CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ai_diary;

CREATE TABLE `events` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT 1,
  `event_type` enum('text','image') NOT NULL,
  `content` text,
  `file_path` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `daily_summaries` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT 1,
  `summary_date` date NOT NULL,
  `content` text NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`summary_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Add indexes for performance
CREATE INDEX idx_events_created_at ON events(created_at);
CREATE INDEX idx_daily_summaries_summary_date ON daily_summaries(summary_date);
