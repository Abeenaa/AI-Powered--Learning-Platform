import React from 'react'

export default function AiRecommendation({price,reason,title}) {
  return (
    <div className='ai-box'>
      <p>{reason}</p>
  <h4>{title}</h4>
    <p><span>$ </span>{price}</p>
    </div>
  )
}
