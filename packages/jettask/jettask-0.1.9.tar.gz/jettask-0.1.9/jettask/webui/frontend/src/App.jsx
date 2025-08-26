import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Layout, ConfigProvider } from 'antd'
import Header from './components/layout/Header'
import Dashboard from './pages/Dashboard'
import Queues from './pages/Queues'
import Workers from './pages/Workers'
import QueueDetail from './pages/QueueDetail'
import { LoadingProvider } from './contexts/LoadingContext'
import './App.css'

const { Content } = Layout

function App() {
  return (
    <ConfigProvider>
      <LoadingProvider>
        <Router>
          <Layout className="app-layout">
            <Header />
            <Content className="main-content">
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/queues" element={<Queues />} />
                <Route path="/queues/:queueName" element={<QueueDetail />} />
                <Route path="/workers" element={<Workers />} />
              </Routes>
            </Content>
          </Layout>
        </Router>
      </LoadingProvider>
    </ConfigProvider>
  )
}

export default App