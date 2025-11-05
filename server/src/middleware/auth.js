import jwt from 'jsonwebtoken'

export function requireAuth(req, res, next) {
  try {
    const header = req.headers.authorization || ''
    const token = header.startsWith('Bearer ') ? header.slice(7) : null
    if (!token) return res.status(401).json({ error: 'Unauthorized' })
    const secret = process.env.JWT_SECRET || 'dev_secret'
    const decoded = jwt.verify(token, secret)
    req.user = { id: decoded.id, email: decoded.email }
    return next()
  } catch (e) {
    return res.status(401).json({ error: 'Unauthorized' })
  }
}


