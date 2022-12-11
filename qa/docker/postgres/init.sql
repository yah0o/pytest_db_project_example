SELECT 'CREATE DATABASE cats'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'cats')