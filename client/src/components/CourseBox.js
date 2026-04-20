import React from 'react';

export default function CourseBox({ image, title, enrolment, level, note, instructor, onClick }) {
  return (
    <div className='course-box'>
      
      <div className='image-wrapper'>
        <img src={image} alt='course' />

        <div className='level-tag'>{level}</div>
        <div className='enrolment-tag'>
          {enrolment ? "Open" : "Closed"}
        </div>
      </div>

      <h2>{title}</h2>
      <p>{note}</p>

      <div className='course-footer'>
        <div>
          <p>Instructor</p>
          <p className='instructor'>{instructor}</p>
        </div>

        <button onClick={onClick}>View Roadmap</button>
      </div>

    </div>
  );
}