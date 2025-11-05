import { Router } from 'express'
import { requireAuth } from '../middleware/auth.js'
import { generateLeads } from '../controllers/leadsController.js'

const router = Router()
router.post('/', requireAuth, generateLeads)

export default router


