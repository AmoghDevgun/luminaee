import dotenv from 'dotenv'
dotenv.config()

export const config = {
  MONGO_URI: process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/leadsdb',
  PORT: process.env.PORT || 4000,
  JWT_SECRET: process.env.JWT_SECRET || 'dev_secret',
}


