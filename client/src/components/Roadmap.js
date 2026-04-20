import React from 'react'
import { FaCheck, FaLock } from "react-icons/fa";
import { IoPlay } from "react-icons/io5";
import '../styles/Home.css'
export default function Roadmap() {
  return (
    <div className='roadmap-text'>
      <div className='roadmap-content'>
        <h1>Interactive<span> Progress Tracking</span></h1>
        <p className='roadmap-desc'>Experience a unique UI where your learning journey is visualized. See what's next, track your accomplishments, and stay motivated with clear milestones.</p>
        <ul>
            <li>Automatic prerequisite unlocking</li>
            <li>Personalized AI adaptive learning</li>
            <li>Certificates of completion </li>
        </ul>
      </div>
       <div className="roadmap-container">
      <div className="header">
        <div>
          <h2>React Architecture Mastery</h2>
          <p>ROADMAP PREVIEW</p>
        </div>
        <div className="progress">
          <h3>25%</h3>
          <span>COMPLETE</span>
        </div>
      </div>

      <div className="timeline">
        {/* Completed */}
        <div className="item">
          <div className="icon completed">
            <FaCheck />
          </div>
          <div className="content">
            <h4>Introduction to React 19</h4>
            <p>Module finished</p>
          </div>
          <span className="time">15m</span>
        </div>

       
        <div className="item">
          <div className="icon active">
            <IoPlay />
          </div>
          <div className="content">
            <h4>State Management with AI</h4>
            <p>Ready to start</p>
          </div>
          <span className="time">25m</span>
        </div>
        <div className="item locked">
          <div className="icon">
            <FaLock />
          </div>
          <div className="content">
            <h4>Server Components Deep Dive</h4>
            <p>Locked until previous module is complete</p>
          </div>
          <span className="time">40m</span>
        </div>

        <div className="item locked">
          <div className="icon">
            <FaLock />
          </div>
          <div className="content">
            <h4>Performance Optimization</h4>
            <p>Locked until previous module is complete</p>
          </div>
          <span className="time">35m</span>
        </div>
      </div>
    </div>
    </div>
  )
}
