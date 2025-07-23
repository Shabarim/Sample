use bank

CREATE TABLE accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    pin VARCHAR(4) NOT NULL,
    balance DECIMAL(65,2) DEFAULT 0.00
);

CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT,
    type VARCHAR(20),
    amount DECIMAL(65,2),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);


DESCRIBE transactions

DESCRIBE accounts

Select * from transactions

DELETE FROM transactions;
DELETE FROM accounts;

ALTER TABLE transactions AUTO_INCREMENT = 1;
ALTER TABLE accounts AUTO_INCREMENT = 1;


