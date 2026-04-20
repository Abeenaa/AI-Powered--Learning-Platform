import React, { useState } from 'react';
import CourseBox from './CourseBox';
import { data } from './CoursesData';
import { Aidata } from './AiData';
import '../styles/courses.css';
import AiRecommendation from './AiRecommendation';
import CourseRoadmap from './CourseRoadmap';
import Footer from './Footer';

export default function Courses() {

  const [selectedCourse, setSelectedCourse] = useState(null);

  return (
    <div>
      <div className='course-container'>
        <h1>Course <span>Catalog</span></h1>
        <p>Choose a roadmap and start building your future.</p>

        <div className='courses-content'>

          {selectedCourse ? (
            <CourseRoadmap course={selectedCourse} />
          ) : (
            <div className='courses-box'>
              {data.map((course, index) => (
                <CourseBox
                  key={index}
                  image={course.img}
                  title={course.title}
                  level={course.level}
                  enrolment={course.enrolment}
                  note={course.note}
                  instructor={course.instructor}
                  onClick={() => setSelectedCourse(course)}
                />
              ))}
            </div>
          )}

          <div className='course-ai'>
            <h2>AI <span>Recommendations</span></h2>
            <p>Personalized for you</p>

            <div>
              {Aidata.map((item, index) => (
                <AiRecommendation
                  key={index}
                  title={item.title}
                  reason={item.reason}
                  price={item.price}
                  onClick={() => setSelectedCourse(item)}
                />
              ))}
            </div>
          </div>

        </div>
      </div>

      <Footer />
    </div>
  );
}