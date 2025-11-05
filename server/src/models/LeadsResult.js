import mongoose from 'mongoose'

const leadsResultSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true, index: true },
  sourceUsername: { type: String, required: true, index: true },
  leadsRanked: { type: Array, default: [] },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
})

leadsResultSchema.index({ userId: 1, sourceUsername: 1 }, { unique: false })

leadsResultSchema.pre('save', function(next) {
  this.updatedAt = new Date()
  next()
})

export default mongoose.model('LeadsResult', leadsResultSchema)


