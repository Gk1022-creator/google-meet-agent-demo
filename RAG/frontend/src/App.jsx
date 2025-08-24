import React, { useState, useRef, useEffect } from 'react'
import './styles.css'

export default function App(){
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [usingRetrieval, setUsingRetrieval] = useState(true)
  const messagesEndRef = useRef(null)

  const sendMessage = async () => {
    if(!input.trim()) return
    const payload = { query: input, use_retrieval: usingRetrieval }
    setMessages(prev=>[...prev, {id:Date.now(), role:'user', text: input}])
    const backendURL = "http://localhost:8000";  // FastAPI backend
    try {
      const r = await fetch(`${backendURL}/chat`, { 
        method:'POST', 
        headers: {'content-type':'application/json'}, 
        body: JSON.stringify(payload)
      })
      const j = await r.json()
      setMessages(prev=>[...prev, {id:Date.now()+1, role:'assistant', text: j.text || 'No answer'}])
      setInput('')
    } catch(e){
      setMessages(prev=>[...prev, {id:Date.now()+1, role:'assistant', text: 'Error: '+String(e)}])
    }
  }

  // Auto scroll to latest message
  useEffect(()=>{
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  return (
    <div className="chat-root">
      <header><h2>Meeting Agent</h2></header>
      
      <div className="controls">
        <label>
          <input 
            type="checkbox" 
            checked={usingRetrieval} 
            onChange={e=>setUsingRetrieval(e.target.checked)} 
          /> Use retrieval
        </label>
      </div>

      <div className="messages">
        {messages.map(m=>(
          <div className={'msg '+m.role} key={m.id}>
            <div className="role">{m.role}</div>
            <div className="txt">{m.text}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="composer">
        <input 
          value={input} 
          onChange={e=>setInput(e.target.value)} 
          placeholder="Ask about meetings..." 
          onKeyDown={e=>e.key==='Enter' && sendMessage()} 
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  )
}
