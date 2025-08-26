import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Space, Button, Badge } from 'antd'
import { 
  DashboardOutlined, 
  AppstoreOutlined, 
  TeamOutlined,
  RocketOutlined,
  ReloadOutlined,
  LoadingOutlined
} from '@ant-design/icons'
import { useLoading } from '../../contexts/LoadingContext'
import './Header.css'

const { Header: AntHeader } = Layout

const Header = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { isLoading } = useLoading()

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '概览',
    },
    {
      key: '/queues',
      icon: <AppstoreOutlined />,
      label: '队列',
    },
    {
      key: '/workers',
      icon: <TeamOutlined />,
      label: 'Workers',
    },
  ]

  const handleMenuClick = ({ key }) => {
    navigate(key)
  }

  const handleRefresh = () => {
    window.location.reload()
  }

  return (
    <AntHeader className="app-header">
      <div className="header-container">
        <div className="header-left">
          <div className="app-logo">
            {isLoading ? (
              <LoadingOutlined 
                className="logo-icon"
                style={{ 
                  fontSize: 24,
                  color: '#1890ff'
                }} 
                spin 
              />
            ) : (
              <RocketOutlined className="logo-icon" />
            )}
            <span className="logo-text">JetTask Monitor</span>
          </div>
        </div>
        
        <div className="header-center">
          <Menu
            mode="horizontal"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={handleMenuClick}
            className="header-menu"
          />
        </div>
        
        <div className="header-right">
          <Space>
            <Badge dot status="success">
              <Button 
                type="text" 
                icon={<ReloadOutlined />} 
                onClick={handleRefresh}
                className="refresh-btn"
              >
                刷新
              </Button>
            </Badge>
          </Space>
        </div>
      </div>
    </AntHeader>
  )
}

export default Header