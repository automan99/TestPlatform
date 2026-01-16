-- 创建租户表
CREATE TABLE IF NOT EXISTS `tenants` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '租户ID',
  `name` VARCHAR(100) NOT NULL COMMENT '租户名称',
  `code` VARCHAR(50) NOT NULL COMMENT '租户代码',
  `description` TEXT COMMENT '描述',
  `logo` VARCHAR(255) COMMENT 'Logo URL',
  `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态: active-激活, suspended-暂停, expired-过期',
  `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否激活',
  `max_users` INT DEFAULT 10 COMMENT '最大用户数',
  `max_projects` INT DEFAULT 5 COMMENT '最大项目数',
  `max_storage_gb` INT DEFAULT 10 COMMENT '最大存储空间(GB)',
  `expire_date` DATE COMMENT '过期日期',
  `settings` JSON COMMENT '租户设置',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` INT COMMENT '创建人ID',
  `updated_by` INT COMMENT '更新人ID',
  `is_deleted` BOOLEAN DEFAULT FALSE COMMENT '是否删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_name` (`name`),
  UNIQUE KEY `uk_code` (`code`),
  KEY `idx_status` (`status`),
  KEY `idx_is_active` (`is_active`),
  KEY `idx_is_deleted` (`is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='租户表';

-- 创建租户用户关联表
CREATE TABLE IF NOT EXISTS `tenant_users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tenant_id` INT NOT NULL COMMENT '租户ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `role` VARCHAR(20) DEFAULT 'member' COMMENT '角色: owner-所有者, admin-管理员, member-成员',
  `is_default` BOOLEAN DEFAULT FALSE COMMENT '是否默认租户',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `is_deleted` BOOLEAN DEFAULT FALSE COMMENT '是否删除',
  PRIMARY KEY (`id`),
  KEY `idx_tenant_id` (`tenant_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_role` (`role`),
  UNIQUE KEY `uk_tenant_user` (`tenant_id`, `user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='租户用户关联表';

-- 插入测试租户
INSERT INTO `tenants` (`name`, `code`, `description`, `status`, `is_active`, `max_users`, `max_projects`, `max_storage_gb`, `expire_date`, `settings`)
VALUES ('测试租户', 'test', '用于测试的默认租户', 'active', TRUE, 100, 50, 100, DATE_ADD(CURDATE(), INTERVAL 10 YEAR), '{"allow_register": true, "default_locale": "zh-CN"}')
ON DUPLICATE KEY UPDATE `name` = `name`;
