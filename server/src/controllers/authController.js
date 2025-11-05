import bcrypt from 'bcryptjs'
import jwt from 'jsonwebtoken'
import User from '../models/User.js'
import { config } from '../config/env.js'

export async function register(req, res) {
  try {
    const { email, password } = req.body || {}
    if (!email || !password) return res.status(400).json({ error: 'email and password required' })
    const existing = await User.findOne({ email: email.toLowerCase().trim() })
    if (existing) return res.status(409).json({ error: 'email already registered' })
    const passwordHash = await bcrypt.hash(password, 10)
    const user = await User.create({ email: email.toLowerCase().trim(), passwordHash })
    return res.json({ id: user._id, email: user.email })
  } catch (e) {
    return res.status(500).json({ error: 'registration failed' })
  }
}

export async function login(req, res) {
  try {
    const { email, password } = req.body || {}
    if (!email || !password) return res.status(400).json({ error: 'email and password required' })
    const user = await User.findOne({ email: email.toLowerCase().trim() })
    if (!user) return res.status(401).json({ error: 'invalid credentials' })
    const ok = await bcrypt.compare(password, user.passwordHash)
    if (!ok) return res.status(401).json({ error: 'invalid credentials' })
    const token = jwt.sign({ id: user._id.toString(), email: user.email }, config.JWT_SECRET, { expiresIn: '7d' })
    return res.json({ token })
  } catch (e) {
    return res.status(500).json({ error: 'login failed' })
  }
}

export async function me(req, res) {
  return res.json({ id: req.user.id, email: req.user.email })
}


