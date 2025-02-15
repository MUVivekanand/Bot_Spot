import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import FakeAccountChecker from "./FakeAccountChecker";
import TwitterChecker from "./TwitterChecker";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<FakeAccountChecker />} />
        <Route path="/twitter" element={<TwitterChecker />} />
      </Routes>
    </Router>
  );
}
