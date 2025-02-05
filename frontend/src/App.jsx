// import React from "react";
// import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
// // import FileUpload from "./components/FileUpload";
// import QuestionInput from "./components/QuestionInput";
// import "./components/styles.css";
// import LegalDocumentCreator from "./components/LegalDocumentCreator";
// const App = () => {
//   return (
//     <Router>
//       <div>
//         <Routes>
//           <Route path="/" element={
//             <div>
//               <h1>Legal Chatbot</h1>
//               {/* <FileUpload /> */}
//               <QuestionInput />
//               <div>
//                 <Link to="/create-document">
//                   <button className="create-document-button">Create Legal Document</button>
//                 </Link>
//               </div>
//             </div>
//           } />
//           <Route path="/create-document" element={<LegalDocumentCreator />} />
//         </Routes>
//       </div>
//     </Router>
//   );
// };

// export default App;
import SplitText from "./assets/SplitText";
import React from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import QuestionInput from "./components/QuestionInput";
import LegalDocumentCreator from "./components/LegalDocumentCreator";
import PrecedenceFinder from "./components/PrecedenceFinder";
import "./App.css";

const Home = () => {
  return (
    <div className="home-container">
      <SplitText text="Welcome to Legal Chatbot" className="mainheading"/>
      <div className="button-group">
        <Link to="/ask-question">
          <button className="nav-button"><a class="btn2"><span class="spn2">IPC Section FInder</span></a></button>
        </Link>
        <Link to="/create-document">
        <button className="nav-button"><a class="btn2"><span class="spn2">Legal Document Creator</span></a></button>
        </Link>
        <Link to="/find-precedents">
        <button className="nav-button"><a class="btn2"><span class="spn2">Precedence Finder</span></a></button>
        </Link>
      </div>
    </div>
  );
};

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/ask-question" element={<QuestionInput />} />
        <Route path="/create-document" element={<LegalDocumentCreator />} />
        <Route path="/find-precedents" element={<PrecedenceFinder />} />
      </Routes>
    </Router>
  );
};

export default App;