import React from "react";

const Chat = ({ response }) => {
  return (
    <div>
      <h2>Chatbot Response</h2>
      <p>{response}</p>
    </div>
  );
};

export default Chat;
