import express from 'express'
import cors from 'cors'
import authRoutes from './routes/auth.js'
import leadsRoutes from './routes/leads.js'
import { connectDB } from './config/db.js'
import { config } from './config/env.js'

const app = express()
app.use(cors({ origin: '*', credentials: false }))
app.use(express.json({ limit: '1mb' }))

connectDB().then(() => console.log('MongoDB connected')).catch(err => { console.error('Mongo error', err); process.exit(1) })

app.get('/health', (req, res) => res.json({ ok: true }))
app.use('/api/auth', authRoutes)
app.use('/api/leads', leadsRoutes)

const server = app.listen(config.PORT, () => {
  console.log(`API listening on ${config.PORT}`)
})
server.setTimeout(1000 * 60 * 30)


