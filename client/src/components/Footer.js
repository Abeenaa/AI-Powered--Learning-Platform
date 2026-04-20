import React from 'react'
import logo from '../assets/images/logo.png'
import '../styles/footer.css'
import { Link } from 'react-router-dom';
import { FaPhoneAlt, FaEnvelope, FaMapMarkerAlt } from "react-icons/fa";
import { FaLinkedin, FaGithub, FaTwitter, FaInstagram } from "react-icons/fa";
export default function Footer() {
  return (
    <div className='footer'>
<div className='footer-container'>
      <div className='footer-logo'>
          <img src={logo} alt='logo' />
          <p>Personalized learning paths generated specifically for your career goals. Empowering the next generation of engineers with AI-driven roadmaps.</p>
         <div className="social-icons">
              <Link href="#"><FaLinkedin className='i' /></Link>
              <Link href="#"><FaGithub className='i'/></Link>
              <Link href="#"><FaTwitter className='i'/></Link>
              <Link href="#"><FaInstagram className='i'/></Link>
         </div>
     </div>
     <div className='platform'>
        <ul>
            <li><h3>Platform</h3></li>
            <li><Link href="">Course Catalog</Link></li>
            <li><Link href="">Student Dashboard</Link></li>
            <li><Link href="">Subscription Plans</Link></li>
            <li><Link href="">Help Center</Link></li>
        </ul>
     </div>
     <div className='support'>
        <ul>
            <li><h3>Support</h3></li>
            <li><Link href="">FAQ</Link></li>
            <li><Link href="">Contact Support</Link></li>
            <li><Link href="">Privacy Policy</Link></li>
            <li><Link href="">Terms of Service</Link></li>
        </ul>
     </div>
     <div className='get-intouch'>
        <ul>
            <li><h3>Get in Touch</h3></li>
            <li><Link href=""> <FaEnvelope className='i'/>support@eduai.com</Link></li>
            <li><Link href=""><FaPhoneAlt className='i'/>+251 912 345 678</Link></li>
            <li><Link href="">   <FaMapMarkerAlt className='i'/>Bole, Addis Ababa, Ethiopia</Link></li>
            
        </ul>
     </div>
</div>
<div className='bottom-footer'>
        <p>© 2026 Next Learning Platform. All rights reserved.</p>
     </div>
     </div>
  )
}

