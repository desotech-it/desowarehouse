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

INSERT INTO `order` (`datetime`, `user_id`)
VALUES
	('2024-01-18', 1),
	('2023-12-31', 2),
	('2022-05-11', 3),
	('2023-06-10', 1),
	('2024-05-17', 2),
	('2021-01-02', 3),
	('2020-08-09', 1),
	('2023-10-22', 2),
	('2021-10-11', 3);

INSERT INTO `order_product` (`order_id`, `product_id`, `quantity`)
VALUES
    (1, 1, 3),
    (1, 2, 2),
    (1, 3, 4),
    (1, 4, 5),
    (2, 5, 1),
    (2, 6, 2),
    (2, 7, 3),
    (2, 8, 4),
    (3, 9, 5),
    (3, 10, 1),
    (3, 1, 2),
    (3, 2, 3),
    (4, 3, 4),
    (4, 4, 5),
    (4, 5, 1),
    (4, 6, 2),
    (5, 7, 3),
    (5, 8, 4),
    (5, 9, 5),
    (5, 10, 1),
    (6, 1, 2),
    (6, 2, 3),
    (6, 3, 4),
    (6, 4, 5),
    (7, 5, 1),
    (7, 6, 2),
    (7, 7, 3),
    (7, 8, 4),
    (8, 9, 5),
    (8, 10, 1),
    (8, 1, 2),
    (8, 2, 3),
    (1, 5, 4),
    (1, 6, 5),
    (2, 9, 1),
    (2, 10, 2),
    (3, 5, 3),
    (3, 6, 4),
    (4, 7, 5),
    (4, 8, 1);

INSERT INTO `role` (`name`)
VALUES
	('admin'),
	('warehouse');

INSERT INTO `user_role` (`user_id`, `role_id`)
VALUES
	(3, 1),
	(2, 2);
