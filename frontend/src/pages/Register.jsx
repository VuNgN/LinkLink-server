import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import '../styles/App.css'

async function fetchWithAuth(url, options = {}, navigate) {
  let res = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${localStorage.getItem('access_token')}`,
    },
  })
  if (res.status === 401 || res.status === 403) {
    // Thử refresh token
    const refresh = localStorage.getItem('refresh_token')
    if (refresh) {
      const refreshRes = await fetch('/api/v1/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refresh })
      })
      if (refreshRes.ok) {
        const data = await refreshRes.json()
        localStorage.setItem('access_token', data.access_token)
        // Thử lại request gốc
        res = await fetch(url, {
          ...options,
          headers: {
            ...options.headers,
            Authorization: `Bearer ${data.access_token}`,
          },
        })
      } else {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        navigate('/login')
        throw new Error('Phiên đăng nhập hết hạn!')
      }
    } else {
      navigate('/login')
      throw new Error('Chưa đăng nhập!')
    }
  }
  return res
}

export default function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    if (password !== confirm) {
      setError('Mật khẩu không khớp!')
      return
    }
    try {
      const res = await fetch('/api/v1/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.detail || 'Lỗi đăng ký!')
        return
      }
      setMessage(data.message || 'Đăng ký thành công!')
      setTimeout(() => navigate('/login'), 2000)
    } catch (err) {
      setError('Lỗi đăng ký!')
    }
  }

  return (
    <div style={{ minHeight: '100vh', width: '100%', maxWidth: '100vw', boxSizing: 'border-box', background: 'var(--color-background, #fff)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0, margin: 0, overflowX: 'hidden' }}>
      <form onSubmit={handleSubmit} style={{ background: 'var(--color-surface)', padding: 32, borderRadius: 16, boxShadow: '0 2px 16px #7C4DFF22', width: '100%', maxWidth: 400, margin: '0 8px' }}>
        <h2 style={{ color: 'var(--color-primary)', marginBottom: 16, textAlign: 'center' }}>Đăng ký</h2>
        <div style={{ marginBottom: 16 }}>
          <input type="text" placeholder="Tên đăng nhập" value={username} onChange={e => setUsername(e.target.value)} required style={{ width: '100%', padding: 12, borderRadius: 8, border: '1px solid #eee', marginBottom: 8 }} />
          <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required style={{ width: '100%', padding: 12, borderRadius: 8, border: '1px solid #eee', marginBottom: 8 }} />
          <input type="password" placeholder="Mật khẩu" value={password} onChange={e => setPassword(e.target.value)} required style={{ width: '100%', padding: 12, borderRadius: 8, border: '1px solid #eee', marginBottom: 8 }} />
          <input type="password" placeholder="Nhập lại mật khẩu" value={confirm} onChange={e => setConfirm(e.target.value)} required style={{ width: '100%', padding: 12, borderRadius: 8, border: '1px solid #eee' }} />
        </div>
        {error && <div style={{ color: 'var(--color-error)', marginBottom: 12, textAlign: 'center' }}>{error}</div>}
        {message && <div style={{ color: 'var(--color-primary)', marginBottom: 12, textAlign: 'center' }}>{message}</div>}
        <button type="submit" style={{ width: '100%', background: 'var(--color-primary)', color: 'var(--color-on-primary)', padding: 12, border: 'none', borderRadius: 8, fontWeight: 600, fontSize: 16, cursor: 'pointer', marginBottom: 8 }}>Đăng ký</button>
        <div style={{ textAlign: 'center', fontSize: 14 }}>
          Đã có tài khoản? <Link to="/login" style={{ color: 'var(--color-primary)', textDecoration: 'underline' }}>Đăng nhập</Link>
        </div>
      </form>
    </div>
  )
} 