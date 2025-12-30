import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE = 'http://localhost:8000/api'

function App() {
  const [isStreaming, setIsStreaming] = useState(false)
  const [detections, setDetections] = useState({ faces: [], objects: [] })
  const [personName, setPersonName] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [persons, setPersons] = useState([])
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)
  const intervalRef = useRef(null)

  useEffect(() => {
    loadPersons()
    return () => {
      stopStreaming()
    }
  }, [])

  const loadPersons = async () => {
    try {
      const response = await axios.get(`${API_BASE}/persons`)
      setPersons(response.data)
    } catch (error) {
      console.error('Error loading persons:', error)
    }
  }

  const startStreaming = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 1280, height: 720 } 
      })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        videoRef.current.play()
        setIsStreaming(true)
        
        // Start detection loop
        intervalRef.current = setInterval(() => {
          captureAndDetect()
        }, 500) // Detect every 500ms
      }
    } catch (error) {
      console.error('Error accessing camera:', error)
      alert('Error accessing camera. Please allow camera permissions.')
    }
  }

  const stopStreaming = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
    setIsStreaming(false)
  }

  const captureAndDetect = async () => {
    if (!videoRef.current || !canvasRef.current) return

    const video = videoRef.current
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')

    // Set canvas size to match video
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    // Draw current frame to canvas
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    // Convert to blob and send to API
    canvas.toBlob(async (blob) => {
      try {
        const formData = new FormData()
        formData.append('file', blob, 'frame.jpg')

        const response = await axios.post(`${API_BASE}/detect`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })

        setDetections(response.data)
        drawDetections(ctx, response.data)
      } catch (error) {
        console.error('Error detecting:', error)
      }
    }, 'image/jpeg', 0.8)
  }

  const drawDetections = (ctx, data) => {
    // Clear canvas
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height)
    
    // Draw video frame
    if (videoRef.current) {
      ctx.drawImage(videoRef.current, 0, 0, ctx.canvas.width, ctx.canvas.height)
    }

    // Draw face detections (green for known, red for unknown)
    data.faces.forEach(face => {
      const [x1, y1, x2, y2] = face.bbox
      ctx.strokeStyle = face.is_known ? '#00ff00' : '#ff0000'
      ctx.lineWidth = 3
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1)
      
      // Draw name label
      ctx.fillStyle = face.is_known ? '#00ff00' : '#ff0000'
      ctx.font = 'bold 20px Arial'
      ctx.fillText(face.name, x1, y1 - 10)
    })

    // Draw object detections (blue)
    data.objects.forEach(obj => {
      const [x1, y1, x2, y2] = obj.bbox
      ctx.strokeStyle = '#0000ff'
      ctx.lineWidth = 2
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1)
      
      // Draw label
      ctx.fillStyle = '#0000ff'
      ctx.font = '16px Arial'
      const label = `${obj.class} (${(obj.confidence * 100).toFixed(0)}%)`
      ctx.fillText(label, x1, y1 - 10)
    })
  }

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0])
  }

  const handleUpload = async () => {
    if (!selectedFile || !personName.trim()) {
      alert('Please select an image and enter a person name')
      return
    }

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('name', personName.trim())

      await axios.post(`${API_BASE}/upload-person`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      alert(`Person ${personName} added successfully!`)
      setPersonName('')
      setSelectedFile(null)
      document.getElementById('file-input').value = ''
      loadPersons()
    } catch (error) {
      console.error('Error uploading:', error)
      alert('Error uploading person. Please try again.')
    }
  }

  const handleDeletePerson = async (personId, personName) => {
    if (!confirm(`Delete ${personName}?`)) return

    if (!personId) {
      alert('Invalid person ID')
      return
    }

    try {
      const url = `${API_BASE}/persons/${personId}`
      console.log('Deleting person:', url, 'ID:', personId, 'Type:', typeof personId)
      const response = await axios.delete(url)
      console.log('Delete response:', response.data)
      loadPersons()
      alert(`${personName} deleted successfully!`)
    } catch (error) {
      console.error('Error deleting:', error)
      console.error('Error details:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        url: error.config?.url,
        personId: personId
      })
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Error deleting person.'
      alert(`Error deleting person: ${errorMsg}`)
    }
  }

  return (
    <div className="app">
      <div className="container">
        <h1>Face Recognition System</h1>
        
        <div className="main-content">
          <div className="camera-section">
            <div className="video-container">
              <video
                ref={videoRef}
                className="video"
                autoPlay
                playsInline
                muted
                style={{ display: isStreaming ? 'block' : 'none' }}
              />
              <canvas
                ref={canvasRef}
                className="canvas"
                style={{ display: isStreaming ? 'block' : 'none' }}
              />
              {!isStreaming && (
                <div className="placeholder">
                  <p>Camera feed will appear here</p>
                  <p className="legend">
                    <span className="legend-item"><span className="box green"></span> Known Face</span>
                    <span className="legend-item"><span className="box red"></span> Unknown Face</span>
                    <span className="legend-item"><span className="box blue"></span> Object</span>
                  </p>
                </div>
              )}
            </div>
            <div className="controls">
              {!isStreaming ? (
                <button onClick={startStreaming} className="btn btn-primary">
                  Start Camera
                </button>
              ) : (
                <button onClick={stopStreaming} className="btn btn-danger">
                  Stop Camera
                </button>
              )}
            </div>
          </div>

          <div className="upload-section">
            <h2>Add Person to Database</h2>
            <div className="upload-form">
              <input
                type="text"
                placeholder="Enter person name"
                value={personName}
                onChange={(e) => setPersonName(e.target.value)}
                className="input"
              />
              <input
                id="file-input"
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="input"
              />
              <button onClick={handleUpload} className="btn btn-success">
                Upload & Add Person
              </button>
            </div>

            <div className="persons-list">
              <h3>Persons in Database ({persons.length})</h3>
              <div className="persons-grid">
                {persons.map(person => (
                  <div key={person.id} className="person-card">
                    <span>{person.name}</span>
                    <button
                      onClick={() => handleDeletePerson(person.id, person.name)}
                      className="btn btn-small btn-danger"
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

