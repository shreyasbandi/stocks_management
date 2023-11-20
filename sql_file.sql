create table stocks(
stock_id varchar(100) not null primary key,
stock_name varchar(25),
market_cap int,
price float,
sector varchar(50)
);


INSERT INTO stocks (stock_id,stock_name,market_cap,sector)
VALUES
('GOOG','Google',169,'Technology'),
('IDEA','Idea',2687,'Telecommunication'),
('AAPL','Apple',2942,'Technology'),
('AMZN','Amazon',148,'Technology'),
('LMT','Lockheed Martin',1104,'Industrials'),
('NVDA','NVIDIA Corporation',1208,'Technology'),
('ADANIPORTS.NS','Adabi_ports',1764,'Energy'),
('PAC','Grupo Aeroportuario',665,'Aerospace'),
('ZS','Zscaler, Inc',276,'Telecommunication');

create table users(
user_id int primary key auto_increment ,
name varchar(50) not null,
password varchar(50) not null,
email varchar(300) not null
);

alter table users add constraint unique (email);


create table holdings(
user_id int,
num_count int ,
stock_id varchar(25),
primary key (user_id,stock_id),
foreign key (user_id) references users(user_id)
on delete cascade,
foreign key (stock_id) references stocks(stock_id)
on delete cascade
);


create table history(
	history_id int primary key auto_increment ,
    net_income int ,
    sold_date date,
    user_id int,
    stock_id varchar(25),
    num_count int
);

alter table history modify net_income float;

create table block_history(
block_id int primary key auto_increment,
user_id int ,
s_id int,
foreign key(s_id) references stock_exchange(supervisior_id)
on delete cascade
);

create table block_history_reason(
block_id int primary key,
reason varchar(150) not null
);




-- call block_user(2,1,'fraud transaction');

create table stock_exchange(
supervisior_id int primary key not null,
supervisior_name varchar(50) not null
);


DELIMITER //
CREATE FUNCTION get_amount(stk varchar(25))
RETURNS float
DETERMINISTIC
READS SQL DATA
BEGIN
	declare result float;
    select price into result from stocks where stock_id=stk;
    RETURN result;
END //
DELIMITER ;

-- use to insert data into users table ie for signup
DELIMITER &&
CREATE PROCEDURE insert_user(in mail varchar(50), in firstname varchar(50), in pass varchar(300))
BEGIN
	insert into users (name,password,email) values (firstname,pass,mail);
END &&
DELIMITER;

DELIMITER &&
CREATE PROCEDURE buy_stocks(in userid int,in stockid varchar(25),in numcount int)
BEGIN
	insert into holdings (user_id,num_count,stock_id) values (userid,numcount,stockid) on duplicate key update num_count=num_count+numcount;
END &&
DELIMITER ;


DELIMITER &&
CREATE PROCEDURE show_portfolio(in userid int)
BEGIN
	 select h.user_id,h.num_count,h.stock_id,s.price from holdings h inner join stocks s on s.stock_id=h.stock_id where h.user_id=userid;
END &&
DELIMITER ;

DELIMITER &&
CREATE PROCEDURE history_insert(in result float ,in useid int ,in sid varchar(25) ,in num int)
BEGIN
	 INSERT INTO history (net_income, sold_date, user_id, stock_id, num_count) VALUES (result,current_date(),useid,sid,num);
END &&
DELIMITER ;

DELIMITER //

CREATE TRIGGER delete_user_before_insert 
AFTER INSERT ON block_history 
FOR EACH ROW 
BEGIN
    DELETE FROM users WHERE user_id = NEW.user_id;
END
//

DELIMITER ;

DELIMITER //
create procedure block_user(in userid int,in sid int,in reason varchar(150))
begin
	insert into block_history (user_id,s_id) values (userid,sid);
    insert into block_history_reason(block_id,reason) values (userid,reason);
end //
DELIMITER ;




call history_insert(10.0,1,'AAPL',10);
select * from history;
describe holdings;
select * from holdings;
SELECT CURRENT_DATE() ;