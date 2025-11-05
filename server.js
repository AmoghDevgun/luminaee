import express from 'express'
import cors from 'cors'
import { spawn } from 'child_process'
import fs from 'fs'
import path from 'path'

const app = express()
app.use(cors())
app.use(express.json({ limit: '1mb' }))

const ROOT = path.resolve(process.cwd())
const OUTPUT_DIR = path.join(ROOT, 'output')

function runPythonPipeline(username) {
  return new Promise((resolve, reject) => {
    const py = spawn('python3', ['main.py'], { cwd: ROOT })

    let stdout = ''
    let stderr = ''

    py.stdout.on('data', (d) => { stdout += d.toString() })
    py.stderr.on('data', (d) => { stderr += d.toString() })

    py.on('error', (err) => reject(err))
    py.on('close', (code) => {
      if (code === 0) return resolve({ stdout, stderr })
      return reject(new Error(`Pipeline exited with code ${code}: ${stderr}`))
    })

    // Provide username to the Python script (it prompts for input)
    py.stdin.write(`${username}\n`)
    py.stdin.end()
  })
}

app.post('/api/leads', async (req, res) => {
  try {
    const username = String((req.body && req.body.username) || '').trim()
    if (!username) return res.status(400).json({ error: 'username is required' })

    // Ensure output directory exists (Python also ensures it, but this is harmless)
    try { fs.mkdirSync(OUTPUT_DIR, { recursive: true }) } catch {}

    // Kick off pipeline
    await runPythonPipeline(username)

    // Read ranked results
    const rankedPath = path.join(OUTPUT_DIR, `${username}_leads_ranked.json`)
    if (!fs.existsSync(rankedPath)) {
      return res.status(202).json({
        status: 'processing',
        message: 'Processing completed but ranked file not found yet. Try again shortly.'
      })
    }

    const data = JSON.parse(fs.readFileSync(rankedPath, 'utf-8'))
    return res.json({ username, leads_ranked: data })
  } catch (err) {
    console.error(err)
    return res.status(500).json({ error: 'Internal Server Error', details: String(err.message || err) })
  }
})

// Increase server timeouts to allow long scraping
const server = app.listen(process.env.PORT || 3000, () => {
  console.log(`Server listening on port ${server.address().port}`)
})
server.setTimeout(1000 * 60 * 30)


