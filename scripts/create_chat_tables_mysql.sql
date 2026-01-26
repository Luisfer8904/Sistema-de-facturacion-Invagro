-- Tablas para chat inteligente
CREATE TABLE IF NOT EXISTS `inva-chat_sessions` (
  id VARCHAR(36) PRIMARY KEY,
  username VARCHAR(50),
  created_at TIMESTAMP NULL,
  updated_at TIMESTAMP NULL,
  INDEX idx_chat_sessions_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `inva-chat_messages` (
  id INT AUTO_INCREMENT PRIMARY KEY,
  session_id VARCHAR(36) NOT NULL,
  role VARCHAR(20) NOT NULL,
  content TEXT,
  created_at TIMESTAMP NULL,
  INDEX idx_chat_messages_session (session_id),
  CONSTRAINT fk_chat_messages_session FOREIGN KEY (session_id) REFERENCES `inva-chat_sessions`(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `inva-chat_summaries` (
  id INT AUTO_INCREMENT PRIMARY KEY,
  session_id VARCHAR(36) NOT NULL,
  summary TEXT,
  updated_at TIMESTAMP NULL,
  INDEX idx_chat_summaries_session (session_id),
  CONSTRAINT fk_chat_summaries_session FOREIGN KEY (session_id) REFERENCES `inva-chat_sessions`(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `inva-chat_audit` (
  id INT AUTO_INCREMENT PRIMARY KEY,
  session_id VARCHAR(36),
  username VARCHAR(50),
  question TEXT,
  tool_name VARCHAR(64),
  params_json TEXT,
  elapsed_ms INT,
  rows_returned INT,
  created_at TIMESTAMP NULL,
  INDEX idx_chat_audit_session (session_id),
  INDEX idx_chat_audit_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
