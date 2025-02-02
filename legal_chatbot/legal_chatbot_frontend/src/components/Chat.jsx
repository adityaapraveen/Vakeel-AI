import React from "react";
import './Chat.css';

const Chat = ({ response }) => {
  // Split the response into an array of points based on ". " delimiter
  const responseArray = response.split('. ').map(item => item.trim()).filter(item => item);

  return (
    <div className="chat-container">
      <h2>Chatbot Response</h2>
      <ul>
        {responseArray.map((item, index) => (
          <li key={index}>{item}{index < responseArray.length - 1 ? '.' : ''}</li>
        ))}
      </ul>
    </div>
  );
};

export default Chat;