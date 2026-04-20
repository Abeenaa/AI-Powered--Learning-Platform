import React from 'react';
import { FaCheck, FaLock,FaArrowLeft} from "react-icons/fa";
import { IoPlay } from "react-icons/io5";
import "../styles/courseRoadmap.css"
import { Link } from 'react-router-dom'
export default function CourseRoadmap({ course }) {
  return (
    <div className='courseRoadmap-text'>
       <div>
       <Link to="/courses">
  <button className="back-btn">
    <FaArrowLeft /> Back to catalog
  </button>
</Link>
<div className='row'>
<p className='course-level'>{course.level}</p>
<p>{course.price}</p> 
</div>
          <h1>{course.title}</h1>
        </div>
      <div className="courseRoadmap-container">
        <div className="course-header">
          <div>
            <h2>{course.title} Mastery</h2>
            <p>ROADMAP PREVIEW</p>
          </div>

          <div className="course-progress">
            <h3>25%</h3>
            <span>COMPLETE</span>
          </div>
        </div>

        <div className="course-timeline">

          <div className="course-item">
            <div className="course-icon active">
               <IoPlay />
            </div>
            <div className="course-content">
              <h4>Introduction to {course.title}</h4>
              <p>Module finished</p>
            </div>
            <span className="course-time">15m</span>
          </div>

          <div className="course-item locked">
            <div className="course-icon locked">
             <FaLock />
            </div>
            <div className="course-content">
              <h4>Core Concepts</h4>
              <p>Ready to start</p>
            </div>
            <span className="course-time">25m</span>
          </div>

          <div className="course-item locked">
            <div className="course-icon">
              <FaLock />
            </div>
            <div className="course-content">
              <h4>Advanced Topics</h4>
              <p>Locked until previous module is complete</p>
            </div>
            <span className="course-time">40m</span>
          </div>

        </div>
      </div>
    </div>
  );
}