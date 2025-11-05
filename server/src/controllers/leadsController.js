import LeadsResult from '../models/LeadsResult.js'
import { runPipeline, readRanked } from '../services/pipeline.js'

export async function generateLeads(req, res) {
  try {
    const username = String((req.body && req.body.username) || '').trim().toLowerCase()
    if (!username) return res.status(400).json({ error: 'username is required' })

    await runPipeline(username)
    const data = readRanked(username)
    if (!data) return res.status(202).json({ status: 'processing' })

    const doc = await LeadsResult.findOneAndUpdate(
      { userId: req.user.id, sourceUsername: username },
      { $set: { leadsRanked: data, updatedAt: new Date() }, $setOnInsert: { createdAt: new Date() } },
      { new: true, upsert: true }
    )

    return res.json({ username, leads_ranked: doc.leadsRanked, id: doc._id })
  } catch (e) {
    return res.status(500).json({ error: 'pipeline failed', details: String(e.message || e) })
  }
}


