import React, { useState, useRef, useEffect } from 'react';
import { Mic, Send, Volume2, Globe, Sparkles } from 'lucide-react';

const SUGGESTIONS = {
  0: ["How to save ₹20?", "Why avoid local lenders?", "Explain money tracking"],
  1: ["Log ₹10 saved", "What is a goal pocket?", "Show my streak details"],
  2: ["Emergency fund target", "PM-JAY health plan", "How much liquid buffer?"],
  3: ["Interest cost calculator", "Snowball method details", "Loan app safety guide"],
  4: ["Explain PPF basics", "How does RD work?", "Start a ₹500 SIP"],
  5: ["Diversification advice", "Explain index funds", "Tax saving schemes"]
};

export default function VoiceChat({ profile, onProfileUpdate }) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState(profile?.persona?.language || 'Hindi');
  const [autoSpeak, setAutoSpeak] = useState(true); // Default to auto-speak enabled for voice-first experience
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const chatEndRef = useRef(null);

  // Sync messages from profile history
  useEffect(() => {
    if (profile?.chatHistory) {
      setMessages(profile.chatHistory);
    }
    if (profile?.persona?.language) {
      setLanguage(profile.persona.language);
    }
  }, [profile]);

  // Scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Browser Text-To-Speech function using Web Speech API
  const speakText = (text) => {
    if (!window.speechSynthesis) {
      console.warn("Text-to-speech not supported in this browser.");
      return;
    }
    
    // Cancel any active speaking
    window.speechSynthesis.cancel();
    
    // Remove markdown symbols (bolding, stars) for cleaner reading
    const cleanText = text.replace(/[*#_`]/g, '');
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    
    // Choose appropriate locale voice code
    let langCode = 'hi-IN';
    if (language === 'English') langCode = 'en-IN';
    else if (language === 'Kannada') langCode = 'kn-IN';
    else if (language === 'Tamil') langCode = 'ta-IN';
    else if (language === 'Marathi') langCode = 'mr-IN';
    
    utterance.lang = langCode;
    
    // Load voices and try to assign
    const voices = window.speechSynthesis.getVoices();
    const matchingVoice = voices.find(v => v.lang.includes(langCode) || v.lang === langCode);
    if (matchingVoice) {
      utterance.voice = matchingVoice;
    }
    
    window.speechSynthesis.speak(utterance);
  };

  const handleSendMessage = async (textToSend) => {
    if (!textToSend.trim() || loading) return;
    
    // Stop speaking when user submits a new prompt
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }

    // Optimistically add user message
    const userMsg = { role: 'user', content: textToSend };
    setMessages(prev => [...prev, userMsg]);
    setInputText('');
    setLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: profile.userId,
          message: textToSend
        }),
      });

      if (!response.ok) throw new Error('API communication error');
      
      const data = await response.json();
      setMessages(data.profile.chatHistory);
      onProfileUpdate(data.profile);
      
      // Speak response if enabled
      if (autoSpeak && data.response) {
        speakText(data.response);
      }
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Connection issue. Please verify the backend is running.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Browser voice capture recording
  const startRecording = async () => {
    if (recording) return;
    audioChunksRef.current = [];
    
    // Stop speaking when recording begins
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = recorder;
      
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await uploadAudio(audioBlob);
        
        // Stop all audio tracks to free mic
        stream.getTracks().forEach(track => track.stop());
      };

      recorder.start(100);
      setRecording(true);
    } catch (err) {
      alert('Could not access microphone: ' + err.message);
    }
  };

  const stopRecording = () => {
    if (!recording) return;
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  const uploadAudio = async (audioBlob) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('userId', profile.userId);
    formData.append('file', audioBlob, 'user_audio.webm');

    try {
      // Optimistically alert user
      setMessages(prev => [...prev, { role: 'user', content: '🎤 [Voice Recording Sent...]' }]);
      
      const response = await fetch('http://127.0.0.1:8000/api/voice-upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Voice translation error');
      
      const data = await response.json();
      
      // Update with matching chat history
      setMessages(data.profile.chatHistory);
      onProfileUpdate(data.profile);
      
      // Speak response if enabled
      if (autoSpeak && data.response) {
        speakText(data.response);
      }
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Apologies. I had trouble reading your voice recording. Try typing instead.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const currentLevel = profile?.seedhiLevel ?? 0;
  const currentSuggestions = SUGGESTIONS[currentLevel] || SUGGESTIONS[0];

  return (
    <div className="assistant-card">
      <div className="assistant-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div className="assistant-avatar">CS</div>
          <div>
            <h4 style={{ margin: 0, fontSize: '0.95rem' }}>ChillarSaathi</h4>
            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Sparkles size={12} color="#c5a880" /> Voice-first Coach
            </span>
          </div>
        </div>

        {/* Auto Speak Toggle Switch */}
        <button 
          onClick={() => {
            const nextVal = !autoSpeak;
            setAutoSpeak(nextVal);
            if (!nextVal && window.speechSynthesis) {
              window.speechSynthesis.cancel();
            }
          }}
          style={{
            background: autoSpeak ? 'var(--color-primary)' : 'none',
            border: autoSpeak ? 'none' : '1px solid var(--color-border)',
            color: autoSpeak ? 'white' : 'var(--color-text-muted)',
            borderRadius: '50px',
            padding: '0.3rem 0.6rem',
            fontSize: '0.75rem',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            transition: 'all 0.2s'
          }}
          title={autoSpeak ? "Auto-speak is ON. Click to mute." : "Auto-speak is OFF. Click to unmute."}
        >
          <Volume2 size={14} />
          <span>{autoSpeak ? "Voice ON" : "Mute"}</span>
        </button>
      </div>

      <div className="assistant-chat-history">
        {messages.map((msg, index) => (
          <div 
            key={index} 
            className={`chat-bubble ${msg.role}`}
            style={{ 
              position: 'relative', 
              paddingRight: msg.role === 'assistant' ? '2rem' : '1.2rem',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <div>{msg.content}</div>
            
            {msg.role === 'assistant' && (
              <button 
                onClick={() => speakText(msg.content)}
                style={{
                  position: 'absolute',
                  right: '6px',
                  bottom: '6px',
                  background: 'none',
                  border: 'none',
                  color: 'var(--color-primary-light)',
                  cursor: 'pointer',
                  padding: '2px',
                  display: 'flex',
                  alignItems: 'center',
                  opacity: 0.7,
                  transition: 'opacity 0.2s'
                }}
                title="Listen to this message"
                onMouseEnter={e => e.currentTarget.style.opacity = 1}
                onMouseLeave={e => e.currentTarget.style.opacity = 0.7}
              >
                <Volume2 size={14} />
              </button>
            )}
          </div>
        ))}
        {loading && (
          <div className="chat-bubble assistant" style={{ fontStyle: 'italic', color: 'var(--color-text-muted)' }}>
            Thinking...
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Suggested Questions */}
      <div className="suggested-qs">
        {currentSuggestions.map((qs, i) => (
          <button 
            key={i} 
            className="suggest-btn"
            onClick={() => handleSendMessage(qs)}
            disabled={loading}
          >
            {qs}
          </button>
        ))}
      </div>

      {/* Input controls */}
      <div className="chat-input-area">
        <input 
          type="text" 
          className="chat-text-input" 
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSendMessage(inputText)}
          placeholder="Ask in Hindi, English, Hinglish..."
          disabled={loading}
        />
        
        <button 
          className="btn btn-primary"
          style={{ width: '42px', height: '42px', borderRadius: '50%', padding: 0 }}
          onClick={() => handleSendMessage(inputText)}
          disabled={loading || !inputText.trim()}
        >
          <Send size={18} />
        </button>

        <button 
          className={`chat-mic-btn ${recording ? 'recording' : ''}`}
          onMouseDown={startRecording}
          onMouseUp={stopRecording}
          onTouchStart={startRecording}
          onTouchEnd={stopRecording}
          title="Hold to Record Mic, Release to Send"
        >
          <Mic size={20} />
        </button>
      </div>
      <div style={{ textAlign: 'center', fontSize: '0.7rem', color: 'var(--color-text-muted)', paddingBottom: '0.5rem', fontWeight: 500 }}>
        {recording ? "🔴 Recording... Release mic button to send" : "🎤 Press and hold mic to speak in Hindi/regional languages"}
      </div>
    </div>
  );
}
