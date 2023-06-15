CREATE TABLE `announcements` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `title` varchar(50) NOT NULL,
    `body` varchar(400) NOT NULL,
    `url` varchar(200) DEFAULT NULL,
    `image` varchar(200) DEFAULT NULL,
    `published_at` DATETIME DEFAULT NULL,
    `createdAt` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,
    `updatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1
