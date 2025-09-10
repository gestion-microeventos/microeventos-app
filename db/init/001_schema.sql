CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT DEFAULT 'organizer'
);

CREATE TABLE IF NOT EXISTS events (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  event_date TIMESTAMP NOT NULL,
  category TEXT,
  price NUMERIC(12,2) DEFAULT 0,
  available_tickets INT DEFAULT 0,
  creator_id INT
);

CREATE TABLE IF NOT EXISTS tickets (
  id SERIAL PRIMARY KEY,
  event_id INT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  buyer_name TEXT NOT NULL,
  buyer_email TEXT,
  price NUMERIC(12,2) NOT NULL,
  sold_at TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE (event_id, buyer_email, buyer_name)
);

CREATE TABLE IF NOT EXISTS attendance (
  id SERIAL PRIMARY KEY,
  ticket_id INT NOT NULL UNIQUE REFERENCES tickets(id) ON DELETE CASCADE,
  checked_in_at TIMESTAMP NOT NULL DEFAULT NOW()
);
