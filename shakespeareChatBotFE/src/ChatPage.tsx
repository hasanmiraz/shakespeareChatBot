import { useState, useRef, useEffect, FC, KeyboardEvent } from 'react';

type Message = {
  sender: 'user' | 'assistant';
  text: string;
};

type ChatResponse = {
  query: string;
  response: string;
};

const ChatPage: FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    const trimmed = inputValue.trim();
    if (!trimmed) return;

    setMessages((prev) => [...prev, { sender: 'user', text: trimmed }]);
    setInputValue('');
    setIsLoading(true);

    const previousUserMessages = messages
      .filter((msg) => msg.sender === 'user')
      .map((msg) => msg.text)
      .join(' | ');

    let combinedQuery = trimmed;
    if (previousUserMessages.length > 0) {
      combinedQuery = `${trimmed}. remember previous prompts: {${previousUserMessages.replace(/\?/g, '')}}`;
    }

    try {
      const encoded = encodeURIComponent(combinedQuery);
      const res = await fetch(`http://127.0.0.1:8000/chatbot/${encoded}`, {
        method: 'GET',
      });

      const data: ChatResponse = await res.json();
      console.log('FastAPI returned:', data);

      const assistantReply = data.response;
      setMessages((prev) => [
        ...prev,
        { sender: 'assistant', text: assistantReply },
      ]);
    } catch (err) {
      console.error('Error talking to /chatbot:', err);
      setMessages((prev) => [
        ...prev,
        { sender: 'assistant', text: 'Error: could not reach server.' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading) sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full p-7 rounded-lg shadow-lg overflow-hidden">
      <header className="p-4 border-b border-gray-700 bg-gray-800 rounded-lg">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white">Gonzago</h1>
          <h2 className="text-lg font-medium text-white">Your digital Shakespeare expert</h2>
        </div>
        <p className="mt-1 text-sm text-blue-200">
          Ask Gonzago about characters, events, scenes and themes in Shakespeare's plays!
        </p>
        <p className="mt-2 text-sm text-gray-300 italic">
          You can help Gonzago by specifying the Act and Scene name, eg: "What does the ghost say to Hamlet in Act I, Scene 1?".
        </p>
      </header>

      <main className="flex-grow p-4 overflow-y-auto bg-gray-900">
        <div className="flex flex-col space-y-2">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`
                max-w-[70%] px-4 py-2 rounded-lg whitespace-pre-wrap break-words
                ${msg.sender === 'user'
                  ? 'bg-blue-600 text-white self-end ml-auto rounded-tr-none'
                  : 'bg-gray-700 text-gray-100 self-start mr-auto rounded-tl-none'}
              `}
            >
              {msg.text}
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      </main>

      <footer className="p-4 border-t border-gray-700 bg-gray-800 flex rounded-lg">
        <textarea
          className="flex-grow resize-none border border-gray-600 rounded-md p-2 text-sm bg-gray-700 text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Type your message..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={isLoading}
        />
        <button
          className={`
            ml-2 px-4 py-2 rounded-md text-sm font-medium
            ${isLoading || !inputValue.trim()
              ? 'bg-blue-600 opacity-50 cursor-not-allowed'
              : 'bg-blue-500 hover:bg-blue-600'}
            text-white
          `}
          onClick={sendMessage}
          disabled={isLoading || !inputValue.trim()}
        >
          {isLoading ? '…' : 'Send'}
        </button>
      </footer>
    </div>
  );
};

export default ChatPage;
