-- 快速添加管理员用户脚本
USE ticket_system;

-- 先删除可能存在的Admin用户
DELETE FROM User WHERE username = 'Admin';

-- 插入管理员用户
INSERT INTO User (username, password, real_name, security_question, security_answer, is_admin) 
VALUES ('Admin', '23336326', '系统管理员', '你的角色是什么？', '管理员', TRUE);

-- 确认插入成功
SELECT user_id, username, real_name, is_admin FROM User WHERE username = 'Admin';

COMMIT;

