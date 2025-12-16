import React, { useState, useEffect, useRef } from 'react';
import MessageBubble from './components/Chat/MessageBubble';
import InputArea from './components/Chat/InputArea';
import TypingIndicator from './components/Chat/TypingIndicator';
import './styles/global.css';
import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';

// Mock Endpoint - In production, this comes from ENV
// Mock Endpoint - In production, this comes from ENV
const API_ENDPOINT = import.meta.env.VITE_API_URL || "https://rdfez2226zrzbjisuw5unsk22i0xuxqh.lambda-url.us-east-1.on.aws/";

function App({ signOut, user }) {
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem('chat_history');
    if (saved) return JSON.parse(saved);
    return [{
      role: 'assistant',
      content: "Hello! I'm your **AWS Migration Assistant**. \n\nI can help you plan your cloud journey, analyze architecture diagrams, or estimate costs. \n\n*How can I help you today?*"
    }];
  });

  // Persist messages to localStorage
  useEffect(() => {
    localStorage.setItem('chat_history', JSON.stringify(messages));
  }, [messages]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (text, imagePayload) => {
    // 1. Add User Message
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // 2. Prepare Payload
      // This matches EXACTLY what migration_agent.py expects

      // Get or Create Session ID
      let sessionId = localStorage.getItem('chat_session_id');
      if (!sessionId) {
        sessionId = `session_${user?.username || 'guest'}_${Date.now()}`;
        localStorage.setItem('chat_session_id', sessionId);
      }

      const payload = {
        input: text,
        user_id: user?.username || 'guest',
        context: {
          session_id: sessionId
        },
        // If image exists, add it
        ...(imagePayload && {
          image_base64: imagePayload.payload,
          image_format: "png" // Default or detect from mime type
        })
      };

      // 3. Call API (Simulated for this demo unless backend is running)
      // Note: Since we don't have the backend running on localhost:8000 yet, 
      // I will add a mock response generator for the UI demo.


      // REAL FETCH IMPLEMENTATION:
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Server Error: ${response.status}`);
      }

      const data = await response.json();
      // Adjust based on actual server response structure
      // BedrockAgentCore usually returns { "output": ... } or direct string if simple
      // Let's assume the previous code expectation:
      let responseText = data.output || data.body || "No response content";

      // If the backend returns a dict, try to find the text
      if (typeof data === 'string') responseText = data;


      // 4. Add Agent Response
      setMessages(prev => [...prev, { role: 'assistant', content: responseText }]);

    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: `⚠️ Error: ${error.message}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header glass-card">
        <div className="logo">🚀</div>
        <div style={{ flex: 1 }}>
          <h1>AWS Migration Assistant</h1>
          <span className="badge">AgentCore Gateway</span>
        </div>

        {/* User Profile & Sign Out */}
        <div className="user-profile" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ textAlign: 'right', fontSize: '0.85rem' }}>
            <div style={{ color: 'var(--text-secondary)' }}>Welcome,</div>
            <div style={{ fontWeight: '600', color: 'var(--accent-primary)' }}>
              {user?.username || user?.signInDetails?.loginId || 'User'}
            </div>
          </div>
          <button onClick={signOut} className="sign-out-btn">
            Sign Out
          </button>
        </div>
      </header>

      <main className="chat-area">
        <div className="messages-list">
          {messages.map((msg, idx) => (
            <MessageBubble key={idx} role={msg.role} content={msg.content} />
          ))}
          {isLoading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>
      </main>

      <footer className="input-area-wrapper">
        <InputArea onSend={handleSendMessage} isDisabled={isLoading} />
      </footer>

      <style jsx="true">{`
        .app-container {
          display: flex;
          flex-direction: column;
          height: 100vh;
          background: radial-gradient(circle at 50% 10%, #1a1a2e 0%, #0f0f12 60%);
        }

        .header {
          padding: 16px 24px;
          display: flex;
          align-items: center;
          gap: 16px;
          z-index: 10;
          border-bottom: 1px solid var(--glass-border);
        }

        .logo {
          font-size: 24px;
          background: var(--bg-tertiary);
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 10px;
        }

        .header h1 {
          font-size: 1.1rem;
          font-weight: 600;
          color: var(--text-primary);
        }

        .badge {
          font-size: 0.75rem;
          background: rgba(99, 102, 241, 0.2);
          color: #818cf8;
          padding: 2px 8px;
          border-radius: 4px;
          border: 1px solid rgba(99, 102, 241, 0.3);
        }

        .chat-area {
          flex: 1;
          overflow-y: auto;
          position: relative;
        }

        .messages-list {
          padding: 24px;
          padding-bottom: 140px; /* Space for input area */
          max-width: 900px;
          margin: 0 auto;
        }

        .input-area-wrapper {
          position: absolute;
          bottom: 24px;
          left: 0;
          right: 0;
          padding: 0 24px;
          z-index: 20;
        }
        .sign-out-btn {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid var(--glass-border);
          color: var(--text-primary);
          padding: 6px 12px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.8rem;
          transition: all 0.2s;
        }
        .sign-out-btn:hover {
          background: rgba(239, 68, 68, 0.2);
          border-color: rgba(239, 68, 68, 0.4);
        }
        .auth-wrapper {
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100vh;
          background: radial-gradient(circle at 50% 10%, #1a1a2e 0%, #0f0f12 60%);
        }
      `}</style>
    </div>
  );
}

// export default App;

export default function AppWithAuth() {
  return (
    <div className="auth-wrapper">
      <Authenticator>
        {({ signOut, user }) => (
          <App signOut={signOut} user={user} />
        )}
      </Authenticator>
    </div>
  );
}
