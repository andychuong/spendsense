import { useParams } from 'react-router-dom'

const RecommendationDetail = () => {
  const { id } = useParams()
  
  return (
    <div>
      <h1>Recommendation Detail</h1>
      <p>Recommendation ID: {id}</p>
      <p>Recommendation detail page - to be implemented in Task 11.4</p>
    </div>
  )
}

export default RecommendationDetail

