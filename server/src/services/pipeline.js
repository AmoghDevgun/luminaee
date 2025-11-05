import { spawn } from 'child_process'
import path from 'path'
import fs from 'fs'

const ROOT = path.resolve(process.cwd(), '..')
const OUTPUT_DIR = path.join(ROOT, 'output')

export function runPipeline(username) {
  return new Promise((resolve, reject) => {
    const py = spawn('python3', ['main.py'], { cwd: ROOT })
    let stderr = ''
    py.stderr.on('data', d => { stderr += d.toString() })
    py.on('error', reject)
    py.on('close', code => {
      if (code === 0) resolve(true)
      else reject(new Error(stderr || `Exited ${code}`))
    })
    py.stdin.write(`${username}\n`)
    py.stdin.end()
  })
}

export function getRankedPath(username) {
  return path.join(OUTPUT_DIR, `${username}_leads_ranked.json`)
}

export function readRanked(username) {
  const p = getRankedPath(username)
  if (!fs.existsSync(p)) return null
  return JSON.parse(fs.readFileSync(p, 'utf-8'))
}


