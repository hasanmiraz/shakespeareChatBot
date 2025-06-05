import React from 'react';
import ChatPage from './ChatPage';

const App: React.FC = () => {
  return (
    <div className="h-screen bg-gray-900 flex items-center justify-center">
      <div className="w-1/2 h-full">
        <ChatPage />
      </div>
    </div>
  );
};

export default App;
