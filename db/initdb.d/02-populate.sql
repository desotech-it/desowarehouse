INSERT INTO `product` (`name`, `price`, `width`, `height`, `depth`, `weight`)
VALUES
	('Oral-B iO 9N', 230.00, 181, 259, 99, 980),
	('Gillette Fusion Lamette Da Barba', 36.99, 110, 252, 24, 140),
	('Aerosol Portatile Silenzioso', 33.84, 146, 66, 151, 250),
	('Giubotto di pelle per moto', 189.00, 400, 600, 200, 3000),
	('Casco AGV K6-S', 479.95, 150, 300, 300, 1500),
	('Marvel\'s Spider-Man Miles Morales', 44.95, 130, 170, 15, 10),
	('LG 27GP950 UltraGear Gaming Monitor 27" UltraHD', 753.82, 609, 291, 574, 7900),
	('Giubbotto Riscaldato 10000mAh', 63.17, 425, 660, 300, 800),
	('Bomboletta Graffiti', 7.00, 65, 200, 65, 410),
	('Design Patterns: Elements of Reusable Object-Oriented Software', 18.92, 194, 237, 264, 885);

INSERT INTO `user` (`first_name`, `last_name`, `mail`, `birthdate`, `password`)
VALUES
	('Gianluca', 'Recchia', 'g.recchia@desolabs.com', '1997-09-16', SHA2('grecchia', 0)),
	('Cristian', 'Gramegna', 'c.gramegna@desolabs.com', '2005-05-02', SHA2('cgramegna', 0)),
	('Francesco', 'Grimaldi', 'f.grimaldi@desolabs.com', '1997-05-09', SHA2('fgrimaldi', 0));

INSERT INTO `inventory` (`product_id`,`quantity`)
VALUES
	(1, FLOOR(RAND()*(10)+1)),
	(2, FLOOR(RAND()*(10)+1)),
	(3, FLOOR(RAND()*(10)+1)),
	(4, FLOOR(RAND()*(10)+1)),
	(5, FLOOR(RAND()*(10)+1)),
	(6, FLOOR(RAND()*(10)+1)),
	(7, FLOOR(RAND()*(10)+1)),
	(8, FLOOR(RAND()*(10)+1)),
	(9, FLOOR(RAND()*(10)+1)),
	(10, FLOOR(RAND()*(10)+1));

INSERT INTO `order` (`datetime`)
VALUES
	('2024-01-18'),
	('2023-12-31'),
	('2022-05-11');

INSERT INTO `order_product` (`order_id`, `product_id`, `quantity`)
VALUES
	(1, 1, 1),
	(2, 4, 1),
	(2, 5, 2),
	(3, 7, 5);

INSERT INTO `role` (`name`)
VALUES
	('admin'),
	('warehouse');

INSERT INTO `user_role` (`user_id`, `role_id`)
VALUES
	(3, 1),
	(2, 2);

INSERT INTO `order` (`id`,`user_id`)
VALUES 
	(1,1),
	(2,2),
	(3,3);

INSERT INTO `order_product` (`order_id`,`product_id`,`quantity`)
VALUES
	(1,1,1),
	(2,2,1),
	(3,3,1);