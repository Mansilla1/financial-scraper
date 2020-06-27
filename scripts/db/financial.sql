CREATE EXTENSION postgis;


CREATE TABLE public.nemo_tech (
	id serial NOT NULL,
	nemo varchar(255) NOT NULL,
	green_bonus float8 NULL,
	djsi float8 NULL,
	etfs_foreign varchar(1) NOT NULL,
	isin varchar(255) NOT NULL,
	coin varchar(10) NOT NULL,
	amount float8 NULL,
	weight float8 NULL,
	close_price float8 NULL,
	buy_price float8 NULL,
	sell_price float8 NULL,
	traded_units float8 NULL,
	variant float8 NULL,
	created_at timestamptz NOT NULL,
	status varchar(25) NOT NULL,
	updated_at timestamptz NOT NULL,
	CONSTRAINT nemo_tech_pkey PRIMARY KEY (id)
);
