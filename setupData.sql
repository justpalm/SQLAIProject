INSERT INTO adress (address_id, street, state, city, zip_code) VALUES
(1, '123 Maple Street', 'UT', 'Provo', 84604),
(2, '456 Oak Road', 'CO', 'Denver', 80203),
(3, '789 Pine Avenue', 'AZ', 'Phoenix', 85004);

INSERT INTO pantry (pantry_id, address_id) VALUES
(1, 1),
(2, 2),
(3, 3);

INSERT INTO shelfs
    (shelf_id, pantry_id, food_name, quantity, best_by_date)
VALUES
(1, 1, 'White Rice', 5, '2028-06-30'),
(2, 1, 'Spaghetti', 3, '2027-09-15'),
(3, 1, 'Canned Black Beans', 8, '2028-03-01'),
(4, 2, 'Rolled Oats', 2, '2027-04-20'),
(5, 2, 'Canned Tomatoes', 6, '2028-01-10'),
(6, 3, 'Peanut Butter', 4, '2027-08-05'),
(7, 3, 'Honey', 1, NULL);

INSERT INTO cupboards
    (cupboard_id, pantry_id, food_name, quantity, best_by_date)
VALUES
(1, 1, 'All-Purpose Flour', 2, '2027-05-01'),
(2, 1, 'Granulated Sugar', 3, NULL),
(3, 2, 'Olive Oil', 1, '2027-07-12'),
(4, 2, 'Ground Coffee', 2, '2027-02-28'),
(5, 3, 'Crackers', 5, '2027-01-15'),
(6, 3, 'Canned Soup', 0, '2028-10-01');