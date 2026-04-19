import React from 'react'
import '../styles/Home.css'
import { IoSearchOutline } from "react-icons/io5";
import {Link} from 'react-router-dom'
import { FaGraduationCap } from "react-icons/fa";
import { IoFlashOutline } from "react-icons/io5";
import { RiRobot2Line } from "react-icons/ri";
import { IoPersonOutline } from "react-icons/io5";
import Card from './Card';
import Roadmap from './Roadmap';
import Works from './Works';
import Journey from './Journey';
export default function Home() {

  return (
    <div>
    <div className='home'>
     
       <div className='home-container'>
        
        <h1>Learn Smarter with <span>AI-Powered Roadmaps</span></h1>
        <p className='description'>Skip the generic tutorials. Get a personalized learning path generated specifically for your career goals, with real-time AI assistance.</p>
        <div className='search-bar'>
              <IoSearchOutline size={22} className='search-icon'/>
              <input placeholder='What do want to learn?'/>
              <button>Generate Roadmap</button>
        </div>
        <div className='home-btns'>
          <button className='course-btn'><Link>Browse Courses</Link></button>
          <button className='dashboard-btn'><Link>Student Dashboard</Link></button>
        </div>
       </div>
    </div>
    <div className='cards'>
      <Card icon={<IoPersonOutline/>} title="Chat Support" description="Direct access to peers and AI mentors for whenever you get stuck."/>
       <Card icon={<IoFlashOutline style={{color:"purple"}}/>} title="Roadmap Learning" description="Stop jumping between random videos. Follow a structured path to mastery."/>
        <Card icon={< RiRobot2Line style={{color:"green"}}/>} title="AI Recommendations" description="Courses and lessons tailored to your specific speed and background."/>
    </div>
    <Roadmap/>
    <Works/>
    <Journey/>
    </div>
  )
}
