import { memo, useState } from 'react'
import { MessageSquareText, X, Send, Sparkles, Bot, User, Mic, Volume2 } from 'lucide-react'

interface Props {
  isOpen: boolean
  onClose: () => void
}

interface Message {
  id: string
  sender: 'user' | 'ai'
  text: string
  timestamp: string
}

const QUICK_QUESTIONS = [
  '💧 How much water does my Cotton crop need today?',
  '🐛 Is Whitefly threat high in Gujarat right now?',
  '📈 What is the best price for Groundnut in APMC?',
  '🧪 What fertilizer should I apply before rain?',
]

export const AIAssistantModal = memo(function AIAssistantModal({ isOpen, onClose }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'ai',
      text: 'Namaste Farmer! 👋 I am your AgriNova AI Assistant. I have analyzed your 3.5-acre Cotton field in Anand (Root Moisture 42.8%, Soil Health 94%). How can I help you today?',
      timestamp: 'Just now',
    },
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)

  if (!isOpen) return null

  const handleSend = (queryText?: string) => {
    const textToSend = queryText || input
    if (!textToSend.trim()) return

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }

    setMessages((prev) => [...prev, userMsg])
    if (!queryText) setInput('')
    setIsTyping(true)

    // Simulate AI agronomic response
    setTimeout(() => {
      let replyText = `Based on your live SoilPulse™ IoT sensor telemetry (pH 7.8, NPK optimal): For your Cotton crop at 45 DAS, keep root moisture above 35%. Since rain is expected tomorrow (27.4mm), delay chemical sprays by 48h.`
      
      if (textToSend.toLowerCase().includes('water') || textToSend.toLowerCase().includes('irrigate')) {
        replyText = '💧 Your root-zone moisture is currently 42.8%. Apply 22 mm drip irrigation today before 11:00 AM to prevent peak ET0 evapotranspiration loss.'
      } else if (textToSend.toLowerCase().includes('pest') || textToSend.toLowerCase().includes('whitefly')) {
        replyText = '🐛 Whitefly nymph count is low (<2/leaf). Inspect leaf undersides this evening. Apply organic Neem oil (5ml/L) if rain delays.'
      } else if (textToSend.toLowerCase().includes('mandi') || textToSend.toLowerCase().includes('price')) {
        replyText = '📈 Cotton (Kapas) is trading at ₹6,880/qtl (+2.4%) in Ahmedabad APMC. Demand is high; we recommend selling 40% of harvest now.'
      }

      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: replyText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }

      setMessages((prev) => [...prev, aiMsg])
      setIsTyping(false)
    }, 700)
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-md flex items-center justify-center p-4 animate-fade-in">
      <div className="bg-white rounded-3xl max-w-lg w-full h-[580px] shadow-2xl border border-emerald-200 flex flex-col justify-between overflow-hidden relative animate-slide-up text-slate-900">
        
        {/* Header */}
        <div className="p-4 bg-gradient-to-r from-emerald-700 via-teal-700 to-emerald-800 text-white flex items-center justify-between shadow-md">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-white/20 border border-white/30 flex items-center justify-center font-bold">
              <Bot className="w-6 h-6 text-emerald-200 animate-bounce" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h3 className="text-base font-black text-white">AgriNova AI Kisan Assistant</h3>
                <Sparkles className="w-4 h-4 text-amber-300 animate-pulse" />
              </div>
              <p className="text-[10px] text-emerald-200 font-semibold">24/7 Precision Agronomic Advisory · Multilingual</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-white transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Message Log */}
        <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-slate-50">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start gap-2.5 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold ${
                msg.sender === 'user' ? 'bg-emerald-600 text-white' : 'bg-amber-100 text-amber-900 border border-amber-300'
              }`}>
                {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4 text-amber-700" />}
              </div>

              <div className={`max-w-[80%] p-3.5 rounded-2xl text-xs space-y-1 ${
                msg.sender === 'user'
                  ? 'bg-emerald-600 text-white rounded-tr-none shadow-xs'
                  : 'bg-white text-slate-800 border border-slate-200/90 rounded-tl-none shadow-xs'
              }`}>
                <p className="font-semibold leading-relaxed">{msg.text}</p>
                <span className={`text-[9px] block text-right font-medium ${msg.sender === 'user' ? 'text-emerald-200' : 'text-slate-400'}`}>
                  {msg.timestamp}
                </span>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex items-center gap-2 text-slate-400 text-xs font-bold pl-2 animate-pulse">
              <Bot className="w-4 h-4 text-emerald-600" />
              <span>AI is evaluating soil & microclimate data...</span>
            </div>
          )}
        </div>

        {/* Quick Questions & Input Footer */}
        <div className="p-3 bg-white border-t border-slate-200 space-y-2">
          {/* Quick Suggestions */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 no-scrollbar">
            {QUICK_QUESTIONS.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(q)}
                className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200/80 whitespace-nowrap flex-shrink-0 transition-colors cursor-pointer"
              >
                {q}
              </button>
            ))}
          </div>

          {/* Form Controls */}
          <form
            onSubmit={(e) => {
              e.preventDefault()
              handleSend()
            }}
            className="flex items-center gap-2"
          >
            <button
              type="button"
              className="p-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors cursor-pointer"
              title="Voice Input (Gujarati / Hindi / English)"
            >
              <Mic className="w-4 h-4 text-emerald-600" />
            </button>

            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about your crops, water, or pests..."
              className="flex-1 px-3.5 py-2.5 rounded-xl bg-slate-100 text-xs font-medium text-slate-900 border border-slate-200 focus:outline-none focus:border-emerald-500 focus:bg-white"
            />

            <button
              type="submit"
              disabled={!input.trim()}
              className="p-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold transition-all disabled:opacity-50 cursor-pointer shadow-xs"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>

      </div>
    </div>
  )
})
