import Navbar from "./components/Navbar";
import { BrowserRouter,Routes,Route } from "react-router-dom";
import Home from './components/Home'
import Courses from './components/Courses'
import Dashboard from './components/Dashboard'
import Chat from './components/Chat'
import Subscription from './components/Subscription'
import Help from './components/Help'
import CourseRoadmap from "./components/CourseRoadmap";

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home/>}/>
        <Route path="/courses" element={<Courses/>}/>
        <Route path="/dashboard" element={<Dashboard/>}/>
        <Route path="/chat" element={<Chat/>}/>
        <Route path="/subscription" element={<Subscription/>}/>
        <Route path="/help" element={<Help/>}/> 
        <Route path="/courseRoadmap" element={<CourseRoadmap/>}/>
     </Routes>
  </BrowserRouter>
  );
}

export default App;