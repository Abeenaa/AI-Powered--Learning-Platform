
import WorkCard from './WorkCard'
import { useRef } from "react";
import { IoArrowForward, IoArrowBack } from "react-icons/io5";
export default function Works() {
  const scrollRef = useRef();

  const scroll = (direction) => {
    const amount = 300;
    if (direction === "next") {
      scrollRef.current.scrollLeft += amount;
    } else {
      scrollRef.current.scrollLeft -= amount;
    }
  };

  return (
    <div className='works-container'>
      <h1>How It Works</h1>
      <p className='work-card-text'>
        Four simple steps to master any skill with our AI platform.
      </p>

      <div className='work-cards' ref={scrollRef}>
       <WorkCard number="01" title="Pick Goals" description="Tell the AI what you want to achieve."/>
         <WorkCard number="02" title="Get Roadmap" description="Follow  step-by-step path."/>
          <WorkCard number="03" title="Learn & Chat" description="Watch lessons and chat with peers."/>
           <WorkCard number="04" title="Get Certified" description="Verify your skills with certificates."/>
      </div>

      <div className='next-prev-btn'>
        <button onClick={() => scroll("prev")}>  <IoArrowBack size={22} /></button>
        <button onClick={() => scroll("next")}> <IoArrowForward size={22} /></button>
      </div>
    </div>
  );
}