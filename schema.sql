DROP TABLE IF EXISTS `permission`;

CREATE TABLE `permission` (
  `permission_id` int(11) NOT NULL AUTO_INCREMENT,
  `permission_codename` varchar(50) DEFAULT NULL,
  `permission_desc` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`permission_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_login` varchar(64) NOT NULL,
  `user_password` varchar(255) NOT NULL,
  `user_email` varchar(64) DEFAULT NULL,
  `user_status` varchar(16) NOT NULL DEFAULT 'active',
  `user_last_login` datetime NOT NULL,
  `last_billed` datetime DEFAULT NULL,
  `order_number` bigint(10) DEFAULT NULL,
  `last_invoice` bigint(10) DEFAULT NULL,
  `2co_status` varchar(16) DEFAULT NULL,
  `date_expire` datetime DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `user_permission`;

CREATE TABLE `user_permission` (
  `up_user_id` int(11) NOT NULL DEFAULT '0',
  `up_permission_id` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`up_user_id`,`up_permission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO permission (permission_codename,permission_desc) VALUES('user','authenticate user');