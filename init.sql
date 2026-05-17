-- Initialize PinPoint Database Schema

-- Deliveries table
CREATE TABLE IF NOT EXISTS deliveries (
    id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    courier_id VARCHAR(50),
    address TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    items JSONB,
    estimated_time INTEGER NOT NULL,
    actual_time INTEGER,
    created_at BIGINT NOT NULL,
    picked_up_at BIGINT,
    delivered_at BIGINT
);

-- Buildings table
CREATE TABLE IF NOT EXISTS buildings (
    id VARCHAR(50) PRIMARY KEY,
    address TEXT NOT NULL UNIQUE,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    building_type VARCHAR(20) NOT NULL,
    floors INTEGER NOT NULL,
    has_elevator BOOLEAN NOT NULL DEFAULT false,
    elevator_type VARCHAR(20),
    difficulty_score INTEGER NOT NULL DEFAULT 1,
    access_notes TEXT
);

-- Building entrances table
CREATE TABLE IF NOT EXISTS building_entrances (
    id VARCHAR(50) PRIMARY KEY,
    building_id VARCHAR(50) NOT NULL REFERENCES buildings(id) ON DELETE CASCADE,
    entrance_number VARCHAR(10) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    is_confirmed BOOLEAN NOT NULL DEFAULT false,
    confirmation_count INTEGER NOT NULL DEFAULT 0,
    last_confirmed BIGINT,
    access_method VARCHAR(20) NOT NULL
);

-- Domofon codes table
CREATE TABLE IF NOT EXISTS domofon_codes (
    id VARCHAR(50) PRIMARY KEY,
    building_id VARCHAR(50) NOT NULL REFERENCES buildings(id) ON DELETE CASCADE,
    entrance_number VARCHAR(10) NOT NULL,
    code VARCHAR(50) NOT NULL,
    code_type VARCHAR(20) NOT NULL,
    is_verified BOOLEAN NOT NULL DEFAULT false,
    verification_count INTEGER NOT NULL DEFAULT 0,
    last_verified BIGINT,
    added_by VARCHAR(50) NOT NULL,
    notes TEXT
);

-- Locations table
CREATE TABLE IF NOT EXISTS locations (
    id VARCHAR(50) PRIMARY KEY,
    courier_id VARCHAR(50) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    accuracy REAL,
    altitude DOUBLE PRECISION,
    timestamp BIGINT NOT NULL
);

-- Location points table (for trajectory)
CREATE TABLE IF NOT EXISTS location_points (
    id VARCHAR(50) PRIMARY KEY,
    delivery_id VARCHAR(50) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    accuracy REAL,
    altitude DOUBLE PRECISION,
    timestamp BIGINT NOT NULL,
    speed REAL,
    activity_type VARCHAR(20) NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_deliveries_courier ON deliveries(courier_id);
CREATE INDEX IF NOT EXISTS idx_deliveries_status ON deliveries(status);
CREATE INDEX IF NOT EXISTS idx_buildings_address ON buildings(address);
CREATE INDEX IF NOT EXISTS idx_building_entrances_building ON building_entrances(building_id);
CREATE INDEX IF NOT EXISTS idx_domofon_codes_building ON domofon_codes(building_id);
CREATE INDEX IF NOT EXISTS idx_locations_courier ON locations(courier_id);
CREATE INDEX IF NOT EXISTS idx_location_points_delivery ON location_points(delivery_id);

-- Insert sample data
INSERT INTO buildings (id, address, latitude, longitude, building_type, floors, has_elevator, elevator_type, difficulty_score, access_notes)
VALUES 
    ('building_1', 'Toshkent, Amir Temur ko''chasi 15', 41.3111, 69.2797, 'MODERN', 16, true, 'CHIP_REQUIRED', 3, 'Lift faqat chip bilan ishlaydi')
ON CONFLICT (id) DO NOTHING;
