-- 为现有表添加 tenant_id 字段

-- 测试套件表添加 tenant_id
ALTER TABLE `test_suites` ADD COLUMN `tenant_id` INT NULL COMMENT '租户ID' AFTER `project_id`;
ALTER TABLE `test_suites` ADD INDEX `idx_tenant_id` (`tenant_id`);

-- 测试用例表添加 tenant_id
ALTER TABLE `test_cases` ADD COLUMN `tenant_id` INT NULL COMMENT '租户ID' AFTER `suite_id`;
ALTER TABLE `test_cases` ADD INDEX `idx_tenant_id` (`tenant_id`);

-- 测试计划表添加 tenant_id
ALTER TABLE `test_plans` ADD COLUMN `tenant_id` INT NULL COMMENT '租户ID' AFTER `project_id`;
ALTER TABLE `test_plans` ADD INDEX `idx_tenant_id` (`tenant_id`);

-- 测试环境表添加 tenant_id
ALTER TABLE `test_environments` ADD COLUMN `tenant_id` INT NULL COMMENT '租户ID' AFTER `project_id`;
ALTER TABLE `test_environments` ADD INDEX `idx_tenant_id` (`tenant_id`);

-- 缺陷表添加 tenant_id
ALTER TABLE `defects` ADD COLUMN `tenant_id` INT NULL COMMENT '租户ID' AFTER `project_id`;
ALTER TABLE `defects` ADD INDEX `idx_tenant_id` (`tenant_id`);
