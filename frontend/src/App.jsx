import React from "react";
import FileUpload from "./components/FileUpload";
import QuestionInput from "./components/QuestionInput";

const App = () => {
  return (
    <div>
      <h1>Multi-PDF Chatbot</h1>
      <FileUpload />
      <QuestionInput />
    </div>
  );
};

export default App;
