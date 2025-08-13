import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database operations
export const supabaseOperations = {
  // Get all combos with votes
  async getCombos(limit = 10) {
    const { data, error } = await supabase
      .from('brand_combos')
      .select('*')
      .order('votes', { ascending: false })
      .limit(limit)
    
    if (error) throw error
    return data
  },

  // Create a new combo
  async createCombo(combo) {
    const { data, error } = await supabase
      .from('brand_combos')
      .insert([combo])
      .select()
    
    if (error) throw error
    return data[0]
  },

  // Vote for a combo
  async voteForCombo(comboId) {
    const { data, error } = await supabase
      .rpc('increment_votes', { combo_id: comboId })
    
    if (error) throw error
    return data
  },

  // Get combo statistics
  async getStats() {
    const { data, error } = await supabase
      .from('brand_combos')
      .select('votes')
    
    if (error) throw error
    
    const totalCombos = data.length
    const totalVotes = data.reduce((sum, combo) => sum + combo.votes, 0)
    
    return { totalCombos, totalVotes }
  }
}