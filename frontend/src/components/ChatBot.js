import React, { useState } from 'react';

const ChatBot = () => {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hi! Ask me anything about your data, request a graph, or ask for a SQL query.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage = { sender: 'user', text: input };
    setMessages((msgs) => [...msgs, userMessage]);
    setInput('');
    setLoading(true);
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });
      const data = await res.json();
      if (data.type === 'graph' && data.plot_urls) {
        setMessages((msgs) => [
          ...msgs,
          { sender: 'bot', text: data.text },
          ...data.plot_urls.map((url) => ({ sender: 'bot', image: url }))
        ]);
      } else if (data.type === 'sql' && data.sql) {
        setMessages((msgs) => [
          ...msgs,
          { sender: 'bot', text: data.text },
          { sender: 'bot', sql: data.sql }
        ]);
      } else {
        setMessages((msgs) => [...msgs, { sender: 'bot', text: data.text }]);
      }
    } catch (err) {
      setMessages((msgs) => [...msgs, { sender: 'bot', text: 'Sorry, something went wrong.' }]);
    }
    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <div className="card p-4 max-w-xl mx-auto mt-8">
      <h2 className="text-lg font-semibold mb-2">Chat with Data Explorer</h2>
      <div className="h-64 overflow-y-auto bg-secondary-50 p-2 rounded mb-2 border border-secondary-200">
        {messages.map((msg, idx) => (
          <div key={idx} className={`mb-2 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
            {msg.text && <div className={`inline-block px-3 py-2 rounded ${msg.sender === 'user' ? 'bg-primary-100 text-primary-800' : 'bg-secondary-200 text-secondary-900'}`}>{msg.text}</div>}
            {msg.sql && <pre className="bg-gray-100 text-blue-700 p-2 rounded mt-1">{msg.sql}</pre>}
            {msg.image && <img src={msg.image} alt="Graph" className="max-w-xs rounded shadow mt-2" />}
          </div>
        ))}
        {loading && <div className="text-secondary-500">Thinking...</div>}
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 border border-secondary-300 rounded px-3 py-2"
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask for a graph, SQL, or data insight..."
          disabled={loading}
        />
        <button className="btn-primary" onClick={sendMessage} disabled={loading}>Send</button>
      </div>
    </div>
  );
};

export default ChatBot; 